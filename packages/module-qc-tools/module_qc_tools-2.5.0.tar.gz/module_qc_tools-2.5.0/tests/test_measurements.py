from __future__ import annotations

from types import SimpleNamespace

import module_qc_tools as mqt
import pytest
from module_qc_database_tools.utils import default_BOMCode_from_layer
from module_qc_tools.measurements import (
    adc_calibration,
    iv_measure,
    long_term_stability_dcs,
)
from module_qc_tools.utils.misc import (
    load_hw_config,
    load_meas_config,
)
from module_qc_tools.utils.power_supply import power_supply
from module_qc_tools.utils.yarr import yarr


@pytest.fixture(autouse=False)
def config(test_type: str, chip_type: str, bom_type: str, layer: str, nchips: int):
    config_hw = load_hw_config(
        mqt.data / "configs" / "hw_config_emulator_merged_vmux.json"
    )
    config_emulator = load_meas_config(
        mqt.data / "configs" / "meas_config.json",
        test_type=test_type,
        chip_type=chip_type,
        bom_type=bom_type,
        layer=layer,
        nchips=nchips,
    )
    config_emulator.update(config_hw)
    return config_emulator


@pytest.fixture(autouse=False)
def hardware(config):
    return SimpleNamespace(
        ps=power_supply(config["power_supply"]),
        hv=power_supply(config["high_voltage"]),
        yr=yarr(config["yarr"]),
    )


@pytest.fixture(autouse=False)
def runner(test_type: str):
    return {
        "ADC_CALIBRATION": adc_calibration.run,
        "IV_MEASURE": iv_measure.run,
        "LONG_TERM_STABILITY_DCS": long_term_stability_dcs.run,
    }[test_type]


@pytest.mark.parametrize(
    ("test_type", "chip_type", "bom_type", "layer", "nchips"),
    [("ADC_CALIBRATION", "RD53B", "_V1bom", "L1", 4)],
)
def test_issue114(config, hardware, runner):
    """
    https://gitlab.cern.ch/atlas-itk/pixel/module/module-qc-tools/-/issues/114
    """
    layer = "L1"
    BOM = default_BOMCode_from_layer(layer)

    hardware.ps.set(
        v=config["v_max"],
        i=config["i_config"],
    )
    hardware.hv.set(
        v=-80,  ## use Vop = 80V for L1 module
        i=1e-6,
    )

    data = runner(config, hardware.ps, hardware.hv, hardware.yr, BOM, False)
    metadata = data[0].get_meta_data()

    assert "ChipConfigs" in metadata
    assert "RD53B" in metadata["ChipConfigs"]
    assert "GlobalConfig" in metadata["ChipConfigs"]["RD53B"]
    assert "InjVcalRange" in metadata["ChipConfigs"]["RD53B"]["GlobalConfig"]


@pytest.mark.parametrize(
    ("test_type", "chip_type", "bom_type", "layer", "nchips"),
    [("IV_MEASURE", "RD53B", "_V1bom", "L2", 4)],
)
def test_missing_hrc_iv(config, hardware, runner):
    layer = "L2"
    config.pop("hrc", None)

    data = runner(config, hardware.ps, hardware.hv, layer)
    data = data.to_dict()
    assert "humidity" in data["Measurements"]


@pytest.mark.parametrize(
    ("test_type", "chip_type", "bom_type", "layer", "nchips"),
    [("LONG_TERM_STABILITY_DCS", "RD53B", "_V1bom", "L2", 4)],
)
def test_missing_hrc_lts(config, hardware, runner):
    config.pop("hrc", None)

    hardware.ps.on(
        v=config["v_max"],
        i=config["i_config"],
    )
    hardware.hv.on(
        v=-120,
        i=1e-6,
    )

    data = runner(config, hardware.ps, hardware.hv)
    data = data.to_dict()
    assert "LV_CURR" in data["Measurements"]


@pytest.mark.parametrize(
    ("test_type", "chip_type", "bom_type", "layer", "nchips"),
    [("LONG_TERM_STABILITY_DCS", "RD53B", "_V1bom", "L2", 4)],
)
def test_issue132(config, hardware, runner):
    """
    long-term stability dcs needs to enforce or check L1/L2 LVPS power (or set it) before running.

    https://gitlab.cern.ch/atlas-itk/pixel/module/module-qc-tools/-/issues/132
    """
    hardware.ps.on(
        v=config["v_max"],
        i=config["i_config"] + 1.0,  # enforce wrong current
    )
    hardware.hv.on(
        v=-120,
        i=1e-6,
    )

    with pytest.raises(RuntimeError, match="Module is not properly powered."):
        runner(config, hardware.ps, hardware.hv)

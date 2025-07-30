from __future__ import annotations

import json

import jsonschema
import module_qc_data_tools as mqdt
import module_qc_tools as mqt
import pytest
from module_qc_tools.cli import app
from typer.testing import CliRunner


@pytest.fixture()
def runner():
    return CliRunner(mix_stderr=False)


@pytest.fixture(scope="session")
def schema():
    return json.loads((mqdt.utils.datapath / "schema_measurement.json").read_text())


@pytest.mark.parametrize(
    ("measurement"),
    [
        "adc-calibration",
        "analog-readback",
        "data-transmission",
        "injection-capacitance",
        "iv-measure",
        "long-term-stability-dcs",
        "lp-mode",
        "overvoltage-protection",
        "sldo",
        "undershunt-protection",
        "vcal-calibration",
    ],
)
def test_measurement(measurement, runner, schema, tmp_path):
    result = runner.invoke(
        app,
        args=[
            "measurement",
            measurement,
            "-c",
            mqt.data / "configs" / "hw_config_emulator_merged_vmux.json",
            "--site",
            "TEST",
            "-o",
            f"{tmp_path}",
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 0, result.stderr

    measurements = list(tmp_path.rglob("*.json"))
    assert measurements, "No measurements found"

    for measurement in measurements:
        output = json.loads(measurement.read_text())
        jsonschema.validate(output, schema)


@pytest.mark.parametrize(
    ("measurement"),
    [
        "analog-readback",
        "injection-capacitance",
        "lp-mode",
        "overvoltage-protection",
        "sldo",
        "undershunt-protection",
        "vcal-calibration",
    ],
)
def test_measurement_adc(measurement, runner, schema, tmp_path):
    result = runner.invoke(
        app,
        args=[
            "measurement",
            measurement,
            "-c",
            mqt.data / "configs" / "hw_config_emulator_merged_vmux.json",
            "--use-calib-adc",
            "--site",
            "TEST",
            "-o",
            f"{tmp_path}",
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 0, result.stderr

    measurements = list(tmp_path.rglob("*.json"))
    assert measurements, "No measurements found"

    for measurement in measurements:
        output = json.loads(measurement.read_text())
        jsonschema.validate(output, schema)


@pytest.mark.parametrize(
    ("measurement"),
    [
        "analog-readback",
        "adc-calibration",
        "data-transmission",
        "injection-capacitance",
        "lp-mode",
        "overvoltage-protection",
        "sldo",
        "undershunt-protection",
        "vcal-calibration",
    ],
)
def test_measurement_disabledChip(measurement, runner, schema, tmp_path):
    result = runner.invoke(
        app,
        args=[
            "measurement",
            measurement,
            "-c",
            mqt.data / "configs" / "hw_config_emulator_merged_vmux.json",
            "-m",
            mqt.data
            / "emulator"
            / "configs"
            / "connectivity"
            / "20UPGXM1234567_Lx_dummy_disabledchip.json",
            "--site",
            "TEST",
            "-o",
            f"{tmp_path}",
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 0, result.stderr

    measurements = list(tmp_path.rglob("*.json"))
    assert measurements, "No measurements found"

    for measurement in measurements:
        output = json.loads(measurement.read_text())
        jsonschema.validate(output, schema)

from __future__ import annotations

import logging

import numpy as np
import typer
from module_qc_data_tools.qcDataFrame import (
    qcDataFrame,
)

from module_qc_tools.cli.globals import (
    CONTEXT_SETTINGS,
)
from module_qc_tools.utils.misc import (
    check_adc_ground,
    initialize_chip_metadata,
    inject_metadata,
    read_vmux,
)
from module_qc_tools.utils.multimeter import multimeter
from module_qc_tools.utils.ntc import ntc

logger = logging.getLogger("measurement")

app = typer.Typer(context_settings=CONTEXT_SETTINGS)

TEST_TYPE = "OVERVOLTAGE_PROTECTION"


@inject_metadata(test_type=TEST_TYPE)
def run(config, ps, hv, yr, layer, use_calib_adc):
    """
    Measurement of the overvoltage protection.

    Args:
        config (dict): Full config dictionary
        ps (Class power_supply): An instance of Class power_supply for power on and power off.
        yr (Class yarr): An instance of Class yarr for chip conifugration and change register.
        layer (str): Layer information for the module
        use_calib_adc (bool): use calibrated ADC instead of multimeter

    Returns:
        data (list): data[chip_id][vmux/imux_type].
    """
    meter = multimeter(config["multimeter"])
    module_ntc = ntc(config["ntc"])

    # measure temperature from NTC
    ntc_temperature, _status = module_ntc.read()
    sensor_bias = None
    sensor_current = None

    if hv:
        try:
            sensor_bias = hv.measV()[0]
            sensor_current = hv.measI()[0]
        except RuntimeError as rerr:
            msg = "Unable to measure HV! Please connect HV. If this is intended, run with `--no-bias`."
            raise RuntimeError(msg) from rerr
    hv_status = {"voltage": sensor_bias, "current": sensor_current}
    logger.info("hv_status " + str(hv_status))

    data = [
        qcDataFrame(
            columns=["Temperature", "SetCurrent", "Current"]
            + [f"Vmux{v_mux}" for v_mux in config["v_mux"]]
            + [f"Imux{i_mux}" for i_mux in config["i_mux"]],
            units=["C", "A", "A"]
            + ["V" for v_mux in config["v_mux"]]
            + ["V" for i_mux in config["i_mux"]],
        )
        for _ in range(yr._number_of_chips)
    ]
    initialize_chip_metadata(yr, data)

    for chip in yr._enabled_chip_positions:
        data[chip].set_x("Current", True)

    # turn off power supply before switching low power mode on
    ps.off()
    # turn on low power mode
    yr.switchLPM("on")
    # turn on power supply and configure all chips
    if yr.running_emulator():
        ps.on(v=config["v_max"], i=config["i_config"][layer])
    else:
        ps.set(
            v=config["v_max"],
            i=config["i_config"][layer],
            check=False,
        )
        ps.on()
        ps.checkTarget(v=config["v_max"], i=config["i_config"][layer])

    # Run an eye diagram
    logger.info("Running eye diagram at the start of scan")
    _eye, _status = yr.eyeDiagram(skipconfig=False)

    _status = yr.configure()

    # Check ADC ground
    if use_calib_adc:
        vmux_adc_gnd, imux_adc_gnd = check_adc_ground(yr, config)
        for i, chip in enumerate(yr._enabled_chip_positions):
            data[chip].add_meta_data("VMUX30_ADC", vmux_adc_gnd[i])
            data[chip].add_meta_data("IMUX63_ADC", imux_adc_gnd[i])

    # Increase current to trigger OVP
    ps.set(v=config["v_max"], i=config["i_ovp"][layer])

    # measure current for power supply
    current, _status = ps.measI()
    i_mea = [{} for _ in range(yr._number_of_chips)]

    # measure v_mux
    for v_mux in config["v_mux"]:
        mea_chips = read_vmux(
            meter,
            yr,
            config,
            v_mux=v_mux,
            use_adc=use_calib_adc,
        )
        for i, chip in enumerate(yr._enabled_chip_positions):
            i_mea[chip][f"Vmux{v_mux}"] = [mea_chips[i]]
    # measure i_mux
    for i_mux in config["i_mux"]:
        mea_chips = read_vmux(
            meter,
            yr,
            config,
            i_mux=i_mux,
            use_adc=use_calib_adc,
        )
        for i, chip in enumerate(yr._enabled_chip_positions):
            i_mea[chip][f"Imux{i_mux}"] = [mea_chips[i]]

    # measure temperature from NTC
    temp, _status = module_ntc.read()

    for chip in yr._enabled_chip_positions:
        i_mea[chip]["SetCurrent"] = [config["i_ovp"][layer]]
        i_mea[chip]["Current"] = [current]
        i_mea[chip]["Temperature"] = [temp]
        data[chip].add_data(i_mea[chip])

    # turn off power supply before switching low power mode off
    ps.off()
    # turn off low power mode
    yr.switchLPM("off")
    # Return to initial state
    if yr.running_emulator():
        ps.on(v=config.nominal["v_max"], i=config.nominal["i_config"])
    else:
        ps.set(v=config.nominal["v_max"], i=config.nominal["i_config"], check=False)
        ps.on()
        ps.checkTarget(v=config.nominal["v_max"], i=config.nominal["i_config"])

    # Run an eye diagram
    logger.info("Running eye diagram at the end of scan")
    _eye, _status = yr.eyeDiagram(skipconfig=False)

    for chip in yr._enabled_chip_positions:
        data[chip].add_meta_data(
            "AverageTemperature", np.average(data[chip]["Temperature"])
        )
        data[chip].dcs_data["SensorVoltage"] = sensor_bias
        data[chip].dcs_data["SensorCurrent"] = sensor_current
        data[chip].dcs_data["ModuleNTC"] = ntc_temperature

    return data

from __future__ import annotations

import logging

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

TEST_TYPE = "INJECTION_CAPACITANCE"


@inject_metadata(test_type=TEST_TYPE)
def run(config, ps, hv, yr, debug_gnd, use_calib_adc):
    """The function which does the injection capacitance measurement.

    Args:
        config (dict): Full config dictionary
        ps (Class power_supply): An instance of Class power_supply for power on and power off.
        hv (Class power_supply): An instance of Class power_supply for high-voltage power on and power off.
        yr (Class yarr): An instance of Class yarr for chip conifugration and change register.
        debug_gnd (bool): Debug GND measurement: measure GND before each Vmux measurement
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
            columns=[
                f"Vmux{v_mux}" for v_mux in config["v_mux"] + [config["v_mux_gnd"]]
            ]
            + [f"Imux{i_mux}" for i_mux in config["i_mux"] + [config["i_mux_gnd"]]],
            units=["V" for v_mux in config["v_mux"] + [config["v_mux_gnd"]]]
            + ["V" for i_mux in config["i_mux"] + [config["i_mux_gnd"]]],
        )
        for _ in range(yr._number_of_chips)
    ]
    initialize_chip_metadata(yr, data)

    if yr.running_emulator():
        ps.on(
            config["v_max"], config["i_config"]
        )  # Only for emulator do the emulation of power on/off
        # For real measurements avoid turn on/off the chip by commands. Just leave the chip running.

    # This sends global pulse
    status = yr.configure()
    assert status >= 0

    # Check ADC ground
    if use_calib_adc:
        vmux_adc_gnd, imux_adc_gnd = check_adc_ground(yr, config)
        for i, chip in enumerate(yr._enabled_chip_positions):
            data[chip].add_meta_data("VMUX30_ADC", vmux_adc_gnd[i])
            data[chip].add_meta_data("IMUX63_ADC", imux_adc_gnd[i])

    # Measure ground just once (unless in debug mode)
    vmux_value_gnd = config["v_mux_gnd"]
    imux_value_gnd = config["i_mux_gnd"]
    vmux_gnd = -999.0
    imux_gnd = -999.0
    if not debug_gnd:
        vmux_gnd = read_vmux(
            meter,
            yr,
            config,
            v_mux=vmux_value_gnd,
            use_adc=use_calib_adc,
        )
        imux_gnd = read_vmux(
            meter,
            yr,
            config,
            i_mux=imux_value_gnd,
            use_adc=use_calib_adc,
        )

    for _i in range(config["n_meas"]):
        v_mea = [{} for _ in range(yr._number_of_chips)]

        # Disable both capmeasure and parasitic circuits
        yr.write_register("CapMeasEn", 0)
        yr.write_register("CapMeasEnPar", 0)

        if debug_gnd:
            vmux_gnd = read_vmux(
                meter,
                yr,
                config,
                v_mux=vmux_value_gnd,
                use_adc=use_calib_adc,
            )
            imux_gnd = read_vmux(
                meter,
                yr,
                config,
                i_mux=imux_value_gnd,
                use_adc=use_calib_adc,
            )

        for vmux_value in config["v_mux"]:
            mea_chips = read_vmux(
                meter,
                yr,
                config,
                v_mux=vmux_value,
                use_adc=use_calib_adc,
            )
            for j, chip in enumerate(yr._enabled_chip_positions):
                v_mea[chip][f"Vmux{vmux_value}"] = [mea_chips[j]]

        for imux_value in config["i_mux"]:
            if imux_value == 10:
                # Enable capmeasure circuit
                yr.write_register("CapMeasEn", 1)
                yr.write_register("CapMeasEnPar", 0)
            elif imux_value == 11:
                # Enable capmeasure circuit
                yr.write_register("CapMeasEn", 0)
                yr.write_register("CapMeasEnPar", 1)
            else:
                # Disable both
                yr.write_register("CapMeasEn", 0)
                yr.write_register("CapMeasEnPar", 0)

            mea_chips = read_vmux(
                meter,
                yr,
                config,
                i_mux=imux_value,
                use_adc=use_calib_adc,
            )
            for j, chip in enumerate(yr._enabled_chip_positions):
                v_mea[chip][f"Imux{imux_value}"] = [mea_chips[j]]

        # Add ground values
        for j, chip in enumerate(yr._enabled_chip_positions):
            v_mea[chip][f"Vmux{vmux_value_gnd}"] = [vmux_gnd[j]]
            v_mea[chip][f"Imux{imux_value_gnd}"] = [imux_gnd[j]]
            data[chip].add_data(v_mea[chip])
            data[chip].dcs_data["SensorVoltage"] = sensor_bias
            data[chip].dcs_data["SensorCurrent"] = sensor_current
            data[chip].dcs_data["ModuleNTC"] = ntc_temperature

    if yr.running_emulator():
        ps.off()

    return data

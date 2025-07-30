from __future__ import annotations

import logging

import numpy as np
from module_qc_data_tools.qcDataFrame import (
    qcDataFrame,
)

from module_qc_tools.utils.misc import (
    check_adc_ground,
    get_chip_type,
    initialize_chip_metadata,
    inject_metadata,
    read_vmux,
)
from module_qc_tools.utils.multimeter import multimeter
from module_qc_tools.utils.ntc import ntc

logger = logging.getLogger("measurement")

TEST_TYPE = "ADC_CALIBRATION"


@inject_metadata(test_type=TEST_TYPE)
def run(config, ps, hv, yr, bom, debug_gnd):
    """The function which does the ADC calibration.

    Args:
        config (dict): Full config dictionary
        ps (Class power_supply): An instance of Class power_supply for power on and power off.
        hv (Class power_supply): An instance of Class power_supply for high-voltage power on and power off.
        yr (Class yarr): An instance of Class yarr for chip conifugration and change register.
        bom (str): BOM code for the module
        debug_gnd (bool): Debug GND measurement: measure GND before each Vmux measurement

    Returns:
        data (list): data[chip_id][vmux/imux_type].
    """

    meter = multimeter(config["multimeter"])
    module_ntc = ntc(config["ntc"])

    # measure temperature from NTC
    ntc_temperature, _status = module_ntc.read()
    # measure sensor high voltage and leakage current
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
            columns=["DACs_input"]
            + [
                f"Vmux{v_mux}"
                for v_mux in config["MonitorV"] + [config["MonitorV_GND"]]
            ]
            + [
                f"ADC_Vmux{v_mux}"
                for v_mux in config["MonitorV"] + [config["MonitorV_GND"]]
            ],
            units=["Count"]
            + ["V" for v_mux in config["MonitorV"] + [config["MonitorV_GND"]]]
            + ["Count" for v_mux in config["MonitorV"] + [config["MonitorV_GND"]]],
        )
        for _ in range(yr._number_of_chips)
    ]

    initialize_chip_metadata(yr, data)
    for chip in yr._enabled_chip_positions:
        chiptype = get_chip_type(data[chip]._meta_data["ChipConfigs"])
        data[chip]._meta_data["ChipConfigs"][chiptype]["GlobalConfig"][
            "InjVcalRange"
        ] = config["InjVcalRange"]
        data[chip].set_x("DACs_input", True)

        # measure temperature from NTC
        # temp, _status = nt.read()

    if yr.running_emulator():
        ps.on(
            config["v_max"], config["i_config"]
        )  # Only for emulator do the emulation of power on/off
        # For real measurements avoid turn on/off the chip by commands. Just leave the chip running.

    status = yr.configure()
    assert status >= 0

    MonitorV = config["MonitorV"]
    yr.write_register("InjVcalRange", config["InjVcalRange"])

    Range = [
        config["Range"]["start"],
        config["Range"]["stop"],
        config["Range"]["step"],
    ]
    DACs = np.arange(start=Range[0], stop=Range[1], step=Range[2])

    # Check ADC ground
    vmux_adc_gnd, imux_adc_gnd = check_adc_ground(yr, config)
    for i, chip in enumerate(yr._enabled_chip_positions):
        data[chip].add_meta_data("VMUX30_ADC", vmux_adc_gnd[i])
        data[chip].add_meta_data("IMUX63_ADC", imux_adc_gnd[i])
        data[chip].add_meta_data("BOMCode", bom)

    # Measure ground (just once at the beginning if the GND debug mode is disabled)
    vmux_value_GNDA = config["MonitorV_GND"]
    gnd_vmux = -999.0
    gnd_adc = -999.0
    if not debug_gnd:
        gnd_vmux = read_vmux(meter, yr, config, v_mux=vmux_value_GNDA, use_adc=False)
        gnd_adc = read_vmux(
            meter,
            yr,
            config,
            v_mux=vmux_value_GNDA,
            use_adc=True,
            raw_adc_counts=True,
        )

    for DAC in DACs:
        yr.write_register("InjVcalMed", DAC)  # write DAC values
        v_mea = [{} for _ in range(yr._number_of_chips)]

        for _i, vmux_value in enumerate(MonitorV):
            # measure GND before each VMUX measurement if dbgGND enabled
            if debug_gnd:
                gnd_vmux = read_vmux(
                    meter, yr, config, v_mux=vmux_value_GNDA, use_adc=False
                )
                gnd_adc = read_vmux(
                    meter,
                    yr,
                    config,
                    v_mux=vmux_value_GNDA,
                    use_adc=True,
                    raw_adc_counts=True,
                )
            mea_chips_vmux = read_vmux(
                meter, yr, config, v_mux=vmux_value, use_adc=False
            )
            mea_chips_adc = read_vmux(
                meter,
                yr,
                config,
                v_mux=vmux_value,
                use_adc=True,
                raw_adc_counts=True,
            )

            for i, chip in enumerate(yr._enabled_chip_positions):
                v_mea[chip][f"Vmux{vmux_value}"] = [mea_chips_vmux[i]]
                v_mea[chip][f"ADC_Vmux{vmux_value}"] = [mea_chips_adc[i]]
                v_mea[chip][f"Vmux{vmux_value_GNDA}"] = [gnd_vmux[i]]
                v_mea[chip][f"ADC_Vmux{vmux_value_GNDA}"] = [gnd_adc[i]]

        # Add data to frame
        for chip in yr._enabled_chip_positions:
            v_mea[chip]["DACs_input"] = [float(DAC)]
            data[chip].add_data(v_mea[chip])

    for chip in yr._enabled_chip_positions:
        data[chip].dcs_data["SensorVoltage"] = sensor_bias
        data[chip].dcs_data["SensorCurrent"] = sensor_current
        data[chip].dcs_data["ModuleNTC"] = ntc_temperature

    if yr.running_emulator():
        ps.off()

    return data

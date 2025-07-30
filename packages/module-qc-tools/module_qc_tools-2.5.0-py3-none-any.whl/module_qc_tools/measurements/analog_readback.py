from __future__ import annotations

import logging
from datetime import datetime

from module_qc_data_tools.qcDataFrame import (
    qcDataFrame,
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

TEST_TYPE = "ANALOG_READBACK"


@inject_metadata(test_type=TEST_TYPE)
def run_vmeas(config, ps, hv, yr, use_calib_adc):
    """
    This function measures given internal voltages by going through all VMUX and IMUX settings provided in the config.

    Args:
        config (dict): Full config dictionary
        ps (Class power_supply): An instance of Class power_supply for power on and power off.
        yr (Class yarr): An instance of Class yarr for chip conifugration and change register.
        use_calib_adc (bool): use calibrated ADC instead of multimeter

    Returns:
        data (list): data[chip_id][vmux/imux_type].
    """
    logger.info("Start V scan!")
    logger.info(f"TimeStart: {datetime.now().strftime('%Y-%m-%d_%H%M%S')}")

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
            config["v_max"],
            config["i_config"],
        )  # Only for emulator do the emulation of power on/off.
        # For real measurements avoid turn on/off the chip by commands. Just leave the chip running.

    # Check ADC ground
    if use_calib_adc:
        vmux_adc_gnd, imux_adc_gnd = check_adc_ground(yr, config)
        for i, chip in enumerate(yr._enabled_chip_positions):
            data[chip].add_meta_data("VMUX30_ADC", vmux_adc_gnd[i])
            data[chip].add_meta_data("IMUX63_ADC", imux_adc_gnd[i])

    # Set and measure current for power supply
    i_mea = [{} for _ in range(yr._number_of_chips)]

    # Measure ground once.
    vmux_value_gnd = config["v_mux_gnd"]
    vmux_gnd = read_vmux(
        meter,
        yr,
        config,
        v_mux=vmux_value_gnd,
        use_adc=use_calib_adc,
    )
    imux_value_gnd = config["i_mux_gnd"]
    imux_gnd = read_vmux(
        meter,
        yr,
        config,
        i_mux=imux_value_gnd,
        use_adc=use_calib_adc,
    )
    for i, chip in enumerate(yr._enabled_chip_positions):
        i_mea[chip][f"Vmux{vmux_value_gnd}"] = [vmux_gnd[i]]
        i_mea[chip][f"Imux{imux_value_gnd}"] = [imux_gnd[i]]

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

    for chip in yr._enabled_chip_positions:
        data[chip].add_data(i_mea[chip])
        data[chip].dcs_data["SensorVoltage"] = sensor_bias
        data[chip].dcs_data["SensorCurrent"] = sensor_current
        data[chip].dcs_data["ModuleNTC"] = ntc_temperature

    logger.info("V scan done!")
    logger.info(f"TimeEnd: {datetime.now().strftime('%Y-%m-%d_%H%M%S')}")

    return data


@inject_metadata(test_type=TEST_TYPE)
def run_tmeas(config, ps, hv, yr, use_calib_adc):
    """
    This function measures temperature of the NTC nad MOS sensor though VMUX and IMUX settings provided in the config.

    Args:
        config (dict): An subdict dumped from json including the task information.
        ps (Class power_supply): An instance of Class power_supply for power on and power off.
        yr (Class yarr): An instance of Class yarr for chip conifugration and change register.

    Returns:
        data (list): data[chip_id][vmux/imux_type or bias/dem].
    """
    logger.info("Start T measurement!")
    logger.info(f"TimeStart: {datetime.now().strftime('%Y-%m-%d_%H%M%S')}")

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
                f"Vmux{v_mux}"
                for v_mux in [
                    config["v_mux_ntc"],
                    config["v_mux_gnd"],
                ]
            ]
            + [
                f"Imux{i_mux}"
                for i_mux in [
                    config["i_mux_ntc"],
                    config["i_mux_gnd"],
                ]
            ]
            + [f"Vmux{v_mux}" for v_mux in config["v_mux_tempsens"]]
            + ["MonSensSldoAnaSelBias"]
            + ["MonSensSldoDigSelBias"]
            + ["MonSensAcbSelBias"]
            + ["MonSensSldoAnaDem"]
            + ["MonSensSldoDigDem"]
            + ["MonSensAcbDem"]
            + ["TExtExtNTC"],
            units=[
                "V"
                for v_mux in [
                    config["v_mux_ntc"],
                    config["v_mux_gnd"],
                ]
            ]
            + [
                "V"
                for i_mux in [
                    config["i_mux_ntc"],
                    config["i_mux_gnd"],
                ]
            ]
            + ["V" for v_mux in config["v_mux_tempsens"]]
            + ["-"]
            + ["-"]
            + ["-"]
            + ["-"]
            + ["-"]
            + ["-"]
            + ["C"],
        )
        for _ in range(yr._number_of_chips)
    ]
    initialize_chip_metadata(yr, data)

    if yr.running_emulator():
        ps.on(
            config["v_max"],
            config["i_config"],
        )  # Only for emulator do the emulation of power on/off.
        # For real measurements avoid turn on/off the chip by commands. Just leave the chip running.

    # Check ADC ground
    if use_calib_adc:
        vmux_adc_gnd, imux_adc_gnd = check_adc_ground(yr, config)
        for i, chip in enumerate(yr._enabled_chip_positions):
            data[chip].add_meta_data("VMUX30_ADC", vmux_adc_gnd[i])
            data[chip].add_meta_data("IMUX63_ADC", imux_adc_gnd[i])

    # Chip config mapping
    bias_maps = {
        14: "MonSensSldoAnaSelBias",
        16: "MonSensSldoDigSelBias",
        18: "MonSensAcbSelBias",
    }
    dem_maps = {
        14: "MonSensSldoAnaDem",
        16: "MonSensSldoDigDem",
        18: "MonSensAcbDem",
    }

    # Measure ground once.
    vmux_value_gnd = config["v_mux_gnd"]
    vmux_gnd = read_vmux(
        meter,
        yr,
        config,
        v_mux=vmux_value_gnd,
        use_adc=use_calib_adc,
    )
    imux_value_gnd = config["i_mux_gnd"]
    imux_gnd = read_vmux(
        meter,
        yr,
        config,
        i_mux=imux_value_gnd,
        use_adc=use_calib_adc,
    )

    i_mea = [{} for _ in range(yr._number_of_chips)]
    # Measure v_mux_tempmeas
    for v_mux in config["v_mux_tempsens"]:
        yr.enable_tempsens(v_mux=v_mux)
        for bias in config[bias_maps[v_mux]]:
            yr.set_tempsens_bias(v_mux=v_mux, bias=bias)
            for dem in config[dem_maps[v_mux]]:
                yr.set_tempsens_dem(
                    v_mux=v_mux,
                    dem=dem,
                )
                mea_chips = read_vmux(
                    meter,
                    yr,
                    config,
                    v_mux=v_mux,
                    use_adc=use_calib_adc,
                )

                for i, chip in enumerate(yr._enabled_chip_positions):
                    # Reset i_mea[chip]
                    i_mea[chip] = {}
                    # Record vmux, bias, and dem.
                    i_mea[chip][f"Vmux{v_mux}"] = [mea_chips[i]]
                    i_mea[chip][bias_maps[v_mux]] = [bias]
                    i_mea[chip][dem_maps[v_mux]] = [dem]
                    data[chip].add_data(i_mea[chip])
                    data[chip].dcs_data["SensorVoltage"] = sensor_bias
                    data[chip].dcs_data["SensorCurrent"] = sensor_current
                    data[chip].dcs_data["ModuleNTC"] = ntc_temperature

    yr.reset_tempsens()

    # Measure NTCs
    # Measure external external (flex) NTC
    mea_ntc, _status = module_ntc.read()
    # Measure external (chip) NTCs
    v_mux_value_ntc = config["v_mux_ntc"]
    v_mux_ntc = read_vmux(
        meter,
        yr,
        config,
        v_mux=v_mux_value_ntc,
        use_adc=use_calib_adc,
    )
    i_mux_value_ntc = config["i_mux_ntc"]
    i_mux_ntc = read_vmux(
        meter,
        yr,
        config,
        i_mux=i_mux_value_ntc,
        use_adc=use_calib_adc,
    )

    max_n_measure = max(len(d["Vmux14"]) if d else 0 for d in data)
    n_measure = 0
    while n_measure < max_n_measure:
        # Clear dictionary to hold data
        i_mea = [{} for _ in range(yr._number_of_chips)]
        for i, chip in enumerate(yr._enabled_chip_positions):
            i_mea[chip][f"Vmux{v_mux_value_ntc}"] = [v_mux_ntc[i]]
            i_mea[chip][f"Vmux{vmux_value_gnd}"] = [vmux_gnd[i]]
            i_mea[chip][f"Imux{i_mux_value_ntc}"] = [i_mux_ntc[i]]
            i_mea[chip][f"Imux{imux_value_gnd}"] = [imux_gnd[i]]
            i_mea[chip]["TExtExtNTC"] = [mea_ntc]
            data[chip].add_data(i_mea[chip])
        n_measure += 1

    logger.info("T measurement done!")
    logger.info(f"TimeEnd: {datetime.now().strftime('%Y-%m-%d_%H%M%S')}")

    return data


@inject_metadata(test_type=TEST_TYPE)
def run_vdda_vddd_vs_trim(config, ps, hv, yr, debug_gnd, use_calib_adc):
    """
    This function measures how VDDA and VDDD changes with Trim.

    Args:
        config (dict): An subdict dumped from json including the task information.
        ps (Class power_supply): An instance of Class power_supply for power on and power off.
        yr (Class yarr): An instance of Class yarr for chip conifugration and change register.

    Returns:
        data (list): data[chip_id][vmux/imux_type or bias/dem].
    """
    logger.info("Start VDD vs Trim measurement!")
    logger.info(f"TimeStart: {datetime.now().strftime('%Y-%m-%d_%H%M%S')}")

    meter = multimeter(config["multimeter"])
    module_ntc = ntc(config["ntc"])

    # measure temperature from NTC
    ntc_temperature, _status = module_ntc.read()
    logger.info("Module NTC temperature: " + str(ntc_temperature))
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

    imux_to_measure = {
        "A": {28: "IinA", 29: "IshuntA"},
        "D": {30: "IinD", 31: "IshuntD"},
    }

    vmux_to_measure = {"A": {33: "VinA"}, "D": {37: "VinD"}}

    idata = []
    vdata = []

    for value in imux_to_measure.values():
        for subkey in value:
            _subkey = "Imux" + str(subkey)
            idata.append(_subkey)
    for value in vmux_to_measure.values():
        for subkey in value:
            _subkey = "Vmux" + str(subkey)
            vdata.append(_subkey)

    data = [
        qcDataFrame(
            columns=["Vmux34"]
            + ["Vmux38"]
            + [f"Vmux{config['v_mux_gnd']}"]
            + vdata
            + [f"Imux{config['i_mux_gnd']}"]
            + idata
            + ["SldoTrimA"]
            + ["SldoTrimD"]
            + [f"ROSC{i}" for i in range(42)],
            units=["V"]
            + ["V"]
            + ["V"]  ## v_mux_gnd
            + ["V"] * len(vdata)
            + ["V"]  ## i_mux_gnd
            + ["V"] * len(idata)
            + ["-"]
            + ["-"]
            + ["MHz" for i in range(42)],
        )
        for _ in range(yr._number_of_chips)
    ]
    initialize_chip_metadata(yr, data)

    if yr.running_emulator():
        ps.on(
            config["v_max"],
            config["i_config"],
        )  # Only for emulator do the emulation of power on/off.
        # For real measurements avoid turn on/off the chip by commands. Just leave the chip running.

    # Check ADC ground
    if use_calib_adc:
        vmux_adc_gnd, imux_adc_gnd = check_adc_ground(yr, config)
        for i, chip in enumerate(yr._enabled_chip_positions):
            data[chip].add_meta_data("VMUX30_ADC", vmux_adc_gnd[i])
            data[chip].add_meta_data("IMUX63_ADC", imux_adc_gnd[i])

    # Trim to Vmux mapping
    vmux_to_trim = {
        34: "SldoTrimA",
        38: "SldoTrimD",
    }

    vmux_value_gnd = config["v_mux_gnd"]
    imux_value_gnd = config["i_mux_gnd"]

    ## trim chip by chip
    for _, chip in enumerate(yr._enabled_chip_positions):  # pylint: disable=too-many-nested-blocks
        vmux_gnd = -999.0
        imux_gnd = -999.0
        # Measure ground once.
        if not debug_gnd:
            vmux_gnd = read_vmux(
                meter,
                yr,
                config,
                v_mux=vmux_value_gnd,
                use_adc=use_calib_adc,
                chip_position=chip,
            )
            imux_gnd = read_vmux(
                meter,
                yr,
                config,
                i_mux=imux_value_gnd,
                use_adc=use_calib_adc,
                chip_position=chip,
            )

        data[chip].dcs_data["SensorVoltage"] = sensor_bias
        data[chip].dcs_data["SensorCurrent"] = sensor_current
        data[chip].dcs_data["ModuleNTC"] = ntc_temperature

        logger.info(f"Trimming chip {chip}")
        # Measure VDDA/VDDD and ROSC vs SldoTrimA/SldoTrimD
        for n, (v_mux, trim_name) in enumerate(vmux_to_trim.items()):
            # Reset i_mea
            i_mea = [{} for _ in range(yr._number_of_chips)]
            domain = "A" if v_mux == 34 else "D"
            # Read initial Trim in chip config
            config_trim, _status = yr.read_register(name=trim_name, chip_position=chip)

            for trim in config[trim_name]:
                # Set trim of all chips
                yr.write_register(name=trim_name, value=trim, chip_position=chip)

                # Run eye-diagram and update the delay in the controller config according to new trim values
                logger.info(f"Running eye diagram for VMUX{v_mux}={trim}")
                _eye, _status = yr.eyeDiagram(skipconfig=True, testsize=100000)

                # if debug GND set, measure the GND for the first VMUX
                if debug_gnd and n == 0:
                    vmux_gnd = read_vmux(
                        meter,
                        yr,
                        config,
                        v_mux=vmux_value_gnd,
                        use_adc=use_calib_adc,
                        chip_position=chip,
                    )
                    imux_gnd = read_vmux(
                        meter,
                        yr,
                        config,
                        i_mux=imux_value_gnd,
                        use_adc=use_calib_adc,
                        chip_position=chip,
                    )

                v_mea_chips = {}
                i_mea_chips = {}

                ## read VDD
                v_mea_chips[v_mux] = read_vmux(
                    meter,
                    yr,
                    config,
                    v_mux=v_mux,
                    use_adc=use_calib_adc,
                    chip_position=chip,
                )

                ## Read muxes vs trim
                for _imux in imux_to_measure[domain]:
                    i_mea_chips[_imux] = read_vmux(
                        meter,
                        yr,
                        config,
                        i_mux=_imux,
                        use_adc=use_calib_adc,
                        chip_position=chip,
                    )

                for _vmux in vmux_to_measure[domain]:
                    v_mea_chips[_vmux] = read_vmux(
                        meter,
                        yr,
                        config,
                        v_mux=_vmux,
                        use_adc=use_calib_adc,
                        chip_position=chip,
                    )

                ## measure VDDA/D vs trim
                if trim_name not in i_mea[chip]:
                    i_mea[chip][trim_name] = []
                i_mea[chip][trim_name].append(trim)

                # Record vmux and trim.
                for _vmux, _vvalue in v_mea_chips.items():
                    if f"Vmux{_vmux}" not in i_mea[chip]:
                        i_mea[chip][f"Vmux{_vmux}"] = []
                    i_mea[chip][f"Vmux{_vmux}"].extend(_vvalue)
                # Record imux and trim
                for _imux, _ivalue in i_mea_chips.items():
                    if f"Imux{_imux}" not in i_mea[chip]:
                        i_mea[chip][f"Imux{_imux}"] = []
                    i_mea[chip][f"Imux{_imux}"].extend(_ivalue)

                if n == 0:
                    # if debug_gnd=False these values will be the same for all trims
                    if f"Vmux{vmux_value_gnd}" not in i_mea[chip]:
                        i_mea[chip][f"Vmux{vmux_value_gnd}"] = []
                        i_mea[chip][f"Imux{imux_value_gnd}"] = []
                    i_mea[chip][f"Vmux{vmux_value_gnd}"].extend(vmux_gnd)
                    i_mea[chip][f"Imux{imux_value_gnd}"].extend(imux_gnd)

                # Read ROSC vs trim
                if v_mux == 38:
                    mea, _status = yr.read_ringosc(chip_position=chip)
                    rosc_mea = [float(num) for num in mea[0].split()]
                    for j, item in enumerate(rosc_mea):
                        if f"ROSC{j}" not in i_mea[chip]:
                            i_mea[chip][f"ROSC{j}"] = []
                        i_mea[chip][f"ROSC{j}"].append(item)

            data[chip].add_data(i_mea[chip])

            i_mea = [{} for _ in range(yr._number_of_chips)]

            # Reset Trim to value in config and restore delay settings via eye diagram
            logger.info(
                f"Set VMUX{v_mux} back to default and re-running :eye: diagram."
            )
            yr.write_register(
                name=trim_name, value=int(config_trim[0]), chip_position=chip
            )
            _eye, _status = yr.eyeDiagram(skipconfig=True)

    logger.info("VDDA/VDDD measurement done!")
    logger.info(f"TimeEnd: {datetime.now().strftime('%Y-%m-%d_%H%M%S')}")

    return data


@inject_metadata(test_type=TEST_TYPE)
def run_readregister(config, ps, yr):
    """
    This function reads register values like Iref trim

    Args:
        config (dict): An subdict dumped from json including the task information.
        ps (Class power_supply): An instance of Class power_supply for power on and power off.
        yr (Class yarr): An instance of Class yarr for chip conifugration and change register.

    Returns:
        data (list): data[chip_id][vmux/imux_type or bias/dem].
    """
    logger.info("Start reading registers")
    logger.info(f"TimeStart: {datetime.now().strftime('%Y-%m-%d_%H%M%S')}")

    data = [
        qcDataFrame(
            columns=config["registers"],
            units=["-"] * len(config["registers"]),
        )
        for _ in range(yr._number_of_chips)
    ]
    initialize_chip_metadata(yr, data)

    if yr.running_emulator():
        ps.on(
            config["v_max"],
            config["i_config"],
        )  # Only for emulator do the emulation of power on/off.
        # For real measurements avoid turn on/off the chip by commands. Just leave the chip running.

    reg_values = {}
    for _, chip in enumerate(yr._enabled_chip_positions):  # pylint: disable=too-many-nested-blocks
        reg_values[chip] = {}
        for register in config["registers"]:
            value, _status = yr.read_register(name=register, chip_position=chip)
            reg_values[chip][register] = value

        data[chip].add_data(reg_values[chip])

    logger.info("Read register done!")
    logger.info(f"TimeEnd: {datetime.now().strftime('%Y-%m-%d_%H%M%S')}")

    return data

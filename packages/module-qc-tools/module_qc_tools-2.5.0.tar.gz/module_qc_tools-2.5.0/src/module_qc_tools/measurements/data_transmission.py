from __future__ import annotations

import logging
import re
from io import StringIO

import numpy as np
import typer
from module_qc_data_tools.qcDataFrame import (
    qcDataFrame,
)

from module_qc_tools.cli.globals import (
    CONTEXT_SETTINGS,
)
from module_qc_tools.utils.misc import initialize_chip_metadata, inject_metadata
from module_qc_tools.utils.ntc import ntc

logger = logging.getLogger("measurement")

app = typer.Typer(context_settings=CONTEXT_SETTINGS)

TEST_TYPE = "DATA_TRANSMISSION"


@inject_metadata(test_type=TEST_TYPE)
def run_eyediagram(config, ps, hv, yr, n_lanes_per_chip, dryrun):
    """The function which runs the eye diagram measurement.

    Args:
        config (dict): Full config dictionary
        ps (Class power_supply): An instance of Class power_supply for power on and power off.
        yr (Class yarr): An instance of Class yarr for chip conifugration and change register.
        n_lanes_per_chip (int): number of lanes per chip
        dryrun (bool): whether to enable dry-run mode or not (relevant for eye-diagram running)

    Returns:
        data (list): data[chip_id][vmux/imux_type].
    """
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

    if yr.running_emulator():
        ps.on(v=config["v_max"], i=config["i_config"])
        # Only for emulator do the emulation of power on/off
        # For real measurements avoid turn on/off the chip by commands. Just leave the chip running.

    status = yr.configure()
    assert status >= 0

    metadata = [
        {
            "Temperature": [],
            "Rx": [],
            **{
                k: []
                for k in (
                    f"{prefix}{i}"
                    for i in range(n_lanes_per_chip)
                    for prefix in ["EyeWidth", "DelaySetting"]
                )
            },
        }
        for _ in range(yr._number_of_chips)
    ]

    meas = [{} for _ in range(yr._number_of_chips)]

    data = [
        qcDataFrame(
            columns=["Delay"] + [f"EyeOpening{i}" for i in range(n_lanes_per_chip)],
            units=[""] + n_lanes_per_chip * [""],
        )
        for _ in range(yr._number_of_chips)
    ]

    initialize_chip_metadata(yr, data)
    for chip in yr._enabled_chip_positions:
        data[chip].set_x("Delay", True)
        for value in config["MonitorV"]:
            yr.set_mux(
                chip_position=chip,
                v_mux=value,
                reset_other_chips=False,
            )

        # measure temperature from NTC
        temp, _status = module_ntc.read()
        metadata[chip]["Temperature"] = [temp]

    logger.info("Running eye-diagram scan...")
    yarr_output = yr.eyeDiagram(dryrun=dryrun)[0]
    logger.debug(f"Result:\n{yarr_output}")

    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    yarr_output_cleaned = ansi_escape.sub("", yarr_output)
    logger.info(f"Result (cleaned): \n{yarr_output_cleaned}")
    assert (
        "Done scanning" in yarr_output_cleaned
    ), "Could not find the right place to split for parsing the eye-diagram. There should be an indication of 'All done' completion."

    done_scanning = yarr_output_cleaned.index("Done scanning")
    end_of_eye_diagram = yarr_output_cleaned[:done_scanning].rfind("\n")

    first_bar_occurrence = yarr_output_cleaned[:end_of_eye_diagram].index("|")
    start_of_eye_diagram = yarr_output_cleaned[:first_bar_occurrence].rfind("\n") + 1

    num_lanes = 16
    colnames = ["Delay"] + [f"lane{i}" for i in range(num_lanes)]
    dtype = [
        (colname, np.int64 if i == 0 else np.float64)
        for i, colname in enumerate(colnames)
    ]
    testdata = np.genfromtxt(
        StringIO(yarr_output_cleaned[start_of_eye_diagram:end_of_eye_diagram]),
        delimiter="|",
        usecols=np.arange(len(colnames)),
        dtype=dtype,
    )

    # TODO: maybe use this info ? [16:24:49:371][  info  ][    SpecRx     ][31126]: Active Rx channels: 0x8

    delay_setting = {k: None for k in range(num_lanes)}
    eye_width = {k: None for k in range(num_lanes)}
    logger.debug(
        f"yarr_output_cleaned(end_of_eye_diagram:)\n {yarr_output_cleaned[end_of_eye_diagram:]}"
    )

    ## 2025.03.20, see https://mattermost.web.cern.ch/itkpixel/pl/5js9ikpng3rybc5ry9a8afbbfo
    ## checking for both cases:
    ## Delay setting for lane 0 with eye width 7: 3
    ## Delay setting for lane 0 with eye width 7.0: 3.0
    pattern = re.compile(
        r"Delay setting for lane (?P<lane>\d+) with eye width (?P<width>\d+)(?:.0)?: (?P<delay>\d+)(?:.0)?"
    )
    for match in pattern.finditer(yarr_output_cleaned[end_of_eye_diagram:]):
        logger.debug(f"match {match}")
        lane = int(match["lane"])
        eye_width[lane] = int(match["width"])
        delay_setting[lane] = int(match["delay"])
        logger.debug(
            f"lane {lane} eye_width {eye_width[lane]} delay {delay_setting[lane]}"
        )

    for chip in yr._enabled_chip_positions:
        meas[chip]["Delay"] = testdata["Delay"].tolist()
        metadata[chip]["Rx"] = [yr._chip_rx[chip]]
        for i in range(n_lanes_per_chip):
            if n_lanes_per_chip > 1:
                lanes_per_group = 4
                lane = yr._chip_rx[chip] * lanes_per_group + i
            else:
                lane = yr._chip_rx[chip]

            meas[chip][f"EyeOpening{i}"] = testdata[f"lane{lane}"].tolist()

            width = eye_width[lane]
            delay = delay_setting[lane]

            if width is None:
                logger.warning(
                    f"[bright_yellow]No good eye width found for lane {lane} :person_shrugging:[/]"
                )
            else:
                metadata[chip][f"EyeWidth{i}"] = (
                    width if n_lanes_per_chip > 1 else [width]
                )

            if delay is None:
                logger.warning(
                    f"[bright_yellow]No good delay setting found for lane {lane} :person_shrugging:[/]"
                )
            else:
                metadata[chip][f"DelaySetting{i}"] = (
                    delay if n_lanes_per_chip > 1 else [delay]
                )

        # inject metadata collected during the measurement back into 'data'
        data[chip].add_meta_data(
            "AverageTemperature", np.average(metadata[chip].pop("Temperature"))
        )
        for key, value in metadata[chip].items():
            data[chip].add_meta_data(key, value)

        data[chip].add_data(meas[chip])
        data[chip].dcs_data["SensorVoltage"] = sensor_bias
        data[chip].dcs_data["SensorCurrent"] = sensor_current
        data[chip].dcs_data["ModuleNTC"] = ntc_temperature

    if yr.running_emulator():
        ps.off()

    return data


@inject_metadata(test_type=TEST_TYPE)
def run_datamerging(config, ps, hv, yr):
    """The function which runs the data merging.

    Args:
        config (dict): Full config dictionary
        ps (Class power_supply): An instance of Class power_supply for power on and power off.
        yr (Class yarr): An instance of Class yarr for chip conifugration and change register.
        n_lanes_per_chip (int): number of lanes per chip

    Returns:
        data (list): data[chip_id][vmux/imux_type].
    """
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

    if yr.running_emulator():
        ps.on(v=config["v_max"], i=config["i_config"])
        # Only for emulator do the emulation of power on/off
        # For real measurements avoid turn on/off the chip by commands. Just leave the chip running.

    status = yr.configure()
    assert status >= 0

    metadata = [
        {
            "Temperature": [],
        }
        for _ in range(yr._number_of_chips)
    ]

    meas = [{} for _ in range(yr._number_of_chips)]

    data = [
        qcDataFrame(
            columns=config["DataMerging"], units=[""] * len(config["DataMerging"])
        )
        for _ in range(yr._number_of_chips)
    ]

    results = {"Passed": 1, "Failed": 0}

    initialize_chip_metadata(yr, data)
    for chip in yr._enabled_chip_positions:
        # measure temperature from NTC
        temp, _status = module_ntc.read()
        metadata[chip]["Temperature"] = [temp]

    yarr_output = {}
    for mode in config["DataMerging"]:
        logger.info(f"Running data merging check in {mode} mode...")
        output = yr.dataMergingCheck(mode=mode)[0]
        logger.info(f"Result:\n{output}")

        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        yarr_output_cleaned = ansi_escape.sub("", output)
        yarr_output[mode] = yarr_output_cleaned.split("\n")[-2]
        logger.debug(yarr_output[mode])

        assert (
            yarr_output[mode] in results
        ), "Could not find the result of the data merging check!"

    for chip in yr._enabled_chip_positions:
        for mode in config["DataMerging"]:
            meas[chip][mode] = [results[yarr_output[mode]]]

        # inject metadata collected during the measurement back into 'data'
        data[chip].add_meta_data(
            "AverageTemperature", np.average(metadata[chip].pop("Temperature"))
        )
        for key, value in metadata[chip].items():
            data[chip].add_meta_data(key, value)

        data[chip].add_data(meas[chip])
        data[chip].dcs_data["SensorVoltage"] = sensor_bias
        data[chip].dcs_data["SensorCurrent"] = sensor_current
        data[chip].dcs_data["ModuleNTC"] = ntc_temperature

    logger.info("Data merging checked. Setting the chips back to their original state!")
    status = yr.configure()
    assert status >= 0

    if yr.running_emulator():
        ps.off()

    return data

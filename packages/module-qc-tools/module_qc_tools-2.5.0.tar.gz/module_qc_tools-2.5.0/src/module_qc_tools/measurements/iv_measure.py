from __future__ import annotations

import logging
import time

import numpy as np
from module_qc_data_tools.qcDataFrame import (
    qcDataFrame,
)
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from rich.table import Table

from module_qc_tools.utils.hrc import hrc
from module_qc_tools.utils.misc import ProgressTable, inject_metadata
from module_qc_tools.utils.ntc import ntc

logger = logging.getLogger("measurement")

TEST_TYPE = "IV_MEASURE"


@inject_metadata(test_type=TEST_TYPE, uses_yarr=False)
def run(config, ps, hv, layer):
    """
    Measure the sensor leakage current against reverse bias voltage.

    Args:
        config (dict): Full config dictionary
        ps (Class power_supply): An instance of Class power_supply for power on and power off.
        hv (Class power_supply): An instance of Class power_supply for high-voltage power on and power off.
        layer (str): Layer information for the module

    Returns:
        data (list): data[chip_id][vmux/imux_type].
    """
    nt = ntc(config["ntc"])
    try:
        hr = hrc(config["hrc"])
    except (KeyError, TypeError):
        hr = None
        logger.warning("No humidity measurement found in the hardware config!")

    data = qcDataFrame(
        columns=[
            "time",
            "voltage",
            "current",
            "sigma current",
            "temperature",
            "humidity",
        ],
        units=["s", "V", "A", "A", "C", "%"],
    )
    data.set_x("voltage", True)

    # get current status
    lv_set = {"voltage": ps.getV(), "current": ps.getI()}
    hv_set = {"voltage": hv.getV(), "current": hv.getI()}

    lv_status = {"voltage": ps.measV(), "current": ps.measI()}
    logger.debug("lv_status " + str(lv_status))
    hv_status = {"voltage": hv.measV(), "current": hv.measI()}
    logger.debug("hv_status " + str(hv_status))

    # turn off LV and HV, set HV for measurement
    if (
        hv_status["voltage"][0] and hv_status["current"][0]
    ):  # if both HV voltage and current are != 0 then HV is on
        logger.debug(
            "HV voltage: "
            + str(hv_status["voltage"][0])
            + " HV current: "
            + str(hv_status["current"][0])
        )
        logger.info("Ramping HV to 0V before starting measurement...")
        hv.rampV(v=0, i=config["i_max"][layer])
        hv.off()

    if (
        lv_status["voltage"][0] and lv_status["current"][0]
    ):  # if both LV voltage and current are != 0 then LV is on
        logger.debug(
            "LV voltage: "
            + str(lv_status["voltage"][0])
            + " LV current: "
            + str(lv_status["current"][0])
        )
        logger.info("Switching off LV before starting measurement...")
        ps.off()

    hv.set(
        v=config["v_min"][layer],
        i=config["i_max"][layer],
        check=False,
    )
    if "emulator" not in hv.on_cmd:
        hv.on()
    hv.checkTarget(v=config["v_min"][layer], i=config["i_max"][layer])

    voltages = np.linspace(
        config["v_min"][layer],
        config["v_max"][layer],
        config["n_points"][layer],
    )
    starttime = time.time()

    table = Table()
    table.add_column("time (s)", justify="right", style="cyan")
    table.add_column("voltage (V)", justify="right")
    table.add_column("current (µA)", justify="right")
    table.add_column("sigma current (nA)", justify="right", style="yellow")
    table.add_column("temperature (C)", justify="right", style="yellow")
    if hr:
        table.add_column("humidity (%)", justify="right", style="yellow")

    progress = ProgressTable(
        SpinnerColumn(),
        *Progress.get_default_columns(),
        TimeElapsedColumn(),
        measurements=table,
        transient=True,
    )

    with progress:
        for value in progress.track(voltages, description="Starting IV measurement..."):
            mea = {}
            currents = []

            # set and measure current for power supply
            try:
                progress.update(
                    0,
                    description=f"Setting HV: {value} V and {config['i_max'][layer]} A...",
                )
                hv.set(
                    v=value, i=config["i_max"][layer]
                )  # will return only when target is reached
            except RuntimeError as err:
                logger.exception(
                    f"{err}: Voltage target ({value} V) cannot be set or reached, possible HV interlock triggered. Ramping down! Please check HV PSU status before continuing QC!"
                )
                break

            if "emulator" not in hv.measV_cmd:
                time.sleep(config["settling_time"][layer])

            progress.update(0, description="Settled! Taking measurements...")
            duration = time.time() - starttime
            # read voltage
            voltage, v_status = hv.measV()
            if v_status:
                logger.error(
                    'Cannot read voltage from the HV supply. Try increase "n_try" in the measurement configuration.'
                )
                break

            # read current
            i_status = 0
            for _j in range(3):  ## takes 0.5s for 3 readings
                current, i_status = hv.measI()
                if i_status:
                    logger.error(
                        'Cannot read current from the HV supply. Try increase "n_try" in the measurement configuration.'
                    )
                    break  ## out of the current loop
                currents.append(current)
            if i_status:
                break  ## out of the voltage loop

            # read temperature
            temp, _temp_status = nt.read()
            # read humidity
            if hr:
                mod_hum, _hum_status = hr.read()

            current_ave = np.mean(currents)
            current_std = np.std(currents)

            # fill in data
            mea["time"] = [duration]
            mea["voltage"] = [voltage]
            mea["current"] = [current_ave]
            mea["sigma current"] = [current_std]
            mea["temperature"] = [temp]

            row = (
                f"{duration:0.2f}",
                f"{voltage:0.2f}",
                f"{current_ave*(1e6):0.4f}",
                f"{current_std*(1e9):0.4f}",
                f"{temp:0.2f}",
            )

            if hr:
                mea["humidity"] = [mod_hum]
                table.add_row(
                    *row,
                    f"{mod_hum:0.2f}",
                )
            else:
                table.add_row(*row)

            data.add_data(mea)

            # progress.console.print(table)

            if abs(mea["current"][0]) >= config["i_max"][layer]:
                logger.warning(
                    f'Measured leakage current {abs(mea["current"][0])}A exceeds the current compliance {config["i_max"][layer]}A! Ramping down!'
                )
                break

    time.sleep(1)
    # Return to initial state
    logger.info(f'Ramping HV back to initial state at {hv_set["voltage"][0]}V...')
    try:
        hv.rampV(v=hv_set["voltage"][0], i=hv_set["current"][0])
    except RuntimeError as err:
        logger.exception(
            f"{err}: HV voltage target during ramp down cannot be set or reached, possible HV interlock triggered. Please check HV PSU status before continuing QC!"
        )
    ps.set(v=lv_set["voltage"][0], i=lv_set["current"][0], check=False)
    ## if not emulator and LV was on previously
    if (
        "emulator" not in ps.on_cmd
        and lv_status["voltage"][0]
        and lv_status["current"][0]
    ):
        ps.on()
        ps.checkTarget(v=lv_set["voltage"][0], i=lv_set["current"][0])

    data.add_meta_data("AverageTemperature", np.average(data["temperature"]))
    data.add_meta_data("SettlingTime", config["settling_time"][layer])
    return data

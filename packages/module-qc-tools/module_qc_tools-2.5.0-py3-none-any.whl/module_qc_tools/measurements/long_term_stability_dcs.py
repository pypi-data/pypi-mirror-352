from __future__ import annotations

import logging
import math
import time

import numpy as np
from module_qc_data_tools.qcDataFrame import (
    qcDataFrame,
)
from module_qc_data_tools.utils import (
    get_layer_from_sn,
    get_n_chips,
    get_sn_from_connectivity,
)
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from rich.table import Table

from module_qc_tools.utils.hrc import hrc
from module_qc_tools.utils.misc import ProgressTable, inject_metadata
from module_qc_tools.utils.ntc import ntc

logger = logging.getLogger("measurement")

TEST_TYPE = "LONG_TERM_STABILITY_DCS"


def build_table(data=None, nrows=-1):
    table = Table()
    table.add_column("time (s)", justify="right", style="cyan")
    table.add_column("bias voltage (V)", justify="right")
    table.add_column("leakage current (µA)", justify="right")
    table.add_column("module voltage (V)", justify="right", style="magenta")
    table.add_column("module current (A)", justify="right", style="magenta")
    table.add_column("temperature (C)", justify="right", style="yellow")
    table.add_column("humidity (%)", justify="right", style="yellow")

    if not data:
        return table

    values = list(
        zip(
            *[
                data[col]
                for col in [
                    "time",
                    "BIAS_VOLT",
                    "LEAKAGE_CURR",
                    "LV_VOLT",
                    "LV_CURR",
                    "MOD_TEMP",
                    "MOD_HUM",
                ]
            ]
        )
    )

    sliced_values = values[:-nrows:-1] if nrows > 0 else values[::-1]

    for row in sliced_values:
        table.add_row(*[f"{x:0.2f}" for x in row])

    return table


@inject_metadata(test_type=TEST_TYPE, uses_yarr=False)
def run(config, ps, hv):
    """
    Measure the sensor leakage current, low-power voltage, and temperature.

    Args:
        config (dict): Full config dictionary
        ps (Class power_supply): An instance of Class power_supply for power on and power off.
        hv (Class power_supply): An instance of Class power_supply for high-voltage power on and power off.

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
            "BIAS_VOLT",
            "LEAKAGE_CURR",
            "LV_VOLT",
            "LV_CURR",
            "MOD_TEMP",
            "MOD_HUM",
        ],
        units=["s", "V", "A", "V", "A", "C", "%"],
    )
    data.set_x("time", True)

    lv_status = {"voltage": ps.measV(), "current": ps.measI()}
    logger.debug("lv_status " + str(lv_status))
    hv_status = {"voltage": hv.measV(), "current": hv.measI()}
    logger.debug("hv_status " + str(hv_status))
    module_serial = get_sn_from_connectivity(config["yarr"]["connectivity"])
    layer = get_layer_from_sn(module_serial)
    nchips = get_n_chips(layer)

    scale_factor = nchips / 3 if layer == "L0" else nchips / 4
    nominal_current = config["tasks"]["GENERAL"]["i_config"] * scale_factor

    if not (hv_status["voltage"][0] and hv_status["current"][0]):
        logger.error("HV must be on (the sensor must be biased for stability testing)")
        msg = f"Module is not properly powered. HV voltage ({hv_status['voltage'][0]}) and current ({hv_status['current'][0]})."
        raise RuntimeError(msg)
    if not (lv_status["voltage"][0] and lv_status["current"][0]):
        logger.error("LV must be on (module must be powered for stability testing)")
        msg = f"Module is not properly powered. LV voltage ({lv_status['voltage'][0]}) and current ({lv_status['current'][0]})."
        raise RuntimeError(msg)

    if not np.allclose(lv_status["current"][0], nominal_current, atol=1e-2):
        logger.error("LV must be powered with nominal_current")
        msg = f"Module is not properly powered. LV current for layer: {layer} should be: {nominal_current}, where this module is powered with: {lv_status['current'][0]}. Please check your LV settings properly and try again!"
        raise RuntimeError(msg)

    logger.info(
        "--------------------------------------------------------------------------"
    )

    end_duration = config["duration"]
    period = config["period"]
    # shorten duration and period if using emulator
    if "emulator" in config["yarr"]["run_dir"]:
        end_duration = 48
        period = 0.5

    starttime = time.time()

    progress = ProgressTable(
        SpinnerColumn(),
        *Progress.get_default_columns(),
        TimeElapsedColumn(),
        measurements=build_table(),
        transient=True,
    )

    duration = 0.0
    with progress:
        task = progress.add_task(
            "Running long-term stability DCS measurements...",
            total=math.ceil(end_duration / period),
        )
        while duration < end_duration:
            # read voltage
            bias_volt, hv_status = hv.measV()
            if hv_status:
                logger.error(
                    'Cannot read voltage from the HV supply. Try increase "n_try" in the measurement configuration.'
                )
                break

            lv_volt, lv_status = ps.measV()
            if lv_status:
                logger.error(
                    'Cannot read voltage from the LV supply. Try increase "n_try" in the measurement configuration.'
                )
                break

            # read current
            leakage_curr, hi_status = hv.measI()
            if hi_status:
                logger.error(
                    'cannot read current from the HV supply. try increase "n_try" in the measurement configuration.'
                )

            lv_curr, li_status = ps.measI()
            if li_status:
                logger.error(
                    'cannot read current from the LV supply. try increase "n_try" in the measurement configuration.'
                )

            # read temperature
            mod_temp, _temp_status = nt.read()

            # fill in data
            mea = {
                "time": [duration],
                "BIAS_VOLT": [bias_volt],
                "LEAKAGE_CURR": [leakage_curr],
                "LV_VOLT": [lv_volt],
                "LV_CURR": [lv_curr],
                "MOD_TEMP": [mod_temp],
            }

            if hr:
                # read humidity
                mod_hum, _hum_status = hr.read()
                mea["MOD_HUM"] = [mod_hum]

            data.add_data(mea)
            progress.measurements = build_table(data, nrows=10)

            progress.update(task, advance=1)
            time.sleep(period)
            duration = time.time() - starttime

    data.add_meta_data("AverageTemperature", np.average(data["MOD_TEMP"]))
    return data

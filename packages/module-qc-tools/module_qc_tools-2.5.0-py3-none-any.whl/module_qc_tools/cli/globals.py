import logging
from enum import Enum
from pathlib import Path
from typing import Optional

import click
import typer
from click.exceptions import MissingParameter
from module_qc_data_tools.utils import (
    check_sn_format,
)

from module_qc_tools.typing_compat import Annotated, TypeAlias
from module_qc_tools.utils.misc import get_institution

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


class LogLevel(str, Enum):
    debug = "DEBUG"
    info = "INFO"
    warning = "WARNING"
    error = "ERROR"


OPTIONS: [str, TypeAlias] = {}


def check_module_connectivity(hw_config_path: Path, module_connectivity: Path):
    # connectivity for emulator is defined in config, not true when running on module (on purpose)
    # NB: even though config_path is 'Path' type, it is a string in the context until passed to an actual function/coerced
    if "emulator" not in str(hw_config_path) and not module_connectivity:
        msg = "must supply path to connectivity file [-m --module-connectivity]"
        raise MissingParameter(
            message=msg, ctx=None, param=click.Option(["-m", "--module-connectivity"])
        )  # synchronize with OPTION_module_connectivity


OPTION_config_meas = Annotated[
    Optional[Path],
    typer.Option(
        "-cm",
        "--config-meas",
        help="Measurement config file path",
        exists=True,
        file_okay=True,
        readable=True,
        writable=True,
        resolve_path=True,
    ),
]
OPTION_config_hw = Annotated[
    Path,
    typer.Option(
        "-c",
        "--config",
        help="Hardware Config file path",
        exists=True,
        file_okay=True,
        readable=True,
        resolve_path=True,
    ),
]
OPTION_output_dir = Annotated[
    Path,
    typer.Option(
        "-o",
        "--output-dir",
        help="output directory",
        exists=False,
        writable=True,
    ),
]


OPTION_module_connectivity = Annotated[
    Optional[Path],
    typer.Option(
        "-m",
        "--module-connectivity",
        help="path to the module connectivity. Used also to identify the module SN, and to set the default output directory",
        exists=True,
        file_okay=True,
        readable=True,
        writable=True,
        resolve_path=True,
    ),
]


def verbosity_callback(ctx: typer.Context, value: LogLevel):
    if ctx.resilient_parsing:
        return None

    logging.getLogger("measurement").setLevel(value.value)
    logging.getLogger("emulator").setLevel(value.value)
    logging.getLogger("upload").setLevel(value.value)
    return value


OPTION_verbosity = Annotated[
    LogLevel,
    typer.Option(
        "-v",
        "--verbosity",
        help="Log level [options: DEBUG, INFO, WARNING, ERROR]",
        callback=verbosity_callback,
    ),
]
OPTION_perchip = Annotated[
    bool,
    typer.Option(
        "--permodule/--perchip",
        help="Store results in one file per chip (default: one file per module)",
    ),
]
OPTION_use_pixel_config = Annotated[
    bool,
    typer.Option(
        help="Use original chip configs; do not create temporary chip configs excluding Pixel Config",
    ),
]
OPTION_measurement_path = Annotated[
    Path,
    typer.Option(
        "-p",
        "--path",
        help="Path to directory with output measurement files",
        exists=True,
        file_okay=True,
        readable=True,
        writable=True,
        resolve_path=True,
    ),
]


def site_callback(ctx: typer.Context, value: str):
    if ctx.resilient_parsing:
        return None

    institution = get_institution(value)
    if not institution:
        msg = 'No institution found. Please specify your testing site as an environmental variable "INSTITUTION" or specify with the --site option.'
        raise typer.BadParameter(msg)

    return institution


OPTION_site = Annotated[
    str,
    typer.Option(
        "--site",
        help='Your testing site. Required when submitting results to the database. Please use institute codes defined on production DB, i.e. "LBNL_PIXEL_MODULES" for LBNL, "IRFU" for Paris-Saclay, ...',
        callback=site_callback,
    ),
]

OPTION_host = Annotated[str, typer.Option("--host", help="localDB server")]
OPTION_port = Annotated[
    int,
    typer.Option(
        "--port",
        help="localDB port",
    ),
]
OPTION_dry_run = Annotated[
    bool,
    typer.Option(
        "-n",
        "--dry-run",
        help="Dry-run, do not submit to localDB or update controller config.",
    ),
]
OPTION_output_path = Annotated[
    Path,
    typer.Option(
        "--out",
        "--output-path",
        help="Analysis output result json file path to save in the local host",
        exists=False,
        writable=True,
    ),
]
OPTION_use_calib_ADC = Annotated[
    bool,
    typer.Option(
        help="Use calibrated ADC instead of multimeter to read IMUX/VMUX",
    ),
]
OPTION_emulator_controller = Annotated[
    Path,
    typer.Option(
        "-r",
        "--controller",
        help="Controller",
        # exists=True,  # NB: enable when fixed for emulator (does not check for valid paths)
        file_okay=True,
        readable=True,
        writable=True,
        resolve_path=True,
    ),
]
OPTION_emulator_connectivity = Annotated[
    Path,
    typer.Option(
        "-c",
        "--connectivity",
        help="Connectivity",
        exists=True,
        file_okay=True,
        readable=True,
        writable=True,
        resolve_path=True,
    ),
]
OPTION_emulator_chip_position = Annotated[
    int, typer.Option("-i", "--chipPosition", help="chip position")
]
OPTION_depl_volt = Annotated[
    float,
    typer.Option(
        "--vdepl",
        help="Depletion voltage from production database",
    ),
]
OPTION_skip_config = Annotated[
    bool,
    typer.Option(
        "-s",
        "--skip-config",
        help="Skip configuring the chip when running eye diagram.",
    ),
]
OPTION_test_size = Annotated[
    int,
    typer.Option(
        "-t",
        "--test-size",
        help="Test size for eye diagram or data merging check.",
    ),
]
OPTION_mode = Annotated[
    str,
    typer.Option(
        "-m",
        "--mode",
        help="Mode of data merging check: '4-to-1' or '2-to-1'",
    ),
]
OPTION_quiet = Annotated[
    bool,
    typer.Option(
        "-q",
        "--quiet",
        help="Quiet mode, no logger in data merging check.",
    ),
]
OPTION_debug_gnd = Annotated[
    bool,
    typer.Option(
        "--debug-gnd",
        help="Measure GND before each Vmux measurement as opposed to just at the beginning. Relevant for ADC Calibration, Analog Readback and Injection capacitance.",
    ),
]
OPTION_save_local = Annotated[
    bool,
    typer.Option(
        help="If true, save measurement to local filesystem and do not upload to localDB. If false, upload to localDB and remove from local filesystem if upload succeeds.",
    ),
]
OPTION_poweroff = Annotated[
    bool,
    typer.Option(
        help="Whether to turn off power supplies (low-voltage, high-voltage) after measurement is done",
    ),
]
OPTION_bias = Annotated[
    bool,
    typer.Option(
        help="Whether to run with bias voltage applied to the sensor. Digital or dummy modules are automatically excluded from needing a bias voltage. Specify `--no-bias` if you intend to test a module (with sensor) without HV applied.",
    ),
]
OPTION_nchips = Annotated[
    int,
    typer.Option(
        "-n",
        "--nChips",
        help="Number of chips powered in parallel (e.g. 4 for a quad module, 3 for a triplet, 1 for an SCC.) If no argument is provided, the number of chips is assumed from the layer.",
    ),
]


def sn_callback(value: str):
    try:
        check_sn_format(value)
    except SystemExit as e:
        msg = f"Invalid serial number format: {value}"
        raise typer.BadParameter(msg) from e
    return value


OPTION_serial_number = Annotated[
    str,
    typer.Option(
        "-sn",
        "--serial-number",
        help="Module serial number",
        callback=sn_callback,
    ),
]

OPTION_scans = Annotated[
    list[str],
    typer.Option(
        "--scan",
        help="scan(s) to run, e.g. 'digitalscan.json -m 1'",
    ),
]

OPTION_tags = Annotated[
    list[str],
    typer.Option(
        "--tag",
        help="tag(s) to add",
    ),
]
OPTION_run_eye_diagram = Annotated[
    bool,
    typer.Option(
        "--skip-eye-diagram/--run-eye-diagram",
        help="Run eye diagram before running the scan(s).",
    ),
]

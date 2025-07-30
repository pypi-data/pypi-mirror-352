import logging
import shlex
from datetime import datetime
from pathlib import Path

import typer
from module_qc_data_tools.utils import (
    get_chip_type_from_serial_number,
    get_layer_from_sn,
    get_sn_from_connectivity,
)
from packaging.version import Version

from module_qc_tools.cli.globals import (
    CONTEXT_SETTINGS,
    LogLevel,
    OPTION_config_hw,
    OPTION_module_connectivity,
    OPTION_output_dir,
    OPTION_run_eye_diagram,
    OPTION_scans,
    OPTION_tags,
    OPTION_use_pixel_config,
    OPTION_verbosity,
    check_module_connectivity,
)
from module_qc_tools.utils.misc import load_hw_config
from module_qc_tools.utils.yarr import yarr

app = typer.Typer(context_settings=CONTEXT_SETTINGS)

# Taking the test-type from the script name which is the test-code in ProdDB.
TEST_TYPE = Path(__file__).stem

logger = logging.getLogger("measurement")


SCANS_MHT = [
    "std_digitalscan.json",
    "std_analogscan.json",
    "std_thresholdscan_hr.json",
    "std_totscan.json -t 6000",
]

# Tuning requires a lot more logic
SCANS_TUN_PRE = ["std_thresholdscan_hr.json", "std_totscan.json -t 6000"]
SCANS_TUN_POST = ["std_thresholdscan_hd.json", "std_totscan.json -t 6000"]

## ToT tuning for v2 chips
SCANS_TUN_TOT = ["std_tune_globalpreamp.json -t 6000 7"]
SCANS_TUN_L0_TOT = ["std_tune_globalthreshold.json -t 1200", *SCANS_TUN_TOT]
SCANS_TUN_L1_L2_TOT = ["std_tune_globalthreshold.json -t 1700", *SCANS_TUN_TOT]

## Tuning by layer
SCANS_TUN_L0 = [
    "std_tune_globalthreshold.json -t 1200",
    "std_tune_pixelthreshold.json -t 1000",
]
SCANS_TUN_L1_L2 = [
    "std_tune_globalthreshold.json -t 1700",
    "std_tune_pixelthreshold.json -t 1500",
]

SCANS_TUN_CORE = {
    ("RD53B", "L0"): SCANS_TUN_L0,
    ("RD53B", "L1"): SCANS_TUN_L1_L2,
    ("RD53B", "L2"): SCANS_TUN_L1_L2,
    ("ITKPIXV2", "L0"): SCANS_TUN_L0_TOT + SCANS_TUN_L0,
    ("ITKPIXV2", "L1"): SCANS_TUN_L1_L2_TOT + SCANS_TUN_L1_L2,
    ("ITKPIXV2", "L2"): SCANS_TUN_L1_L2_TOT + SCANS_TUN_L1_L2,
}

SCANS_PFA = [
    "std_digitalscan.json -m 1",
    "std_analogscan.json",
    "std_thresholdscan_hd.json",
    "std_totscan.json -t 6000",
    "std_noisescan.json",
    "std_discbumpscan.json",
    "std_mergedbumpscan.json -t 2000",
]


def generate_scan_table_docstring(scans, indent=4):
    # NB: the "\n" is very important to render docstrings properly
    docstring = """\n| Scan      | Additional Args                          |
| ----------- | ------------------------------------ |
"""

    for scan_str in scans:
        scan, *scan_opts = shlex.split(scan_str)
        scan_opt = f"`{shlex.join(scan_opts)}`" if scan_opts else "none"
        docstring += f"| `{scan}` | {scan_opt} |\n"

    indent_str = " " * indent
    return indent_str + (f"\n{indent_str}").join(docstring.splitlines())


@app.command("scan")
def main(
    hw_config_path: OPTION_config_hw = ...,
    base_output_dir: OPTION_output_dir = Path("outputs"),
    module_connectivity: OPTION_module_connectivity = None,
    use_pixel_config: OPTION_use_pixel_config = True,
    _verbosity: OPTION_verbosity = LogLevel.info,
    scans: OPTION_scans = ...,
    tags: OPTION_tags = None,
    run_eye_diagram: OPTION_run_eye_diagram = False,
):
    """
    Run general yarr scan
    """
    check_module_connectivity(
        hw_config_path=hw_config_path, module_connectivity=module_connectivity
    )

    tags = tags or []

    timestart = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    # if -o option used, overwrite the default output directory
    output_dir = module_connectivity.parent if module_connectivity else base_output_dir

    if base_output_dir != Path("outputs"):
        output_dir = base_output_dir

    output_dir = output_dir.joinpath("Measurements", TEST_TYPE, timestart)
    # Make output directory and start log file
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Start {TEST_TYPE.replace('_',' ')}!")
    logger.info(f"TimeStart: {timestart}")

    logger.addHandler(logging.FileHandler(output_dir.joinpath("output.log")))

    config_hw = load_hw_config(hw_config_path)

    if module_connectivity:
        config_hw["yarr"]["connectivity"] = module_connectivity

    # Taking the module SN from YARR path to config in the connectivity file.
    module_serial = get_sn_from_connectivity(config_hw["yarr"]["connectivity"])
    chip_type = get_chip_type_from_serial_number(module_serial)

    # initialize hardware
    yr = yarr(config_hw["yarr"])

    if not use_pixel_config:
        yr.omit_pixel_config()

    scan_output = output_dir / "data"
    scan_output.mkdir(parents=True, exist_ok=True)

    logger.info("Scan output directory: %s", scan_output)

    if run_eye_diagram:
        yr.eyeDiagram()

    required_yarr_version = "1.5.3"
    if any("corecolumnscan.json" in scan for scan in scans) and Version(
        yr.version
    ) < Version(required_yarr_version):
        msg = "Your YARR version is {yr.version} but some of the scans you requested require {required_yarr_version}"
        raise RuntimeError(msg)

    for scan in scans:
        # update the scan name to inject the prefix needed
        scan_opts = shlex.split(scan)
        scan_path = str(
            yr.run_dir / "configs" / "scans" / chip_type.lower() / scan_opts.pop(0)
        )

        yr.run_scan(
            shlex.join([scan_path, *scan_opts]),
            output=output_dir,
            skip_reset=False,
            tags=tags,
        )

    logger.info("Done!")
    logger.info(f"TimeEnd: {datetime.now().strftime('%Y-%m-%d_%H%M%S')}")

    # Delete temporary files
    if not use_pixel_config:
        yr.remove_tmp_connectivity()


@app.command("mht")
def mht(
    hw_config_path: OPTION_config_hw = ...,
    base_output_dir: OPTION_output_dir = Path("outputs"),
    module_connectivity: OPTION_module_connectivity = None,
    use_pixel_config: OPTION_use_pixel_config = True,
    _verbosity: OPTION_verbosity = LogLevel.info,
    tags: OPTION_tags = None,
):
    """
    Run Minimum Health Test
    \f
    MHT Scans:

    {}
    """
    check_module_connectivity(
        hw_config_path=hw_config_path, module_connectivity=module_connectivity
    )

    tags = list({*(tags or []), "MHT"})

    main(
        hw_config_path,
        base_output_dir,
        module_connectivity,
        use_pixel_config,
        _verbosity,
        scans=SCANS_MHT,
        tags=tags,
        run_eye_diagram=True,
    )


@app.command("tun")
def tun(
    hw_config_path: OPTION_config_hw = ...,
    base_output_dir: OPTION_output_dir = Path("outputs"),
    module_connectivity: OPTION_module_connectivity = None,
    use_pixel_config: OPTION_use_pixel_config = True,
    _verbosity: OPTION_verbosity = LogLevel.info,
    tags: OPTION_tags = None,
):
    """
    Run TUNing
    \f
    TUN Scans (for `chip_type` and `layer`):

    {}
    """
    check_module_connectivity(
        hw_config_path=hw_config_path, module_connectivity=module_connectivity
    )

    config_hw = load_hw_config(hw_config_path)

    if module_connectivity:
        config_hw["yarr"]["connectivity"] = module_connectivity

    # Taking the module SN from YARR path to config in the connectivity file.
    module_serial = get_sn_from_connectivity(config_hw["yarr"]["connectivity"])
    layer = get_layer_from_sn(module_serial)
    chip_type = get_chip_type_from_serial_number(module_serial)

    scans = SCANS_TUN_PRE + SCANS_TUN_CORE[(chip_type, layer)] + SCANS_TUN_POST

    tags = list({*(tags or []), "TUN"})

    main(
        hw_config_path,
        base_output_dir,
        module_connectivity,
        use_pixel_config,
        _verbosity,
        scans=scans,
        tags=tags,
        run_eye_diagram=True,
    )


@app.command("pfa")
def pfa(
    hw_config_path: OPTION_config_hw = ...,
    base_output_dir: OPTION_output_dir = Path("outputs"),
    module_connectivity: OPTION_module_connectivity = None,
    use_pixel_config: OPTION_use_pixel_config = True,
    _verbosity: OPTION_verbosity = LogLevel.info,
    tags: OPTION_tags = None,
):
    """
    Run Pixel Failure Analysis
    \f
    PFA Scans:

    {}
    """
    check_module_connectivity(
        hw_config_path=hw_config_path, module_connectivity=module_connectivity
    )

    tags = list({*(tags or []), "PFA"})

    main(
        hw_config_path,
        base_output_dir,
        module_connectivity,
        use_pixel_config,
        _verbosity,
        scans=SCANS_PFA,
        tags=tags,
        run_eye_diagram=True,
    )


@app.command("core-column")
def core_column(
    hw_config_path: OPTION_config_hw = ...,
    base_output_dir: OPTION_output_dir = Path("outputs"),
    module_connectivity: OPTION_module_connectivity = None,
    use_pixel_config: OPTION_use_pixel_config = True,
    _verbosity: OPTION_verbosity = LogLevel.info,
    tags: OPTION_tags = None,
):
    """
    Run the core-column scan.
    """
    check_module_connectivity(
        hw_config_path=hw_config_path, module_connectivity=module_connectivity
    )

    main(
        hw_config_path,
        base_output_dir,
        module_connectivity,
        use_pixel_config,
        _verbosity,
        scans=["corecolumnscan.json"],
        tags=tags,
    )


# needed for dynamically generated tables in docstrings
mht.__doc__ = mht.__doc__.format(generate_scan_table_docstring(SCANS_MHT))
tun.__doc__ = tun.__doc__.format(
    "\n\n".join(
        f"""
    === "`{chip_type}`, `{layer}`"

{generate_scan_table_docstring(SCANS_TUN_PRE + scans + SCANS_TUN_POST, indent=8)}"""
        for (chip_type, layer), scans in SCANS_TUN_CORE.items()
    )
)
pfa.__doc__ = pfa.__doc__.format(generate_scan_table_docstring(SCANS_PFA))

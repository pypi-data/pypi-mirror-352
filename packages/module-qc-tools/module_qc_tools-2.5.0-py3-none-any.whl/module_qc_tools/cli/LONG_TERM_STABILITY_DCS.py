import logging
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import typer
from module_qc_data_tools.qcDataFrame import (
    outputDataFrame,
)
from module_qc_data_tools.utils import (
    get_chip_type_from_serial_number,
    get_layer_from_sn,
    get_sn_from_connectivity,
    save_dict_list,
)
from module_qc_database_tools.utils import (
    get_BOMCode_from_file,
    get_cutFile_suffix,
)

from module_qc_tools.cli.globals import (
    CONTEXT_SETTINGS,
    LogLevel,
    OPTION_config_hw,
    OPTION_config_meas,
    OPTION_module_connectivity,
    OPTION_nchips,
    OPTION_output_dir,
    OPTION_poweroff,
    OPTION_save_local,
    OPTION_site,
    OPTION_verbosity,
    check_module_connectivity,
)
from module_qc_tools.console import console
from module_qc_tools.measurements.long_term_stability_dcs import run
from module_qc_tools.utils import datapath as mqt_data
from module_qc_tools.utils.misc import (
    add_identifiers_metadata,
    copytree,
    load_hw_config,
    load_meas_config,
)
from module_qc_tools.utils.power_supply import power_supply
from module_qc_tools.utils.yarr import yarr

logger = logging.getLogger("measurement")

app = typer.Typer(context_settings=CONTEXT_SETTINGS)

# Taking the test-type from the script name which is the test-code in ProdDB.
TEST_TYPE = Path(__file__).stem


@app.command()
def main(
    hw_config_path: OPTION_config_hw = ...,
    meas_config_path: OPTION_config_meas = mqt_data / "configs" / "meas_config.json",
    base_output_dir: OPTION_output_dir = Path("outputs"),
    module_connectivity: OPTION_module_connectivity = None,
    _verbosity: OPTION_verbosity = LogLevel.info,
    institution: OPTION_site = "",
    save_local: OPTION_save_local = True,
    poweroff: OPTION_poweroff = False,
    nchips: OPTION_nchips = None,
):
    """
    Collect DCS data for the long-term stability test (high-voltage power, module temperature).

    !!! note

        HV must be powered on (we won't know the correct bias so the user must have the HV powered on and script will exit early if not)

    !!! note

        LV must be powered on (we won't know the low-voltage power for the module, sometimes a chip is disabled)

    The following are measured:

    - duration (time of DCS "measurement")
    - HVPS voltage (sensor bias voltage)
    - HVPS current (sensor leakage current)
    - NTC (module temperature)
    - HRC (module humidity)
    """
    check_module_connectivity(
        hw_config_path=hw_config_path, module_connectivity=module_connectivity
    )

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
    layer = get_layer_from_sn(module_serial)
    chip_type = get_chip_type_from_serial_number(module_serial)

    # try to retrieve the BOM information from the config files
    BOM_file = (
        Path(config_hw["yarr"]["connectivity"]).parent / f"{module_serial}_info.json"
    )
    bom = get_BOMCode_from_file(BOM_file, layer)
    bom_suffix = get_cutFile_suffix(bom)

    # Load the  measurement config and combine it with the hardware config
    config = load_meas_config(
        meas_config_path,
        test_type=TEST_TYPE,
        chip_type=chip_type,
        bom_type=bom_suffix,
        layer=layer,
        nchips=nchips,
    )
    config.update(config_hw)

    # initialize hardware
    ps = power_supply(config["power_supply"])
    hv = power_supply(config["high_voltage"], name="high_voltage", is_hv=True)
    yr = yarr(config["yarr"])

    if yr.running_emulator():
        logger.info(
            f"Turning on power supply with V={config['v_max']}, I={config['i_config']}"
        )
        ps.on(v=config["v_max"], i=config["i_config"])
        hv.on(v=-100.0, i=1e-6)
        # Only for emulator do the emulation of power on/off
        # For real measurements avoid turn on/off the chip by commands. Just leave the chip running.

    try:
        data = run(config, ps, hv)
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt")
    except Exception as err:
        logger.exception(err)
        raise typer.Exit(1) from err

    if poweroff:
        logger.info("Ramping HV back to 0V...")
        hv.rampV(v=0, i=hv.getI())
        hv.off()

        logger.info("Turning module off...")
        ps.off()

    add_identifiers_metadata(data, module_serial, institution)

    alloutput = []

    console.print(data)
    outputDF = outputDataFrame()
    outputDF._serialNumber = module_serial
    outputDF.set_test_type(TEST_TYPE)

    if yr.running_emulator():
        logger.info("Tweaking TimeEnd to pretend this ran for 8 hours.")
        metadata = data.get_meta_data()
        duration = metadata["TimeEnd"] - metadata["TimeStart"]
        data.add_meta_data("TimeEnd", metadata["TimeStart"] + 60 * 60 * 8)
        data._data["time"]["Values"] = [
            i * (60 * 60 * 8 / duration) for i in data._data["time"]["Values"]
        ]

    outputDF.set_results(data)
    alloutput += [outputDF.to_dict()]

    with TemporaryDirectory() as tmpdirname:
        save_dict_list(
            Path(tmpdirname).joinpath(f"{module_serial}.json"),
            alloutput,
        )

        # for now, set to false until localDB upload functionality implemented
        upload_failed = True
        upload_implemented = False

        if not save_local:
            # add in logic here to upload to localDB
            msg = "Not implemented yet"
            raise RuntimeError(msg)

        if upload_failed or save_local:
            copytree(tmpdirname, output_dir)
            if upload_failed and upload_implemented:
                logger.warning(
                    "The upload to localDB failed. Please fix and retry uploading the measurement output again."
                )

            logger.info(f"Writing output measurements in {output_dir}")

    logger.info("Done!")
    logger.info(f"TimeEnd: {datetime.now().strftime('%Y-%m-%d_%H%M%S')}")


if __name__ == "__main__":
    typer.run(main)

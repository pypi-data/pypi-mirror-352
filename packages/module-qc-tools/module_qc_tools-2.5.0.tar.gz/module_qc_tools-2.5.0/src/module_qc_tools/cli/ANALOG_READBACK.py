import logging
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import itksn
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
    OPTION_bias,
    OPTION_config_hw,
    OPTION_config_meas,
    OPTION_debug_gnd,
    OPTION_module_connectivity,
    OPTION_nchips,
    OPTION_output_dir,
    OPTION_perchip,
    OPTION_save_local,
    OPTION_site,
    OPTION_use_calib_ADC,
    OPTION_use_pixel_config,
    OPTION_verbosity,
    check_module_connectivity,
)
from module_qc_tools.console import console
from module_qc_tools.measurements.analog_readback import (
    run_readregister,
    run_tmeas,
    run_vdda_vddd_vs_trim,
    run_vmeas,
)
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
    perchip: OPTION_perchip = False,
    use_pixel_config: OPTION_use_pixel_config = False,
    institution: OPTION_site = "",
    use_calib_adc: OPTION_use_calib_ADC = False,
    save_local: OPTION_save_local = True,
    debug_gnd: OPTION_debug_gnd = False,
    bias: OPTION_bias = True,
    nchips: OPTION_nchips = None,
):
    """
    run_xyz() creates the qcDataFrame where the measurements are stored in the qcDataFrame.
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

    if not bias or any(
        item in itksn.parse(module_serial.encode("utf-8")).component_code.lower()
        for item in ["digital", "dummy"]
    ):
        hv = None

    if not use_pixel_config:
        yr.omit_pixel_config()

    ps.set(v=config["v_max"], i=config["i_config"])
    yr.configure()

    # Measure internal vmux
    try:
        data = run_vmeas(config, ps, hv, yr, use_calib_adc)
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt")
        yr.remove_tmp_connectivity()
    except Exception as err:
        logger.info("Error in measuring all vmux values.")
        logger.exception(err)
        yr.remove_tmp_connectivity()
        raise typer.Exit(1) from err
    add_identifiers_metadata(data, module_serial, institution)

    # Measure vdda/vddd vs trim
    try:
        data_vdda_vddd_vs_trim = run_vdda_vddd_vs_trim(
            config,
            ps,
            hv,
            yr,
            debug_gnd,
            use_calib_adc,
        )
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt")
        yr.remove_tmp_connectivity()
    except Exception as err:
        logger.info("Error in measuring VDDA/VDDD vs trim.")
        logger.exception(err)
        yr.remove_tmp_connectivity()
        raise typer.Exit(1) from err
    add_identifiers_metadata(data_vdda_vddd_vs_trim, module_serial, institution)

    # Read register values
    if "itkpixv2" in chip_type.lower():
        try:
            data_register = run_readregister(config, ps, yr)
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt")
            yr.remove_tmp_connectivity()
        except Exception as err:
            logger.info("Error in reading registers.")
            logger.exception(err)
            yr.remove_tmp_connectivity()
            raise typer.Exit(1) from err
        add_identifiers_metadata(data_register, module_serial, institution)

    # Measure temperature at the end of the measurement to ensure temperature stability
    try:
        data_tempmeas = run_tmeas(config, ps, hv, yr, use_calib_adc)
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt")
        yr.remove_tmp_connectivity()
    except Exception as err:
        logger.info("Error in measuring temperature.")
        logger.exception(err)
        yr.remove_tmp_connectivity()
        raise typer.Exit(1) from err
    add_identifiers_metadata(data_tempmeas, module_serial, institution)

    # save results in json
    alloutput = []
    chipnames = []

    for chip in yr._enabled_chip_positions:
        console.print(data[chip])
        console.print(data_tempmeas[chip])
        chip_name = data[chip]._meta_data["Name"]

        for dataobj in [data, data_tempmeas, data_vdda_vddd_vs_trim]:
            dataobj[chip].add_meta_data("useCalibAdc", use_calib_adc)

        # Save to an output json file
        outputDF = outputDataFrame()
        outputDF.set_test_type(TEST_TYPE)
        outputDF.set_subtest_type("AR_VMEAS")
        outputDF.set_results(data[chip])

        outputDF_tempmeas = outputDataFrame()
        outputDF_tempmeas.set_test_type(TEST_TYPE)
        outputDF_tempmeas.set_subtest_type("AR_TEMP")
        outputDF_tempmeas.set_results(data_tempmeas[chip])

        outputDF_vdda_vddd_vs_trim = outputDataFrame()
        outputDF_vdda_vddd_vs_trim.set_test_type(TEST_TYPE)
        outputDF_vdda_vddd_vs_trim.set_subtest_type("AR_VDD")
        outputDF_vdda_vddd_vs_trim.set_results(data_vdda_vddd_vs_trim[chip])

        alloutput += [
            outputDF.to_dict(),
            outputDF_tempmeas.to_dict(),
            outputDF_vdda_vddd_vs_trim.to_dict(),
        ]

        if "itkpixv2" in chip_type.lower():
            outputDF_register = outputDataFrame()
            outputDF_register.set_test_type(TEST_TYPE)
            outputDF_register.set_subtest_type("AR_REGISTER")
            outputDF_register.set_results(data_register[chip])
            alloutput += [outputDF_register.to_dict()]

        chipnames += [chip_name]

    with TemporaryDirectory() as tmpdirname:
        if perchip:
            for outputDF, chip_name in zip(alloutput, chipnames):
                save_dict_list(
                    Path(tmpdirname).joinpath(f"{chip_name}.json"),
                    [outputDF],
                )
        else:
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

    # Delete temporary files
    if not use_pixel_config:
        yr.remove_tmp_connectivity()


if __name__ == "__main__":
    typer.run(main)

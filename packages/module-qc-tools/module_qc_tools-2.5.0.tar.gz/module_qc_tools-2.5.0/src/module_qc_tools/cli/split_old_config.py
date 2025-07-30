import json
import logging
from importlib import resources
from pathlib import Path

import typer

from module_qc_tools.cli.globals import CONTEXT_SETTINGS
from module_qc_tools.typing_compat import Annotated
from module_qc_tools.utils.misc import (
    check_hw_config,
)

app = typer.Typer(context_settings=CONTEXT_SETTINGS)


@app.command()
def main(
    old_config_path: Annotated[
        Path,
        typer.Option(
            "-c",
            "--old-config",
            help="path to old qc config file",
            exists=True,
            file_okay=True,
            readable=True,
            resolve_path=True,
        ),
    ] = ...,
):
    """
    This code takes the old QC measurement config and splits it in two,
    one for the hardware, and one for the measurements.
    """

    logger = logging.getLogger("split-old-config")
    logger.setLevel("INFO")

    # open the old config json as 'data'
    with resources.as_file(old_config_path) as path:
        data = json.loads(path.read_text(encoding="utf-8"))

    # Separate the input JSON into two parts
    part1 = {
        "yarr": data["yarr"],
        "power_supply": data["power_supply"],
        "high_voltage": data["high_voltage"],
        "multimeter": {
            **data["multimeter"],
            "share_vmux": data["tasks"]["GENERAL"]["share_vmux"],
            "v_mux_channels": data["tasks"]["GENERAL"]["v_mux_channels"],
        },
        "ntc": data["ntc"],
    }

    part2 = {"tasks": data["tasks"]}
    del part2["tasks"]["GENERAL"]["share_vmux"]
    del part2["tasks"]["GENERAL"]["v_mux_channels"]

    # check that the new dicts match the schema
    check_hw_config(part1)
    #    check_meas_config(part2)

    # Save the parts to separate JSON files
    file_path1 = Path("new_hw_config.json")
    with file_path1.open("w", encoding="utf-8") as file1:
        json.dump(part1, file1, indent=4)

    #    file_path2 = Path("new_meas_config.json")
    #    with file_path2.open("w", encoding="utf-8") as file2:
    #        json.dump(part2, file2, indent=4)

    logger.info(f"Split {old_config_path} and created new_hw_config.json")
    logger.info(
        "The measurement information from the old config was not saved, as the default measurement config should be used when running standard QC scans."
    )


if __name__ == "__main__":
    typer.run(main)

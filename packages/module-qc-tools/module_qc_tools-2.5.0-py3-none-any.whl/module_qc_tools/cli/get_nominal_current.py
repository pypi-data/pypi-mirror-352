import json
import logging

import typer
from module_qc_data_tools.utils import (
    get_chip_type_from_serial_number,
    get_layer_from_sn,
    get_nominal_current,
)

from module_qc_tools.cli.globals import (
    CONTEXT_SETTINGS,
    OPTION_config_meas,
    OPTION_nchips,
    OPTION_serial_number,
)
from module_qc_tools.utils import datapath as mqt_data

app = typer.Typer(context_settings=CONTEXT_SETTINGS)

logger = logging.getLogger("measurement")


@app.command()
def main(
    meas_config_path: OPTION_config_meas = str(mqt_data / "configs/meas_config.json"),
    serial_number: OPTION_serial_number = "",
    n_chips_input: OPTION_nchips = 0,
):
    """Print the nominal current value required for the given module."""

    # Taking the module SN from YARR path to config in the connectivity file.
    layer = get_layer_from_sn(serial_number)
    chip_type = get_chip_type_from_serial_number(serial_number)

    # Load the  measurement config just to retrieve general info
    # could be improved, need to see the requirements
    meas_config = json.loads(meas_config_path.read_text())

    nom_current = get_nominal_current(meas_config, layer, chip_type, n_chips_input)

    typer.echo(f"{nom_current:.2f}")


if __name__ == "__main__":
    typer.run(main)

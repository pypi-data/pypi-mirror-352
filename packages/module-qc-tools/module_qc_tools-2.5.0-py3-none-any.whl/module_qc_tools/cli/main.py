"""
Top-level entrypoint for the command line interface.
"""
import typer

import module_qc_tools
from module_qc_tools.cli.ADC_CALIBRATION import main as adc_calibration
from module_qc_tools.cli.ANALOG_READBACK import main as analog_readback
from module_qc_tools.cli.DATA_TRANSMISSION import main as data_transmission
from module_qc_tools.cli.get_nominal_current import main as get_nominal_current
from module_qc_tools.cli.globals import (
    CONTEXT_SETTINGS,
)
from module_qc_tools.cli.hardware_emulator import (
    app as app_emulator,
)
from module_qc_tools.cli.INJECTION_CAPACITANCE import main as injection_capacitance
from module_qc_tools.cli.IV_MEASURE import main as iv_measure
from module_qc_tools.cli.LONG_TERM_STABILITY_DCS import main as long_term_stability_dcs
from module_qc_tools.cli.LP_MODE import main as lp_mode
from module_qc_tools.cli.OVERVOLTAGE_PROTECTION import main as overvoltage_protection
from module_qc_tools.cli.SLDO import main as sldo
from module_qc_tools.cli.split_old_config import main as split_old_config
from module_qc_tools.cli.UNDERSHUNT_PROTECTION import main as undershunt_protection
from module_qc_tools.cli.upload_localdb import main as upload_localdb
from module_qc_tools.cli.VCAL_CALIBRATION import main as vcal_calibration
from module_qc_tools.cli.yarr import app as app_yarr
from module_qc_tools.typing_compat import Annotated
from module_qc_tools.utils import datapath as mqt_data

# subcommands
app = typer.Typer(context_settings=CONTEXT_SETTINGS)
app_measurement = typer.Typer(context_settings=CONTEXT_SETTINGS)

app.add_typer(app_emulator, name="emulator")
app.add_typer(app_measurement, name="measurement")
app.add_typer(app_yarr, name="yarr", help="Execute yarr scans")


@app.callback(invoke_without_command=True)
def main(
    version: Annotated[
        bool, typer.Option("--version", help="Print the current version.")
    ] = False,
    prefix: Annotated[
        bool, typer.Option("--prefix", help="Print the path prefix for data files.")
    ] = False,
) -> None:
    """
    Manage top-level options
    """
    if version:
        typer.echo(f"module-qc-tools v{module_qc_tools.__version__}")
        raise typer.Exit()
    if prefix:
        typer.echo(mqt_data.resolve())
        raise typer.Exit()


app_measurement.command("adc-calibration")(adc_calibration)
app_measurement.command("analog-readback")(analog_readback)
app_measurement.command("data-transmission")(data_transmission)
app_measurement.command("sldo")(sldo)
app_measurement.command("vcal-calibration")(vcal_calibration)
app_measurement.command("injection-capacitance")(injection_capacitance)
app_measurement.command("lp-mode")(lp_mode)
app_measurement.command("overvoltage-protection")(overvoltage_protection)
app_measurement.command("undershunt-protection")(undershunt_protection)
app_measurement.command("iv-measure")(iv_measure)
app_measurement.command("long-term-stability-dcs")(long_term_stability_dcs)

app.command("upload")(upload_localdb)
app.command("split-old-config")(split_old_config)
app.command("get-nom-current")(get_nominal_current)

# for generating documentation using mkdocs-click
typer_click_object = typer.main.get_command(app)

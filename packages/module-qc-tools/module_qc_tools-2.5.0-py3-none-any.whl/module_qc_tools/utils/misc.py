#!/usr/bin/env python3
from __future__ import annotations

import copy
import functools
import json
import logging
import os
import shutil
import sys
from collections.abc import Iterable
from datetime import datetime, timezone
from importlib import resources
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema import validate
from module_qc_data_tools import get_n_chips, get_nominal_current
from rich.console import RenderableType
from rich.progress import Progress

from module_qc_tools import __version__, data

if sys.version_info >= (3, 11):
    from datetime import UTC
else:
    UTC = timezone.utc

logger = logging.getLogger("measurement")


# https://github.com/scipp-atlas/mapyde/blob/956edebdad348cabd66aa143acac7fdcfcff6dae/src/mapyde/utils.py#L33-L49
def merge(base: dict, other: dict, path: list | None = None):
    """
    Deeply merge dictionaries of dictionaries.

    This mutates the base dictionary - the contents of the other dictionary are
    added to the base dictionary. The (mutated) base dictionary is also
    returned. If you want to keep the base dictionary non-mutated, you could
    call it like so: merge(dict(base), other).

    Args:
        base (:obj:`dict`): Base dictionary for merging.
        other (:obj:`dict`): Corresponding dictionary for merging into the base.
        path (:obj:`list`): A key on which to deeply merge items if set.

    Returns:
        :obj:`dict`: Deeply merged base dictionary.

    Example:
        >>> import module_qc_tools.utils.misc
        >>> module_qc_tools.utils.misc.merge({1:{"a":"A"},2:{"b":"B"}}, {2:{"c":"C"},3:{"d":"D"}})
        {1: {'a': 'A'}, 2: {'b': 'B', 'c': 'C'}, 3: {'d': 'D'}}
        >>> module_qc_tools.utils.misc.merge({1:{"a":"A"},2:{"b":"B"}}, {1:{"a":"A"},2:{"b":"C"}})  # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        ValueError: Conflict at 2.b


    """

    path = path or []

    for key in other:
        if key in base:
            if isinstance(base[key], dict) and isinstance(other[key], dict):
                merge(base[key], other[key], [*path, str(key)])
            elif base[key] != other[key]:
                msg = f"Conflict at {'.'.join([*path, str(key)])}"
                raise ValueError(msg)
        else:
            base[key] = other[key]
    return base


def load_meas_config(config_path, test_type, chip_type, bom_type, layer, nchips):
    with resources.as_file(config_path) as path:
        config = json.loads(path.read_text(encoding="utf-8"))

    # if nchips was not entered as a command line argument, use the default number of chips for the given layer
    if nchips is None:
        nchips = get_n_chips(layer)

    check_meas_config(config)
    logger.info(f"Using {config_path} for measurement config")
    return Config(
        config,
        test_type=test_type,
        chip_type=chip_type,
        bom_type=bom_type,
        layer=layer,
        nchips=nchips,
    )


def load_hw_config(config_path):
    with resources.as_file(config_path) as path:
        config = json.loads(path.read_text(encoding="utf-8"))

    # check if config is in the old format
    if "tasks" in config and "yarr" in config:
        logger.error(
            f"{config_path} has both measurement and hardware configs in it. This config structure is now deprecated. You can generate a new config by calling the following:"
        )
        logger.error(f"mqt split-old-config -c {config_path}")

    check_hw_config(config)
    logger.info(f"Using {config_path} for hardware config")
    return config


def get_chip_type(config):
    chiptype = ""
    try:
        chiptype = next(iter(config))
    except IndexError:
        logger.error("[bright_red]One of your chip configuration files is empty[/]")

    if chiptype not in {"RD53B", "ITKPIXV2"}:
        logger.warning(
            "[bright_yellow]Chip name in configuration not one of expected chip names (RD53B or ITKPIXV2)[/]"
        )
    return chiptype


def get_identifiers(config):
    identifiers = {}
    chiptype = get_chip_type(config)
    identifiers["ChipID"] = config[chiptype]["Parameter"]["ChipId"]
    identifiers["Name"] = config[chiptype]["Parameter"]["Name"]
    identifiers["Institution"] = ""
    identifiers["ModuleSN"] = ""
    return identifiers


def get_meta_data(config):
    return {
        "FirmwareVersion": "",
        "FirmwareIdentifier": "",
        "ChannelConfig": "",
        "SoftwareVersion": "",
        "ChipConfigs": config,
        "SoftwareType": "",
    }


def check_meas_config(input_data, path=None):
    info_schema = json.loads((data / "schema" / "meas_config.json").read_text())
    try:
        validate(instance=input_data, schema=info_schema)
    except jsonschema.exceptions.ValidationError as err:
        msg = "[bright_red]Input measurement config fails schema check with the following error:[/]"
        if path:
            msg += f"\n[bright_red]Input config: {path}[/]"
        msg += f"[bright_red]Json Schema: {data / 'schema/meas_config.json'!s}[/]"

        logger.exception(msg)
        raise RuntimeError() from err


def check_hw_config(input_data, path=None):
    info_schema = json.loads((data / "schema" / "hw_config.json").read_text())
    try:
        validate(instance=input_data, schema=info_schema)
    except jsonschema.exceptions.ValidationError as err:
        msg = "[bright_red]Input hardware config fails schema check with the following error:[/]"
        if path:
            msg += f"\n[bright_red]Input config: {path}[/]"
        msg += f"[bright_red]Json Schema: {data / 'schema/hw_config.json'!s}[/]"

        logger.exception(msg)
        raise RuntimeError() from err


# Function to check that reading ground through ADC does return 0 counts
def check_adc_ground(yr, scan_config):
    vmux_gnd = yr.read_adc(
        30,
        readCurrent=False,
        rawCounts=True,
        share_vmux=scan_config["multimeter"]["share_vmux"],
    )[0].split()
    imux_gnd = yr.read_adc(
        63,
        readCurrent=True,
        rawCounts=True,
        share_vmux=scan_config["multimeter"]["share_vmux"],
    )[0].split()
    if any(int(x) > 100 for x in vmux_gnd) or any(int(x) > 100 for x in imux_gnd):
        logger.error(
            f"[bright_red]Reading Vmux30(Imux63) (ground) through ADC gave {vmux_gnd}({imux_gnd}) counts - when it should be 0(0)! Please check.[/]"
        )
        raise RuntimeError()
    if any(int(x) > 0 for x in vmux_gnd) or any(int(x) > 0 for x in imux_gnd):
        logger.error(
            f"[bright_yellow]Reading Vmux30(Imux63) (ground) through ADC gave small but non-zero counts: {vmux_gnd}({imux_gnd}).[/]"
        )
    return vmux_gnd, imux_gnd


# Convert micro-amps to voltages using rImux
# TODO: Decide if I should change read-adc script to return V instead
def microItoV(read_uA, yr):
    read_V = []
    for r, chip in zip(read_uA, yr._enabled_chip_positions):
        try:
            chipconfig = yr.get_config(chip)
            rImux = chipconfig[get_chip_type(chipconfig)]["Parameter"]["ADCcalPar"][2]
        except Exception:
            rImux = 4.99e3  # Default in YARR read-adc script
            logger.warning(
                f"[bright_yellow]Unable to find rImux from ADCcalPar in chip config - using default rImux = {rImux} Ohm[/]"
            )
        read_V += [r * 1e-6 * rImux]
    return read_V


# Function to read vmux through multimter or ADC, handles shared / separate vmux
def read_vmux(
    meter,
    yr,
    scan_config,
    chip_position=None,
    v_mux=-1,
    i_mux=-1,
    use_adc=False,
    raw_adc_counts=False,
):
    logger.debug(
        f"Reading monitorV={v_mux}, monitorI={i_mux} with use_adc={use_adc} and raw_adc_counts={raw_adc_counts}"
    )
    reads = []

    # Read through ADC
    if use_adc:
        # Read ground as 0
        if (19 <= v_mux <= 30) or (i_mux == 63):
            for chip in yr._enabled_chip_positions:
                if chip != chip_position and chip_position is not None:
                    continue
                reads.append(0.0)
        else:
            if i_mux > -1:
                read = yr.read_adc(
                    i_mux,
                    readCurrent=True,
                    rawCounts=raw_adc_counts,
                    chip_position=chip_position,
                    share_vmux=scan_config["multimeter"]["share_vmux"],
                )[0]
            else:
                read = yr.read_adc(
                    v_mux,
                    readCurrent=False,
                    rawCounts=raw_adc_counts,
                    chip_position=chip_position,
                    share_vmux=scan_config["multimeter"]["share_vmux"],
                )[0]
            try:
                if raw_adc_counts:
                    reads = [int(x) for x in read.split()]
                else:
                    reads = [float(x) for x in read.split()[0::2]]  # Remove units
            except Exception as e:
                logger.error(f"Unable to decode return from read_adc: {read}")
                raise RuntimeError() from e

            # If we read current, we need to convert back to V
            if i_mux > -1:
                reads = microItoV(reads, yr)

    # Read through multimeter
    else:
        for chip in yr._enabled_chip_positions:
            if chip != chip_position and chip_position is not None:
                continue
            yr.set_mux(
                chip_position=chip,
                v_mux=v_mux,
                i_mux=i_mux,
                reset_other_chips=scan_config["multimeter"]["share_vmux"],
            )
            meas, _status = meter.measure_dcv(
                channel=scan_config["multimeter"]["v_mux_channels"][chip]
            )
            reads.append(meas)

    return reads


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = Path(src) / item
        d = Path(dst) / item
        if Path(s).is_dir():
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def get_institution(site):
    institution = os.getenv("INSTITUTION")
    if site:
        if institution is not None:
            logger.warning(
                f"[bright_yellow]Overwriting default institution {institution} with manual input {site}![/]"
            )
        return site

    return institution


def initialize_chip_metadata(yr, output_data):
    """
    Initialize output dataframes' metadata with corresponding metadata/identifiers from yarr.

    Args:
        yr (yarr): yarr object
        output_data (module_qc_data_tools.outputDataFrame or list[...] or list[list[...]]): one or more output dataframes to update metadata on recursively
    """
    for chip in yr._enabled_chip_positions:
        # NB: we are merging in nested configurations to ensure uniform structure
        chip_metadata = get_meta_data(yr.get_config(chip))
        identifiers = get_identifiers(yr.get_config(chip))

        chip_data = output_data[chip]

        for subtest in chip_data if isinstance(chip_data, list) else [chip_data]:
            subtest._meta_data = merge(
                copy.deepcopy({**chip_metadata, **identifiers}), subtest._meta_data
            )


def add_identifiers_metadata(output_data, module_serial, institution):
    """
    Add module serial number and institution to the output dataframe, recursively.

    Args:
        output_data (module_qc_data_tools.outputDataFrame or list[module_qc_data_tools.outputDataFrame]): one or more output dataframes to update metadata on
        module_serial (str): module serial number
        institution (str): institution code
    """
    for item in output_data if isinstance(output_data, list) else [output_data]:
        if isinstance(item, list):
            add_identifiers_metadata(item, module_serial, institution)
        else:
            item.add_meta_data("Institution", institution)
            item.add_meta_data("ModuleSN", module_serial)


def add_version_metadata(output_data, test_type):
    """
    Add measurement version to the output dataframe.

    Args:
        output_data (module_qc_data_tools.outputDataFrame): output dataframe to update metadata on
        test_type (str): test type code
    """
    for item in output_data if isinstance(output_data, list) else [output_data]:
        if isinstance(item, list):
            add_version_metadata(item, test_type)
        else:
            item.add_property(f"{test_type}_MEASUREMENT_VERSION", __version__)


def add_yarr_version(output_data, yarr):
    """
    Add YARR version to the output dataframe.

    Args:
        output_data (module_qc_data_tools.outputDataFrame): output dataframe to update metadata on
    """
    for item in output_data if isinstance(output_data, list) else [output_data]:
        if isinstance(item, list):
            add_yarr_version(item, yarr.version)
        else:
            item.add_property("YARR_VERSION", yarr.version)


def add_timestamps_metadata(output_data, time_start, time_end):
    """
    Add timestamping (start and end) to the output dataframe, recursively.

    Args:
        output_data (module_qc_data_tools.outputDataFrame or list[module_qc_data_tools.outputDataFrame]): one or more output dataframes to update metadata on
        time_start (int): starting timestamp in seconds since unix epoch
        time_end (int): ending timestamp in seconds since unix epoch
    """
    for item in output_data if isinstance(output_data, list) else [output_data]:
        if isinstance(item, list):
            add_timestamps_metadata(item, time_start, time_end)
        else:
            item.add_meta_data("TimeStart", time_start)
            item.add_meta_data("TimeEnd", time_end)


def inject_metadata(original_function=None, *, test_type=None, uses_yarr=True):
    """
    This is a decorator that allows for wrapping common functionality injecting metadata in as needed across all functions we use. Currently, this will add in the TimeStart/TimeEnd metadata, and update the metadata.

    If test_type is specified, it will additionally add in {test_type}_MEASUREMENT_VERSION' as a property.

    If uses_yarr is set False, it will not rely on the yarr object for iterating over the output dataframe.

    Args:
        original_function (callable): Function to decorate
        test_type (str): test type code
        uses_yarr (bool): whether to iterate over the dataframes to set metadata using the enabled chips

    This can be called in some ways:

        @inject_metadata
        def run(..., yr, ...) -> data: ...

        @inject_metadata(test_type="ADC_CALIBRATION")
        def run(..., yr, ...) -> data: ...

    """

    def _decorate(function):
        @functools.wraps(function)
        def wrapped_function(*args, **kwargs):
            yr = None
            for arg in args:
                if hasattr(arg, "_enabled_chip_positions"):
                    yr = arg
                    break
            if yr is None and uses_yarr:
                msg = "Cannot find yarr object in function call."
                raise RuntimeError(msg)

            time_start = round(datetime.timestamp(datetime.now(timezone.utc)))
            output_data = function(*args, **kwargs)
            time_end = round(datetime.timestamp(datetime.now(timezone.utc)))

            if uses_yarr:
                for chip in yr._enabled_chip_positions:
                    chip_data = output_data[chip]
                    add_timestamps_metadata(chip_data, time_start, time_end)
                    add_yarr_version(chip_data, yr)
                    if test_type:
                        add_version_metadata(chip_data, test_type)
            else:
                add_timestamps_metadata(output_data, time_start, time_end)
                if test_type:
                    add_version_metadata(output_data, test_type)

            return output_data

        return wrapped_function

    if original_function:
        return _decorate(original_function)

    return _decorate


def get_yarr_logging_timestamp():
    dt = datetime.now(UTC)
    return f"{dt:%H:%M:%S}.{dt.microsecond // 1000:03d}"


class Config(dict):
    def __init__(
        self,
        config: dict[Any, Any],
        *,
        test_type: str,
        chip_type: str,
        bom_type: str,
        layer: str,
        nchips: int,
    ):
        super().__init__(config)
        self._test_type = test_type

        # update the config to only store the General current setting for this chip, BOM type, and layer
        general_i_config = get_nominal_current(
            config, layer, chip_type, bom_type, nchips
        )
        config["tasks"]["GENERAL"]["i_config"] = general_i_config
        logger.info(f"Will use {general_i_config} A for PS current ({nchips} chips)")

        if test_type == "SLDO":
            chip_type_bom = chip_type
            if chip_type == "ITKPIXV2":
                if bom_type in ["_V1bom", "_V2bom"]:
                    chip_type_bom += bom_type
                else:
                    msg = f"Invalid BOM type ({bom_type}) for {chip_type} chip"
                    logger.error(msg)
                    raise ValueError(msg)
            # update the config to only store the SLDO Current settings for this chip and BOM type
            sldo_imin_config = config["tasks"]["SLDO"]["i_min"][chip_type_bom]
            config["tasks"]["SLDO"]["i_min"] = sldo_imin_config

            sldo_imax_config = config["tasks"]["SLDO"]["i_max"][chip_type_bom]
            config["tasks"]["SLDO"]["i_max"] = sldo_imax_config

            sldo_n_points_config = config["tasks"]["SLDO"]["n_points"][chip_type_bom]
            config["tasks"]["SLDO"]["n_points"] = sldo_n_points_config

    @property
    def test_type(self):
        return self._test_type

    @property
    def nominal(self):
        return self["tasks"]["GENERAL"]

    @property
    def measurement(self):
        return self["tasks"][self.test_type] if self.test_type else {}

    def __missing__(self, key):
        return self.measurement.get(key, self.nominal.get(key))


class ProgressTable(Progress):
    def __init__(self, *args, measurements=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.measurements = measurements

    def get_renderables(self) -> Iterable[RenderableType]:
        """Display progress together with info table"""
        task_table = self.make_tasks_table(self.tasks)
        if getattr(self, "measurements", None):
            yield self.measurements

        yield task_table

#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import json
import logging
import re
import tempfile
import time
from pathlib import Path

from module_qc_tools.utils.hardware_control_base import hardware_control_base

# if sys.version_info >= (3, 9):
#    from importlib import resources
# else:
#    import importlib_resources as resources

logger = logging.getLogger("measurement")


class yarr(hardware_control_base):
    def __init__(self, config, *args, name="yarr", **kwargs):
        self.version = ""
        self.run_dir = ""
        self.controller = ""
        self.tmp_dir = ""
        self.connectivity = ""
        self.scanConsole_exe = ""
        self.write_register_exe = ""
        self.read_register_exe = ""
        self.read_adc_exe = ""
        self.switchLPM_exe = ""
        self.lpm_digitalscan = ""
        self.read_ringosc_exe = ""
        self.dataMergingCheck_exe = ""
        self.eyeDiagram_exe = ""
        self.exe_postOpts = ""
        self.success_code = 0
        self.emulator = False
        self.max_attempts = (
            2  # max retries in case of communication failure with module
        )
        self.sleep_attempts = 2  # time (seconds) to sleep after each failed attempt
        super().__init__(config, *args, name=name, **kwargs)

        if "emulator" in self.scanConsole_exe:
            self.emulator = True
            logger.info(f"[{name}] running scanConsole emulator!!")
        if "emulator" in self.write_register_exe:
            self.emulator = True
            logger.info(f"[{name}] running write_register emulator!!")
        if "emulator" in self.switchLPM_exe:
            self.emulator = True
            logger.info(f"[{name}] running switchLPM emulator!!")
        if "emulator" in self.eyeDiagram_exe:
            self.emulator = True
            logger.info(f"[{name}] running eyeDiagram emulator!!")
        if "emulator" in self.dataMergingCheck_exe:
            self.emulator = True
            logger.info(f"[{name}] running dataMergingCheck emulator!!")

        self.version = self.get_yarr_version()
        logger.info(f"YARR version: {self.version}")

        connect_spec = self.get_connectivity()
        self._number_of_chips = len(connect_spec["chips"])
        self._enabled_chip_positions = set()
        self._chip_rx = {}
        for chip in range(self._number_of_chips):
            if connect_spec["chips"][chip]["enable"]:
                self._enabled_chip_positions.add(chip)
            self._chip_rx[chip] = connect_spec["chips"][chip]["rx"]
        self._register = [{} for chip in range(self._number_of_chips)]

    def running_emulator(self):
        return self.emulator

    def configure(self, skip_reset=False):
        cmd = f'{self.scanConsole_exe} -r {self.controller} -c {self.connectivity} {"--skip-reset" if skip_reset else ""}'

        self._register = [{} for chip in range(self._number_of_chips)]

        currLevel = logger.getEffectiveLevel()
        logger.setLevel(logging.DEBUG)
        # Below is the only case where success_code=1 is the default.
        # This is because the exit code of scanConsole for configuring the chip is 1 for success.
        # This will have to be removed once the YARR MR is merged (https://gitlab.cern.ch/YARR/YARR/-/issues/192).
        n_try = 0
        while n_try < self.max_attempts:
            try:
                logger.debug(f"Sending command (attempt {n_try}): ")
                logger.debug(cmd)
                self.send_command(cmd, purpose="configure module", success_code=1)
                logger.setLevel(currLevel)
                break
            except RuntimeError as err:
                n_try += 1
                if n_try < self.max_attempts:
                    logger.warning(
                        "Failed to configure. Running eye diagram scan and retrying."
                    )
                    time.sleep(self.sleep_attempts)
                    self.eyeDiagram(skipconfig=True)
                    continue
                msg = f"Unable to configure module after {self.max_attempts} attempts. Stopping measurement."
                raise RuntimeError(msg) from err

        # Check for LP-mode
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                filename = handler.baseFilename
                with Path(filename).open(encoding="utf-8") as f:
                    for line in f:
                        if "LPM Status" in line:
                            match = int(re.search(r":\s*(\d+)$", line).group(1))
                            if match != 0:
                                logger.warning(
                                    "[bright_yellow]Attention! Module is in low-power mode. If this is not intended, you can turn it off by running `./bin/switchLPM off` in YARR directory.[/]"
                                )

        return 0

    def get_yarr_version(self):
        if self.emulator:
            return "emulator"
        cmd = f"{self.scanConsole_exe} --version"
        try:
            # not really gitinfo but version info, looks like this:
            # {
            # "build_flags": "",
            # "build_time": "2025-04-24 15:42:03 UTC",
            # "build_type": "Release",
            # "git_branch": "build_info",
            # "git_date": "2025-04-03 13:29:03 +0100",
            # "git_hash": "c610839cf6318500971fb6b025f2ab8c01fc1746",
            # "git_subject": "Add build type/flags to version info",
            # "git_tag": "v1.5.3-90-gc610839cf"
            # }

            gitinfo, _status = self.send_command_and_read(cmd)
            gitinfo = json.loads(gitinfo)
            return gitinfo.get("git_tag")
        except Exception as e:
            logger.warning(f"Unable to find YARR version! Require YARR >= v1.5.2 {e}")
            try:
                defines = {}
                with Path.open(
                    self.run_dir / "src/libYarr/include/yarr_version.h",
                    encoding="utf-8",
                ) as header_file:
                    for line in header_file.readlines():
                        if line.startswith("#define"):
                            line.rstrip()
                            m = re.search(r"#define\s+([A-Za-z]\w+)\s+(.*)", line)
                            if m:
                                defines[m.group(1)] = m.group(2).strip('"')
                logger.debug(defines)
                logger.debug(self.version)
                return defines["YARR_GIT_TAG"]
            except Exception as ex:
                logger.warning(f"Unable to find YARR version: {ex}")
                return ""

    # Reads controller file, returns spec number
    def get_spec(self):
        controller_path = self.run_dir / self.controller
        with controller_path.open(encoding="utf-8") as file:
            controller_params = json.load(file)
        try:
            return controller_params.get("ctrlCfg").get("cfg").get("specNum")
        except Exception:
            logger.warning(
                "Unable to read specNum from controller file. Assuming spec #0"
            )
            return 0

    def run_scan(self, scan, output=None, skip_reset=False, tags: list | None = None):
        tags = tags or []
        # this escaping needed due to https://gitlab.cern.ch/YARR/YARR/-/issues/338
        tag_str = (f"-W '{json.dumps(tags)}'" if tags else "").replace('"', '\\"')
        output = f"-o {output}" if output else ""
        cmd = f'{self.scanConsole_exe} -r {self.controller} -c {self.connectivity} -s {scan} {tag_str} {output} {"--skip-reset" if skip_reset else ""} {self.exe_postOpts}'

        self._register = [{} for chip in range(self._number_of_chips)]

        logger.info(f"Running YARR scan: {scan} ...")
        # Always save scan output in log file
        currLevel = logger.getEffectiveLevel()
        logger.setLevel("DEBUG")
        n_try = 0
        while n_try < self.max_attempts:
            try:
                logger.debug(f"Sending command (attempt {n_try}): ")
                logger.debug(cmd)
                self.send_command(cmd, purpose="configure module", success_code=0)
                logger.setLevel(currLevel)
                break
            except RuntimeError as err:
                n_try += 1
                if n_try < self.max_attempts:
                    logger.warning(
                        "Failed to run scan. Running eye diagram scan and retrying."
                    )
                    time.sleep(self.sleep_attempts)
                    self.eyeDiagram()
                    continue
                msg = f"Unable to run scan after {self.max_attempts} attempts. Stopping measurement."
                raise RuntimeError(msg) from err

        return 0

    def write_register(self, name, value, chip_position=None, reset_other_chips=True):
        if (
            chip_position is not None
            and chip_position not in self._enabled_chip_positions
        ):
            return 0
        ## if shared_vmux then skip writing registers which should already have the target value to save time
        ## https://gitlab.cern.ch/atlas-itk/pixel/module/module-qc-tools/-/merge_requests/208
        ## https://gitlab.cern.ch/atlas-itk/pixel/module/module-qc-tools/-/issues/158
        ## reset_other_chips is equivalent to shared_vmux and only necessary in this case
        if (
            reset_other_chips
            and chip_position is not None
            and self._register[chip_position].get(name) == value
        ):
            return 0

        cmd = f'{self.write_register_exe} -r {self.controller} -c {self.connectivity} {"-i "+str(chip_position) if chip_position is not None else ""} {name} {value} {self.exe_postOpts}'

        n_try = 0
        while n_try < self.max_attempts:
            try:
                logger.debug(f"Writing register {name} to {value} (attempt {n_try}): ")
                logger.debug(cmd)
                self.send_command(
                    cmd,
                    purpose=f"write register {name}: {value}",
                    success_code=self.success_code,
                )
                break
            except RuntimeError as err:
                n_try += 1
                if n_try < self.max_attempts:
                    logger.warning(
                        "Failed to write register. Running eye diagram scan and retrying."
                    )
                    time.sleep(self.sleep_attempts)
                    self.eyeDiagram(skipconfig=True)
                    continue
                msg = f"Unable to write register after {self.max_attempts} attempts. Stopping measurement."
                raise RuntimeError(msg) from err

        if chip_position is not None:
            self._register[chip_position][name] = value
        else:
            for chip in range(self._number_of_chips):
                self._register[chip][name] = value

        return 0

    def read_register(self, name, chip_position=None):
        if (
            chip_position is not None
            and chip_position not in self._enabled_chip_positions
        ):
            return 0
        cmd = f'{self.read_register_exe} -r {self.controller} -c {self.connectivity} {"-i "+str(chip_position) if chip_position is not None else ""} {name} {self.exe_postOpts}'
        n_try = 0
        while n_try < self.max_attempts:
            try:
                logger.debug(f"Sending command (attempt {n_try}): ")
                logger.debug(cmd)
                result, status = self.send_command_and_read(
                    cmd, purpose="read register", success_code=self.success_code
                )
                break
            except RuntimeError as err:
                n_try += 1
                if n_try < self.max_attempts:
                    logger.warning(
                        "Failed to read register. Running eye diagram scan and retrying."
                    )
                    time.sleep(self.sleep_attempts)
                    self.eyeDiagram(skipconfig=True)
                    continue
                msg = f"Unable to read register after {self.max_attempts} attempts. Stopping measurement."
                raise RuntimeError(msg) from err

        try:
            result = result.split()
        except Exception:
            logger.debug(
                f"read_register returned a single value ({result}), this happens if only single chip is enabled."
            )
            result = [result]
        return result, status

    def dataMergingCheck(self, testsize=None, mode=None, verbose=False, quiet=False):
        if not self.dataMergingCheck_exe:
            msg = "No `dataMergingCheck_exe` found in hardware config file! Check and compare to https://gitlab.cern.ch/atlas-itk/pixel/module/module-qc-tools/-/blob/v2.5.0/src/module_qc_tools/data/configs/hw_config_example_merged_vmux_itkpixv2.json!"
            raise RuntimeError(msg)

        _mode = "4-to-1"
        _testsize = ""
        _verbose = ""
        _quiet = ""

        valid_modes = ["4-to-1", "2-to-1"]
        self._register = [{} for chip in range(self._number_of_chips)]
        if testsize is not None:
            _testsize = f"-t {testsize!s}"
        if mode in valid_modes:
            _mode = f"-m {mode}"
        else:
            logger.error(f"Invalid mode: {mode}! Valid modes are {valid_modes}")
        if verbose:
            _verbose = "-v"
        if quiet:
            _quiet = "-q"

        cmd = f"{self.dataMergingCheck_exe} -r {self.controller} -c {self.connectivity} {_testsize} {_mode} {_verbose} {_quiet} {self.exe_postOpts}"

        ### passed and failed return the same success code
        n_try = 0

        while n_try < self.max_attempts:
            try:
                logger.debug(f"Sending command (attempt {n_try}): ")
                logger.debug(cmd)
                result = self.send_command_and_read(
                    cmd,
                    dtype=str,
                    purpose="data merging check",
                    success_code=self.success_code,
                )
                break
            except RuntimeError as err:
                n_try += 1
                if n_try < self.max_attempts:
                    logger.warning("Failed to run data merging check. Retrying.")
                    time.sleep(self.sleep_attempts)
                    continue
                msg = f"Unable to run data merging check after {self.max_attempts} attempts. Stopping measurement."
                raise RuntimeError(msg) from err
        return result

    def eyeDiagram(self, dryrun=False, skipconfig=False, testsize=None):
        if not self.eyeDiagram_exe:
            msg = "No `eyeDiagram_exe` found in hardware config file! Check and compare to https://gitlab.cern.ch/atlas-itk/pixel/module/module-qc-tools/-/blob/v2.5.0/src/module_qc_tools/data/configs/hw_config_example_merged_vmux_itkpixv2.json!"
            raise RuntimeError(msg)
        _dryrun = ""
        _skipconfig = ""
        _testsize = ""
        if dryrun:
            _dryrun = "-n"
        if skipconfig:
            _skipconfig = "-s"
        else:
            self._register = [{} for chip in range(self._number_of_chips)]
        if testsize is not None:
            _testsize = f"-t {testsize!s}"

        cmd = f"{self.eyeDiagram_exe} -r {self.controller} -c {self.connectivity} {_dryrun} {_skipconfig} {_testsize} {self.exe_postOpts}"
        n_try = 0
        while n_try < self.max_attempts:
            try:
                logger.debug(f"Sending command (attempt {n_try}): ")
                logger.debug(cmd)
                result = self.send_command_and_read(
                    cmd,
                    dtype=str,
                    purpose="eye diagram",
                    success_code=self.success_code,
                )
                break
            except RuntimeError as err:
                n_try += 1
                if n_try < self.max_attempts:
                    logger.warning("Failed to run eye diagram. Retrying.")
                    time.sleep(self.sleep_attempts)
                    continue
                msg = f"Unable to run eye diagram after {self.max_attempts} attempts. Stopping measurement."
                raise RuntimeError(msg) from err
        return result

    def read_adc(
        self,
        vmux,
        chip_position=None,
        readCurrent=False,
        rawCounts=False,
        share_vmux=True,
    ):
        if (
            chip_position is not None
            and chip_position not in self._enabled_chip_positions
        ):
            return 0
        cmd = f'{self.read_adc_exe} -r {self.controller} -c {self.connectivity} {"-i "+str(chip_position) if chip_position is not None else ""} {"-I " if readCurrent else ""} {"-R " if rawCounts else ""} {"-s 63" if share_vmux else ""} {vmux} {self.exe_postOpts}'
        n_try = 0
        while n_try < self.max_attempts:
            try:
                logger.debug(f"Sending command (attempt {n_try}): ")
                logger.debug(cmd)
                result = self.send_command_and_read(
                    cmd, dtype=str, purpose="read adc", success_code=self.success_code
                )
                break
            except RuntimeError as err:
                n_try += 1
                if n_try < self.max_attempts:
                    logger.warning(
                        "Failed to read ADC. Running eye diagram scan and retrying."
                    )
                    time.sleep(self.sleep_attempts)
                    self.eyeDiagram(skipconfig=True)
                    continue
                msg = f"Unable to read ADC after {self.max_attempts} attempts. Stopping measurement."
                raise RuntimeError(msg) from err
        return result

    def read_ringosc(self, chip_position=None):
        if (
            chip_position is not None
            and chip_position not in self._enabled_chip_positions
        ):
            return 0
        cmd = f'{self.read_ringosc_exe} -r {self.controller} -c {self.connectivity} {"-i "+str(chip_position) if chip_position is not None else ""} {self.exe_postOpts}'
        n_try = 0
        while n_try < self.max_attempts:
            try:
                logger.debug(f"Sending command (attempt {n_try}): ")
                logger.debug(cmd)
                mea, status = self.send_command_and_read(
                    cmd, dtype=str, purpose="read ringsoc"
                )
                break
            except RuntimeError as err:
                n_try += 1
                if n_try < self.max_attempts:
                    logger.warning(
                        "Failed to read ring oscillator. Running eye diagram scan and retrying."
                    )
                    time.sleep(self.sleep_attempts)
                    self.eyeDiagram(skipconfig=True)
                    continue
                msg = f"Unable to read ring oscillator after {self.max_attempts} attempts. Stopping measurement."
                raise RuntimeError(msg) from err
        mea = mea.splitlines()
        return mea, status

    def set_mux(self, chip_position=None, v_mux=-1, i_mux=-1, reset_other_chips=True):
        for chip in range(self._number_of_chips):
            if reset_other_chips:
                self.write_register(
                    name="MonitorV",
                    value=63,
                    chip_position=chip,
                    reset_other_chips=reset_other_chips,
                )
                self.write_register(
                    name="MonitorI",
                    value=63,
                    chip_position=chip,
                    reset_other_chips=reset_other_chips,
                )
        for chip in range(self._number_of_chips):
            if chip == chip_position:
                # Set Vmux=1 to measure the I_mux pad voltage when a non-negative I_mux value is passed.
                if i_mux >= 0:
                    v_mux = 1
                # TODO: Consider this in read-adc script too
                # Set Imux=63 when measuring NTC pad voltage through Vmux2.
                if v_mux == 2:
                    self.write_register(
                        name="MonitorI",
                        value=63,
                        chip_position=chip,
                        reset_other_chips=reset_other_chips,
                    )
                    self.write_register(
                        name="MonitorV",
                        value=v_mux,
                        chip_position=chip,
                        reset_other_chips=reset_other_chips,
                    )
                self.write_register(
                    name="MonitorV",
                    value=v_mux,
                    chip_position=chip,
                    reset_other_chips=reset_other_chips,
                )
                if i_mux >= 0:
                    self.write_register(
                        name="MonitorI",
                        value=i_mux,
                        chip_position=chip,
                        reset_other_chips=reset_other_chips,
                    )
        return 0

    def reset_tempsens_enable(self, chip_position=None):
        self.write_register(
            name="MonSensSldoAnaEn", value=0, chip_position=chip_position
        )
        self.write_register(
            name="MonSensSldoDigEn", value=0, chip_position=chip_position
        )
        self.write_register(name="MonSensAcbEn", value=0, chip_position=chip_position)

        return 0

    def reset_tempsens_bias(self, chip_position=None):
        self.write_register(
            name="MonSensSldoAnaSelBias", value=0, chip_position=chip_position
        )

        self.write_register(
            name="MonSensSldoDigSelBias", value=0, chip_position=chip_position
        )

        self.write_register(
            name="MonSensAcbSelBias", value=0, chip_position=chip_position
        )

        return 0

    def reset_tempsens_dem(self, chip_position=None):
        self.write_register(
            name="MonSensSldoAnaDem", value=0, chip_position=chip_position
        )

        self.write_register(
            name="MonSensSldoDigDem", value=0, chip_position=chip_position
        )

        self.write_register(name="MonSensAcbDem", value=0, chip_position=chip_position)

        return 0

    def reset_tempsens(self, chip_position=None):
        self.reset_tempsens_enable(chip_position=chip_position)
        self.reset_tempsens_bias(chip_position=chip_position)
        self.reset_tempsens_dem(chip_position=chip_position)

        return 0

    def enable_tempsens(self, chip_position=None, v_mux=-1, reset_other_chips=True):
        # First reset all MOS sensors.
        self.reset_tempsens_enable(chip_position=chip_position)

        if v_mux == 14:
            self.write_register(
                name="MonSensSldoAnaEn", value=1, chip_position=chip_position
            )
        elif v_mux == 16:
            self.write_register(
                name="MonSensSldoDigEn", value=1, chip_position=chip_position
            )
        elif v_mux == 18:
            self.write_register(
                name="MonSensAcbEn", value=1, chip_position=chip_position
            )
        else:
            msg = "Incorrect VMUX value for measuring temperature!"
            raise RuntimeError(msg)

        if reset_other_chips and chip_position is not None:
            for chip in range(self._number_of_chips):
                if chip == chip_position:
                    continue
                self.reset_tempsens_enable(chip_position=chip)

        return 0

    def set_tempsens_bias(
        self, chip_position=None, v_mux=-1, bias=0, reset_other_chips=True
    ):
        if v_mux == 14:
            self.write_register(
                name="MonSensSldoAnaSelBias", value=bias, chip_position=chip_position
            )
        elif v_mux == 16:
            self.write_register(
                name="MonSensSldoDigSelBias", value=bias, chip_position=chip_position
            )
        elif v_mux == 18:
            self.write_register(
                name="MonSensAcbSelBias", value=bias, chip_position=chip_position
            )
        else:
            msg = "Incorrect VMUX value for measuring temperature!"
            raise RuntimeError(msg)

        if reset_other_chips and chip_position is not None:
            for chip in range(self._number_of_chips):
                if chip == chip_position:
                    continue
                self.reset_tempsens(chip_position=chip)

        return 0

    # TODO Does it even make sense to have reset option here? That only matters when setting MonitorV
    def set_tempsens_dem(
        self, chip_position=None, v_mux=-1, dem=0, reset_other_chips=True
    ):
        if v_mux == 14:
            self.write_register(
                name="MonSensSldoAnaDem", value=dem, chip_position=chip_position
            )
        elif v_mux == 16:
            self.write_register(
                name="MonSensSldoDigDem", value=dem, chip_position=chip_position
            )
        elif v_mux == 18:
            self.write_register(
                name="MonSensAcbDem", value=dem, chip_position=chip_position
            )
        else:
            msg = "Incorrect VMUX value for measuring temperature!"
            raise RuntimeError(msg)
        if reset_other_chips and chip_position is not None:
            for chip in range(self._number_of_chips):
                if chip == chip_position:
                    continue
                self.reset_tempsens(chip_position=chip)

        return 0

    def set_trim(self, chip_position=None, v_mux=-1, trim=0):
        if v_mux == 34:
            self.write_register(
                name="SldoTrimA", value=trim, chip_position=chip_position
            )
        elif v_mux == 38:
            self.write_register(
                name="SldoTrimD", value=trim, chip_position=chip_position
            )
        else:
            msg = "Incorrect VMUX value for setting trim!"
            raise RuntimeError(msg)

        return 0

    def switchLPM(self, position):
        connect_spec = self.get_connectivity()

        # retrieve all the tx values listed in the connectivity file
        tx_list = list({chip["tx"] for chip in connect_spec["chips"]})

        # go through the list and build the correct mask to act on all of them
        enable_mask = 0
        for tx in tx_list:
            enable_mask |= 1 << tx

        cmd = f"{self.switchLPM_exe} {position} -m -e {enable_mask} -s {self.get_spec()} {self.exe_postOpts}"
        return self.send_command(cmd, purpose="switch LP mode on/off")

    def get_connectivity(self):
        with Path(self.connectivity).open(encoding="utf-8") as file:
            return json.load(file)

    def get_config(self, chip_position):
        connect_spec = self.get_connectivity()
        config_path = connect_spec["chips"][chip_position]["config"]
        path = Path(self.connectivity).parent / config_path

        with Path(path).open(encoding="utf-8") as file:
            spec = json.load(file)

        with contextlib.suppress(KeyError):
            chipname = ""
            try:
                chipname = next(iter(spec))
            except IndexError:
                logger.warning("Empty Chip Config")
            spec[chipname].pop("PixelConfig")

        return spec

    def omit_pixel_config(self):
        self.tmp_dir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        logger.info(
            f"Creating temporary connectivity file and chip configs without pixel config in {self.tmp_dir.name}"
        )

        # Create new connectivity file pointing to new chip config files
        new_conn = (
            str(Path(self.connectivity).with_suffix("").stem) + "_noPixConfig.json"
        )
        with Path(self.connectivity).open(encoding="utf-8") as file:
            orig_config = json.load(file)
        new_config = orig_config
        for i, c in enumerate(orig_config["chips"]):
            new_path = str(Path(c["config"]).with_suffix("").stem) + "_noPixConfig.json"
            new_config["chips"][i]["config"] = new_path
            new_config["chips"][i][
                "path"
            ] = "relToCon"  # always will be relative now that files are copied over

            # Save temporary chip config (without Pixel Config)
            new_chip_config = Path(self.tmp_dir.name) / new_path
            new_chip_config.touch(exist_ok=False)
            with new_chip_config.open(mode="w", encoding="utf-8") as file:
                json.dump(self.get_config(i), file, indent=4)

        new_conn_file = Path(self.tmp_dir.name) / new_conn
        new_conn_file.touch(exist_ok=False)
        with new_conn_file.open(mode="w", encoding="utf-8") as fp:
            json.dump(new_config, fp, indent=4)

        # Use temporary connectivity file
        self.connectivity = Path(self.tmp_dir.name) / new_conn
        return 0

    def remove_tmp_connectivity(self):
        logger.info(f"Deleting temporary files: {Path(self.connectivity).parent}")
        if not self.tmp_dir:
            logger.warning(
                "[bright_yellow]Requesting to delete temporary config files - but temporary config files are not being used! Will not delete any files.[/]"
            )
            return 0
        self.tmp_dir.cleanup()
        self.tmp_dir = ""
        return 0

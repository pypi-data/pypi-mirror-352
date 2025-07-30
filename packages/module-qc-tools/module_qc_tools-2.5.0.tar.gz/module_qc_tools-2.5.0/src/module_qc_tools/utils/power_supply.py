#!/usr/bin/env python3
from __future__ import annotations

import logging
import time

import numpy as np

from module_qc_tools.utils.hardware_control_base import hardware_control_base

logger = logging.getLogger("measurement")


class power_supply(hardware_control_base):
    def __init__(self, config, *args, name="power_supply", is_hv=False, **kwargs):
        self.on_cmd = ""
        self.off_cmd = ""
        self.set_cmd = ""
        self.ramp_cmd = ""
        self.getV_cmd = ""
        self.getI_cmd = ""
        self.measV_cmd = ""
        self.measI_cmd = ""
        self.polarity = 1
        self.checkTarget_timeout = 30  # wait for the target to be reached max 30sec.
        self.is_hv = is_hv  # if True (False), checkTarget will be on voltage (current)
        self.n_try = 0
        self.success_code = 0
        super().__init__(config, *args, name=name, **kwargs)
        if "emulator" in self.on_cmd:
            logger.info(f"[{name}] running power supply emulator!!")

    def on(self, v=None, i=None, check=True):
        cmd = f'{self.on_cmd.replace("{v}", str(v)).replace("{i}", str(i))}'
        return_code = self.send_command(
            cmd,
            purpose=f"turn on power supply with {v}V, {i}A",
            pause=0 if check else 1,
            success_code=self.success_code,
        )
        if check:  # wait until target is reached
            self.checkTarget(v, i)

        return return_code

    def set(self, v=None, i=None, check=True):
        cmd = f'{self.set_cmd.replace("{v}", str(v)).replace("{i}", str(i))}'
        return_code = self.send_command(
            cmd,
            purpose=f"set power supply to {v}V, {i}A",
            pause=0 if check else 1,
            success_code=self.success_code,
        )
        if check:  # wait until target is reached
            self.checkTarget(v, i)

        return return_code

    def off(self):
        return self.send_command(
            self.off_cmd,
            purpose="turn off power supply",
            extra_error_messages=[
                f"Run directory: `{self.run_dir}`"
                f"Off command: `{self.off_cmd}`"
                "Please manually turn off power supply!!"
            ],
            success_code=self.success_code,
        )

    def getV(self):
        return self.send_command_and_read(
            self.getV_cmd,
            purpose="inquire set voltage",
            unit="V",
            max_nTry=self.n_try,
            success_code=self.success_code,
        )

    def getI(self):
        return self.send_command_and_read(
            self.getI_cmd,
            purpose="inquire set current",
            unit="A",
            max_nTry=self.n_try,
            success_code=self.success_code,
        )

    def measV(self):
        return self.send_command_and_read(
            self.measV_cmd,
            purpose="measure output voltage",
            unit="V",
            max_nTry=self.n_try,
            success_code=self.success_code,
        )

    def measI(self):
        return self.send_command_and_read(
            self.measI_cmd,
            purpose="measure output current",
            unit="A",
            max_nTry=self.n_try,
            success_code=self.success_code,
        )

    def getPolarity(self):
        if "int" in str(type(self.polarity)) or "float" in str(type(self.polarity)):
            return self.polarity

        return self.send_command_and_read(
            self.polarity,
            dtype=int,
            purpose="get polarity (-1 or 1)",
            success_code=self.success_code,
        )[0]

    def rampV(self, v=None, i=None, stepsize=5):
        if self.ramp_cmd:
            cmd = (
                f'{self.ramp_cmd.replace("{v}", str(v)).replace("{r}", str(stepsize))}'
            )
            return self.send_command(
                cmd,
                purpose=f"ramp power supply to {v}V at {stepsize}V/s",
                pause=1,
                success_code=self.success_code,
            )
        v_init, _v_status = self.getV()
        # protection if measV != getV for HV (e.g. if HV interlock was triggered)
        if self.is_hv:
            v_meas, _v_meas_status = self.measV()
            if abs(v_meas - v_init) > 0.05:
                logger.warning(
                    f"[{self._name}] measured voltage != target ({v_meas} vs {v_init} V), resetting target to measured value before ramping."
                )
                self.set(v_meas, i)
                v_init, _v_status = self.getV()
        v_final = v
        v_diff = v_final - v_init  ## gives the correct sign for the ramping direction
        logger.debug("v_diff " + str(v_diff))
        stepsize = np.sign(v_diff) * stepsize
        logger.debug("stepsize " + str(stepsize))
        if stepsize != 0:
            nsteps = int(v_diff / stepsize)
            logger.debug("nsteps " + str(nsteps))
            v_target = v_init
            for _step in range(nsteps):
                v_target = v_target + stepsize
                logger.debug("step " + str(_step) + " target " + str(v_target))
                self.set(v_target, i)  ## check target is reached for each step
        self.set(v_final, i)  # last step, check target as well
        return self.getV()

    def checkTarget(self, v=None, i=None):
        target = v if self.is_hv else i  # v (i) for HV (LV)
        if target is None:
            return True
        threshold = 0.1 if self.is_hv else 0.005  # 100mV/5mA, hard-coded
        start = time.time()
        while True:
            measurement, _status = self.measV() if self.is_hv else self.measI()
            if abs(measurement - target) < threshold:
                return True
            if time.time() - start > self.checkTarget_timeout:
                msg = f"[{self._name}] target ({target}) not reached ({measurement}) after timeout ({self.checkTarget_timeout}sec.). Exiting."
                raise RuntimeError(msg)
            time.sleep(2)

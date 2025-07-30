#!/usr/bin/env python3
from __future__ import annotations

import logging

from module_qc_tools.utils.hardware_control_base import hardware_control_base

logger = logging.getLogger("measurement")


class ntc(hardware_control_base):
    def __init__(self, config, *args, name="ntc", **kwargs):
        self.cmd = ""
        self.n_try = 0
        self.success_code = 0
        super().__init__(config, *args, name=name, **kwargs)
        if "emulator" in self.cmd:
            logger.info(f"[{name}] running NTC emulator!!")

    def read(self):
        return self.send_command_and_read(
            self.cmd,
            purpose="read temperature",
            unit="C",
            max_nTry=self.n_try,
            success_code=self.success_code,
        )

#!/usr/bin/env python3
from __future__ import annotations

import logging

from module_qc_tools.utils.hardware_control_base import hardware_control_base

logger = logging.getLogger("measurement")


class multimeter(hardware_control_base):
    def __init__(self, config, *args, name="multimeter", **kwargs):
        self.dcv_cmd = []
        self.n_try = 0
        self.success_code = 0
        super().__init__(config, *args, name, **kwargs)
        if any("emulator" in dcv_cmd for dcv_cmd in self.dcv_cmd):
            logger.info(f"[{name}] running multimeter emulator!!")

    def measure_dcv(self, channel=0):
        return self.send_command_and_read(
            self.dcv_cmd[channel],
            purpose=f"read voltage channel {channel}",
            unit="V",
            max_nTry=self.n_try,
            success_code=self.success_code,
        )

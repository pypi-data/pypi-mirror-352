#!/usr/bin/env python3
from __future__ import annotations

import logging
import subprocess
import time
from pathlib import Path

logger = logging.getLogger("measurement")


class hardware_control_base:
    def __init__(self, config, name="hardware_control_base"):
        self._name = name
        self.run_dir = None
        member_variables = [
            attr
            for attr in dir(self)
            if not callable(getattr(self, attr)) and not attr.startswith("_")
        ]
        for member in config:
            if member in member_variables:
                setattr(self, member, config[member])

        if self.run_dir == "emulator":
            self.run_dir = Path.cwd()
            from module_qc_tools.utils import (  # pylint: disable=import-outside-toplevel
                subprocess_emulator,
            )

            self.run = subprocess_emulator.run
        else:
            self.run_dir = Path(self.run_dir)
            self.run = subprocess.run

    def send_command(
        self,
        cmd,
        purpose="send command",
        extra_error_messages=None,
        pause=0,
        success_code=0,
    ):
        extra_error_messages = extra_error_messages or []

        logger.debug("Sending command: ")
        logger.debug(cmd)
        result = self.run(
            cmd, shell=True, capture_output=True, check=False, cwd=self.run_dir
        )
        if result.stdout:
            logger.debug(result.stdout.decode("utf-8"))

        if result.stderr:
            logger.error(result.stderr.decode("utf-8"))

        if result.returncode != success_code:
            for extra_error_message in extra_error_messages:
                logger.info(f"[{self._name}] {extra_error_message}")
            msg = f"[{self._name}] fail to {purpose}!!"
            raise RuntimeError(msg)
        logger.debug(f"[{self._name}] {purpose}")

        time.sleep(pause)

        return result.returncode

    def send_command_and_read(
        self,
        cmd,
        dtype=float,
        purpose="send command and read",
        unit="",
        extra_error_messages=None,
        max_nTry=0,
        success_code=0,
    ):
        extra_error_messages = extra_error_messages or []
        logger.debug("Sending command: ")
        logger.debug(cmd)
        result = self.run(
            cmd, shell=True, capture_output=True, check=False, cwd=self.run_dir
        )

        logger.debug(result.stdout.decode())

        # A while loop to retry communications in case of timeout error.
        # The maximum number of tries is determined by the function argument max_nTry.
        nTry = 0
        while result.returncode != success_code and nTry < max_nTry:
            nTry += 1
            for extra_error_message in extra_error_messages:
                logger.info(f"[{self._name}] {extra_error_message}")
            logger.info(f"Try again. Send command and read attempt {nTry} time(s).")
            logger.debug("Sending command: ")
            logger.debug(cmd)
            result = self.run(
                cmd, shell=True, capture_output=True, check=False, cwd=self.run_dir
            )
            logger.debug(result.stdout.decode())

        if result.returncode != success_code:
            msg = f"[{self._name}] fail to {purpose}!! Exit with returncode {result.returncode}.\nstdout:\n {result.stdout.decode()}\nstderr: {result.stderr.decode()}"
            raise RuntimeError(msg)
        try:
            value = dtype(result.stdout.decode())
        except Exception:
            logger.debug(
                "Failed to return type of decoded send command, will return un-typed result (this happens for read-register)"
            )
            value = result.stdout.decode()
        for _extra_error_message in extra_error_messages:
            logger.info(f"[{self._name}] {purpose}: {value}{unit}")

        return value, result.returncode

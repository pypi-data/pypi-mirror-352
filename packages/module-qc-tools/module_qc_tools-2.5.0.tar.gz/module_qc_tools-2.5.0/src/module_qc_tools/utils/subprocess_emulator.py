from __future__ import annotations

import os
import shlex
from pathlib import Path
from subprocess import CompletedProcess

import typer
from typer.testing import CliRunner

from module_qc_tools.cli import app as app_mqt  # pylint: disable=cyclic-import

app = typer.Typer()
app.add_typer(app_mqt, name="mqt")
runner = CliRunner(mix_stderr=False)


def run(args, *, capture_output=False, shell=False, cwd=None, check=False):
    """
    emulator.run mimics the behavior of subprocess.run but bypasses to use the emulator via click/typer CliRunner.

    This will return a subprocess.CompletedProcess object.

    The following keyword arguments are not implemented/supported:
        - stdin
        - input
        - stdout
        - stderr
        - timeout
        - encoding
        - errors
        - text
        - env
        - universal_newlines
        - any other Popen keyword arguments

    """
    if capture_output is not True:
        msg = "emulator.run not implemented for capture_output != True"
        raise ValueError(msg)
    if shell is not True:
        msg = "emulator.run not implemented for shell != True"
        raise ValueError(msg)
    if check is not False:
        msg = "emulator.run not implemented for check != False"
        raise ValueError(msg)

    orig_cwd = Path.cwd()
    if cwd is not None:
        cwd = os.fsdecode(cwd)
        os.chdir(cwd)

    result = runner.invoke(
        app, args=shlex.split(args), catch_exceptions=False, prog_name=""
    )

    if cwd is not None:
        os.chdir(orig_cwd)

    stderr = result.stderr_bytes if capture_output else None
    return CompletedProcess(args, result.exit_code, result.stdout_bytes, stderr)

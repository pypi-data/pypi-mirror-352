#!/usr/bin/env python3
from __future__ import annotations

from importlib import resources

datapath = resources.files("module_qc_tools") / "data"

__all__ = ("datapath",)

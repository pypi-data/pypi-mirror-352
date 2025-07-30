"""
Typing helpers.
"""

from __future__ import annotations

import sys
from typing import Annotated

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

__all__ = (
    "Annotated",
    "TypeAlias",
)

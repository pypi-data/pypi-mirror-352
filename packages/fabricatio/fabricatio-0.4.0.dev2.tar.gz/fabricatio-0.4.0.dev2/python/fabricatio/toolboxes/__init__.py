"""Contains the built-in toolboxes for the Fabricatio package."""

from typing import Set

from fabricatio.toolboxes.arithmetic import arithmetic_toolbox
from fabricatio.toolboxes.fs import fs_toolbox
from fabricatio_core.models.tool import ToolBox

basic_toolboxes: Set[ToolBox] = {arithmetic_toolbox}

__all__ = [
    "arithmetic_toolbox",
    "basic_toolboxes",
    "fs_toolbox",
]

"""Magique AI toolsets package."""

__version__ = "0.2.8"

from .utils.remote import connect_remote
from .toolset import ToolSet, tool, run_toolsets

__all__ = ["connect_remote", "ToolSet", "tool", "run_toolsets"]

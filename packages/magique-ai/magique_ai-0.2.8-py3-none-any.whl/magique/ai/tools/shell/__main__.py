from .shell import ShellToolSet
from ...utils.remote import toolset_cli


toolset_cli(ShellToolSet, "shell")

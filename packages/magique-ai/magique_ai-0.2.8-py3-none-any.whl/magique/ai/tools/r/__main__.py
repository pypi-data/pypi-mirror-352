from .r_interpreter import RInterpreterToolSet
from ...utils.remote import toolset_cli


toolset_cli(RInterpreterToolSet, "r-interpreter")

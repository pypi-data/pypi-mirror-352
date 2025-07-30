from .python_interpreter import PythonInterpreterToolSet
from ...utils.remote import toolset_cli


toolset_cli(PythonInterpreterToolSet, "python-interpreter")

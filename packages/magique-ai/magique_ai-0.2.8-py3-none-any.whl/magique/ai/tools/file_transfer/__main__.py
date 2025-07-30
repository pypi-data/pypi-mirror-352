from .worker import FileTransferToolSet
from ...utils.remote import toolset_cli


toolset_cli(FileTransferToolSet, "file-transfer")

from .rag import VectorRAGToolSet
from ...utils.remote import toolset_cli


toolset_cli(VectorRAGToolSet, "vector-rag")

from ...toolset import ToolSet, tool
from ...utils.log import logger
from ...rag.vectordb import VectorDB


class VectorRAGToolSet(ToolSet):
    def __init__(
            self,
            name: str,
            db_path: str,
            worker_params: dict | None = None,
            allow_insert: bool = False,
            allow_delete: bool = False,
            db_params: dict | None = None,
            **kwargs,
            ):
        super().__init__(name, worker_params, **kwargs)
        self.db = VectorDB(db_path, **(db_params or {}))
        if allow_insert:
            self.insert_vector_db = tool(self.insert_vector_db)
        if allow_delete:
            self.delete_vector_db = tool(self.delete_vector_db)
        self.inject_description()

    def inject_description(self):
        _doc = (
            f"\n\nDatabase description: {self.db.metadata['description']}"
            f"\n\nDatabase items: {','.join(self.db.metadata['items'])}"
        )
        self.query_vector_db.__func__.__doc__ += _doc
        self.insert_vector_db.__func__.__doc__ += _doc
        self.delete_vector_db.__func__.__doc__ += _doc

    @tool
    async def query_vector_db(self, query: str, top_k: int = 3) -> list:
        """Query the vector database."""
        return await self.db.query(query, top_k)

    async def insert_vector_db(self, text: str, metadata: dict | None = None):
        """Insert a text into the vector database."""
        await self.db.insert(text, metadata)

    async def delete_vector_db(self, id: str | list[str]):
        """Delete a text from the vector database."""
        await self.db.delete(id)

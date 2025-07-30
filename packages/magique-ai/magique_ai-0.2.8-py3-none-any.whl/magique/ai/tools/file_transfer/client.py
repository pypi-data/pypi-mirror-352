from magique.client import MagiqueError

from ...utils.remote import connect_remote
from ...constant import DEFAULT_SERVER_URL


class FileTransferClient:
    def __init__(
            self,
            service_id_or_name: str,
            server_url: str = DEFAULT_SERVER_URL,
            connect_params: dict | None = None,
            ):
        self._service = None
        self.service_id_or_name = service_id_or_name
        self.server_url = server_url
        self.connect_params = connect_params

    async def connect(self):
        if self._service is None:
            params = self.connect_params or {}
            self._service = await connect_remote(
                self.service_id_or_name,
                self.server_url,
                **params,
            )
        return self._service

    async def list_files(self, sub_dir: str | None = None) -> list[dict]:
        service = await self.connect()
        resp = await service.invoke("list_files", {"sub_dir": sub_dir})
        if resp.get("error"):
            raise MagiqueError(resp["error"])
        return resp

    async def create_directory(self, sub_dir: str):
        service = await self.connect()
        resp = await service.invoke("create_directory", {"sub_dir": sub_dir})
        if resp.get("error"):
            raise MagiqueError(resp["error"])
        return resp

    async def delete_directory(self, sub_dir: str):
        service = await self.connect()
        resp = await service.invoke("delete_directory", {"sub_dir": sub_dir})
        if resp.get("error"):
            raise MagiqueError(resp["error"])
        return resp

    async def delete_file(self, file_path: str):
        service = await self.connect()
        resp = await service.invoke("delete_file", {"file_path": file_path})
        if resp.get("error"):
            raise MagiqueError(resp["error"])
        return resp

    async def send_file(self, file: str, target_file_path: str, chunk_size: int = 1024):
        service = await self.connect()
        resp = await service.invoke("open_file_for_write", {"file_path": target_file_path})
        if resp.get("error"):
            raise MagiqueError(resp["error"])
        handle_id = resp["handle_id"]
        with open(file, "rb") as f:
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                resp = await service.invoke("write_chunk", {"handle_id": handle_id, "data": data})
                if resp.get("error"):
                    await service.invoke("close_file", {"handle_id": handle_id})
                    raise MagiqueError(resp["error"])
        resp = await service.invoke("close_file", {"handle_id": handle_id})
        if resp.get("error"):
            raise MagiqueError(resp["error"])
        return resp

    async def fetch_file(self, local_file_path: str, file_path: str, chunk_size: int = 1024):
        service = await self.connect()
        with open(local_file_path, "wb") as f:

            async def receive_chunk(data: bytes):
                f.write(data)

            resp = await service.invoke(
                "read_file",
                {
                    "file_path": file_path,
                    "receive_chunk": receive_chunk,
                    "chunk_size": chunk_size,
                },
            )
            if resp.get("error"):
                raise MagiqueError(resp["error"])
        return resp

import os
import sys
from pathlib import Path
import base64

from executor.engine import Engine, LocalJob, ProcessJob
from executor.engine.job.extend import SubprocessJob

from ..toolset import tool
from ..constant import DEFAULT_SERVER_URL
from ..utils.remote import connect_remote
from ..tools.file_transfer import FileTransferToolSet
from ..utils.log import logger


class Endpoint(FileTransferToolSet):
    def __init__(
        self,
        name: str = "pantheon-chatroom-endpoint",
        workspace_path: str = "./.pantheon-chatroom-workspace",
        worker_params: dict | None = None,
        config: dict | None = None,
    ):
        Path(workspace_path).mkdir(parents=True, exist_ok=True)
        super().__init__(name, workspace_path, worker_params)
        self.services: list[dict] = []
        self.config = config or {}

    @tool
    async def list_services(self) -> list[dict]:
        res = []
        for s in self.services:
            res.append({
                "name": s["name"],
                "id": s["id"],
            })
        return res

    @tool
    async def fetch_image_base64(self, image_path: str) -> dict:
        """Fetch an image and return the base64 encoded image."""
        if '..' in image_path:
            return {"success": False, "error": "Image path cannot contain '..'"}
        i_path = self.path / image_path
        if not i_path.exists():
            return {"success": False, "error": "Image does not exist"}
        format = i_path.suffix.lower()
        if format not in [".jpg", ".jpeg", ".png", ".gif"]:
            return {"success": False, "error": "Image format must be jpg, jpeg, png or gif"}
        with open(i_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
            data_uri = f"data:image/{format};base64,{b64}"
        return {
            "success": True,
            "image_path": image_path,
            "data_uri": data_uri,
        }

    @tool
    async def add_service(self, service_id: str):
        """Add a service to the endpoint."""
        try:
            s = await connect_remote(service_id, DEFAULT_SERVER_URL)
            info = await s.fetch_service_info()
            self.services.append({
                "id": service_id,
                "name": info.service_name,
            })
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @tool
    async def get_service(self, service_id_or_name: str) -> dict | None:
        """Get a service by id or name."""
        for s in self.services:
            if (
                s["id"] == service_id_or_name
                or s["name"] == service_id_or_name
            ):
                return s
        return None

    async def run_builtin_services(self, engine: Engine):
        services = []
        default_services = [
            "python_interpreter",
            "file_manager",
            "web_browse",
        ]
        builtin_services = self.config.get("builtin_services", default_services)
        for service in builtin_services:
            if isinstance(service, str):
                service_type = service
                params = {}
            else:
                service_type = service.get("type", service)
                params = service.copy()
                del params["type"]

            if service_type == "python_interpreter":
                from ..tools.python import PythonInterpreterToolSet
                toolset = PythonInterpreterToolSet(
                    name=params.get("name", "python_interpreter"),
                    workdir=str(self.path),
                    endpoint_service_id=self.service_id,
                )
            elif service_type == "file_manager":
                from ..tools.file_manager import FileManagerToolSet
                toolset = FileManagerToolSet(
                    name=params.get("name", "file_manager"),
                    path=str(self.path),
                    endpoint_service_id=self.worker.service_id,
                )
            elif service_type == "web_browse":
                from ..tools.web_browse import WebBrowseToolSet
                toolset = WebBrowseToolSet(
                    name=params.get("name", "web_browse"),
                    endpoint_service_id=self.worker.service_id,
                )
            elif service_type == "r_interpreter":
                from ..tools.r import RInterpreterToolSet
                toolset = RInterpreterToolSet(
                    name=params.get("name", "r_interpreter"),
                    endpoint_service_id=self.worker.service_id,
                )
            elif service_type == "shell":
                from ..tools.shell import ShellToolSet
                toolset = ShellToolSet(
                    name=params.get("name", "shell"),
                    endpoint_service_id=self.worker.service_id,
                )
            elif service_type == "vector_rag":
                from ..tools.vector_rag import VectorRAGToolSet
                db_path = params.get("db_path")
                if not db_path:
                    raise ValueError("db_path is required for vector_rag service")
                if params.get("download_from_huggingface"):
                    from ..rag.build import download_from_huggingface
                    download_path = params.get("download_path", "tmp/db")
                    if not os.path.exists(download_path):
                        logger.info(f"Downloading vector database from Hugging Face to {download_path}")
                        download_from_huggingface(download_path)
                    else:
                        logger.info(f"Vector database already exists in {download_path}")
                toolset = VectorRAGToolSet(
                    name=params.get("name", "vector_rag"),
                    db_path=db_path,
                    endpoint_service_id=self.worker.service_id,
                )
            elif service_type == "scraper":
                from ..tools.scraper import ScraperToolSet
                toolset = ScraperToolSet(
                    name=params.get("name", "scraper"),
                    endpoint_service_id=self.worker.service_id,
                )
            services.append(toolset)

        for service in services:
            job = ProcessJob(
                service.run,
                args=(self.config.get("log_level", "INFO"),),
            )
            await engine.submit_async(job)
            await job.wait_until_status("running")

    async def add_outer_services(self):
        for service_id in self.config.get("outer_services", []):
            logger.info(f"Adding outer service {service_id}")
            resp = await self.add_service(service_id)
            if not resp["success"]:
                logger.error(f"Failed to add outer service {service_id}: {resp['error']}")

    async def run_docker_services(self, engine: Engine):
        data_dir = str(self.path.absolute())
        for docker_image_name in self.config.get("docker_services", []):
            cmd = f"docker run -e MAGIQUE_SERVER_URL={DEFAULT_SERVER_URL} -e ENDPOINT_SERVICE_ID={self.service_id} -v {data_dir}:/data {docker_image_name}"
            job = SubprocessJob(cmd)
            await engine.submit_async(job)
            await job.wait_until_status("running")

    async def run(self):
        from loguru import logger
        logger.remove()
        logger.add(sys.stderr, level=self.config.get("log_level", "INFO"))
        engine = Engine()
        job = LocalJob(self.worker.run)
        await engine.submit_async(job)
        await job.wait_until_status("running")
        await self.run_builtin_services(engine)
        await self.add_outer_services()
        await self.run_docker_services(engine)
        await engine.wait_async()

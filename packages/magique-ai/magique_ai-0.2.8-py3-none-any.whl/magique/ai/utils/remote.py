import asyncio
from magique.client import connect_to_server, ServiceProxy, MagiqueError

from ..constant import DEFAULT_SERVER_URL


async def connect_remote(
        service_name_or_id: str,
        server_url: str = DEFAULT_SERVER_URL,
        server_timeout: float = 5.0,
        service_timeout: float = 10.0,
        time_delta: float = 0.5,
        try_direct_connection: bool = True,
        ) -> ServiceProxy:
    server = None
    async def _get_server():
        nonlocal server
        while server is None:
            try:
                server = await connect_to_server(server_url)
            except Exception:
                await asyncio.sleep(time_delta)

    await asyncio.wait_for(_get_server(), server_timeout)
    service = None

    async def _get_service():
        nonlocal service
        while service is None:
            try:
                service = await server.get_service(service_name_or_id, try_direct_connection=try_direct_connection)
            except MagiqueError:
                await asyncio.sleep(time_delta)

    await asyncio.wait_for(_get_service(), service_timeout)
    return service


def toolset_cli(toolset_type, default_service_name: str):
    import fire

    async def main(service_name: str = default_service_name, **kwargs):
        toolset = toolset_type(service_name, **kwargs)
        await toolset.run()

    fire.Fire(main)

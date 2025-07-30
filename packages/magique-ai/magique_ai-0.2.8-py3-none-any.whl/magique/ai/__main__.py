import fire
from .utils.log import logger


async def remote_call(service_name_or_id: str, method_name: str, **kwargs):
    from .utils.remote import connect_remote
    from pprint import pprint
    service = await connect_remote(service_name_or_id)
    result = await service.invoke(method_name, kwargs)
    logger.info("Result:")
    pprint(result)


async def build_rag_db(yaml_path: str, output_dir: str):
    from .rag.build import build_all
    await build_all(yaml_path, output_dir)


fire.Fire({
    "build_rag_db": build_rag_db,
    "remote_call": remote_call,
})

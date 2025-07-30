import os
import os.path
import shutil

import fire
import yaml

from . import Endpoint
from ..utils.log import logger


HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_TEMPLATE = os.path.join(HERE, "endpoint.yaml")


def generate_config(output_path: str = "endpoint.yaml", overwrite: bool = False):
    if os.path.exists(output_path) and not overwrite:
        logger.warning(f"Config file already exists at {output_path}, skipping")
        return
    shutil.copy(CONFIG_TEMPLATE, output_path)
    logger.info(f"Config file generated at {output_path}")


async def start_endpoint(config_path: str | None = None):
    if config_path is None:
        config_path = "endpoint.yaml"
    if not os.path.exists(config_path):
        logger.error(f"Config file not found at {config_path}")
        logger.info("Please run `python -m magique.ai.endpoint config` to generate a config file")
        return
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    service_name = config.get("service_name", "pantheon-chatroom-endpoint")
    workspace_path = config.get("workspace_path", "./.pantheon-chatroom-workspace")
    worker_params = config.get("worker_params", {})

    endpoint = Endpoint(
        service_name,
        workspace_path,
        worker_params,
        config,
    )
    await endpoint.run()


if __name__ == "__main__":
    fire.Fire({
        "start": start_endpoint,
        "config": generate_config,
    })

import importlib
import os
import sys

from structlog import get_logger
from structlog._config import BoundLoggerLazyProxy
from typer import Argument, Typer

from .model import BasePlugin

logger: BoundLoggerLazyProxy = get_logger()

app = Typer()


@app.command()
def make(plugin_path: str = Argument(default="src.your_plugin:plugin")):

    try:

        module_str, app_name_str = plugin_path.split(":", 1)

        # Add current directory to sys.path

        sys.path.append(os.getcwd())

        module = importlib.import_module(module_str)

        plugin_object: BasePlugin = getattr(module, app_name_str)

    except (ImportError, AttributeError) as e:
        logger.error(f"Error importing plugin: {e}")
        raise

    logger.debug(type(plugin_object))

    plugin_object.generate_manifest()
    plugin_object.generate_providers()
    plugin_object.generate_tools()

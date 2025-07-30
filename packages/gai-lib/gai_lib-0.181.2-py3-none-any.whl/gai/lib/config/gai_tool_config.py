import os
import copy
import yaml
from abc import ABC
from pydantic import BaseModel, Field
from typing import Dict, Optional, Union, Literal
from gai.lib.utils import get_app_path
from gai.lib.logging import getLogger
logger = getLogger(__name__)

from .config_base import ConfigBase, ModuleConfig

class MissingToolConfigError(Exception):
    """Custom Exception with a message"""
    def __init__(self, message):
        super().__init__(message)


class GaiToolConfig(ConfigBase, ABC):
    type: str
    name: str
    extra: Optional[Dict] = None
    class Config:
        extra = "allow"

    @classmethod
    def get_builtin_config_path(cls, this_file) -> str:
        """
        This method is for server subclass to locate the server config file
        """
        from pathlib import Path
        cfg_file = Path(this_file).resolve().parent / "gai.yml"
        file_path = str(cfg_file)
        return file_path

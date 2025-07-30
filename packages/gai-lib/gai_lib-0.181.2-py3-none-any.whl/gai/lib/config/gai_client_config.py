import copy
import os
import yaml
from pydantic import BaseModel
from typing import Dict, Optional
from gai.lib.utils import get_app_path
from gai.lib.logging import getLogger
logger = getLogger(__name__)

from .config_base import ConfigBase

class GaiClientConfig(ConfigBase):
    client_type: str
    type: Optional[str] = None
    engine: Optional[str] = None
    model: Optional[str] = None
    name: Optional[str] = None
    url: Optional[str] = None
    env: Optional[Dict] = None
    extra: Optional[Dict] = None
    hyperparameters: Optional[Dict] = {}


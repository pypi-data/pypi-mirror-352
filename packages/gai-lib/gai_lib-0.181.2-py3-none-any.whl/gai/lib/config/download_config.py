from pydantic import BaseModel
from typing import Optional, Literal, Union

from gai.lib.logging import getLogger
logger = getLogger(__name__)

class DownloadConfigBase(BaseModel):
    local_dir: str

class HuggingfaceDownloadConfig(DownloadConfigBase):
    type: Literal["huggingface"]
    repo_id: str
    revision: str
    file: Optional[str]=None

class CivitaiDownloadConfig(DownloadConfigBase):
    type: Literal["civitai"]
    url: str
    download: str

DownloadConfig = Union[
    "HuggingfaceDownloadConfig",
    "CivitaiDownloadConfig",
]
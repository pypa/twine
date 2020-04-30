from types import ModuleType
from typing import Any
from typing import Optional
from typing import Union

from .distribution import Distribution

class Installed(Distribution):
    package_name: str
    package: ModuleType
    metadata_version: Optional[str]
    def __init__(
        self, package: ModuleType, metadata_version: Optional[str] = ...
    ) -> None: ...
    def read(self) -> Optional[str]: ...

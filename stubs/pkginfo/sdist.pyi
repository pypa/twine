from typing import Optional

from .distribution import Distribution

class SDist(Distribution):
    filename: str
    metadata_version: Optional[str]
    def __init__(
        self, filename: str, metadata_version: Optional[str] = ...
    ) -> None: ...
    def read(self) -> bytes: ...

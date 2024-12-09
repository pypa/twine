class Distribution:
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def read(self) -> bytes:
        raise NotImplementedError

    @property
    def py_version(self) -> str:
        return "any"

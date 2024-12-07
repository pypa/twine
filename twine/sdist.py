import os
import tarfile

from twine import distribution
from twine import exceptions


class SDist(distribution.Distribution):

    @property
    def py_version(self) -> str:
        return "source"

    def read(self) -> bytes:
        fqn = os.path.abspath(os.path.normpath(self.filename))
        if not os.path.exists(fqn):
            raise exceptions.InvalidDistribution(f"No such file: {fqn}")

        with tarfile.open(fqn, "r:gz") as sdist:
            members = [m for m in sdist.getmembers() if m.name.endswith("/PKG-INFO")]
            members.sort(key=lambda x: len(x.name.split("/")))
            for member in members:
                fd = sdist.extractfile(member)
                assert fd is not None, "for mypy"
                data = fd.read()
                if b"Metadata-Version" in data:
                    return data

        raise exceptions.InvalidDistribution(
            f"No PKG-INFO in archive or PKG-INFO missing 'Metadata-Version': {fqn}"
        )

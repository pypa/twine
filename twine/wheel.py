import os
import re
import zipfile

from pkginfo import distribution
from pkginfo.distribution import Distribution

# Monkeypatch Metadata 2.0 support
distribution.HEADER_ATTRS_2_0 = distribution.HEADER_ATTRS_1_2
distribution.HEADER_ATTRS.update({"2.0": distribution.HEADER_ATTRS_2_0})


wheel_file_re = re.compile(
    r"""^(?P<namever>(?P<name>.+?)(-(?P<ver>\d.+?))?)
        ((-(?P<build>\d.*?))?-(?P<pyver>.+?)-(?P<abi>.+?)-(?P<plat>.+?)
        \.whl|\.dist-info)$""",
    re.VERBOSE)


class Wheel(Distribution):

    def __init__(self, filename, metadata_version=None):
        self.filename = filename
        self.metadata_version = metadata_version
        self.extractMetadata()

    @property
    def py_version(self):
        wheel_info = wheel_file_re.match(self.filename)
        return wheel_info.group("pyver")

    def read(self):
        fqn = os.path.abspath(os.path.normpath(self.filename))
        if not os.path.exists(fqn):
            raise ValueError('No such file: %s' % fqn)

        if fqn.endswith('.whl'):
            archive = zipfile.ZipFile(fqn)
            names = archive.namelist()

            def read_file(name):
                return archive.read(name)
        else:
            raise ValueError('Not a known archive format: %s' % fqn)

        try:
            tuples = [x.split('/') for x in names if 'METADATA' in x]
            schwarz = sorted([(len(x), x) for x in tuples])
            for path in [x[1] for x in schwarz]:
                candidate = '/'.join(path)
                data = read_file(candidate)
                if b'Metadata-Version' in data:
                    return data
        finally:
            archive.close()

        raise ValueError('No METADATA in archive: %s' % fqn)

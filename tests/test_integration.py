from twine.cli import dispatch


def test_devpi_upload(devpi_server, uploadable_dist):
    command = [
        'upload',
        '--repository-url', devpi_server.url,
        '--username', devpi_server.username,
        '--password', devpi_server.password,
        str(uploadable_dist),
    ]
    dispatch(command)


twine_sampleproject_token = (
    "pypi-AgENdGVzdC5weXBpLm9yZwIkNDgzYTFhMjEtMzEwYi00NT"
    "kzLTkwMzYtYzc1Zjg4NmFiMjllAAJEeyJwZXJtaXNzaW9ucyI6IH"
    "sicHJvamVjdHMiOiBbInR3aW5lLXNhbXBsZXByb2plY3QiXX0sIC"
    "J2ZXJzaW9uIjogMX0AAAYg2kBZ1tN8lj8dlmL3ScoVvr_pvQE0t"
    "6PKqigoYJKvw3M"
)


def test_pypi_upload(sampleproject_dist):
    command = [
        'upload',
        '--repository-url', 'https://test.pypi.org/legacy/',
        '--username', '__token__',
        '--password', twine_sampleproject_token,
        str(sampleproject_dist),
    ]
    dispatch(command)


def test_pypiserver_upload(pypiserver_instance, uploadable_dist):
    command = [
        'upload',
        '--repository-url', pypiserver_instance.url,
        '--username', 'any',
        '--password', 'any',
        str(uploadable_dist),
    ]
    dispatch(command)

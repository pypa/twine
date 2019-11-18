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


def test_pypiserver_upload(pypiserver_instance, uploadable_dist):
    command = [
        'upload',
        '--repository-url', pypiserver_instance.url,
        '--username', 'any',
        '--password', 'any',
        str(uploadable_dist),
    ]
    dispatch(command)

# Copyright 2015 Ian Cordasco
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import requests

from twine import repository
from twine.utils import DEFAULT_REPOSITORY, TEST_REPOSITORY

import pretend
import pytest
from contextlib import contextmanager


def test_gpg_signature_structure_is_preserved():
    data = {
        'gpg_signature': ('filename.asc', 'filecontent'),
    }

    tuples = repository.Repository._convert_data_to_list_of_tuples(data)
    assert tuples == [('gpg_signature', ('filename.asc', 'filecontent'))]


def test_content_structure_is_preserved():
    data = {
        'content': ('filename', 'filecontent'),
    }

    tuples = repository.Repository._convert_data_to_list_of_tuples(data)
    assert tuples == [('content', ('filename', 'filecontent'))]


def test_iterables_are_flattened():
    data = {
        'platform': ['UNKNOWN'],
    }

    tuples = repository.Repository._convert_data_to_list_of_tuples(data)
    assert tuples == [('platform', 'UNKNOWN')]

    data = {
        'platform': ['UNKNOWN', 'ANOTHERPLATFORM'],
    }

    tuples = repository.Repository._convert_data_to_list_of_tuples(data)
    assert tuples == [('platform', 'UNKNOWN'),
                      ('platform', 'ANOTHERPLATFORM')]


def test_set_client_certificate():
    repo = repository.Repository(
        repository_url=DEFAULT_REPOSITORY,
        username='username',
        password='password',
    )

    assert repo.session.cert is None

    repo.set_client_certificate(('/path/to/cert', '/path/to/key'))
    assert repo.session.cert == ('/path/to/cert', '/path/to/key')


def test_set_certificate_authority():
    repo = repository.Repository(
        repository_url=DEFAULT_REPOSITORY,
        username='username',
        password='password',
    )

    assert repo.session.verify is True

    repo.set_certificate_authority('/path/to/cert')
    assert repo.session.verify == '/path/to/cert'


def test_make_user_agent_string():
    repo = repository.Repository(
        repository_url=DEFAULT_REPOSITORY,
        username='username',
        password='password',
    )

    assert 'User-Agent' in repo.session.headers

    user_agent = repo.session.headers['User-Agent']
    assert 'twine/' in user_agent
    assert 'requests/' in user_agent
    assert 'requests-toolbelt/' in user_agent
    assert 'pkginfo/' in user_agent
    assert 'setuptools/' in user_agent


def response_with(**kwattrs):
    resp = requests.Response()
    for attr, value in kwattrs.items():
        if hasattr(resp, attr):
            setattr(resp, attr, value)

    return resp


def test_package_is_uploaded_404s():
    repo = repository.Repository(
        repository_url=DEFAULT_REPOSITORY,
        username='username',
        password='password',
    )
    repo.session = pretend.stub(
        get=lambda url, headers: response_with(status_code=404)
    )
    package = pretend.stub(
        safe_name='fake',
        metadata=pretend.stub(version='2.12.0'),
    )

    assert repo.package_is_uploaded(package) is False


def test_package_is_uploaded_200s_with_no_releases():
    repo = repository.Repository(
        repository_url=DEFAULT_REPOSITORY,
        username='username',
        password='password',
    )
    repo.session = pretend.stub(
        get=lambda url, headers: response_with(status_code=200,
                                               _content=b'{"releases": {}}',
                                               _content_consumed=True),
    )
    package = pretend.stub(
        safe_name='fake',
        metadata=pretend.stub(version='2.12.0'),
    )

    assert repo.package_is_uploaded(package) is False


@pytest.mark.parametrize('disable_progress_bar', [
    True,
    False
])
def test_disable_progress_bar_is_forwarded_to_tqdm(monkeypatch, tmpdir,
                                                   disable_progress_bar):
    """Test whether the disable flag is passed to tqdm
        when the disable_progress_bar option is passed to the
        repository
    """
    @contextmanager
    def progressbarstub(*args, **kwargs):
        assert "disable" in kwargs
        assert kwargs["disable"] == disable_progress_bar
        yield

    monkeypatch.setattr(repository, "ProgressBar", progressbarstub)
    repo = repository.Repository(
        repository_url=DEFAULT_REPOSITORY,
        username='username',
        password='password',
        disable_progress_bar=disable_progress_bar
    )

    repo.session = pretend.stub(
        post=lambda url, data, allow_redirects, headers: response_with(
            status_code=200)
    )

    fakefile = tmpdir.join('fake.whl')
    fakefile.write('.')

    def dictfunc():
        return {"name": "fake"}

    package = pretend.stub(
        safe_name='fake',
        metadata=pretend.stub(version='2.12.0'),
        basefilename="fake.whl",
        filename=str(fakefile),
        metadata_dictionary=dictfunc
    )

    repo.upload(package)


@pytest.mark.parametrize('package_meta,repository_url,release_urls', [
    # Single package
    (
        [('fake', '2.12.0')],
        DEFAULT_REPOSITORY,
        {'https://pypi.org/project/fake/2.12.0/'},
    ),
    # Single package to testpypi
    (
        [('fake', '2.12.0')],
        TEST_REPOSITORY,
        {'https://test.pypi.org/project/fake/2.12.0/'},
    ),
    # Multiple packages (faking a wheel and an sdist)
    (
        [('fake', '2.12.0'), ('fake', '2.12.0')],
        DEFAULT_REPOSITORY,
        {'https://pypi.org/project/fake/2.12.0/'},
    ),
    # Multiple releases
    (
        [('fake', '2.12.0'), ('fake', '2.12.1')],
        DEFAULT_REPOSITORY,
        {
            'https://pypi.org/project/fake/2.12.0/',
            'https://pypi.org/project/fake/2.12.1/',
        },
    ),
    # Not pypi
    (
        [('fake', '2.12.0')],
        'http://devpi.example.com',
        set(),
    ),
    # No packages
    (
        [],
        DEFAULT_REPOSITORY,
        set(),
    ),
])
def test_release_urls(package_meta, repository_url, release_urls):
    packages = [
        pretend.stub(
            safe_name=name,
            metadata=pretend.stub(version=version),
        )
        for name, version in package_meta
    ]

    repo = repository.Repository(
        repository_url=repository_url,
        username='username',
        password='password',
    )

    assert repo.release_urls(packages) == release_urls

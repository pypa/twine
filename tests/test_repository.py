# Copyright 2015 Ian Cordasco
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from twine import repository


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
        repository_url='https://pypi.python.org/pypi',
        username='username',
        password='password',
    )

    assert repo.session.cert is None

    repo.set_client_certificate(('/path/to/cert', '/path/to/key'))
    assert repo.session.cert == ('/path/to/cert', '/path/to/key')


def test_set_certificate_authority():
    repo = repository.Repository(
        repository_url='https://pypi.python.org/pypi',
        username='username',
        password='password',
    )

    assert repo.session.verify is True

    repo.set_certificate_authority('/path/to/cert')
    assert repo.session.verify == '/path/to/cert'


def test_make_user_agent_string():
    repo = repository.Repository(
        repository_url='https://pypi.python.org/pypi',
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

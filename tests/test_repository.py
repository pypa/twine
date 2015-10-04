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

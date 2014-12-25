# Copyright 2014 Ian Cordasco
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
import requests

from twine import common
from twine import utils


def post_data(distribution, action):
    """Take the distribution and the action and generate post data."""
    meta = distribution.metadata
    data = {
        ':action': action,
        'metadata_version': '1.0',
        'name': meta.get_name(),
        'version': meta.get_version(),
        'summary': meta.get_description(),
        'home_page': meta.get_url(),
        'author': meta.get_contact(),
        'author_email': meta.get_contact_email(),
        'license': meta.get_licence(),
        'description': meta.get_long_description(),
        'keywords': meta.get_keywords(),
        'platform': meta.get_platforms(),
        'classifiers': meta.get_classifiers(),
        'download_url': meta.get_download_url(),
        # PEP 314
        'provides': meta.get_provides(),
        'requires': meta.get_requires(),
        'obsoletes': meta.get_obsoletes(),
    }
    if data['provides'] or data['requires'] or data['obsoletes']:
        data['metadata_version'] = '1.1'
    # We rely on requests to generate the multipart form-data for us. In order
    # to not rely on the requests-toolbelt, we need to send tuples as values
    # so the values are not interpreted as files.
    return dict((k, ('', data[k])) for k in data)


def register(repository, username, password, **kwargs):
    # Get our config from ~/.pypirc
    try:
        config = utils.get_config()[repository]
    except KeyError:
        raise KeyError(
            "Missing '{0}' section from the configuration file".format(
                repository,
            ),
        )

    username = utils.get_username(username, config)
    password = utils.get_password(password, config)

    session = requests.Session()
    session.auth = (username, password)
    distribution = None
    resp = session.post(config["repository"],
                        files=post_data(distribution, "submit"))
    resp.close()
    session.close()
    resp.raise_for_status()


def main(args):
    parser = common.common_arguments("twine register")
    args = parser.parse_args(args)
    register(**vars(args))

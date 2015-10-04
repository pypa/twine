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
from __future__ import absolute_import, unicode_literals, print_function

import requests
from requests_toolbelt.multipart import MultipartEncoder


KEYWORDS_TO_NOT_FLATTEN = set(["gpg_signature", "content"])


class Repository(object):
    def __init__(self, repository_url, username, password):
        self.url = repository_url
        self.session = requests.session()
        self.session.auth = (username, password)

    def close(self):
        self.session.close()

    @staticmethod
    def _convert_data_to_list_of_tuples(data):
        data_to_send = []
        for key, value in data.items():
            if (key in KEYWORDS_TO_NOT_FLATTEN or
                    not isinstance(value, (list, tuple))):
                data_to_send.append((key, value))
            else:
                for item in value:
                    data_to_send.append((key, item))
        return data_to_send

    def register(self, package):
        data = package.metadata_dictionary()
        data.update({
            ":action": "submit",
            "protocol_version": "1",
        })

        print("Registering {0}".format(package.basefilename))

        data_to_send = self._convert_data_to_list_of_tuples(data)
        encoder = MultipartEncoder(data_to_send)
        resp = self.session.post(
            self.url,
            data=encoder,
            allow_redirects=False,
            headers={'Content-Type': encoder.content_type},
        )
        # Bug 28. Try to silence a ResourceWarning by releasing the socket.
        resp.close()
        return resp

    def upload(self, package):
        data = package.metadata_dictionary()
        data.update({
            # action
            ":action": "file_upload",
            "protcol_version": "1",
        })

        data_to_send = self._convert_data_to_list_of_tuples(data)

        print("Uploading {0}".format(package.basefilename))

        with open(package.filename, "rb") as fp:
            data_to_send.append((
                "content",
                (package.basefilename, fp, "application/octet-stream"),
            ))
            encoder = MultipartEncoder(data_to_send)

            resp = self.session.post(
                self.url,
                data=encoder,
                allow_redirects=False,
                headers={'Content-Type': encoder.content_type},
            )

        return resp

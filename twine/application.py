# Copyright 2013 Donald Stufft
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
from __future__ import absolute_import, division, print_function

import argparse
import collections
import logging
import logging.config

import six

import twine.commands


logger = logging.getLogger(__name__)


class Twine(object):

    def cli(self, argv):
        def _generate_parser(parser, commands):
            # Generate our commands
            subparsers = parser.add_subparsers()
            for name, command in six.iteritems(commands):
                cmd_parser = subparsers.add_parser(name)

                if hasattr(command, "create_parser"):
                    command.create_parser(cmd_parser)

                if isinstance(command, collections.Mapping):
                    _generate_parser(cmd_parser, command)
                else:
                    cmd_parser.set_defaults(_cmd=command)

        parser = argparse.ArgumentParser(prog="twine")
        parser.add_argument(
            "-v", "--verbose",
            dest="_verbose",
            action="count",
            default=0,
        )
        parser.add_argument(
            "-q", "--quiet",
            dest="_quiet",
            action="store_true",
            default=False,
        )

        _generate_parser(parser, twine.commands.__commands__)

        args = parser.parse_args(argv)

        logging.config.dictConfig({
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "simple": {
                    "format": "%(message)s",
                },
            },
            "handlers": {
                "console": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "formatter": "simple",
                },
            },
            "loggers": {
                "requests": {
                    "propagate": False,
                },
            },
            "root": {
                "level": logging.getLevelName(
                    max(
                        (20 - (args._verbose * 10)),
                        10,
                    ) if not args._quiet else "CRITICAL"
                ),
                "handlers": ["console"],
            },
        })

        if getattr(args, "_cmd", None):
            return args._cmd(
                *args._get_args(),
                **{
                    k: v for k, v in args._get_kwargs()
                    if not k.startswith("_")
                }
            )
        else:
            parser.print_help()

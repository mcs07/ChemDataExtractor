# -*- coding: utf-8 -*-
"""
chemdataextractor.config
~~~~~~~~~~~~~~~~~~~~~~~~

Config file reader/writer.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import io
import os
from collections import MutableMapping

import appdirs
import yaml
from yaml import SafeLoader


def construct_yaml_str(self, node):
    """Override the default string handling function to always return unicode objects."""
    return self.construct_scalar(node)


SafeLoader.add_constructor(u'tag:yaml.org,2002:str', construct_yaml_str)


class Config(MutableMapping):
    """Read and write to config file.

    A config object is essentially a string key-value store that can be treated like a dictionary::

        c = Config()
        c['foo'] = 'bar'
        print c['foo']

    The file location may be specified::

        c = Config('~/matt/anotherconfig.yml')
        c['where'] = 'in a different file'

    If no location is specified, the environment variable CHEMDATAEXTRACTOR_CONFIG is checked and used if available.
    Otherwise, a standard config location is used, which varies depending on the operating system. You can check the
    location using the ``path`` property. For more information see https://github.com/ActiveState/appdirs

    It is possible to edit the file by hand with a text editor. It is in YAML format.

    Warning: multiple instances of Config() pointing to the same file will not see each others' changes, and will
    overwrite the entire file when any key is changed.

    """

    def __init__(self, path=None):
        """

        :param string path: (Optional) Path to config file location.
        """
        self._path = path
        self._data = {}

        # Use CHEMDATAEXTRACTOR_CONFIG environment variable if set
        if not self._path:
            self._path = os.environ.get('CHEMDATAEXTRACTOR_CONFIG')
        # Use OS-dependent config directory given by appdirs
        if not self._path:
            self._path = os.path.join(appdirs.user_config_dir('ChemDataExtractor'), 'chemdataextractor.yml')
        if os.path.isfile(self.path):
            with io.open(self.path, encoding='utf8') as f:
                self._data = yaml.safe_load(f)

    @property
    def path(self):
        """The path to the config file."""
        return self._path

    def _flush(self):
        """Save the contents of data to the file on disk. You should not need to call this manually."""
        d = os.path.dirname(self.path)
        if not os.path.isdir(d):
            os.makedirs(d)
        with io.open(self.path, 'w', encoding='utf8') as f:
            yaml.safe_dump(self._data, f, default_flow_style=False, encoding=None)

    def __contains__(self, k):
        return k in self._data

    def __getitem__(self, k):
        return self._data[k]

    def __setitem__(self, k, v):
        self._data[k] = v
        self._flush()

    def __delitem__(self, k):
        del self._data[k]
        self._flush()

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return '<Config: %s>' % self.path

    def clear(self):
        """Clear all values from config."""
        self._data = {}
        self._flush()


#: Global config instance.
config = Config()

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

import os
from collections import MutableMapping

import appdirs
import six
from six.moves.configparser import SafeConfigParser, NoOptionError


class Config(MutableMapping):
    """Read and write to config file.

    A config object is essentially a string key-value store that can be treated like a dictionary::

        c = Config()
        c['foo'] = 'bar'
        print c['foo']

    The file location may be specified::

        c = Config('~/matt/anotherconfig.cfg')
        c['where'] = 'in a different file'

    If no location is specified, the environment variable CHEMDATAEXTRACTOR_CONFIG is checked and used if available.
    Otherwise, a standard config location is used, which varies depending on the operating system. You can check the
    location using the ``path`` property. For more information see https://github.com/ActiveState/appdirs

    It is possible to edit the file by hand with a text editor.

    Warning: multiple instances of Config() pointing to the same file will not see each others' changes, and will
    overwrite the entire file when any key is changed.

    """

    #: These values will be present in a config object unless they are explicitly defined otherwise in the config file
    default_values = {}

    def __init__(self, path=None):
        """

        :param string path: (Optional) Path to config file location.
        """
        self._path = path

        # Use CHEMDATAEXTRACTOR_CONFIG environment variable if set
        if not self._path:
            self._path = os.environ.get('CHEMDATAEXTRACTOR_CONFIG')
        # Use OS-dependent config directory given by appdirs
        if not self._path:
            self._path = os.path.join(appdirs.user_config_dir('ChemDataExtractor'), 'config.cfg')
        self._parser = SafeConfigParser()
        if os.path.isfile(self.path):
            with open(self.path) as f:
                self._parser.readfp(f)
        if not self._parser.has_section('cde'):
            self._parser.add_section('cde')
        for k, v in six.iteritems(self.default_values):
            if not self._parser.has_option('cde', k.encode('utf-8')):
                self._parser.set('cde', k.encode('utf-8'), v.encode('utf-8'))

    @property
    def path(self):
        """The path to the config file."""
        return self._path

    def _flush(self):
        """Save the contents of data to the file on disk. You should not need to call this manually."""
        d = os.path.dirname(self.path)
        if not os.path.isdir(d):
            os.makedirs(d)
        with open(self.path, 'w') as f:
            self._parser.write(f)

    def __contains__(self, k):
        return self._parser.has_option('cde', k.encode('utf-8'))

    def __getitem__(self, k):
        try:
            return self._parser.get('cde', k.encode('utf-8'))
        except NoOptionError:
            raise KeyError(k)

    def __setitem__(self, k, v):
        self._parser.set('cde', k.encode('utf-8'), v.encode('utf-8'))
        self._flush()

    def __delitem__(self, k):
        try:
            self._parser.remove_option('cde', k.encode('utf-8'))
            self._flush()
        except NoOptionError:
            raise KeyError(k)

    def __iter__(self):
        return (k for k, v in self._parser.items('cde'))

    def __len__(self):
        return len(self._parser.items('cde'))

    def __repr__(self):
        return '<Config: %s>' % self.path

    def clear(self):
        """Clear all values from config."""
        self._parser.remove_section('cde')
        self._parser.add_section('cde')
        self._flush()


#: Global config instance.
config = Config()

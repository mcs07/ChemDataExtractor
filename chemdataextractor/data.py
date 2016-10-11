# -*- coding: utf-8 -*-
"""
chemdataextractor.data
~~~~~~~~~~~~~~~~~~~~~~

Tools for loading and caching data files.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import io
import logging
import os

import appdirs
import requests
import six

from .config import config
from .errors import ModelNotFoundError
from .utils import python_2_unicode_compatible, ensure_dir

log = logging.getLogger(__name__)


SERVER_ROOT = 'http://data.chemdataextractor.org/'


@python_2_unicode_compatible
class Package(object):
    """Data package."""

    def __init__(self, path):
        self.path = path

    @property
    def remote_path(self):
        """"""
        return SERVER_ROOT + self.path

    @property
    def local_path(self):
        """"""
        return find_data(self.path, warn=False)

    def remote_exists(self):
        """"""
        r = requests.get(self.remote_path)
        if r.status_code in {400, 401, 403, 404}:
            return False
        return True

    def local_exists(self):
        """"""
        if os.path.isfile(self.local_path):
            return True
        return False

    def download(self, force=False):
        """"""
        log.debug('Considering %s', self.remote_path)
        ensure_dir(os.path.dirname(self.local_path))
        r = requests.get(self.remote_path, stream=True)
        r.raise_for_status()
        # Check if already downloaded
        if self.local_exists():
            # Skip if existing, unless the file has changed
            if not force and os.path.getsize(self.local_path) == int(r.headers['content-length']):
                log.debug('Skipping existing: %s', self.local_path)
                return False
            else:
                log.debug('File size mismatch for %s', self.local_path)
        log.info('Downloading %s to %s', self.remote_path, self.local_path)
        with io.open(self.local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024*1024):  # Large 10MB chunks
                if chunk:
                    f.write(chunk)
        return True

    def __repr__(self):
        return '<Package: %s>' % self.path

    def __str__(self):
        return '<Package: %s>' % self.path


#: Current active data packages
PACKAGES = [
    Package('models/cem_crf-1.0.pickle'),
    Package('models/cem_crf_chemdner_cemp-1.0.pickle'),
    Package('models/cem_dict_cs-1.0.pickle'),
    Package('models/cem_dict-1.0.pickle'),
    Package('models/clusters_chem1500-1.0.pickle'),
    Package('models/pos_ap_genia_nocluster-1.0.pickle'),
    Package('models/pos_ap_genia-1.0.pickle'),
    Package('models/pos_ap_wsj_genia_nocluster-1.0.pickle'),
    Package('models/pos_ap_wsj_genia-1.0.pickle'),
    Package('models/pos_ap_wsj_nocluster-1.0.pickle'),
    Package('models/pos_ap_wsj-1.0.pickle'),
    Package('models/pos_crf_genia_nocluster-1.0.pickle'),
    Package('models/pos_crf_genia-1.0.pickle'),
    Package('models/pos_crf_wsj_genia_nocluster-1.0.pickle'),
    Package('models/pos_crf_wsj_genia-1.0.pickle'),
    Package('models/pos_crf_wsj_nocluster-1.0.pickle'),
    Package('models/pos_crf_wsj-1.0.pickle'),
    Package('models/punkt_chem-1.0.pickle')
]


def get_data_dir():
    """Return path to the data directory."""
    # Use data_dir config value if set, otherwise use OS-dependent data directory given by appdirs
    return config.get('data_dir', appdirs.user_data_dir('ChemDataExtractor'))


def find_data(path, warn=True):
    """Return the absolute path to a data file within the data directory."""
    full_path = os.path.join(get_data_dir(), path)
    if warn and not os.path.isfile(full_path):
        for package in PACKAGES:
            if path == package.path:
                log.warn('%s doesn\'t exist. Run `cde data download` to get it.' % path)
                break
    return full_path


#: A dictionary used to cache models so they only need to be loaded once.
_model_cache = {}


def load_model(path):
    """Load a model from a pickle file in the data directory. Cached so model is only loaded once."""
    abspath = find_data(path)
    cached = _model_cache.get(abspath)
    if cached is not None:
        log.debug('Using cached copy of %s' % path)
        return cached
    log.debug('Loading model %s' % path)
    try:
        with io.open(abspath, 'rb') as f:
            model = six.moves.cPickle.load(f)
    except IOError:
        raise ModelNotFoundError('Could not load %s. Have you run `cde data download`?' % path)
    _model_cache[abspath] = model
    return model

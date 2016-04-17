# -*- coding: utf-8 -*-
"""
chemdataextractor.utils
~~~~~~~~~~~~~~~~~~~~~~~

Miscellaneous utility functions.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import errno
import functools
import logging
import os

import six


log = logging.getLogger(__name__)


def memoized_property(fget):
    """Decorator to create memoized properties."""
    attr_name = '_{}'.format(fget.__name__)

    @functools.wraps(fget)
    def fget_memoized(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fget(self))
        return getattr(self, attr_name)
    return property(fget_memoized)


def memoize(obj):
    """Decorator to create memoized functions, methods or classes."""
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        if args not in cache:
            cache[args] = obj(*args, **kwargs)
        return cache[args]
    return memoizer


def python_2_unicode_compatible(klass):
    """Fix __str__, __unicode__ and __repr__ methods under Python 2."""
    if six.PY2:
        if '__str__' not in klass.__dict__:
            raise ValueError("Define __str__() on %s to use @python_2_unicode_compatible" % klass.__name__)
        klass.__unicode__ = klass.__str__
        klass._unicode_repr = klass.__repr__
        klass.__str__ = lambda self: self.__unicode__().encode('utf-8')
        klass.__repr__ = lambda self: self._unicode_repr().encode('ascii', errors='backslashreplace')
    return klass


class Singleton(type):
    """Singleton metaclass."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def flatten(x):
    """Return a single flat list containing elements from nested lists."""
    result = []
    for el in x:
        if hasattr(el, '__iter__') and not isinstance(el, six.string_types):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result


def first(el):
    if len(el) > 0:
        return el[0]
    else:
        return None


def ensure_dir(path):
    """Ensure a directory exists."""
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

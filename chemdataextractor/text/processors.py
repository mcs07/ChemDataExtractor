# -*- coding: utf-8 -*-
"""
chemdataextractor.text.processors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Text processors.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from abc import ABCMeta, abstractmethod
import logging
import re

import six
from . import EMAIL_RE, APOSTROPHES


log = logging.getLogger(__name__)


class BaseProcessor(six.with_metaclass(ABCMeta)):
    """Abstract processor class from which all processors inherit. Subclasses must implement a ``__call__()`` method."""

    @abstractmethod
    def __call__(self, text):
        """Process the text.

        :param string text: The input text.
        :returns: The processed text or None.
        :rtype: string or None
        """
        return text


class Chain(object):
    """Apply a series of processors in turn. Stops if a processors returns None."""

    def __init__(self, *callables):
        self.callables = callables

    def __call__(self, value):
        for func in self.callables:
            if value is None:
                break
            value = func(value)
        return value


class Discard(object):
    """Return None if value matches a string."""

    def __init__(self, *match):
        self.match = match

    def __call__(self, value):
        if value in self.match:
            return None
        return value


class LAdd(object):
    """Add a substring to the start of a value."""

    def __init__(self, substring):
        self.substring = substring

    def __call__(self, value):
        return '%s%s' % (self.substring, value)


class RAdd(object):
    """Add a substring to the end of a value."""

    def __init__(self, substring):
        self.substring = substring

    def __call__(self, value):
        return '%s%s' % (value, self.substring)


class LStrip(object):
    """Remove a substring from the start of a value."""

    def __init__(self, *substrings):
        self.substrings = substrings

    def __call__(self, value):
        for substring in self.substrings:
            if value.startswith(substring):
                return value[len(substring):]
        return value


class RStrip(object):
    """Remove a substring from the end of a value."""

    def __init__(self, *substrings):
        self.substrings = substrings

    def __call__(self, value):
        for substring in self.substrings:
            if value.endswith(substring):
                return value[:-len(substring)]
        return value


def floats(s):
    """Convert string to float. Handles more string formats that the standard python conversion."""
    try:
        return float(s)
    except ValueError:
        s = re.sub(r'(\d)\s*\(\d+(\.\d+)?\)', r'\1', s)        # Remove bracketed numbers from end
        s = re.sub(r'(\d)\s*±\s*\d+(\.\d+)?', r'\1', s)        # Remove uncertainties from end
        s = s.rstrip('\'"+-=<>/,.:;!?)]}…∼~≈×*_≥≤')             # Remove trailing punctuation
        s = s.lstrip('\'"+=<>/([{∼~≈×*_≥≤£$€#§')                # Remove leading punctuation
        s = s.replace(',', '')                                 # Remove commas
        s = ''.join(s.split())                                  # Strip whitespace
        s = re.sub(r'(\d)\s*[×x]\s*10\^?(-?\d)', r'\1e\2', s)  # Convert scientific notation
        return float(s)


def strip_querystring(url):
    """Remove the querystring from the end of a URL."""
    p = six.moves.urllib.parse.urlparse(url)
    return p.scheme + "://" + p.netloc + p.path


class Substitutor(object):
    """Perform a list of substitutions defined by regex on text.

    Useful to clean up text where placeholders are used in place of actual unicode characters.
    """

    def __init__(self, substitutions):
        """

        :param substitutions: List of (regex, string) tuples that define the substitution.
        """
        self.substitutions = []
        for pattern, replacement in substitutions:
            if isinstance(pattern, six.string_types):
                pattern = re.compile(pattern, re.I | re.U)
            self.substitutions.append((pattern, replacement))

    def __call__(self, t):
        """Run substitutions on given text and return it.

        :param string t: The text to run substitutions on.
        """
        for pattern, replacement in self.substitutions:
            t = pattern.sub(replacement, t)
        return t


def extract_emails(text):
    """Return a list of email addresses extracted from the string."""
    text = text.replace(u'\u2024', '.')
    emails = []
    for m in EMAIL_RE.findall(text):
        emails.append(m[0])
    return emails


def unapostrophe(text):
    """Strip apostrophe and 's' from the end of a string."""
    text = re.sub(r'[%s]s?$' % ''.join(APOSTROPHES), '', text)
    return text

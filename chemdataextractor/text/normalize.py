# -*- coding: utf-8 -*-
"""
chemdataextractor.text.normalize
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tools for normalizing text.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from abc import ABCMeta, abstractmethod
import re
import unicodedata

import six

from . import CONTROLS, HYPHENS, QUOTES, DOUBLE_QUOTES, ACCENTS, SINGLE_QUOTES, APOSTROPHES, SLASHES, TILDES, MINUSES
from .processors import BaseProcessor


class BaseNormalizer(six.with_metaclass(ABCMeta, BaseProcessor)):
    """Abstract normalizer class from which all normalizers inherit.

    Subclasses must implement a ``normalize()`` method.
    """

    @abstractmethod
    def normalize(self, text):
        """Normalize the text.

        :param string text: The text to normalize.
        :returns: Normalized text.
        :rtype: string
        """
        return text

    def __call__(self, text):
        """Calling a normalizer instance like a function just calls the normalize method."""
        return self.normalize(text)


class Normalizer(BaseNormalizer):
    """Main Normalizer class for generic English text.

    Normalize unicode, hyphens, quotes, whitespace.

    By default, the normal form NFKC is used for unicode normalization. This applies a compatibility decomposition,
    under which equivalent characters are unified, followed by a canonical composition. See Python docs for information
    on normal forms: http://docs.python.org/2/library/unicodedata.html#unicodedata.normalize
    """

    def __init__(self, form='NFKC', strip=True, collapse=True, hyphens=False, quotes=False, ellipsis=False,
                 slashes=False, tildes=False):
        """

        :param string form: Normal form for unicode normalization.
        :param bool strip: Whether to strip whitespace from start and end.
        :param bool collapse: Whether to collapse all whitespace (tabs, newlines) down to single spaces.
        :param bool hyphens: Whether to normalize all hyphens, minuses and dashes to the ASCII hyphen-minus character.
        :param bool quotes: Whether to normalize all apostrophes, quotes and primes to the ASCII quote character.
        :param bool ellipsis: Whether to normalize ellipses to three full stops.
        :param bool slashes: Whether to normalize slash characters to the ASCII slash character.
        :param bool tildes: Whether to normalize tilde characters to the ASCII tilde character.
        """
        self.form = form
        self.strip = strip
        self.collapse = collapse
        self.hyphens = hyphens
        self.quotes = quotes
        self.ellipsis = ellipsis
        self.slashes = slashes
        self.tildes = tildes

    def normalize(self, text):
        """Run the Normalizer on a string.

        :param text: The string to normalize.
        """
        # Normalize to canonical unicode (using NFKC by default)
        if self.form is not None:
            text = unicodedata.normalize(self.form, text)

        # Strip out any control characters (they occasionally creep in somehow)
        for control in CONTROLS:
            text = text.replace(control, '')

        # Normalize unusual whitespace not caught by unicodedata
        text = text.replace('\u000b', ' ').replace('\u000c', ' ').replace(u'\u0085', ' ')
        text = text.replace('\u2028', '\n').replace('\u2029', '\n').replace('\r\n', '\n').replace('\r', '\n')

        # Normalize all hyphens, minuses and dashes to ascii hyphen-minus and remove soft hyphen entirely
        if self.hyphens:
            # TODO: Better normalization of em/en dashes to '--' if surrounded by spaces or start/end?
            for hyphen in HYPHENS | MINUSES:
                text = text.replace(hyphen, '-')
            text = text.replace('\u00ad', '')

        # Normalize all quotes and primes to ascii apostrophe and quotation mark
        if self.quotes:
            for double_quote in DOUBLE_QUOTES:
                text = text.replace(double_quote, '"')  # \u0022
            for single_quote in (SINGLE_QUOTES | APOSTROPHES | ACCENTS):
                text = text.replace(single_quote, "'")  # \u0027
            text = text.replace('′', "'")     # \u2032 prime
            text = text.replace('‵', "'")     # \u2035 reversed prime
            text = text.replace('″', "''")    # \u2033 double prime
            text = text.replace('‶', "''")    # \u2036 reversed double prime
            text = text.replace('‴', "'''")   # \u2034 triple prime
            text = text.replace('‷', "'''")   # \u2037 reversed triple prime
            text = text.replace('⁗', "''''")  # \u2057 quadruple prime

        if self.ellipsis:
            text = text.replace('…', '...').replace(' . . . ', ' ... ')  # \u2026

        if self.slashes:
            for slash in SLASHES:
                text = text.replace(slash, '/')

        if self.tildes:
            for tilde in TILDES:
                text = text.replace(tilde, '~')

        if self.strip:
            text = text.strip()

        # Collapse all whitespace down to a single space
        if self.collapse:
            text = ' '.join(text.split())
        return text

#: Default normalize that canonicalizes unicode and fixes whitespace.
normalize = Normalizer(strip=True, collapse=True, hyphens=False, quotes=False, ellipsis=False)
#: More aggressive normalize that also standardizes hyphens, and quotes.
strict_normalize = Normalizer(strip=True, collapse=True, hyphens=True, quotes=True, ellipsis=True, tildes=True)


class ExcessNormalizer(Normalizer):
    """Excessive string normalization.

    This is useful when doing fuzzy string comparisons. A common use case is to run this before calculating the
    Levenshtein distance between two strings, so that only "important" differences are counted.
    """

    def __init__(self, form='NFKC', strip=True, collapse=True, hyphens=True, quotes=True, ellipsis=True, tildes=True):
        """"""
        super(ExcessNormalizer, self).__init__(form, strip=strip, collapse=collapse, hyphens=hyphens, quotes=quotes,
                                               ellipsis=ellipsis, tildes=tildes)

    def normalize(self, text):
        # Lowercase and normalize unicode
        text = super(ExcessNormalizer, self).normalize(text.lower())
        # Remove all whitespace
        text = ''.join(text.split())
        # Convert all apostrophes, quotes, accents, primes to single ascii apostrophe
        for quote in QUOTES:
            text = text.replace(quote, "'")
        # Convert all brackets to regular parentheses
        for ob in {'(', '<', '[', '{', '&lt;'}:
            text = text.replace(ob, '(')
        for cb in {')', '>', ']', '}', '&gt;'}:
            text = text.replace(cb, '(')
        return text


excess_normalize = ExcessNormalizer(strip=True, collapse=True, hyphens=True, quotes=True, ellipsis=True, tildes=True)


class ChemNormalizer(Normalizer):
    """Normalizer that also unifies chemical spelling."""

    def __init__(self, form='NFKC', strip=True, collapse=True, hyphens=True, quotes=True, ellipsis=True, tildes=True,
                 chem_spell=True):
        """"""
        super(ChemNormalizer, self).__init__(form, strip=strip, collapse=collapse, hyphens=hyphens, quotes=quotes,
                                             ellipsis=ellipsis, tildes=tildes)
        self.chem_spell = chem_spell

    def normalize(self, text):
        """Normalize unicode, hyphens, whitespace, and some chemistry terms and formatting."""
        text = super(ChemNormalizer, self).normalize(text)
        # Normalize element spelling
        if self.chem_spell:
            text = re.sub(r'sulph', r'sulf', text, flags=re.I)
            text = re.sub(r'aluminum', r'aluminium', text, flags=re.I)
            text = re.sub(r'cesium', r'caesium', text, flags=re.I)
        return text


chem_normalize = ChemNormalizer(strip=True, collapse=True, hyphens=True, quotes=True, ellipsis=True, tildes=True,
                                chem_spell=True)

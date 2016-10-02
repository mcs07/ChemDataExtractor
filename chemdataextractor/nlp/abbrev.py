# -*- coding: utf-8 -*-
"""
chemdataextractor.nlp.abbreviations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Abbreviation detection.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import re

from ..text import bracket_level


log = logging.getLogger(__name__)


class AbbreviationDetector(object):
    """Detect abbreviation definitions in a list of tokens.

    Similar to the algorithm in Schwartz & Hearst 2003.
    """

    # TODO: Extend to Greek characters (custom method instead of .isalnum())

    #: Minimum abbreviation length
    abbr_min = 3
    #: Maximum abbreviation length
    abbr_max = 10
    #: String equivalents to use when detecting abbreviations.
    abbr_equivs = []

    def __init__(self, abbr_min=None, abbr_max=None, abbr_equivs=None):
        self.abbr_min = abbr_min if abbr_min is not None else self.abbr_min
        self.abbr_max = abbr_max if abbr_max is not None else self.abbr_max
        self.abbr_equivs = abbr_equivs if abbr_equivs is not None else self.abbr_equivs

    def _is_allowed_abbr(self, tokens):
        """Return True if text is an allowed abbreviation."""
        if len(tokens) <= 2:
            abbr_text = ''.join(tokens)
            if self.abbr_min <= len(abbr_text) <= self.abbr_max and bracket_level(abbr_text) == 0:
                if abbr_text[0].isalnum() and any(c.isalpha() for c in abbr_text):
                    # Disallow property values
                    if re.match('^\d+(\.\d+)?(g|m[lL]|cm)$', abbr_text):
                        return False
                    return True
        return False

    def _max_long_length(self, abbr):
        abbr_len = len(''.join(abbr))
        return min(abbr_len + 5, abbr_len * 2)

    def _get_candidates(self, tokens):
        candidates = []
        bracket_spans = []
        for i, t1 in enumerate(tokens):
            if t1 == '=':
                # abbr = long
                abbr_span = (i-1, i)
                abbr = tokens[abbr_span[0]:abbr_span[1]]
                if i > 0 and self._is_allowed_abbr(abbr):
                    long_span = self._get_long_span(tokens, abbr_span, start=i+1)
                    #long = self._get_long(abbr, tokens[i+1:], fix_left=True)
                    if long_span:
                        candidates.append((abbr_span, long_span))
                        #candidates.append((abbr, long))
            if t1 == '(':
                for j, t2 in enumerate(tokens[i+1:]):
                    if t2 in {')', ';', ','}:
                        bracket_spans.append((i+1, i+j+1))
                        break
        for span in bracket_spans:
            inside = tokens[span[0]:span[1]]
            if self._is_allowed_abbr(inside):
                # long ( abbr ) or ; or ,
                #long = self._get_long(inside, tokens[:span[0]-1], fix_right=True)
                long_span = self._get_long_span(tokens, span, end=span[0]-1)
                if long_span:
                    candidates.append((span, long_span))
                    #candidates.append((inside, long))
            elif tokens[span[1]] == ')':
                if span[0] - 1 > 0 and self._is_allowed_abbr([tokens[span[0]-2]]):
                    # abbr ( long )
                    #abbr = [tokens[span[0]-2]]
                    abbr_span = (span[0]-2, span[0]-1)
                    #long = self._get_long(abbr, inside, fix_left=True, fix_right=True)
                    long_span = self._get_long_span(tokens, abbr_span, start=span[0], end=span[1])
                    if long_span:
                        candidates.append((abbr_span, long_span))
            elif tokens[span[1]] == ',':
                for j, t2 in enumerate(tokens[span[1]+2:span[1]+4]):
                    if t2 == ')':
                        # ( long , abbr )
                        #abbr = tokens[span[1]+1:span[1]+2+j]
                        abbr_span = (span[1]+1, span[1]+2+j)
                        #long = self._get_long(abbr, inside, fix_left=True, fix_right=True)
                        long_span = self._get_long_span(tokens, abbr_span, start=span[0], end=span[1])
                        if long_span:
                            candidates.append((abbr_span, long_span))
                        break
        return candidates

    def _get_long_span(self, tokens, abbr_span, start=None, end=None):
        """"""
        abbr = tokens[abbr_span[0]:abbr_span[1]]
        #print(abbr)
        # Get the maximum allowed number of tokens
        max_length = self._max_long_length(abbr)
        #print(max_length)
        if start is not None and end is not None:
            if end - start <= max_length and self._is_valid_long(abbr, tokens[start:end]):
                return start, end
        elif start is None and end is not None:
            # Expand long backwards from end
            for i in range(1, min(max_length + 1, len(tokens) + 1)):
                if self._is_valid_long(abbr, tokens[end-i:end]):
                    return (end-i, end)
        elif start is not None and end is None:
            # Expand long forwards from start
            for i in range(1, min(max_length + 1, len(tokens) + 1)):
                if self._is_valid_long(abbr, tokens[start:start+i]):
                    return (start, start+i)

    def _is_valid_long(self, abbr, tokens):
        """"""

        def _is_valid(abbr, long):
            # Disallowed characters - @ typically in emails
            if '@' in long:
                return False
            l_i = len(long) - 1
            for a_i in range(len(abbr) - 1, -1, -1):
                current = abbr[a_i].lower()
                #print('current: %s' % current)
                # Ignore non-alphanumeric  # TODO: Greek!
                if not current.isalnum():
                    continue
                while (l_i >= 0 and not long[l_i].lower() == current) or (a_i == 0 and l_i > 0 and long[l_i-1].isalnum()):
                    #print('L: %s' % long[l_i])
                    l_i -= 1
                if l_i < 0:
                    #print('l_i < 0 : fail')
                    return False
                l_i -= 1
            return True

        abbr = ''.join(abbr)
        longs = {' '.join(tokens)}
        for before, after in self.abbr_equivs:
            newlongs = set()
            for long in longs:
                newlongs.add(long.replace(before, after))
            longs.update(newlongs)
        for long in longs:
            if _is_valid(abbr, long):
                return True
        return False

    def _filter_candidates(self, tokens, candidates):
        """Discard if long shorter than abbr, or if abbr token(s) are in the long token(s)."""
        results = []
        for abbr_span, long_span in candidates:
            abbr = tokens[abbr_span[0]:abbr_span[1]]
            long = tokens[long_span[0]:long_span[1]]
            if not all(a in long for a in abbr) and len(''.join(long)) > len(''.join(abbr)):
                results.append((abbr_span, long_span))
        return results

    def detect(self, tokens):
        """Return a (abbr, long) pair for each abbreviation definition."""
        results = []
        for abbr_span, long_span in self.detect_spans(tokens):
            results.append((tokens[abbr_span[0]:abbr_span[1]], tokens[long_span[0]:long_span[1]]))
        return results

    def detect_spans(self, tokens):
        """Return (abbr_span, long_span) pair for each abbreviation definition.

        abbr_span and long_span are (int, int) spans defining token ranges.
        """
        candidates = self._get_candidates(tokens)
        results = self._filter_candidates(tokens, candidates)
        return results


class ChemAbbreviationDetector(AbbreviationDetector):
    """Chemistry-aware abbreviation detector.

    This abbreviation detector has an additional list of string equivalents (e.g. Silver = Ag) that improve abbreviation
    detection on chemistry texts.
    """

    #: Minimum abbreviation length
    abbr_min = 3
    #: Maximum abbreviation length
    abbr_max = 10
    #: String equivalents to use when detecting abbreviations.
    abbr_equivs = [
        ('silver', 'Ag'),
        ('gold', 'Au'),
        ('mercury', 'Hg'),
        ('lead', 'Pb'),
        ('tin', 'Sn'),
        ('tungsten', 'W'),
        ('iron', 'Fe'),
        ('sodium', 'Na'),
        ('potassium', 'K'),
        ('copper', 'Cu'),
        ('sulfate', 'SO4'),
        ('methanol', 'MeOH'),
        ('ethanol', 'EtOH'),
        ('hydroxy', 'OH'),
        ('hexadecyltrimethylammonium bromide', 'CTAB'),
        ('cytarabine', 'Ara-C'),
        ('hydroxylated', 'OH'),
        ('hydrogen peroxide', 'H2O2'),
        ('quartz', 'SiO2'),
        ('amino', 'NH2'),
        ('amino', 'NH2'),
        ('ammonia', 'NH3'),
        ('ammonium', 'NH4'),
        ('methyl', 'CH3'),
        ('nitro', 'NO2'),
        ('potassium carbonate', 'K2CO3'),
        ('carbonate', 'CO3'),
        ('borohydride', 'BH4'),
        ('triethylamine', 'NEt3'),
        ('triethylamine', 'Et3N'),
    ]

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_nlp_ner
~~~~~~~~~~~~

Unit tests for named entity recognition.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import unittest

from chemdataextractor.nlp.tag import DictionaryTagger


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestDictionaryTagger(unittest.TestCase):

    def test_dictionary_simple(self):
        """Test the Dictionary Tagger on a simple sentence."""
        dt = DictionaryTagger(words=[['Washington'], ['Washington', ',', 'D.C.']])
        self.assertEqual(
            [('The', None),
             ('Washington', 'B-CM'),
             ('Monument', None),
             ('is', None),
             ('the', None),
             ('most', None),
             ('prominent', None),
             ('structure', None),
             ('in', None),
             ('Washington', 'B-CM'),
             (',', 'I-CM'),
             ('D.C.', 'I-CM')],
            dt.tag(['The', 'Washington', 'Monument', 'is', 'the', 'most', 'prominent', 'structure', 'in', 'Washington', ',', 'D.C.'])
        )

    def test_dictionary_simple2(self):
        """Test the Dictionary Tagger on a simple sentence."""
        dt = DictionaryTagger(words=[['Washington'], ['Washington', 'Monument'], ['Washington', ',', 'D.C.']])
        self.assertEqual(
            [('The', None),
             ('Washington', 'B-CM'),
             ('Monument', 'I-CM'),
             ('is', None),
             ('the', None),
             ('most', None),
             ('prominent', None),
             ('structure', None),
             ('in', None),
             ('Washington', 'B-CM'),
             (',', 'I-CM'),
             ('D.C.', 'I-CM')],
            dt.tag(['The', 'Washington', 'Monument', 'is', 'the', 'most', 'prominent', 'structure', 'in', 'Washington', ',', 'D.C.'])
        )

    def test_dictionary_simple3(self):
        """Test the Dictionary Tagger on a simple sentence."""
        dt = DictionaryTagger(words=[['Washington']])
        self.assertEqual(
            [('The', None),
             ('Washington', 'B-CM'),
             ('Monument', None),
             ('is', None),
             ('the', None),
             ('most', None),
             ('prominent', None),
             ('structure', None),
             ('in', None),
             ('Washington', 'B-CM'),
             (',', None),
             ('D.C.', None)],
            dt.tag(['The', 'Washington', 'Monument', 'is', 'the', 'most', 'prominent', 'structure', 'in', 'Washington', ',', 'D.C.'])
        )

    def test_dictionary_simple4(self):
        """Test the Dictionary Tagger on a simple sentence."""
        dt = DictionaryTagger(words=[['Washington'], ['Washington', 'Monument']])
        self.assertEqual(
            [('The', None),
             ('Washington', 'B-CM'),
             ('Monument', 'I-CM'),
             ('is', None),
             ('the', None),
             ('most', None),
             ('prominent', None),
             ('structure', None),
             ('in', None),
             ('Washington', 'B-CM'),
             (',', None),
             ('D.C.', None)],
            dt.tag(['The', 'Washington', 'Monument', 'is', 'the', 'most', 'prominent', 'structure', 'in', 'Washington', ',', 'D.C.'])
        )


if __name__ == '__main__':
    unittest.main()

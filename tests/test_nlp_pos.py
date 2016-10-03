#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for tagging."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import unittest

from chemdataextractor.doc.text import Text
from chemdataextractor.nlp import ApPosTagger, ChemApPosTagger


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestApPosTagger(unittest.TestCase):
    """Test the ApPosTagger that is trained on the WSJ corpus."""

    @classmethod
    def setUpClass(cls):
        cls.t = ApPosTagger()

    def test_tag_simple(self):
        """Test the PerceptronTagger on a simple sentence."""
        self.assertEqual(
            [('And', 'CC'), ('now', 'RB'), ('for', 'IN'), ('something', 'NN'), ('completely', 'RB'), ('different', 'JJ')],
            self.t.tag(['And', 'now', 'for', 'something', 'completely', 'different'])
        )

    def test_text_sentence(self):
        """Test tagging through the Text and Sentence API."""
        t = Text('And now for something completely different', pos_tagger=ApPosTagger())
        self.assertEqual(
            [[(u'And', u'CC'), (u'now', u'RB'), (u'for', u'IN'), (u'something', u'NN'), (u'completely', u'RB'), (u'different', u'JJ')]],
            t.pos_tagged_tokens
        )


class TestChemApPosTagger(unittest.TestCase):
    """Test ChemApPosTagger."""

    @classmethod
    def setUpClass(cls):
        cls.t = ChemApPosTagger()

    def test_tag_simple(self):
        """Test the ChemApPosTagger  on a simple sentence."""
        self.assertEqual(
            [('And', 'CC'), ('now', 'RB'), ('for', 'IN'), ('something', 'NN'), ('completely', 'RB'), ('different', 'JJ')],
            self.t.tag(['And', 'now', 'for', 'something', 'completely', 'different'])
        )

    def test_text_sentence(self):
        """Test tagging through the Text and Sentence API."""
        t = Text('And now for something completely different')
        self.assertEqual(
            [[(u'And', u'CC'), (u'now', u'RB'), (u'for', u'IN'), (u'something', u'NN'), (u'completely', u'RB'), (u'different', u'JJ')]],
            t.pos_tagged_tokens
        )


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_nlp_ner
~~~~~~~~~~~~

Unit tests for named entity recognition.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import unittest

from chemdataextractor.doc import Span, Document
from chemdataextractor.nlp.cem import CiDictCemTagger, CrfCemTagger, CemTagger

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestCrfCemTagger(unittest.TestCase):

    def test_false_pos(self):
        """Test the Chem CRF Tagger on a simple sentence."""
        dt = CrfCemTagger()
        self.assertEqual(
            [
                (('UV-vis', 'JJ'), 'O'),
                (('spectrum', 'NN'), 'O'),
                (('of', 'IN'), 'O'),
                (('Coumarin', 'NN'), 'B-CM'),
                (('343', 'CD'), 'O'),
                (('in', 'IN'), 'O'),
                (('THF', 'NN'), 'B-CM')
            ],
            dt.tag([
                ('UV-vis', 'JJ'),
                ('spectrum', 'NN'),
                ('of', 'IN'),
                ('Coumarin', 'NN'),
                ('343', 'CD'),
                ('in', 'IN'),
                ('THF', 'NN')
            ])
        )


class TestCemDictionaryTagger(unittest.TestCase):

        def test_unicode_combining_characters(self):
            """Test the Dictionary Tagger on unicode combining characters.

             These introduce space within normalized token text.
             """
            dt = CiDictCemTagger()
            self.assertEqual(
                [(u'Novel', None),
                 (u'imidazo\xfd1,2-a\xa8pyridine', u'B-CM'),
                 (u'and', None),
                 (u'imidazo\xfd1,2-b\xa8pyridazine', u'B-CM'),
                 (u'derivatives', None)],
                dt.tag(['Novel', 'imidazo\xfd1,2-a\xa8pyridine', 'and', 'imidazo\xfd1,2-b\xa8pyridazine', 'derivatives'])
            )


class TestCemTagger(unittest.TestCase):
    """Test combined CemTagger."""

    def test_stoplist(self):
        """Test CemTagger removes words in stoplist, including words entirely made up of ignore prefix/suffix.

        GitHub issue #12.
        """
        ct = CemTagger()
        self.assertEqual([(('benzene-aromatic', 'NN'), 'B-CM')], ct.tag([('benzene-aromatic', 'NN')]))
        self.assertEqual([(('-aromatic', 'JJ'), None)], ct.tag([('-aromatic', 'JJ')]))
        self.assertEqual([(('non-aromatic', 'JJ'), None)], ct.tag([('non-aromatic', 'JJ')]))

    def test_cems_stoplist(self):
        """Test Document cems removes words in stoplist, ncluding words entirely made up of ignore prefix/suffix.

        GitHub issue #12.
        """
        self.assertEqual([Span('benzene', 0, 7)], Document('benzene-aromatic').cems)
        self.assertEqual([], Document('-aromatic').cems)
        self.assertEqual([], Document('non-aromatic').cems)


# TODO: Test entity recognition on a sentence containing a generic abbreviation that is only picked up through its definition


if __name__ == '__main__':
    unittest.main()

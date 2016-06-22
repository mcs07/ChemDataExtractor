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

from chemdataextractor.nlp.cem import CiDictCemTagger, CrfCemTagger


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


# TODO: Test entity recognition on a sentence containing a generic abbreviation that is only picked up through its definition


if __name__ == '__main__':
    unittest.main()

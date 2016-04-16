# -*- coding: utf-8 -*-
"""
test_parse_cem
~~~~~~~~~~~~~~



:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import unittest
from lxml import etree

from chemdataextractor.doc.text import Sentence
from chemdataextractor.parse.cem import cem_phrase

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('cde').setLevel(logging.DEBUG)
log = logging.getLogger(__name__)


class TestParseCem(unittest.TestCase):

    maxDiff = None

    def do_parse(self, input, expected):
        s = Sentence(input)
        log.debug(s)
        log.debug(s.tagged_tokens)
        results = []
        for i, r in enumerate(cem_phrase.scan(s.tagged_tokens)):
            log.debug(etree.tostring(r[0], pretty_print=True, encoding='unicode'))
            results.append(etree.tostring(r[0], encoding='unicode'))
        self.assertEqual(expected, results)

    def test_simple(self):
        s = 'Such as 2,4,6-trinitrotoluene with acetone.'
        expected = [
            '<cem_phrase><cem><name>2,4,6-trinitrotoluene</name></cem></cem_phrase>',
            '<cem_phrase><cem><name>acetone</name></cem></cem_phrase>'
        ]
        self.do_parse(s, expected)

    def test_without_tags(self):
        """Test on input where the CEM tagger has missed some obvious chemical entities."""
        tagged_tokens = [(u'A', u'DT'), (u'sample', u'NN'), (u'of', u'IN'), (u'aspartic', u'NN'), (u'acid', u'NN'), (u'with', u'IN'), (u'Ala-Arg-Val', u'NN'), (u'.', u'.')]
        expected = [
            '<cem_phrase><cem><name>aspartic acid</name></cem></cem_phrase>',
            '<cem_phrase><cem><name>Ala-Arg-Val</name></cem></cem_phrase>'
        ]
        results = []
        for i, r in enumerate(cem_phrase.scan(tagged_tokens)):
            log.debug(etree.tostring(r[0], pretty_print=True, encoding='unicode'))
            results.append(etree.tostring(r[0], encoding='unicode'))
        self.assertEqual(expected, results)

    def test_no_doi(self):
        s = 'DOI: 10.1039/C5TC02077H (Paper) J. Mater. Chem. C, 2015, 3, 10177-10187'
        expected = []
        self.do_parse(s, expected)

    def test_no_issn(self):
        s = '1234-567X'
        expected = []
        self.do_parse(s, expected)

    def test_no_email(self):
        s = 'a.test.account@gmail.com'
        expected = []
        self.do_parse(s, expected)


if __name__ == '__main__':
    unittest.main()

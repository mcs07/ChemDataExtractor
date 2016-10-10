# -*- coding: utf-8 -*-
"""
test_parse_apparatus
~~~~~~~~~~~~~~~~~~~~



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

from chemdataextractor.doc.text import Sentence, Paragraph
from chemdataextractor.parse.context import context_phrase


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestParseApparatus(unittest.TestCase):
    """Simple apparatus parse tests."""

    maxDiff = None

    def do_parse(self, input, expected):
        s = Sentence(input)
        log.debug(s)
        log.debug(s.tagged_tokens)
        results = []
        for i, r in enumerate(context_phrase.scan(s.tagged_tokens)):
            log.debug(etree.tostring(r[0], pretty_print=True, encoding='unicode'))
            results.append(etree.tostring(r[0], encoding='unicode'))
        self.assertEqual(expected, results)

    def test_apparatus(self):
        """"""

        s = 'The photoluminescence quantum yield (PLQY) was measured using a HORIBA Jobin Yvon FluoroMax-4 spectrofluorimeter'
        expected = ['<context_phrase><measurement><quantum_yield>photoluminescence quantum yield PLQY</quantum_yield></measurement><apparatus>HORIBA Jobin Yvon FluoroMax-4 spectrofluorimeter</apparatus></context_phrase>']
        self.do_parse(s, expected)

    def test_apparatus2(self):
        """"""
        s = '1H NMR spectra were recorded on a Varian MR-400 MHz instrument.'
        expected = ['<context_phrase><measurement><nmr>1H</nmr></measurement><apparatus>Varian MR-400 MHz instrument</apparatus></context_phrase>']
        self.do_parse(s, expected)

    def test_apparatus_record(self):
        """"""
        p = Paragraph('The photoluminescence quantum yield (PLQY) was measured using a HORIBA Jobin Yvon FluoroMax-4 spectrofluorimeter.')
        expected = [{'quantum_yields': [{'apparatus': u'HORIBA Jobin Yvon FluoroMax-4 spectrofluorimeter'}]}]
        self.assertEqual(expected, [r.serialize() for r in p.records])

    def test_apparatus_record2(self):
        """"""
        p = Paragraph('NMR was run on a 400 MHz Varian NMR.')
        expected = [{'nmr_spectra': [{'apparatus': '400 MHz Varian NMR'}]}]
        self.assertEqual(expected, [r.serialize() for r in p.records])


if __name__ == '__main__':
    unittest.main()

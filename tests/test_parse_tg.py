# -*- coding: utf-8 -*-
"""
test_parse_tg
~~~~~~~~~~~~~

Test glass transition parser.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import unittest

from lxml import etree

from chemdataextractor.doc.text import Sentence
from chemdataextractor.parse.tg import tg_phrase


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestParseTg(unittest.TestCase):

    maxDiff = None

    def do_parse(self, input, expected):
        s = Sentence(input)
        log.debug(s)
        log.debug(s.tagged_tokens)
        result = next(tg_phrase.scan(s.tagged_tokens))[0]
        log.debug(etree.tostring(result, pretty_print=True, encoding='unicode'))
        self.assertEqual(expected, etree.tostring(result, encoding='unicode'))

    # Test: "glass transition temperature of"
    def test_tg1(self):
        s = 'The poly(azide) shows a glass transition temperature of 282.6 °C.'
        expected = '<tg_phrase><tg><value>282.6</value><units>°C</units></tg></tg_phrase>'
        self.do_parse(s, expected)
    
    # Test: "glass transition temp. of with temperature withing '()'"
    def test_tg2(self):
        s = 'Differential scanning calorimetry revealed a glass transition temp. of (-19) ° for the homopolymer and 20° for the copolymer.'
        expected = '<tg_phrase><tg><value>-19</value><units>°</units></tg></tg_phrase>'
        self.do_parse(s, expected)

    # Test: "Tg of "
    def test_tg3(self):
        s = 'Polymandelide is a glassy amorphous polymer with a Tg of 100 °C, with rheol.'
        expected = '<tg_phrase><tg><value>100</value><units>°C</units></tg></tg_phrase>'
        self.do_parse(s, expected)

    # Test: "Tg of ca. (or Tg of about)"
    def test_tg4(self):
        s = 'It has been found that PSHQ4 has a Tg of ca. 130°'
        expected = '<tg_phrase><tg><value>130</value><units>°</units></tg></tg_phrase>'
        self.do_parse(s, expected)

    # Test: (Tg) of
    def test_tg5(self):
        s = 'The resulting poly(AdS) had predicted mol. wts., narrow mol. wt. distributions, and high glass transition temp. (Tg) around 232 °C.'
        expected = '<tg_phrase><tg><NN>Tg</NN><value>232</value><units>\xb0C</units></tg></tg_phrase>'
        self.do_parse(s, expected)

    # Test ommitting "transition"
    def test_tg6(self):
        s = 'One phase had a glass temp. of ∼-30°, corresponding to the amorphous ethylene segments.'
        expected = '<tg_phrase><tg><value>∼-30</value><units>°</units></tg></tg_phrase>'
        self.do_parse(s, expected)

    # Test Tg: (or Tg >) 
    def test_tg7(self):
        s = 'The four-armed compd. (ANTH-OXA6t-OC12) with the dodecyloxy surface group is a high glass transition temp. (Tg:  211°) material and exhibits good soly.'
        #s = 'The four-armed compd. (ANTH-OXA6t-OC12) with the dodecyloxy surface group is a high glass transition temp. (Tg > 211°) material and exhibits good soly.'
        expected = '<tg_phrase><tg><value>211</value><units>°</units></tg></tg_phrase>'
        #expected = '<tg_phrase><tg><value>&gt;211</value><units>°</units></tg></tg_phrase>'
        self.do_parse(s, expected)

    def test_tg8(self):
        s= 'DSC experiments revealed that PGFDTDPP has a high glass-transition temperature at 150 °C compared with 90 °C for PGFDTDPP.'
        expected = '<tg_phrase><tg><value>150</value><units>\xb0C</units></tg></tg_phrase>'
        self.do_parse(s, expected)


if __name__ == '__main__':
    unittest.main()

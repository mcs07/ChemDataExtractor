# -*- coding: utf-8 -*-
"""
test_parse_mp
~~~~~~~~~~~~~

Test melting point parser

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
from chemdataextractor.parse.mp import mp


logging.basicConfig(level=logging.DEBUG)
logging.getLogger('cde').setLevel(logging.DEBUG)
log = logging.getLogger(__name__)


class TestParseNmr(unittest.TestCase):

    maxDiff = None

    def do_parse(self, input, expected):
        s = Sentence(input)
        log.debug(s)
        log.debug(s.tagged_tokens)
        result = mp.scan(s.tagged_tokens).next()[0]
        log.debug(etree.tostring(result, pretty_print=True, encoding='unicode'))
        self.assertEqual(expected, etree.tostring(result, encoding='unicode'))

    def test_mp1(self):
        s = 'Colorless solid (81% yield, 74.8 mg, 0.22 mmol); mp 77.2–77.5 °C.'
        expected = '<mp><value>77.2–77.5</value><units>°C</units></mp>'
        self.do_parse(s, expected)

    def test_mp2(self):
        s = 'Mp > 280 °C.'
        expected = '<mp><value>&gt;280</value><units>°C</units></mp>'
        self.do_parse(s, expected)

    def test_mp3(self):
        s = 'Mp: 105-110 °C'
        expected = '<mp><value>105-110</value><units>°C</units></mp>'
        self.do_parse(s, expected)



if __name__ == '__main__':
    unittest.main()

# -*- coding: utf-8 -*-
"""
test_parse_ir
~~~~~~~~~~~~~



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
from chemdataextractor.parse.ir import ir, IrParser

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestParseIr(unittest.TestCase):

    maxDiff = None

    def do_parse(self, input, expected):
        s = Sentence(input)
        log.debug(s)
        log.debug(s.tagged_tokens)
        result = next(ir.scan(s.tagged_tokens))[0]
        log.debug(etree.tostring(result, pretty_print=True, encoding='unicode'))
        self.assertEqual(expected, etree.tostring(result, encoding='unicode'))
        for c in IrParser().parse(s.tagged_tokens):
            print(c.serialize())

    def test_ir1(self):
        s = 'IR (ATR): ṽ [cm−1] 3024 (w), 2980 (w), 2918 (w), 1601 (w), 1485 (m), 1460 (m), 1438 (w), 1358 (w), ' \
            '1290 (w), 1188 (w), 1115 (w), 1002 (m), 954 (m), 912 (w), 853 (m), 814 (s), 793 (s), 762 (s), 739 (m), ' \
            '687 (s), 671 (m).'
        expected = '<ir><type>IR</type><solvent>ATR</solvent><units>[cm\u22121]</units><peaks><peak><value>3024</value><strength>w</strength></peak><peak><value>2980</value><strength>w</strength></peak><peak><value>2918</value><strength>w</strength></peak><peak><value>1601</value><strength>w</strength></peak><peak><value>1485</value><strength>m</strength></peak><peak><value>1460</value><strength>m</strength></peak><peak><value>1438</value><strength>w</strength></peak><peak><value>1358</value><strength>w</strength></peak><peak><value>1290</value><strength>w</strength></peak><peak><value>1188</value><strength>w</strength></peak><peak><value>1115</value><strength>w</strength></peak><peak><value>1002</value><strength>m</strength></peak><peak><value>954</value><strength>m</strength></peak><peak><value>912</value><strength>w</strength></peak><peak><value>853</value><strength>m</strength></peak><peak><value>814</value><strength>s</strength></peak><peak><value>793</value><strength>s</strength></peak><peak><value>762</value><strength>s</strength></peak><peak><value>739</value><strength>m</strength></peak><peak><value>687</value><strength>s</strength></peak><peak><value>671</value><strength>m</strength></peak></peaks></ir>'
        self.do_parse(s, expected)

    def test_ir2(self):
        s = 'IR (KBr/cm–1): 4321, 2222, 1734, 1300, 1049, 777, 620.'
        expected = '<ir><type>IR</type><solvent>KBr</solvent><units>cm\u20131</units><peaks><peak><value>4321</value></peak><peak><value>2222</value></peak><peak><value>1734</value></peak><peak><value>1300</value></peak><peak><value>1049</value></peak><peak><value>777</value></peak><peak><value>620</value></peak></peaks></ir>'
        self.do_parse(s, expected)

    def test_ir3(self):
        s = 'FTIR (KBr): ν/cm‒1 3315, 3002, 1630, 1593 (νCH=N), 1251;'
        expected = '<ir><type>FTIR</type><solvent>KBr</solvent><units>cm\u20121</units><peaks><peak><value>3315</value></peak><peak><value>3002</value></peak><peak><value>1630</value></peak><peak><value>1593</value><bond>\u03bdCH = N</bond></peak><peak><value>1251</value></peak></peaks></ir>'
        self.do_parse(s, expected)

    def test_ir4(self):
        s = 'IR-ATR:  3380, 3190,  2973, 2873, 1669, 1646, 1602, 1495, 1178, 828 cm-1.'
        expected = '<ir><type>IR-ATR</type><peaks><peak><value>3380</value></peak><peak><value>3190</value></peak><peak><value>2973</value></peak><peak><value>2873</value></peak><peak><value>1669</value></peak><peak><value>1646</value></peak><peak><value>1602</value></peak><peak><value>1495</value></peak><peak><value>1178</value></peak><peak><value>828</value></peak></peaks><units>cm-1</units></ir>'
        self.do_parse(s, expected)


if __name__ == '__main__':
    unittest.main()

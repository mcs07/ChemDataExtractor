# -*- coding: utf-8 -*-
"""
test_parse_uvvis
~~~~~~~~~~~~~~~~



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
from chemdataextractor.parse.uvvis import uvvis, UvvisParser


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestParseUvvis(unittest.TestCase):

    maxDiff = None

    def do_parse(self, input, expected):
        s = Sentence(input)
        log.debug(s)
        log.debug(s.tagged_tokens)
        result = next(uvvis.scan(s.tagged_tokens))[0]
        log.debug(etree.tostring(result, pretty_print=True, encoding='unicode'))
        self.assertEqual(expected, etree.tostring(result, encoding='unicode'))
        for c in UvvisParser().parse(s.tagged_tokens):
            print(c.serialize())

    def test_uvvis1(self):
        s = 'λabs/nm 320, 380, 475, 529;'
        expected = '<uvvis><units>nm</units><peaks><peak><value>320</value></peak><peak><value>380</value></peak><peak><value>475</value></peak><peak><value>529</value></peak></peaks></uvvis>'
        self.do_parse(s, expected)


if __name__ == '__main__':
    unittest.main()

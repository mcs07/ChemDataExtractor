# -*- coding: utf-8 -*-
"""
test_parse_doi
~~~~~~~~~~~~~~

Test DOI parser.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import unittest

from lxml import etree

from chemdataextractor.doc.text import Sentence
from chemdataextractor.parse.doi import doi

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestParseDOI(unittest.TestCase):
    maxDiff = None

    def do_parse(self, input, expected):
        s = Sentence(input)
        log.debug(s)
        log.debug(s.tagged_tokens)
        result = next(doi.scan(s.tagged_tokens))[0]
        log.debug(etree.tostring(result, pretty_print=True, encoding='unicode'))
        self.assertEqual(expected, etree.tostring(result, encoding='unicode'))

    def test_doi1(self):
        tests = [
            'DOI:10.1021/jo101758t',
            'doi:10.3390/molecules201219848\n hello world',
            'Molecules 2015, 20(12), 22272-22285; doi:10.3390/molecules201219846'
        ]
        values = [
            '<doi>10.1021/jo101758t</doi>',
            '<doi>10.3390/molecules201219848</doi>',
            '<doi>10.3390/molecules201219846</doi>'
        ]
        for test, expected in zip(tests, values):
            self.do_parse(test, expected)

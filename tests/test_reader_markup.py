# -*- coding: utf-8 -*-
"""
test_reader_markup
~~~~~~~~~~~~~~~~~~

Test XML/HTML reader.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import unittest

from chemdataextractor.doc import Paragraph
from chemdataextractor.reader import HtmlReader


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestReaderHtml(unittest.TestCase):

    maxDiff = None

    def test_paragraphs(self):
        """Test paragraphs are correctly split."""
        r = HtmlReader()
        d = r.parse('<p>First para</p><p>Second Para</p>')
        self.assertEqual(len(d.elements), 2)
        self.assertEqual(d.elements[0].text, 'First para')
        self.assertEqual(d.elements[1].text, 'Second Para')
        for el in d.elements:
            self.assertIsInstance(el, Paragraph)

    def test_paragraphs2(self):
        """Test paragraphs are correctly split with no closing element."""
        r = HtmlReader()
        d = r.parse('<p>First para<p>Second Para')
        self.assertEqual(len(d.elements), 2)
        self.assertEqual(d.elements[0].text, 'First para')
        self.assertEqual(d.elements[1].text, 'Second Para')
        for el in d.elements:
            self.assertIsInstance(el, Paragraph)

    def test_linebreak(self):
        """Test br splits paragraph."""
        r = HtmlReader()
        d = r.parse('First line<br/>Second line')
        self.assertEqual(len(d.elements), 2)
        self.assertEqual(d.elements[0].text, 'First line')
        self.assertEqual(d.elements[1].text, 'Second line')
        for el in d.elements:
            self.assertIsInstance(el, Paragraph)

    def test_linebreak2(self):
        """Test br splits paragraph."""
        r = HtmlReader()
        d = r.parse('<span>First line</span><br/><span>Second line</span>')
        self.assertEqual(len(d.elements), 2)
        self.assertEqual(d.elements[0].text, 'First line')
        self.assertEqual(d.elements[1].text, 'Second line')
        for el in d.elements:
            self.assertIsInstance(el, Paragraph)


if __name__ == '__main__':
    unittest.main()

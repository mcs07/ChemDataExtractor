# -*- coding: utf-8 -*-
"""
test_reader_uspto
~~~~~~~~~~~~~~~~~

Test reading USPTO XML files.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import unittest

from chemdataextractor.doc import Table
from chemdataextractor.reader import UsptoXmlReader
from chemdataextractor import Document

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestReaderUspto(unittest.TestCase):

    maxDiff = None

    def test_reader_explicit(self):
        """"""
        with open('data/US07314849-20080101.XML') as f:
            doc = UsptoXmlReader().read(f)
            self.assertEqual(len(doc.elements), 606)

    def test_uspto1(self):
        """"""
        with open('data/US07314849-20080101.XML') as f:
            doc = Document.from_file(f)
            self.assertEqual(len(doc.elements), 606)

    def test_uspto2(self):
        """"""
        with open('data/US07470803-20081230.XML') as f:
            doc = Document.from_file(f)
            self.assertEqual(len(doc.elements), 130)

        # doc = Document.from_file(f)
        # for element in doc:
        #     print(repr(element))
        #     if isinstance(element, Table):
        #         for hrow in element.headings:
        #             print(hrow)
        #         print('=========')
        #         for row in element.rows:
        #             print(row)
        #         for footnote in element.footnotes:
        #             print(repr(footnote))


if __name__ == '__main__':
    unittest.main()

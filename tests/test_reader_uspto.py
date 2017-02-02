# -*- coding: utf-8 -*-
"""
test_reader_uspto
~~~~~~~~~~~~~~~~~

Test USPTO reader.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import io
import logging
import os
import unittest

from chemdataextractor import Document
from chemdataextractor.reader import UsptoXmlReader


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestUsptoReader(unittest.TestCase):

    maxDiff = None

    def test_detect(self):
        """Test UsptoXmlReader can detect a USPTO XML document."""
        r = UsptoXmlReader()
        fname = 'US06840965B2.xml'
        f = io.open(os.path.join(os.path.dirname(__file__), 'data', 'uspto', fname), 'rb')
        content = f.read()
        self.assertEqual(r.detect(content, fname=fname), True)

    def test_direct_usage(self):
        """Test UsptoXmlReader used directly to parse file."""
        r = UsptoXmlReader()
        fname = 'US06840965B2.xml'
        f = io.open(os.path.join(os.path.dirname(__file__), 'data', 'uspto', fname), 'rb')
        content = f.read()
        d = r.readstring(content)
        self.assertEqual(len(d.elements), 112)

    def test_document_usage(self):
        """Test UsptoXmlReader used via Document.from_file."""
        fname = 'US06840965B2.xml'
        f = io.open(os.path.join(os.path.dirname(__file__), 'data', 'uspto', fname), 'rb')
        d = Document.from_file(f, readers=[UsptoXmlReader()])
        self.assertEqual(len(d.elements), 112)


if __name__ == '__main__':
    unittest.main()

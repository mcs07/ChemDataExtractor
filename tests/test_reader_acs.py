# -*- coding: utf-8 -*-
"""
test_reader_acs
~~~~~~~~~~~~~~~

Test ACS reader.

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
from chemdataextractor.reader import AcsHtmlReader


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestAcsHtmlReader(unittest.TestCase):

    maxDiff = None

    def test_detect(self):
        """Test AcsHtmlReader can detect an ACS document."""
        r = AcsHtmlReader()
        fname = 'acs.jmedchem.6b00723.html'
        f = io.open(os.path.join(os.path.dirname(__file__), 'data', 'acs', fname), 'rb')
        content = f.read()
        self.assertEqual(r.detect(content, fname=fname), True)

    def test_direct_usage(self):
        """Test AcsHtmlReader used directly to parse file."""
        r = AcsHtmlReader()
        fname = 'acs.jmedchem.6b00723.html'
        f = io.open(os.path.join(os.path.dirname(__file__), 'data', 'acs', fname), 'rb')
        content = f.read()
        d = r.readstring(content)
        self.assertEqual(len(d.elements), 198)

    def test_document_usage(self):
        """Test AcsHtmlReader used via Document.from_file."""
        fname = 'acs.jmedchem.6b00723.html'
        f = io.open(os.path.join(os.path.dirname(__file__), 'data', 'acs', fname), 'rb')
        d = Document.from_file(f, readers=[AcsHtmlReader()])
        self.assertEqual(len(d.elements), 198)


if __name__ == '__main__':
    unittest.main()

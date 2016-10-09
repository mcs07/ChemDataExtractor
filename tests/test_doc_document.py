# -*- coding: utf-8 -*-
"""
test_doc_document
~~~~~~~~~~~~~~~~~

Test the Document class.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import unittest

from chemdataextractor.doc.document import Document

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestDocument(unittest.TestCase):
    """Simple Document instantiation tests."""

    def test_text_elements(self):
        """Test Document can be instantiated with a list of strings."""
        els = [
            'A first paragraph. With two sentences.',
            'A second paragraph.',
            'A third paragraph.'
        ]
        d = Document(*els)
        self.assertEqual(d.elements[0].text, 'A first paragraph. With two sentences.')
        self.assertEqual(d.elements[0].sentences[1].text, 'With two sentences.')
        self.assertEqual(d.elements[1].document, d)

    def test_bytestring_elements(self):
        """Test Document can be instantiated with a list of bytestrings."""
        els = [
            'A first paragraph. With two sentences.'.encode('ascii'),
            'A second paragraph. \u00a9'.encode('utf-8'),
            'A third paragraph (\u00b6).'.encode('windows-1252'),
        ]
        d = Document(*els)
        self.assertEqual(d.elements[0].text, 'A first paragraph. With two sentences.')
        self.assertEqual(d.elements[0].sentences[1].text, 'With two sentences.')
        self.assertEqual(d.elements[1].document, d)

    def test_document_iter(self):
        """Test Document can be iterated like a list to access its elements."""
        els = [
            'A first paragraph. With two sentences.',
            'A second paragraph.',
            'A third paragraph.'
        ]
        d = Document(*els)
        self.assertEqual(len(d), 3)
        self.assertEqual(d[2].text, 'A third paragraph.')
        self.assertEqual([e.text for e in d], els)


if __name__ == '__main__':
    unittest.main()

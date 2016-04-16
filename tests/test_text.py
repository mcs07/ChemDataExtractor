# -*- coding: utf-8 -*-
"""
test_text
~~~~~~~~~

Test the text package.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import unittest

from chemdataextractor.text.latex import latex_to_unicode
from chemdataextractor.text.normalize import normalize
from chemdataextractor.text.processors import extract_emails


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestNormalization(unittest.TestCase):

    def test_normalize(self):
        """Test normalize function."""
        # Weird control characters
        self.assertEqual(u'The quick brown fox jumped', normalize(u'The\u0003 quick br\u0005own fo\u0008x jumped'))
        # Unusual whitespace characters
        self.assertEqual(u'The quick brown fox jumped', normalize(u'The\u00A0quick\u2000brown\u2008fox\u000Bjumped'))
        # u2024 instead of full stop
        self.assertEqual(u'www.bbc.co.uk', normalize(u'www\u2024bbc\u2024co\u2024uk'))


class TestLaTeX(unittest.TestCase):

    def test_latex_to_unicode_names(self):
        self.assertEqual(u'Bernd van Linder', latex_to_unicode('Bernd {van Linder}', capitalize='name'))
        self.assertEqual(u'Bernd van Linder', latex_to_unicode('Bernd van Linder', capitalize='name'))
        self.assertEqual(u'John-Jules Ch. Meyer', latex_to_unicode('{John-Jules Ch.} meyer', capitalize='name'))
        self.assertEqual(u'Eijkhof, Frank van den', latex_to_unicode('eijkhof, frank {v}an {d}en', capitalize='name'))
        self.assertEqual(u'Feng, Wen-Mei Hwu', latex_to_unicode('Feng, Wen-mei Hwu', capitalize='name'))
        self.assertEqual(u'Feng, Wen-mei Hwu', latex_to_unicode('Feng, Wen{-mei} Hwu', capitalize='name'))
        self.assertEqual(u'McCartney, Paul', latex_to_unicode('McCartney, Paul', capitalize='name'))
        self.assertEqual(u'Leo MacGarry', latex_to_unicode('Leo MacGarry', capitalize='name'))
        self.assertEqual(u'Patrick O\'Mahoney', latex_to_unicode('Patrick O\'Mahoney', capitalize='name'))
        self.assertEqual(u'O\'Boyle, Jim', latex_to_unicode('O\'Boyle, Jim', capitalize='name'))

    def test_latex_to_unicode_titles(self):
        self.assertEqual(u'A guide for ChemDataExtractor', latex_to_unicode('A Guide For {ChemDataExtractor}', capitalize='sentence'))
        self.assertEqual(u'A Guide for ChemDataExtractor', latex_to_unicode('A Guide For {ChemDataExtractor}', capitalize='title'))
        self.assertEqual(u'A Guide for ChemDataExtractor', latex_to_unicode('A Guide For {ChemDataExtractor}', capitalize='title'))

    def test_latex_to_unicode_math(self):
        self.assertEqual(u'[g,f]-colorings of Partial k-trees',
                         latex_to_unicode('$[g,f]$-colorings of Partial $k$-trees', capitalize='title'))
        self.assertEqual(u'On K_3,3-free or K_5-free Graphs',
                         latex_to_unicode('On {$K_{3,3}$}-free or {$K_5$}-free graphs', capitalize='title'))
        self.assertEqual(u'Clique-width \u22643 Graphs',
                         latex_to_unicode('clique-width $\\leq 3$ graphs', capitalize='title'))
        self.assertEqual(u'An O(n^2.5) Algorithm',
                         latex_to_unicode('An {O}($n^{2.5}$) Algorithm', capitalize='title'))
        self.assertEqual(u'An n \xd7 N Board',
                         latex_to_unicode('an $n \\times n$ board', capitalize='title'))
        self.assertEqual(u'Of k-trees Is O(k)',
                         latex_to_unicode('of \\mbox{$k$-trees} is {$O(k)$}', capitalize='title'))


class TestExtraction(unittest.TestCase):

    def test_extract_emails(self):
        """Test extract_urls function."""
        self.assertEqual([u'matt+test@example.com', u'test%what@example.com'],
                         extract_emails('Send to <matt+test@example.com> or <test%what@example.com>'))
        self.assertEqual([u'example@example.com'],
                         extract_emails('The email is example@example.com.'))
        self.assertEqual([u'matt@server.department.company.ac.uk'],
                         extract_emails('What about <matt@server.department.company.ac.uk>?'))
        self.assertEqual([],
                         extract_emails('Invalid - matt@me...com, hithere@ex*ample.com'))


if __name__ == '__main__':
    unittest.main()

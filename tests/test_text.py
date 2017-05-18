# -*- coding: utf-8 -*-
"""
test_text
~~~~~~~~~

Test the text package.

"""





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
        self.assertEqual('The quick brown fox jumped', normalize('The\u0003 quick br\u0005own fo\u0008x jumped'))
        # Unusual whitespace characters
        self.assertEqual('The quick brown fox jumped', normalize('The\u00A0quick\u2000brown\u2008fox\u000Bjumped'))
        # u2024 instead of full stop
        self.assertEqual('www.bbc.co.uk', normalize('www\u2024bbc\u2024co\u2024uk'))


class TestLaTeX(unittest.TestCase):

    def test_latex_to_unicode_names(self):
        self.assertEqual('Bernd van Linder', latex_to_unicode('Bernd {van Linder}', capitalize='name'))
        self.assertEqual('Bernd van Linder', latex_to_unicode('Bernd van Linder', capitalize='name'))
        self.assertEqual('John-Jules Ch. Meyer', latex_to_unicode('{John-Jules Ch.} meyer', capitalize='name'))
        self.assertEqual('Eijkhof, Frank van den', latex_to_unicode('eijkhof, frank {v}an {d}en', capitalize='name'))
        self.assertEqual('Feng, Wen-Mei Hwu', latex_to_unicode('Feng, Wen-mei Hwu', capitalize='name'))
        self.assertEqual('Feng, Wen-mei Hwu', latex_to_unicode('Feng, Wen{-mei} Hwu', capitalize='name'))
        self.assertEqual('McCartney, Paul', latex_to_unicode('McCartney, Paul', capitalize='name'))
        self.assertEqual('Leo MacGarry', latex_to_unicode('Leo MacGarry', capitalize='name'))
        self.assertEqual('Patrick O\'Mahoney', latex_to_unicode('Patrick O\'Mahoney', capitalize='name'))
        self.assertEqual('O\'Boyle, Jim', latex_to_unicode('O\'Boyle, Jim', capitalize='name'))

    def test_latex_to_unicode_titles(self):
        self.assertEqual('A guide for ChemDataExtractor', latex_to_unicode('A Guide For {ChemDataExtractor}', capitalize='sentence'))
        self.assertEqual('A Guide for ChemDataExtractor', latex_to_unicode('A Guide For {ChemDataExtractor}', capitalize='title'))
        self.assertEqual('A Guide for ChemDataExtractor', latex_to_unicode('A Guide For {ChemDataExtractor}', capitalize='title'))

    def test_latex_to_unicode_math(self):
        self.assertEqual('[g,f]-colorings of Partial k-trees',
                         latex_to_unicode('$[g,f]$-colorings of Partial $k$-trees', capitalize='title'))
        self.assertEqual('On K_3,3-free or K_5-free Graphs',
                         latex_to_unicode('On {$K_{3,3}$}-free or {$K_5$}-free graphs', capitalize='title'))
        self.assertEqual('Clique-width \u22643 Graphs',
                         latex_to_unicode('clique-width $\\leq 3$ graphs', capitalize='title'))
        self.assertEqual('An O(n^2.5) Algorithm',
                         latex_to_unicode('An {O}($n^{2.5}$) Algorithm', capitalize='title'))
        self.assertEqual('An n \xd7 N Board',
                         latex_to_unicode('an $n \\times n$ board', capitalize='title'))
        self.assertEqual('Of k-trees Is O(k)',
                         latex_to_unicode('of \\mbox{$k$-trees} is {$O(k)$}', capitalize='title'))


class TestExtraction(unittest.TestCase):

    def test_extract_emails(self):
        """Test extract_urls function."""
        self.assertEqual(['matt+test@example.com', 'test%what@example.com'],
                         extract_emails('Send to <matt+test@example.com> or <test%what@example.com>'))
        self.assertEqual(['example@example.com'],
                         extract_emails('The email is example@example.com.'))
        self.assertEqual(['matt@server.department.company.ac.uk'],
                         extract_emails('What about <matt@server.department.company.ac.uk>?'))
        self.assertEqual([],
                         extract_emails('Invalid - matt@me...com, hithere@ex*ample.com'))


if __name__ == '__main__':
    unittest.main()

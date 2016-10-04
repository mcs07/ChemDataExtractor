# -*- coding: utf-8 -*-
"""
test_scrape_clean
~~~~~~~~~~~~~~~~~

Test the HTML/XML Cleaner.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import unittest

from lxml.etree import tostring
from lxml import html

from chemdataextractor.scrape.clean import Cleaner, clean, strip, strip_markup, strip_html


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


# Input HTML
HTML1 = '''
<html>
  <body>
    <!-- A comment at the start of the document -->
    <div><h1>Heading</h1></div>
    <div><a href="page">Link</a></div>
    <div><div>Nested</div></div>
  </body>
</html>
'''
HTML2 = '<html><head><title>title</title></head><body>Start body<!-- A comment --><script>alert(\'test\');</script><p>This i<span>s</span>s a <strong>test</strong>.Test <a href="link">link</a></body></html>'
HTML3 = '<div><p>First<p>Second<p>Third<p>Fourth<p>Fifth<p>Sixth</div>'
HTML4 = '<p>Here is a text para with some <em>inline</em> markup, like <strong>this</strong>. Also a <a href="#thing">link</a></p>'

# Results from stripping HTML
STRIP1 = '<html>\nHeading\nLink\nNested\n</html>'
STRIP2 = '<html>\ntitle\nStart body\nThis iss a test.Test link\n</html>'
STRIP3 = '<div>\nFirst\nSecond\nThird\nFourth\nFifth\nSixth\n</div>'
STRIP4 = '<p>Here is a text para with some inline markup, like this. Also a link</p>'

# Results from stripping HTML and leaving whitespace to match input
STRIPWS1 = '<html>\n  \n    \n    Heading\n    Link\n    Nested\n  \n</html>'
STRIPWS2 = '<html>titleStart bodyThis iss a test.Test link</html>'
STRIPWS3 = '<div>FirstSecondThirdFourthFifthSixth</div>'
STRIPWS4 = '<p>Here is a text para with some inline markup, like this. Also a link</p>'

# Results of cleaning HTML
CLEAN1 = '<html>\n<body>\n<div>\n<h1>Heading</h1>\n</div>\n<div><a href="page">Link</a></div>\n<div>\n<div>Nested</div>\n</div>\n</body>\n</html>'
CLEAN2 = '<html>\n<head>\n<title>title</title>\n</head>\n<body>Start body\n<p>This i<span>s</span>s a <strong>test</strong>.Test <a href="link">link</a></p>\n</body>\n</html>'
CLEAN3 = '<div>\n<p>First</p>\n<p>Second</p>\n<p>Third</p>\n<p>Fourth</p>\n<p>Fifth</p>\n<p>Sixth</p>\n</div>'
CLEAN4 = '<p>Here is a text para with some <em>inline</em> markup, like <strong>this</strong>. Also a <a href="#thing">link</a></p>'

# Results of stripping HTML and killing strong tags
STRIPKS1 = '<html>\nHeading\nLink\nNested\n</html>'
STRIPKS2 = '<html>\ntitle\nStart body\nThis iss a .Test link\n</html>'
STRIPKS3 = '<div>\nFirst\nSecond\nThird\nFourth\nFifth\nSixth\n</div>'
STRIPKS4 = '<p>Here is a text para with some inline markup, like . Also a link</p>'


class TestCleaner(unittest.TestCase):

    def test_strip1(self):
        """Test applying the default strip to HTML document."""
        tree = html.fromstring(HTML1)
        strip(tree)
        self.assertEqual(STRIP1, tostring(tree).decode())

    def test_strip2(self):
        """Test applying the default strip to HTML document."""
        tree = html.fromstring(HTML2)
        strip(tree)
        self.assertEqual(STRIP2, tostring(tree).decode())

    def test_strip3(self):
        """Test applying the default strip to HTML document."""
        tree = html.fromstring(HTML3)
        strip(tree)
        self.assertEqual(STRIP3, tostring(tree).decode())

    def test_strip4(self):
        """Test applying the default strip to HTML document."""
        tree = html.fromstring(HTML4)
        strip(tree)
        self.assertEqual(STRIP4, tostring(tree).decode())

    def test_strip_markup_doc(self):
        """Test applying the default strip_markup to HTML document."""
        original_tree = html.fromstring(HTML1)
        original_string = tostring(original_tree).decode()
        stripped_tree = strip_markup(original_tree)
        stripped_string = tostring(stripped_tree).decode()
        self.assertEqual(STRIP1, stripped_string)
        self.assertEqual(original_string, tostring(original_tree).decode())  # tree shouldn't change as strip_markup copies

    def test_strip_html1(self):
        """Test applying the default strip_markup to HTML string."""
        self.assertEqual(STRIP1, strip_html(HTML1))

    def test_strip_html2(self):
        """Test applying the default strip_markup to HTML string."""
        self.assertEqual(STRIP2, strip_html(HTML2))

    def test_strip_html3(self):
        """Test applying the default strip_markup to HTML string."""
        self.assertEqual(STRIP3, strip_html(HTML3))

    def test_strip_leave_whitespace1(self):
        """Test applying a ``Cleaner`` instance with ``fix_whitespace=False``."""
        cleaner = Cleaner(fix_whitespace=False, strip_xpath='.//*')
        tree = html.fromstring(HTML1)
        cleaner(tree)
        self.assertEqual(STRIPWS1, tostring(tree).decode())

    def test_strip_leave_whitespace2(self):
        """Test applying a ``Cleaner`` instance with ``fix_whitespace=False``."""
        cleaner = Cleaner(fix_whitespace=False, strip_xpath='.//*')
        tree = html.fromstring(HTML2)
        cleaner(tree)
        self.assertEqual(STRIPWS2, tostring(tree).decode())

    def test_strip_leave_whitespace3(self):
        """Test applying a ``Cleaner`` instance with ``fix_whitespace=False``."""
        cleaner = Cleaner(fix_whitespace=False, strip_xpath='.//*')
        tree = html.fromstring(HTML3)
        cleaner(tree)
        self.assertEqual(STRIPWS3, tostring(tree).decode())

    def test_strip_leave_whitespace4(self):
        """Test applying a ``Cleaner`` instance with ``fix_whitespace=False``."""
        cleaner = Cleaner(fix_whitespace=False, strip_xpath='.//*')
        tree = html.fromstring(HTML4)
        cleaner(tree)
        self.assertEqual(STRIPWS4, tostring(tree).decode())

    def test_clean1(self):
        """Test apply the default clean to HTML document."""
        tree = html.fromstring(HTML1)
        clean(tree)
        self.assertEqual(CLEAN1, tostring(tree).decode())

    def test_clean2(self):
        """Test apply the default clean to HTML document."""
        tree = html.fromstring(HTML2)
        clean(tree)
        self.assertEqual(CLEAN2, tostring(tree).decode())

    def test_clean3(self):
        """Test apply the default clean to HTML document."""
        tree = html.fromstring(HTML3)
        clean(tree)
        self.assertEqual(CLEAN3, tostring(tree, method='html').decode())

    def test_clean4(self):
        """Test apply the default clean to HTML document."""
        tree = html.fromstring(HTML4)
        clean(tree)
        self.assertEqual(CLEAN4, tostring(tree, method='html').decode())

    def test_strip_kill_strong1(self):
        """Test applying a ``Cleaner`` instance that kills strong tags."""
        cleaner = Cleaner(strip_xpath='.//*', kill_xpath='.//script | .//style | .//comment() | .//processing-instruction() | .//strong')
        tree = html.fromstring(HTML1)
        cleaner(tree)
        self.assertEqual(STRIPKS1, tostring(tree).decode())

    def test_strip_kill_strong2(self):
        """Test applying a ``Cleaner`` instance that kills strong tags."""
        cleaner = Cleaner(strip_xpath='.//*', kill_xpath='.//script | .//style | .//comment() | .//processing-instruction() | .//strong')
        tree = html.fromstring(HTML2)
        cleaner(tree)
        self.assertEqual(STRIPKS2, tostring(tree).decode())

    def test_strip_kill_strong3(self):
        """Test applying a ``Cleaner`` instance that kills strong tags."""
        cleaner = Cleaner(strip_xpath='.//*', kill_xpath='.//script | .//style | .//comment() | .//processing-instruction() | .//strong')
        tree = html.fromstring(HTML3)
        cleaner(tree)
        self.assertEqual(STRIPKS3, tostring(tree).decode())

    def test_strip_kill_strong4(self):
        """Test applying a ``Cleaner`` instance that kills strong tags."""
        cleaner = Cleaner(strip_xpath='.//*', kill_xpath='.//script | .//style | .//comment() | .//processing-instruction() | .//strong')
        tree = html.fromstring(HTML4)
        cleaner(tree)
        self.assertEqual(STRIPKS4, tostring(tree).decode())


if __name__ == '__main__':
    unittest.main()

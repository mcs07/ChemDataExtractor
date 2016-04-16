# -*- coding: utf-8 -*-
"""
test_scrape_fields
~~~~~~~~~~~~~~~~~~

Test scraping using different field classes.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import datetime
import logging
import unittest

from chemdataextractor.scrape.fields import StringField, IntField, FloatField, BoolField, DateTimeField
from chemdataextractor.scrape.entity import Entity
from chemdataextractor.scrape.selector import Selector


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


HTML = '''
<html>
  <body>
    <h1>Book Title</h1>
    <div class="container">
      <h2>Chapter <span class="chnum">2</span></h2>
      <p>Here is some introduction text.</p>


      <a href="Chapter3.html" id="next">Next Chapter</a>
      <p>Price: <span class="cost">$2.99</span></p>
      <p>Last updated on 24th September 2003.</p>
      <p>Public: Yes</p>
    </div>
  </body>
</html>
'''


class BookChapter(Entity):
    """An entity with various different field types."""
    book = StringField('body>h1::text')
    number = IntField('.chnum::text')
    price = FloatField('.cost::text', re='\$(.+)')
    public = BoolField('p::text', re='Public: (.+)')
    updated = DateTimeField('p::text', re='Last updated on (.+).')
    next_url = StringField('#next::attr("href")', lower=True)


class TestFieldScrape(unittest.TestCase):
    """Test scraping different fields."""

    def setUp(self):
        """Instantiate the Entity from a HTML string."""
        self.scraped = BookChapter(Selector.from_text(HTML))

    def test_string(self):
        """Test StringField."""
        self.assertEqual(self.scraped.book, 'Book Title')

    def test_int(self):
        """Test IntField."""
        self.assertEqual(self.scraped.number, 2)

    def test_float(self):
        """Test FloatField."""
        self.assertEqual(self.scraped.price, 2.99)

    def test_bool(self):
        """Test BoolField."""
        self.assertEqual(self.scraped.public, True)

    def test_date(self):
        """Test DateTimeField."""
        self.assertEqual(self.scraped.updated, datetime.datetime(2003, 9, 24, 0, 0))

    def test_lowerstring(self):
        """Test LowerStringField."""
        self.assertEqual(self.scraped.next_url, 'chapter3.html')

    def test_serialize(self):
        """Test serialization to python dictionary."""
        self.assertEqual(self.scraped.serialize(), {
            'book': u'Book Title',
            'next_url': u'chapter3.html',
            'number': 2,
            'price': 2.99,
            'public': True,
            'updated': '2003-09-24T00:00:00'
        })


if __name__ == '__main__':
    unittest.main()

# -*- coding: utf-8 -*-
"""
test_scrape_entity
~~~~~~~~~~~~~~~~~~

Test scraping using Entity class directly.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import unittest

import six

from chemdataextractor.scrape.fields import StringField, EntityField
from chemdataextractor.scrape.entity import Entity, EntityList
from chemdataextractor.scrape.selector import Selector
from chemdataextractor.text.processors import Chain, RAdd

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


SIMPLE_HTML = '''
<html>
  <body>
    <div><h1>heading</h1></div>
    <div><a href="http://Google.com">Go to Google</a></div>
    <div><a href="http://apPle.com">Go to Apple</a></div>
    <div><div>Nested</div></div>
  </body>
</html>
'''


class SimpleContent(Entity):
    """A simple entity defined using XPath expressions."""
    title = StringField('//div/h1/text()', xpath=True)
    link_text = StringField('//div/a/text()', xpath=True)
    link_url = StringField('//div/a/@href', xpath=True)
    urls = StringField('/html/body/div/a/@href', xpath=True, all=True, lower=True)
    in_divs = StringField('//div/div', xpath=True, all=True)

    process_title = Chain(six.text_type.capitalize, RAdd('!'))

    # def clean_title(self, value):
    #     """Capitalize title and add exclamation mark."""
    #     value = value[:1].upper() + value[1:] + '!'
    #     return value

    # def clean_urls(self, value):
    #     """Lowercase listed URL values."""
    #     value = [u.lower() for u in value]
    #     return value


class TestSimpleScrape(unittest.TestCase):
    """Test basic scrape functionality."""

    def setUp(self):
        """Instantiate the Entity from a HTML string."""
        self.scraped = SimpleContent(Selector.from_text(SIMPLE_HTML))

    def test_scrape(self):
        """Test scraping and cleaning of strings."""
        self.assertEqual(self.scraped.title, 'Heading!')
        self.assertEqual(self.scraped.link_text, 'Go to Google')
        self.assertEqual(self.scraped.link_url, 'http://Google.com')

    def test_listfield(self):
        """Test scraping and cleaning of lists of strings."""
        self.assertEqual(self.scraped.urls, ['http://google.com', 'http://apple.com'])
        self.assertEqual(self.scraped.in_divs, ['Nested'])

    def test_serialize(self):
        """Test serialization to python dictionary."""
        self.assertEqual(self.scraped.serialize(), {
            'in_divs': ['Nested'],
            'link_text': 'Go to Google',
            'link_url': 'http://Google.com',
            'title': 'Heading!',
            'urls': ['http://google.com', 'http://apple.com']
        })


ARTICLE_HTML = '''
<html>
  <body>
    <div><h1>First article</h1><p>First para</p><p>Second para</p></div>
    <div><h1>Second article</h1><p>Para 1</p><p>Para 2</p></div>
    <div><h1>Third article</h1><p>Thing one</p><p>Thing two</p></div>
  </body>
</html>
'''


class Blog(Entity):
    title = StringField('./h1/text()', xpath=True)
    content = StringField('./p/text()', xpath=True, all=True)


class TestMultiScrape(unittest.TestCase):
    """Test scrape with a custom root and multiple occurrences."""

    def setUp(self):
        self.blogs = Blog.scrape(Selector.from_text(ARTICLE_HTML), root='/html/body/div', xpath=True)

    def test_scrape_multiple(self):
        """Test using the scrape classmethod to get multiple scrapes from the same HTML."""
        self.assertEqual(self.blogs[0].title, 'First article')
        self.assertEqual(self.blogs[0].content, ['First para', 'Second para'])
        self.assertEqual(self.blogs[1].title, 'Second article')
        self.assertEqual(self.blogs[1].content, ['Para 1', 'Para 2'])
        self.assertEqual(self.blogs[2].title, 'Third article')
        self.assertEqual(self.blogs[2].content, ['Thing one', 'Thing two'])

    def test_scrape_results(self):
        """Test the EntityList class."""
        self.assertIsInstance(self.blogs, EntityList)
        self.assertEqual(len(self.blogs), 3)
        self.assertEqual([s.title for s in self.blogs[1:]], ['Second article', 'Third article'])

    def test_serialize(self):
        """Test serialization of results to a list of dictionaries."""
        self.assertEqual(self.blogs.serialize(), [
            {'content': [u'First para', u'Second para'], 'title': u'First article'},
            {'content': [u'Para 1', u'Para 2'], 'title': u'Second article'},
            {'content': [u'Thing one', u'Thing two'], 'title': u'Third article'}
        ])


COMPLEX_HTML = '''
<html>
  <body>
    <div><h1>First article</h1><div class="author"><span class="firstname">Matt</span> <span class="lastname">Swain</span></div><p>First para</p><p>Second para</p></div>
    <div><h1>Second article</h1><div class="author"><span class="firstname">John</span> <span class="lastname">Smith</span></div><p>Para 1</p><p>Para 2</p></div>
    <div><h1>Third article</h1><div class="author"><span class="firstname">James</span> <span class="lastname">Bond</span></div><p>Thing one</p><p>Thing two</p></div>
  </body>
</html>
'''


class Author(Entity):
    firstname = StringField('./span[@class="firstname"]/text()', xpath=True)
    lastname = StringField('./span[@class="lastname"]/text()', xpath=True)


class Article(Entity):
    title = StringField('./h1/text()', xpath=True)
    content = StringField('./p/text()', xpath=True, all=True)
    authors = EntityField(Author, './div[@class="author"]', xpath=True, all=True)


class TestComplexScrape(unittest.TestCase):
    """Test scrape with a custom root and embedded entity."""

    def setUp(self):
        self.scrapes = Article.scrape(Selector.from_text(COMPLEX_HTML), root='/html/body/div', xpath=True)

    def test_scrape_multiple(self):
        """Test using the scrape classmethod to get multiple scrapes from the same HTML."""
        self.assertEqual(self.scrapes[0].title, 'First article')
        self.assertEqual(self.scrapes[0].content, ['First para', 'Second para'])
        self.assertEqual(self.scrapes[1].title, 'Second article')
        self.assertEqual(self.scrapes[1].content, ['Para 1', 'Para 2'])
        self.assertEqual(self.scrapes[2].title, 'Third article')
        self.assertEqual(self.scrapes[2].content, ['Thing one', 'Thing two'])

    def test_scrape_results(self):
        """Test the ScrapeResults class."""
        self.assertIsInstance(self.scrapes, EntityList)
        self.assertEqual(len(self.scrapes), 3)
        self.assertEqual([s.title for s in self.scrapes[1:]], ['Second article', 'Third article'])

    def test_serialize(self):
        """Test serialization of results to a list of dictionaries."""
        self.assertEqual(self.scrapes.serialize(), [
            {'content': [u'First para', u'Second para'], 'title': u'First article', 'authors': [{'lastname': u'Swain', 'firstname': u'Matt'}]},
            {'content': [u'Para 1', u'Para 2'], 'title': u'Second article', 'authors': [{'lastname': u'Smith', 'firstname': u'John'}]},
            {'content': [u'Thing one', u'Thing two'], 'title': u'Third article', 'authors': [{'lastname': u'Bond', 'firstname': u'James'}]}
        ])


class AuthorC(Entity):
    firstname = StringField('span.firstname::text')
    lastname = StringField('span.lastname::text')


class ArticleC(Entity):
    title = StringField('h1::text')
    content = StringField('p::text', all=True)
    authors = EntityField(AuthorC, 'div.author', all=True)


class TestCssScrape(unittest.TestCase):
    """Test scrape using CSS selectors."""

    def setUp(self):
        self.scrapes = ArticleC.scrape(Selector.from_text(COMPLEX_HTML), root='html>body>div')

    def test_scrape_multiple(self):
        """Test using the scrape classmethod to get multiple scrapes from the same HTML."""
        self.assertEqual(self.scrapes[0].title, 'First article')
        self.assertEqual(self.scrapes[0].content, ['First para', 'Second para'])
        self.assertEqual(self.scrapes[1].title, 'Second article')
        self.assertEqual(self.scrapes[1].content, ['Para 1', 'Para 2'])
        self.assertEqual(self.scrapes[2].title, 'Third article')
        self.assertEqual(self.scrapes[2].content, ['Thing one', 'Thing two'])

    def test_scrape_results(self):
        """Test the ScrapeResults class."""
        self.assertIsInstance(self.scrapes, EntityList)
        self.assertEqual(len(self.scrapes), 3)
        self.assertEqual([s.title for s in self.scrapes[1:]], ['Second article', 'Third article'])

    def test_serialize(self):
        """Test serialization of results to a list of dictionaries."""
        self.assertEqual(self.scrapes.serialize(), [
            {'content': [u'First para', u'Second para'], 'title': u'First article', 'authors': [{'lastname': u'Swain', 'firstname': u'Matt'}]},
            {'content': [u'Para 1', u'Para 2'], 'title': u'Second article', 'authors': [{'lastname': u'Smith', 'firstname': u'John'}]},
            {'content': [u'Thing one', u'Thing two'], 'title': u'Third article', 'authors': [{'lastname': u'Bond', 'firstname': u'James'}]}
        ])


if __name__ == '__main__':
    unittest.main()

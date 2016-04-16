# -*- coding: utf-8 -*-
"""
test_scrape_selector
~~~~~~~~~~~~~~~~~~~~

Test the HTML/XML Selector.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import unittest

from chemdataextractor.scrape.selector import Selector


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


HTML = '''
<html>
  <body>
    <div><h1>Heading</h1></div>
    <div><a href="page">Link</a></div>
    <div><div>Nested</div></div>
  </body>
</html>
'''


class TestSelector(unittest.TestCase):

    def test_html_xpath(self):
        selector = Selector.from_text(HTML)
        self.assertEqual(len(selector.xpath('.//div')), 4)
        self.assertEqual(selector.xpath('.//a').extract(), ['Link'])
        self.assertEqual(selector.xpath('.//a').extract(raw=True), ['<a href="page">Link</a>'])
        self.assertEqual(selector.xpath('.//a/text()').extract(), ['Link'])
        self.assertEqual(selector.xpath('.//a/@href').extract(), ['page'])
        self.assertEqual(selector.xpath('/html/body/div/h1/text()').extract(), ['Heading'])

    def test_html_css(self):
        selector = Selector.from_text(HTML)
        self.assertEqual(len(selector.css('div')), 4)
        self.assertEqual(selector.css('a').extract(), ['Link'])
        self.assertEqual(selector.css('a').extract(raw=True), ['<a href="page">Link</a>'])
        self.assertEqual(selector.css('a::text').extract(), ['Link'])
        self.assertEqual(selector.css('a::attr(href)').extract(), ['page'])
        self.assertEqual(selector.css('html>body>div>h1::text').extract(), ['Heading'])


if __name__ == '__main__':
    unittest.main()

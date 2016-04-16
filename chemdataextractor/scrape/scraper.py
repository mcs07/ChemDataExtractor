# -*- coding: utf-8 -*-
"""
chemdataextractor.scrape.scraper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from abc import abstractmethod
import logging

import requests

from .base import BaseScraper, BaseRequester, BaseFormat
from .entity import EntityList
from .selector import Selector


log = logging.getLogger(__name__)


class HtmlFormat(BaseFormat):
    """Process HTML response and return a Selector."""

    def process_response(self, response):
        return Selector.from_html(response)


class XmlFormat(BaseFormat):
    """Process XML response and return a Selector."""

    namespaces = None

    def process_response(self, response):
        return Selector.from_xml(response, namespaces=self.namespaces)


class GetRequester(BaseRequester):

    def make_request(self, session, url, **kwargs):
        """Make a HTTP GET request.

        :param url: The URL to get.
        :returns: The response to the request.
        :rtype: requests.Response
        """
        log.debug('Making request: GET %s %s' % (url, kwargs))
        return session.get(url, **kwargs)


class PostRequester(BaseRequester):

    def make_request(self, session, url, **kwargs):
        """Make a HTTP POST request.

        :param url: The URL to post to.
        :param data: The data to post.
        :returns: The response to the request.
        :rtype: requests.Response
        """
        log.debug('Making request: POST %s %s' % (url, kwargs))
        return session.post(url, **kwargs)


class UrlScraper(GetRequester, HtmlFormat, BaseScraper):
    """Scraper that takes a URL as input."""

    def process_url(self, url):
        """Override to filter or process input URL prior to making request."""
        return url

    def run(self, url):
        """Request URL, scrape response and return an EntityList."""
        url = self.process_url(url)
        if not url:
            return
        response = self.make_request(self.http, url)
        selector = self.process_response(response)
        entities = []
        for root in self.get_roots(selector):
            entity = self.entity(root)
            entity = self.process_entity(entity)
            if entity:
                entities.append(entity)
        return EntityList(*entities)


class RssScraper(XmlFormat, UrlScraper):
    """RSS scraper"""
    # Treat each RSS item as entity root
    root = 'item'
    # Add common RSS XML namespaces
    namespaces = {
        'atom': 'http://www.w3.org/2005/Atom',
        'feedburner': 'http://rssnamespace.org/feedburner/ext/1.0',
    }


class SearchScraper(GetRequester, HtmlFormat, BaseScraper):
    """Scraper that takes a search query as input."""

    def process_query(self, query):
        """Override to filter or process input query prior to making request."""
        return query

    @abstractmethod
    def perform_search(self, query, page):
        """Override to implement search. Take query input and return a response."""
        return

    def run(self, query, page=1):
        query = self.process_query(query)
        if not query:
            return
        response = self.perform_search(query, page)
        selector = self.process_response(response)
        entities = []
        for root in self.get_roots(selector):
            entity = self.entity(root)
            entity = self.process_entity(entity)
            if entity:
                entities.append(entity)
        return EntityList(*entities)



# TODO: Consider removing the necessity to sublass UrlScraper, RssScraper by allowing entity, root to be passed as constructor arguments
# Subclassing then optional if further customization desired.

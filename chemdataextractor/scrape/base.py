# -*- coding: utf-8 -*-
"""
chemdataextractor.scrape.base
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Abstract base classes that define the interface for Scrapers, Fields, Crawlers, etc.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from abc import ABCMeta, abstractproperty, abstractmethod
import logging

import requests
import six

log = logging.getLogger(__name__)


class BaseScraper(six.with_metaclass(ABCMeta)):
    """Abstract Scraper class from which all Scrapers inherit."""

    #: CSS selector or XPath expression that returns the root of each entity.
    root = None
    #: Whether the root is an XPath expression instead of a CSS selector.
    root_xpath = False

    def __init__(self):
        """"""
        # Create a HTTP session for all requests
        self.http = self.create_session()

    def create_session(self):
        """Override to set up default data (e.g. headers, authentication) on each request."""
        http = requests.Session()
        return http

    def name(self):
        """A unique name for this scraper."""
        return ''.join('_%s' % c if c.isupper() else c for c in self.__class__.__name__).strip('_').lower()

    @abstractproperty
    def entity(self):
        """The Entity to scrape."""
        pass

    def process_entity(self, entity):
        """Override to process each entity."""
        return entity

    @abstractmethod
    def make_request(self, url, data):
        """Make a HTTP request.

        :param url: The URL to get.
        :param data: Query data.
        :returns: The response to the request.
        :rtype: requests.Response
        """
        return

    @abstractmethod
    def process_response(self, response):
        """Return a Selector for the given response.

        :param requests.Response response: The response object.
        :rtype: Selector
        """
        return

    def get_roots(self, selector):
        """"""
        if not self.root:
            yield selector
        elif self.root_xpath:
            for root in selector.xpath(self.root):
                yield root
        else:
            for root in selector.css(self.root):
                yield root


class BaseFormat(six.with_metaclass(ABCMeta)):
    """"""

    @abstractmethod
    def process_response(self, response):
        """Return a Selector for the given response.

        :param requests.Response response: The response object.
        :rtype: Selector
        """
        return


class BaseRequester(six.with_metaclass(ABCMeta)):
    """"""

    @abstractmethod
    def make_request(self, url, data):
        """Make a HTTP request.

        :param url: The URL to get.
        :param data: Query data.
        :returns: The response to the request.
        :rtype: requests.Response
        """
        return


class BaseEntityProcessor(six.with_metaclass(ABCMeta)):
    """Abstract EntityProcessor class from which all EntityProcessors inherit."""

    @abstractmethod
    def process_entity(self, entity):
        """Process an Entity. Return None to filter Entity from the pipeline.

        :param Entity entity: The Entity to process.
        :returns: The processed Entity.
        :rtype: Entity or None
        """
        return entity


class BaseEntity(six.with_metaclass(ABCMeta)):
    """Abstract Entity class from which all Entities inherit."""
    pass


class EntityMeta(ABCMeta):
    """Metaclass for Entity."""

    def __new__(mcs, name, bases, attrs):
        fields = {}
        for attr_name, attr_value in six.iteritems(attrs):
            if isinstance(attr_value, BaseField):
                # Set the name attribute on the field to the attribute name on the Entity
                attr_value.name = six.text_type(attr_name)
                fields[attr_name] = attr_value
        #attrs['fields'] = fields
        # Set default _meta values, then update with any custom definitions from meta
        #attrs['_meta'] = {'root': None}
        #attrs['_meta'].update(attrs.pop('meta', {}))
        cls = super(EntityMeta, mcs).__new__(mcs, name, bases, attrs)
        cls.fields = cls.fields.copy()
        cls.fields.update(fields)
        return cls


class BaseField(six.with_metaclass(ABCMeta)):
    """Base class for all fields."""

    # This is assigned by EntityMeta to match the attribute on the Entity
    name = None

    def __init__(self, selection, xpath=False, re=None, all=False, default=None, null=False, raw=False):
        """

        :param string selection: The CSS selector or XPath expression used to select the content to scrape.
        :param bool xpath: (Optional) Whether selection is an XPath expression instead of a CSS selector. Default False.
        :param re: (Optional) Regular expression to apply to scraped content.
        :param bool all: (Optional) Whether to scrape all occurrences instead of just the first. Default False.
        :param default: (Optional) The default value for this field if none is set.
        :param bool null: (Optional) Include in serialized output even if value is None. Default False.
        :param bool raw: (Optional) Whether to scrape the raw HTML/XML instead of the text contents. Default False.
        """
        self.selection = selection
        self.xpath = xpath
        self.re = re
        self.all = all
        self.default = default
        self.null = null
        self.raw = raw

    def __get__(self, instance, owner):
        """Descriptor for retrieving a value from a field in an Entity."""
        # Check if Entity class is being called, rather than Entity instance
        if instance is None:
            return self
        # Get value from Entity instance if available
        value = instance._values.get(self.name)
        # If value is None, empty list or empty string return the default value if set
        if value in [None, [], ''] and self.default is not None:
            return self.default
        # Otherwise if value is None and all, return empty list
        if self.all and value is None:
            return []
        return value

    def __set__(self, instance, value):
        """Descriptor for assigning a value to a field in a Entity."""
        instance._values[self.name] = value

    def _post_scrape(self, value, processor=None):
        """Apply processing to the scraped value."""
        # Pass each value through the field's clean method
        value = [self.process(v) for v in value]
        # Filter None values
        value = [v for v in value if v is not None]
        # Pass each value through processors defined on the entity
        if processor:
            value = [processor(v) for v in value]
            value = [v for v in value if v is not None]
        # Take first unless all is specified
        if not self.all:
            value = value[0] if value else None
        log.debug('Scraped %s: %s from %s' % (self.name, value, self.selection))
        return value

    def scrape(self, selector, cleaner=None, processor=None):
        """Scrape the value for this field from the selector."""
        # Apply CSS or XPath expression to the selector
        selected = selector.xpath(self.selection) if self.xpath else selector.css(self.selection)
        # Extract the value and apply regular expression if specified
        value = selected.re(self.re) if self.re else selected.extract(raw=self.raw, cleaner=cleaner)
        return self._post_scrape(value, processor=processor)

    def serialize(self, value):
        """Serialize this field."""
        if hasattr(value, 'serialize'):
            return value.serialize()
        else:
            return value

    def process(self, value):
        """Override to perform custom processing of a value."""
        return value

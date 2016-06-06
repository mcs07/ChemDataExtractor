# -*- coding: utf-8 -*-
"""
chemdataextractor.scrape.entity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An entity to extract.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from collections import Sequence
import json
import logging

import six

from .base import BaseEntity, EntityMeta
from .fields import StringField, DateTimeField, UrlField
from ..text.normalize import normalize


log = logging.getLogger(__name__)


class Entity(six.with_metaclass(EntityMeta, BaseEntity)):

    fields = {}

    def __init__(self, selector):
        """

        :param Selector selector: The selector to scrape.
        """
        self._values = {}
        # Iterate all defined fields
        for field_name, field in six.iteritems(self.fields):
            # Scrape field values from selector
            cleaner = getattr(self, 'clean_%s' % field_name, None)
            processor = getattr(self, 'process_%s' % field_name, None)
            value = field.scrape(selector, cleaner=cleaner, processor=processor)
            # Finalize value using finalize_* method on scrape, if it exists
            if hasattr(self, 'finalize_%s' % field_name):
                value = getattr(self, 'finalize_%s' % field_name)(value)
            log.debug('Assigning %s: %s' % (field_name, value))
            setattr(self, field_name, value)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._values == other._values
        return False

    def __len__(self):
        return len(self._values)

    def __iter__(self):
        return iter(self._values)

    def __delattr__(self, attr):
        """Handle deletion of field values by setting to default if specified."""
        # Set to default value
        if attr in self.fields:
            setattr(self, attr, self.fields[attr].default)
        else:
            super(Entity, self).__delattr__(attr)

    def __getitem__(self, key):
        """Redirect dictionary-style field access to attribute-style."""
        try:
            if key in self.fields:
                return getattr(self, key)
        except AttributeError:
            pass
        raise KeyError(key)

    def __setitem__(self, key, value):
        """Redirect dictionary-style field setting to attribute-style."""
        if key not in self.fields:
            raise KeyError(key)
        return setattr(self, key, value)

    def __contains__(self, name):
        try:
            val = getattr(self, name)
            return val is not None
        except AttributeError:
            return False

    def __repr__(self):
        return '%s()' % self.__class__.__name__

    @classmethod
    def scrape(cls, selector, root, xpath=False):
        """Return EntityList for the given selector."""
        log.debug('Called scrape classmethod with root: %s' % root)
        roots = selector.xpath(root) if xpath else selector.css(root)
        results = [cls(r) for r in roots]
        return EntityList(*results)

    def serialize(self):
        """Convert Entity to python dictionary."""
        # Serialize fields to a dict
        data = {}
        for field_name in self:
            value = self._values.get(field_name)
            field = self.fields.get(field_name)
            if value is not None:
                if field.all:
                    value = [field.serialize(v) for v in value]
                else:
                    value = field.serialize(value)
            # Skip empty fields unless field.null
            if not field.null and ((field.all and value == []) or (not field.all and value in {None, ''})):
                continue
            data[field.name] = value
        return data

    def to_json(self, *args, **kwargs):
        """Convert Entity to JSON."""
        return json.dumps(self.serialize(), *args, **kwargs)


class EntityList(Sequence):
    """Wrapper around a list of Entities to facilitate operations on all at once."""

    def __init__(self, *entities):
        self.entities = list(entities)

    def __getitem__(self, index):
        return self.entities[index]

    def __len__(self):
        return len(self.entities)

    def serialize(self):
        """Serialize to a list of python dictionaries."""
        return [e.serialize() for e in self.entities]

    def to_json(self, *args, **kwargs):
        """Convert EntityList to JSON."""
        return json.dumps(self.serialize(), *args, **kwargs)


class DocumentEntity(Entity):
    """Generic document entity."""
    doi = StringField('//meta[@name="citation_doi"]/@content | //meta[@name="dc.identifier"]/@content | //meta[@name="DC.identifier"]/@content | //meta[@name="DC.Identifier"]/@content | //meta[@name="dc.Identifier"]/@content', xpath=True, lower=True)
    title = StringField('//meta[@name="citation_title"]/@content | //meta[@name="dc.title"]/@content | //meta[@name="DC.title"]/@content | //meta[@name="DC.Title"]/@content | //meta[@name="dc.Title"]/@content | //meta[@name="title"]/@content', xpath=True, strip=True)
    authors = StringField('//meta[@name="citation_author"]/@content | //meta[@name="dc.creator"]/@content | //meta[@name="DC.creator"]/@content | //meta[@name="DC.Creator"]/@content | //meta[@name="dc.Creator"]/@content', xpath=True, all=True)
    published_date = DateTimeField('//meta[@name="citation_publication_date"]/@content | //meta[@name="prism.publicationDate"]/@content | //meta[@name="citation_date"]/@content | //meta[@name="dc.date"]/@content | //meta[@name="DC.date"]/@content | //meta[@name="DC.Date"]/@content | //meta[@name="dc.Date"]/@content', xpath=True)
    online_date = DateTimeField('//meta[@name="citation_online_date"]/@content', xpath=True)
    journal = StringField('//meta[@name="citation_journal_title"]/@content | //meta[@name="citation_journal_abbrev"]/@content | //meta[@name="prism.publicationName"]/@content | //meta[@name="dc.source"]/@content | //meta[@name="DC.source"]/@content | //meta[@name="DC.Source"]/@content', xpath=True, strip=True)
    volume = StringField('//meta[@name="citation_volume"]/@content | //meta[@name="prism.volume"]/@content', xpath=True)
    issue = StringField('//meta[@name="citation_issue"]/@content | //meta[@name="prism.number"]/@content | //meta[@name="citation_technical_report_number"]/@content', xpath=True)
    firstpage = StringField('//meta[@name="citation_firstpage"]/@content | //meta[@name="prism.startingPage"]/@content', xpath=True)
    lastpage = StringField('//meta[@name="citation_lastpage"]/@content', xpath=True)
    abstract = StringField('//meta[@name="citation_abstract"]/@content', xpath=True, strip=True)
    publisher = StringField('//meta[@name="citation_publisher"]/@content | //meta[@name="dc.publisher"]/@content | //meta[@name="DC.publisher"]/@content | //meta[@name="dc.Publisher"]/@content | //meta[@name="DC.Publisher"]/@content', xpath=True)
    issn = StringField('//meta[@name="citation_issn"]/@content | //meta[@name="prism.issn"]/@content', xpath=True)
    language = StringField('//meta[@name="citation_language"]/@content | //meta[@name="dc.language"]/@content | //meta[@name="DC.language"] | //meta[@name="DC.Language"]/@content', xpath=True)
    copyright = StringField('//meta[@name="dc.copyright"]/@content | //meta[@name="DC.copyright"]/@content | //meta[@name="DC.Copyright"]/@content | //meta[@name="prism.copyright"]/@content', xpath=True)
    license = UrlField('//a[@rel="license"]/@href', xpath=True)
    html_url = UrlField('//meta[@name="citation_fulltext_html_url"]/@content', xpath=True)
    pdf_url = UrlField('//meta[@name="citation_pdf_url"]/@content', xpath=True)
    landing_url = UrlField('//meta[@name="citation_abstract_html_url"]/@content', xpath=True)

    process_title = normalize
    process_journal = normalize
    process_publisher = normalize
    process_authors = normalize
    process_abstract = normalize

    # TODO: Abbreviations: <abbr title="Australia">AU</abbr>

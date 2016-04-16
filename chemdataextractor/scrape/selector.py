# -*- coding: utf-8 -*-
"""
chemdataextractor.scrape.selector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tool for selecting content from HTML or XML using CSS or XPath expressions.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from collections import Sequence
from copy import deepcopy
import logging
import re
from bs4 import UnicodeDammit

from lxml.etree import XMLParser, fromstring, tostring
from lxml.html import HTMLParser
import six

from ..utils import flatten
from .csstranslator import CssHTMLTranslator, CssXmlTranslator


log = logging.getLogger(__name__)


class Selector(object):
    """Tool for selecting content from HTML or XML using XPath selectors."""

    #: Default namespaces for all selectors
    _namespaces = {
        're': 'http://exslt.org/regular-expressions',
        'set': 'http://exslt.org/sets',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'prism': 'http://prismstandard.org/namespaces/basic/2.0/',
        'xml': 'http://www.w3.org/XML/1998/namespace',
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns',
    }

    def __init__(self, root, fmt='html', translator=CssHTMLTranslator, namespaces=None):
        self.fmt = fmt
        self._root = root
        self._translator = translator() if type(translator) == type else translator
        self.namespaces = dict(self._namespaces)
        if namespaces is not None:
            self.namespaces.update(namespaces)

    def __eq__(self, other):
        if isinstance(other, Selector):
            return self._root == other._root
        return NotImplemented

    @classmethod
    def from_text(cls, text, base_url=None, parser=HTMLParser, translator=CssHTMLTranslator, fmt='html', namespaces=None, encoding=None):
        log.debug('Parsing {} with {}'.format(fmt, parser))
        root = fromstring(text, parser=parser(recover=True, encoding=cls._get_encoding(text, encoding)), base_url=base_url)
        if base_url and hasattr(root, 'make_links_absolute'):
            root.make_links_absolute()
        return cls(root, translator=translator, fmt=fmt, namespaces=namespaces)

    @classmethod
    def from_html_text(cls, text, base_url=None, namespaces=None, encoding=None):
        return cls.from_text(text, base_url=base_url, parser=HTMLParser, translator=CssHTMLTranslator, fmt='html', namespaces=namespaces, encoding=encoding)

    @classmethod
    def from_xml_text(cls, text, base_url=None, namespaces=None, encoding=None):
        return cls.from_text(text, base_url=base_url, parser=XMLParser, translator=CssXmlTranslator, fmt='xml', namespaces=namespaces, encoding=encoding)

    @classmethod
    def from_response(cls, response, parser=HTMLParser, translator=CssHTMLTranslator, fmt='html', namespaces=None):
        return cls.from_text(response.content, response.url, parser, translator, fmt, namespaces=namespaces, encoding=response.encoding)

    @classmethod
    def from_html(cls, response, namespaces=None):
        return cls.from_response(response, parser=HTMLParser, translator=CssHTMLTranslator, fmt='html', namespaces=namespaces)

    @classmethod
    def from_xml(cls, response, namespaces=None):
        return cls.from_response(response, parser=XMLParser, translator=CssXmlTranslator, fmt='xml', namespaces=namespaces)

    @property
    def path(self):
        """Absolute path to the root of this selector."""
        return self._root.getroottree().getpath(self._root)

    @property
    def tag(self):
        """Tag name of the root of this selector."""
        return self._root.tag

    def xpath(self, query):
        result = self._root.xpath(query, namespaces=self.namespaces, smart_strings=False)
        if type(result) is not list:
            result = [result]
        #log.debug('Selecting XPath: {}: {}'.format(query, result))
        result = [self.__class__(root=x, fmt=self.fmt, translator=self._translator, namespaces=self.namespaces) for x in result]
        return SelectorList(*result)

    def css(self, query):
        return self.xpath(self._translator.css_to_xpath(query))

    def re(self, regex):
        if isinstance(regex, six.string_types):
            regex = re.compile(regex, re.U)
        text = self.extract()
        return flatten(regex.findall(text))

    def extract(self, cleaner=None, raw=False):
        try:
            root = deepcopy(self._root)
            if cleaner:
                cleaner(root)
            return tostring(root, method=self.fmt if raw else 'text', encoding=six.text_type, with_tail=False)
        except (AttributeError, TypeError) as e:
            #log.warn(e)
            return six.text_type(self._root)

    @classmethod
    def _get_encoding(cls, input_string, encoding):
        converted = UnicodeDammit(input_string, [encoding] if encoding else [])
        # Not worth raising exception? lxml will raise if parse fails.
        # if not converted.unicode_markup:
        #     raise UnicodeDecodeError('Failed to detect encoding')
        return converted.original_encoding


class SelectorList(Sequence):
    """Wrapper around a list of Selectors to allow selecting from all at once."""

    def __init__(self, *selectors):
        self.selectors = list(selectors)

    def __getitem__(self, index):
        return self.selectors[index]

    def __len__(self):
        return len(self.selectors)

    def xpath(self, xpath):
        return self.__class__(*flatten([x.xpath(xpath) for x in self.selectors]))

    def re(self, regex):
        return flatten([x.re(regex) for x in self.selectors])

    def extract(self, cleaner=None, raw=False):
        return [x.extract(cleaner=cleaner, raw=raw) for x in self.selectors]

    def extract_first(self, cleaner=None, raw=False, default=None):
        for x in self.selectors:
            return x.extract(cleaner=cleaner, raw=raw)
        else:
            return default

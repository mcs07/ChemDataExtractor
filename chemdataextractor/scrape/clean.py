# -*- coding: utf-8 -*-
"""
chemdataextractor.scrape.clean
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tools for cleaning up XML/HTML by removing tags entirely or replacing with their contents.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import copy
import logging
import re
from lxml.etree import fromstring, tostring
from lxml.html import fromstring as html_fromstring
import six

from . import BLOCK_ELEMENTS


log = logging.getLogger(__name__)


class Cleaner(object):
    """Clean HTML or XML by removing tags completely or replacing with their contents.

    A Cleaner instance provides a ``clean_markup`` method::

        cleaner = Cleaner()
        htmlstring = '<html><body><script>alert("test")</script><p>Some text</p></body></html>'
        print(cleaner.clean_markup(htmlstring))

    A Cleaner instance is also a callable that can be applied to lxml document trees::

        tree = lxml.etree.fromstring(htmlstring)
        cleaner(tree)
        print(lxml.etree.tostring(tree))

    Elements that are matched by ``kill_xpath`` are removed entirely, along with their contents. By default,
    ``kill_xpath`` matches all script and style tags, as well as comments and processing instructions.

    Elements that are matched by ``strip_xpath`` are replaced with their contents. By default, no elements are stripped.
    A common use-case is to set ``strip_xpath`` to ``.//*``, which specifies that all elements should be stripped.

    Elements that are matched by ``allow_xpath`` are excepted from stripping, even if they are also matched by
    ``strip_xpath``. This is useful when setting ``strip_xpath`` to strip all tags, allowing a few expections to be
    specified by ``allow_xpath``.
    """

    kill_xpath = './/script | .//style | .//comment() | .//processing-instruction() | .//*[@style="display:none;"]'
    strip_xpath = None
    allow_xpath = None
    fix_whitespace = True

    namespaces = {
        're': 'http://exslt.org/regular-expressions',
        'set': 'http://exslt.org/sets',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'prism': 'http://prismstandard.org/namespaces/basic/2.0/',
        'xml': 'http://www.w3.org/XML/1998/namespace',
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns',
    }

    def __init__(self, **kwargs):
        """Behaviour can be customized by overriding attributes in a subclass or setting them in the constructor.

        :param string kill_xpath: XPath expression for tags to remove along with their contents.
        :param string strip_xpath: XPath expression for tags to replace with their contents.
        :param string allow_xpath: XPath expression for tags to except from strip_xpath.
        :param bool fix_whitespace: Normalize whitespace to a single space and ensure newlines around block elements.
        :param dict namespaces: Namespace prefixes to register for the XPaths.
        """
        # TODO: This is weird. Why don't we change to proper individual keyword arguments with class attribs as default
        for name, value in kwargs.items():
            if not hasattr(self, name):
                raise TypeError('Unknown parameter: %s=%r' % (name, value))
            setattr(self, name, value)

    def __call__(self, doc):
        """Clean the document."""
        if hasattr(doc, 'getroot'):
            doc = doc.getroot()

        if self.fix_whitespace:
            # Ensure newlines around block elements
            for el in doc.iterdescendants():
                if el.tag in BLOCK_ELEMENTS:
                    el.tail = (el.tail or '') + '\n'
                    previous = el.getprevious()
                    parent = el.getparent()
                    if previous is None:
                        parent.text = (parent.text or '') + '\n'
                    else:
                        previous.tail = (previous.tail or '') + '\n'

        # Remove elements that match kill_xpath
        if self.kill_xpath:
            for el in doc.xpath(self.kill_xpath, namespaces=self.namespaces):
                #log.debug('Killing: %s' % tostring(el))
                parent = el.getparent()
                # We can't kill the root element!
                if parent is None:
                    continue
                if el.tail:
                    previous = el.getprevious()
                    if previous is None:
                        parent.text = (parent.text or '') + el.tail
                    else:
                        previous.tail = (previous.tail or '') + el.tail
                parent.remove(el)

        # Collect all the allowed elements
        to_keep = [el for el in doc.xpath(self.allow_xpath, namespaces=self.namespaces)] if self.allow_xpath else []

        # Replace elements that match strip_xpath with their contents
        if self.strip_xpath:
            for el in doc.xpath(self.strip_xpath, namespaces=self.namespaces):
                # Skip if allowed by allow_xpath
                if el in to_keep:
                    continue
                parent = el.getparent()
                previous = el.getprevious()
                # We can't strip the root element!
                if parent is None:
                    continue
                # Append the text to previous tail (or parent text if no previous), ensuring newline if block level
                if el.text and isinstance(el.tag, six.string_types):
                    if previous is None:
                        parent.text = (parent.text or '') + el.text
                    else:
                        previous.tail = (previous.tail or '') + el.text
                # Append the tail to last child tail, or previous tail, or parent text, ensuring newline if block level
                if el.tail:
                    if len(el):
                        last = el[-1]
                        last.tail = (last.tail or '') + el.tail
                    elif previous is None:
                        parent.text = (parent.text or '') + el.tail
                    else:
                        previous.tail = (previous.tail or '') + el.tail
                index = parent.index(el)
                parent[index:index+1] = el[:]

        # Collapse whitespace down to a single space or a single newline
        if self.fix_whitespace:
            for el in doc.iter():
                if el.text is not None:
                    el.text = re.sub(r'\s*\n\s*', '\n', el.text)
                    el.text = re.sub(r'[ \t]+', ' ', el.text)
                    # el.text = re.sub(r'\s+', ' ', el.text)
                if el.tail is not None:
                    el.tail = re.sub(r'\s*\n\s*', '\n', el.tail)
                    el.tail = re.sub(r'[ \t]+', ' ', el.tail)
                    # el.tail = re.sub(r'\s+', ' ', el.tail)

    def clean_html(self, html):
        """Apply ``Cleaner`` to HTML string or document and return a cleaned string or document."""
        result_type = type(html)
        if isinstance(html, six.string_types):
            doc = html_fromstring(html)
        else:
            doc = copy.deepcopy(html)
        self(doc)
        if issubclass(result_type, six.binary_type):
            return tostring(doc, encoding='utf-8')
        elif issubclass(result_type, six.text_type):
            return tostring(doc, encoding='unicode')
        else:
            return doc

    def clean_markup(self, markup, parser=None):
        """Apply ``Cleaner`` to markup string or document and return a cleaned string or document."""
        result_type = type(markup)
        if isinstance(markup, six.string_types):
            doc = fromstring(markup, parser=parser)
        else:
            doc = copy.deepcopy(markup)
        self(doc)
        if issubclass(result_type, six.binary_type):
            return tostring(doc, encoding='utf-8')
        elif issubclass(result_type, six.text_type):
            return tostring(doc, encoding='unicode')
        else:
            return doc


#: A default Cleaner instance, which kills comments, processing instructions, script tags, style tags.
clean = Cleaner()

#: Convenience function for applying ``clean`` to a string.
clean_markup = clean.clean_markup

#: Convenience function for applying ``clean`` to a HTML string.
clean_html = clean.clean_html

#: A Cleaner instance that is configured to strip all tags, replacing them with their text contents.
strip = Cleaner(strip_xpath='.//*')

#: Convenience function for applying ``strip`` to a string.
strip_markup = strip.clean_markup

#: Convenience function for applying ``strip`` to a HTML string.
strip_html = strip.clean_html

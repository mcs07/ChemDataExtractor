# -*- coding: utf-8 -*-
"""
chemdataextractor.scrape.nlm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tools for scraping documents from NLM Journal Archiving and Interchange DTD XML files.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import re

from ...text.normalize import normalize
from ...text.processors import Chain, Discard
from ..clean import Cleaner
from ..entity import Entity
from ..fields import StringField, EntityField, UrlField, IntField

log = logging.getLogger(__name__)


#: XML stripper that kills reference links, footnote links, equations, footnotes
strip_pmc_xml = Cleaner(strip_xpath='.//*', kill_xpath='.//disp-formula|.//inline-formula|.//mml:math|.//xref[@ref-type="bibr"]|.//xref[@ref-type="p"]|.//xref[@ref-type="fn"]|.//fn|.//private-char', namespaces={'mml': 'http://www.w3.org/1998/Math/MathML'})
#: XML stripper that also kills headings
strip_pmc_abstract_xml = Cleaner(strip_xpath='.//*', kill_xpath='.//disp-formula|.//inline-formula|.//mml:math|.//xref[@ref-type="bibr"]|.//xref[@ref-type="p"]|.//xref[@ref-type="fn"]|.//fn|.//private-char|.//title', namespaces={'mml': 'http://www.w3.org/1998/Math/MathML'})
#: XML stripper that also kills tables and figures
strip_pmc_paragraph_xml = Cleaner(strip_xpath='.//*', kill_xpath='.//disp-formula|.//inline-formula|.//mml:math|.//xref[@ref-type="bibr"]|.//xref[@ref-type="p"]|.//xref[@ref-type="fn"]|.//fn|.//private-char|.//table-wrap|.//fig', namespaces={'mml': 'http://www.w3.org/1998/Math/MathML'})


def space_labels(document):
    """Ensure space around bold compound labels."""
    for label in document.xpath('.//bold'):
        # TODO: Make this more permissive to match chemical_label in parser
        if not label.text or not re.match('^\(L?\d\d?[a-z]?\):?$', label.text, re.I):
            continue
        parent = label.getparent()
        previous = label.getprevious()
        if previous is None:
            text = parent.text or ''
            if not text.endswith(' '):
                parent.text = text + ' '
        else:
            text = previous.tail or ''
            if not text.endswith(' '):
                previous.tail = text + ' '
        text = label.tail or ''
        if not text.endswith(' '):
            label.tail = text + ' '
    return document


def tidy_nlm_references(document):
    """Remove punctuation around references like brackets, commas, hyphens."""

    def strip_preceding(text):
        stext = text.rstrip()
        if stext.endswith('[') or stext.endswith('('):
            #log.debug('%s -> %s' % (text, stext[:-1]))
            return stext[:-1]
        return text

    def strip_between(text):
        stext = text.strip()
        if stext in {',', '-', '\u2013', '\u2212'}:
            #log.debug('%s -> %s' % (text, ''))
            return ''
        return text

    def strip_following(text):
        stext = text.lstrip()
        if stext.startswith(']') or stext.startswith(')'):
            #log.debug('%s -> %s' % (text, stext[1:]))
            return stext[1:]
        return text

    for ref in document.xpath('.//xref[@ref-type="bibr"]'):
        parent = ref.getparent()
        previous = ref.getprevious()
        next = ref.getnext()
        if previous is None:
            parent.text = strip_preceding(parent.text or '')
        else:
            previous.tail = strip_preceding(previous.tail or '')
        if next is not None and next.tag == 'xref' and next.get('ref-type') == 'bibr':
            ref.tail = strip_between(ref.tail or '')
        ref.tail = strip_following(ref.tail or '')
    return document


class NlmXmlAuthor(Entity):
    """Author information from NLM XML file."""
    givennames = StringField('./name/given-names/text()', xpath=True)
    lastname = StringField('./name/surname/text()', xpath=True)
    email = StringField('./email/text()', xpath=True, strip=True)

    process_givennames = normalize
    process_lastname = normalize


class NlmXmlImage(Entity):
    """Figure information from NLM XML file."""
    label = StringField('./label', xpath=True)
    caption = StringField('./caption', xpath=True)
    reference = StringField('@id', xpath=True, strip=True)

    clean_caption = Chain(tidy_nlm_references, strip_pmc_xml)

    process_caption = normalize


class NlmXmlTable(Entity):
    """Table information from NLM XML file."""
    label = StringField('./label', xpath=True)
    caption = StringField('./caption', xpath=True)
    reference = StringField('@id', xpath=True)
    src = StringField('.', xpath=True, strip=True, raw=True)

    clean_caption = Chain(tidy_nlm_references, strip_pmc_xml)

    process_caption = normalize


class NlmXmlDocument(Entity):
    """Document information from a NLM  XML file."""
    # ui = StringField('/art/ui/text()', xpath=True, strip=True)
    doi = StringField('/article/front/article-meta/article-id[@pub-id-type="doi"]/text()', xpath=True, lower=True)
    pmid = IntField('/article/front/article-meta/article-id[@pub-id-type="pmid"]/text()', xpath=True)
    pmcid = IntField('/article/front/article-meta/article-id[@pub-id-type="pmc"]/text()', xpath=True)
    title = StringField('/article/front/article-meta//article-title', xpath=True)
    authors = EntityField(NlmXmlAuthor, '/article/front/article-meta//contrib[@contrib-type="author"]', xpath=True, all=True)
    journal_title = StringField('/article/front/journal-meta//journal-title/text()', xpath=True)
    journal_abbreviation = StringField('/article/front/journal-meta/journal-id[@journal-id-type="iso-abbrev"]/text()|/article/front/journal-meta/journal-id[@journal-id-type="nlm-ta"]/text()', xpath=True)
    publisher = StringField('/article/front/journal-meta//publisher-name/text()', xpath=True)
    volume = StringField('/article/front/article-meta/volume/text()', xpath=True)
    firstpage = StringField('/article/front/article-meta/fpage/text()', xpath=True)
    lastpage = StringField('/article/front/article-meta/lpage/text()', xpath=True)
    issue = StringField('/article/front/article-meta/issue/text()', xpath=True)
    issn = StringField('/article/front/journal-meta/issn/text()', xpath=True, all=True)
    coden = StringField('/article/front/journal-meta/journal-id[@journal-id-type="coden"]/text()', xpath=True, all=True)
    abstract = StringField('/article/front/article-meta/abstract', xpath=True)
    online_year = IntField('/article/front/article-meta/pub-date[@pub-type="epub"]/year/text()', xpath=True)
    online_month = IntField('/article/front/article-meta/pub-date[@pub-type="epub"]/month/text()', xpath=True)
    online_day = IntField('/article/front/article-meta/pub-date[@pub-type="epub"]/day/text()', xpath=True)
    published_year = IntField('/article/front/article-meta/pub-date[@pub-type="ppub"]/year/text()', xpath=True)
    published_month = IntField('/article/front/article-meta/pub-date[@pub-type="ppub"]/month/text()', xpath=True)
    published_day = IntField('/article/front/article-meta/pub-date[@pub-type="ppub"]/day/text()', xpath=True)
    accepted_year = IntField('/article/front/article-meta/history/date[@date-type="accepted"]/year/text()', xpath=True)
    accepted_month = IntField('/article/front/article-meta/history/date[@date-type="accepted"]/month/text()', xpath=True)
    accepted_day = IntField('/article/front/article-meta/history/date[@date-type="accepted"]/day/text()', xpath=True)
    received_year = IntField('/article/front/article-meta/history/date[@date-type="received"]/year/text()', xpath=True)
    received_month = IntField('/article/front/article-meta/history/date[@date-type="received"]/month/text()', xpath=True)
    received_day = IntField('/article/front/article-meta/history/date[@date-type="received"]/day/text()', xpath=True)
    license = UrlField('/article/front/article-meta/permissions/license/@xlink:href|/article/front/article-meta/permissions/license//ext-link/@xlink:href', xpath=True)
    # figures = EntityField(NlmXmlImage, '/article/body//fig', xpath=True, all=True)
    # tables = EntityField(NlmXmlTable, '/article/body//table-wrap', xpath=True, all=True)
    # headings = StringField('/article/body//sec/title', xpath=True, all=True)
    # paragraphs = StringField('/article/body//sec/p', xpath=True, all=True)

    clean_title = strip_pmc_xml
    clean_abstract = strip_pmc_abstract_xml
    # clean_headings = Chain(tidy_nlm_references, strip_pmc_xml)
    # clean_paragraphs = Chain(tidy_nlm_references, strip_pmc_paragraph_xml)

    process_title = normalize
    process_publisher = normalize
    process_abstract = normalize
    # process_headings = normalize
    # process_paragraphs = Chain(normalize, Discard(''))

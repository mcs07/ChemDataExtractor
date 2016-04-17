# -*- coding: utf-8 -*-
"""
chemdataextractor.scrape.springer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tools for scraping documents from Springer, Biomed Central and Chemistry Central XML files.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging

from ...text.normalize import normalize
from ...text.processors import Chain, LStrip, RStrip, Discard
from ..clean import Cleaner
from ..entity import Entity
from ..fields import StringField, EntityField, UrlField, IntField

log = logging.getLogger(__name__)


#: XML stripper that also kills equations/formulas.
strip_springer_xml = Cleaner(strip_xpath='.//*', kill_xpath='.//display-formula|.//inline-formula|.//m:math|.//abbrgrp', namespaces={'m': 'http://www.w3.org/1998/Math/MathML'})
#: XML stripper that also kills headings
strip_springer_abstract_xml = Cleaner(strip_xpath='.//*', kill_xpath='.//display-formula|.//inline-formula|.//m:math|.//abbrgrp|.//st', namespaces={'m': 'http://www.w3.org/1998/Math/MathML'})


def tidy_springer_references(document):
    """Remove punctuation around references like brackets, commas, hyphens."""

    def strip_preceding(text):
        stext = text.rstrip()
        if stext.endswith('[') or stext.endswith('('):
            #log.debug('%s -> %s' % (text, stext[:-1]))
            return stext[:-1]
        return text

    def strip_between(text):
        stext = text.strip()
        if stext in {',', '-', '\u2013'}:
            #log.debug('%s -> %s' % (text, ''))
            return ''
        return text

    def strip_following(text):
        stext = text.lstrip()
        if stext.startswith(']') or stext.startswith(')'):
            #log.debug('%s -> %s' % (text, stext[1:]))
            return stext[1:]
        return text

    for ref in document.xpath('.//abbrgrp'):
        parent = ref.getparent()
        previous = ref.getprevious()
        next = ref.getnext()
        if previous is None:
            parent.text = strip_preceding(parent.text or '')
        else:
            previous.tail = strip_preceding(previous.tail or '')
        if next is not None and next.tag == 'abbrgrp':
            ref.tail = strip_between(ref.tail or '')
        ref.tail = strip_following(ref.tail or '')
    return document



class SpringerXmlAuthor(Entity):
    """Author information from a Springer XML file."""
    firstname = StringField('./fnm', xpath=True, strip=True)
    middlename = StringField('./mnm|./mi', xpath=True, strip=True)
    lastname = StringField('./snm', xpath=True, strip=True)
    suffix = StringField('./suf', xpath=True, strip=True)
    email = StringField('./email', xpath=True, strip=True)

    process_email = Discard('')


class SpringerXmlImage(Entity):
    """Figure information from a Springer XML file."""
    label = StringField('./title', xpath=True, strip=True)
    caption = StringField('./text', xpath=True, strip=True)
    reference = StringField('@id', xpath=True, strip=True)

    clean_caption = strip_springer_xml

    process_caption = normalize


class SpringerXmlTable(Entity):
    """Table information from a Springer XML file."""
    label = StringField('./title', xpath=True, strip=True)
    caption = StringField('./caption', xpath=True, strip=True)
    reference = StringField('@id', xpath=True, strip=True)
    src = StringField('.', xpath=True, strip=True, raw=True)

    clean_caption = strip_springer_xml

    process_caption = normalize


class SpringerXmlDocument(Entity):
    """Document information from a Springer XML file."""
    ui = StringField('/art/ui/text()', xpath=True, strip=True)
    doi = StringField('/art/fm/bibl/xrefbib//pubid[@idtype="doi"]/text()', xpath=True, lower=True)
    title = StringField('/art/fm/bibl/title', xpath=True, strip=True)
    authors = EntityField(SpringerXmlAuthor, '/art/fm/bibl/aug/au', xpath=True, all=True)
    journal = StringField('/art/fm/bibl/source/text()', xpath=True, strip=True)
    firstpage = StringField('/art/fm/bibl/fpage/text()', xpath=True, strip=True)
    year = IntField('/art/fm/bibl/pubdate/text()', xpath=True)
    volume = StringField('/art/fm/bibl/volume/text()', xpath=True, strip=True)
    issue = StringField('/art/fm/bibl/issue/text()', xpath=True, strip=True)
    issn = StringField('/art/fm/bibl/issn/text()', xpath=True, strip=True)
    landing_url = UrlField('/art/fm/bibl/url/text()', xpath=True)
    abstract = StringField('/art/fm/abs/sec/p|/art/fm/abs', xpath=True, strip=True)
    published_year = IntField('/art/fm/history/pub/date/year/text()', xpath=True)
    published_month = IntField('/art/fm/history/pub/date/month/text()', xpath=True)
    published_day = IntField('/art/fm/history/pub/date/day/text()', xpath=True)
    accepted_year = IntField('/art/fm/history/acc/date/year/text()', xpath=True)
    accepted_month = IntField('/art/fm/history/acc/date/month/text()', xpath=True)
    accepted_day = IntField('/art/fm/history/acc/date/day/text()', xpath=True)
    received_year = IntField('/art/fm/history/rec/date/year/text()', xpath=True)
    received_month = IntField('/art/fm/history/rec/date/month/text()', xpath=True)
    received_day = IntField('/art/fm/history/rec/date/day/text()', xpath=True)
    license = UrlField('/art/fm/cpyrt/note/url/text()', xpath=True, strip=True)
    figures = EntityField(SpringerXmlImage, '/art/bdy//fig', xpath=True, all=True)
    schemes = EntityField(SpringerXmlImage, '/art/bdy//scheme', xpath=True, all=True)
    tables = EntityField(SpringerXmlTable, '/art/bdy//tbl|/art/bdy//table', xpath=True, all=True)
    headings = StringField('/art/bdy//st', xpath=True, strip=True, all=True)
    paragraphs = StringField('/art/bdy//sec/p', xpath=True, strip=True, all=True)

    clean_title = strip_springer_xml
    clean_abstract = Chain(tidy_springer_references, strip_springer_abstract_xml)
    clean_headings = strip_springer_xml
    clean_paragraphs = Chain(tidy_springer_references, strip_springer_xml)

    process_abstract = normalize
    process_headings = normalize
    process_paragraphs = Chain(normalize, Discard(''))
    process_license = Chain(LStrip('('), RStrip(')'))

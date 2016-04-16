# -*- coding: utf-8 -*-
"""
chemdataextractor.reader.nlm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Readers for NLM Journal Archiving and Interchange DTD XML files. (i.e. from PubMed Central)

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ..scrape.clean import clean
from ..scrape.pub.nlm import tidy_nlm_references, space_labels
from .markup import XmlReader


class NlmXmlReader(XmlReader):
    """Reader for NLM XML documents."""

    cleaners = [clean, tidy_nlm_references, space_labels]

    root_css = 'article'
    title_css = 'front article-meta article-title'
    heading_css = 'title'
    table_css = 'table-wrap'
    table_caption_css = 'caption p'
    table_head_row_css = 'table thead tr'
    table_body_row_css = 'table tbody tr'
    table_footnote_css = 'table-wrap-foot p'
    figure_css = 'fig'
    figure_caption_css = 'caption p'
    reference_css = 'xref'
    citation_css = 'ref-list ref'
    ignore_css = 'xref[ref-type="bibr"], tex-math'

    inline_elements = {
        'b', 'big', 'i', 'small', 'tt', 'abbr', 'acronym', 'cite', 'code', 'dfn', 'em', 'kbd', 'strong', 'samp', 'var',
        'a', 'bdo', 'br', 'img', 'map', 'object', 'q', 'script', 'span', 'sub', 'sup', 'button', 'input', 'label',
        'select', 'textarea', 'blink', 'font', 'marquee', 'nobr', 's', 'strike', 'u', 'wbr',
        'xref', 'underline', 'italic', 'bold', 'inline-formula', 'alternatives', 'tex-math',
        '{http://www.w3.org/1998/math/mathml}math', '{http://www.w3.org/1998/math/mathml}msubsup',
        '{http://www.w3.org/1998/math/mathml}mrow', '{http://www.w3.org/1998/math/mathml}mo',
        '{http://www.w3.org/1998/math/mathml}mi', '{http://www.w3.org/1998/math/mathml}mn'
    }

    def detect(self, fstring, fname=None):
        """"""
        if fname and not (fname.endswith('.xml') or fname.endswith('.nxml')):
            return False
        if b'xmlns="http://jats.nlm.nih.gov/ns/archiving' in fstring:
            return True
        if b'JATS-archivearticle1.dtd' in fstring:
            return True
        if b'-//NLM//DTD JATS' in fstring:
            return True
        return False

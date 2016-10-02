# -*- coding: utf-8 -*-
"""
chemdataextractor.reader.cssp
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Readers for ChemSpider SyntheticPages.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging

from ..doc.text import Footnote
from ..scrape.pub.rsc import replace_rsc_img_chars
from ..scrape.clean import clean
from .markup import HtmlReader


log = logging.getLogger(__name__)


class CsspHtmlReader(HtmlReader):
    """Reader for ChemSpider SyntheticPages HTML documents."""

    root_css = '.article-container'
    title_css = '.article-container > h2'
    heading_css = 'h3, h4, h5, h6'
    citation_css = '#csm-article-part-lead_ref > p, #csm-article-part-other_refs > p'

    def _parse_table_footnotes(self, fns, refs, specials):
        """Override to account for awkward RSC table footnotes."""
        footnotes = []
        for fn in fns:
            footnote = self._parse_text(fn, refs=refs, specials=specials, element_cls=Footnote)[0]
            footnote += Footnote('', id=fn.getprevious().get('id'))
            footnotes.append(footnote)
        return footnotes

    def detect(self, fstring, fname=None):
        """"""
        if fname and not (fname.endswith('.html') or fname.endswith('.htm')):
            return False
        if b'meta name="DC.Publisher" content="ChemSpider SyntheticPages"' in fstring:
            return True
        return False

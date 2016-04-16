# -*- coding: utf-8 -*-
"""
chemdataextractor.reader.acs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Readers for documents from the ACS.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .markup import HtmlReader
from ..scrape.clean import clean, Cleaner


#: Additional cleaner for ACS HTML  TODO: Move to ignore_css?
clean_acs_html = Cleaner(kill_xpath='.//ul[@class="anchors"] | .//div[@class="citationLinks"]')


class AcsHtmlReader(HtmlReader):
    """Reader for HTML documents from the ACS."""

    cleaners = [clean, clean_acs_html]

    root_css = '#articleMain, article'
    title_css = 'h1.articleTitle'
    heading_css = 'h2, h3, h4, h5, h6, .title1, span.title2, span.title3'
    table_css = '.NLM_table-wrap'
    table_caption_css = '.NLM_caption'
    table_footnote_css = '.footnote'
    figure_css = '.figure'
    figure_caption_css = '.caption'
    citation_css = '.reference'
    ignore_css = 'a[href="JavaScript:void(0);"], a.ref sup'

    def detect(self, fstring, fname=None):
        """"""
        if fname and not (fname.endswith('.html') or fname.endswith('.htm')):
            return False
        if b'<meta name="dc.Identifier" scheme="doi" content="10.1021/' in fstring:
            return True
        return False

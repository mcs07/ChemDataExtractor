# -*- coding: utf-8 -*-
"""
test_scrape_rsc
~~~~~~~~~~~~~~~

Test scraping documents from the Royal Society of Chemistry.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import unittest

from chemdataextractor.scrape.pub.rsc import rsc_substitute, strip_rsc_html


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestRscSubstitutor(unittest.TestCase):
    """Test escape sequences in titles/abstracts from RSC are converted to unicode characters."""

    def test_small_beta(self):
        original = 'A sensitive colorimetric strategy for sensitively monitoring cerebral [small beta]-amyloid peptides in AD based on dual-functionalized gold nanoplasmic particles'
        fixed = 'A sensitive colorimetric strategy for sensitively monitoring cerebral β-amyloid peptides in AD based on dual-functionalized gold nanoplasmic particles'
        self.assertEqual(rsc_substitute(original), fixed)

    def test_prime(self):
        original = 'Selective formation of benzo[c]cinnoline by photocatalytic reduction of 2,2[prime or minute]-dinitrobiphenyl using TiO2 and under UV light irradiation'
        fixed = 'Selective formation of benzo[c]cinnoline by photocatalytic reduction of 2,2′-dinitrobiphenyl using TiO2 and under UV light irradiation'
        self.assertEqual(rsc_substitute(original), fixed)

    def test_beta_gamma(self):
        original = '[small beta],[gamma]-Bis-substituted PNA with configurational and conformational switch: preferred binding to cDNA/RNA and cell-uptake studies'
        fixed = 'β,γ-Bis-substituted PNA with configurational and conformational switch: preferred binding to cDNA/RNA and cell-uptake studies'
        self.assertEqual(rsc_substitute(original), fixed)


class TestStripRscHtml(unittest.TestCase):

    def test_title_footnote(self):
        """Test that footnote links are removed from the end of titles."""
        html = '<span class="title_heading">Rationale for the sluggish oxidative addition of aryl halides to Au(<span class="small_caps">I</span>)<a title="Electronic supplementary information (ESI) available. CCDC 891201–891204 and 964933. For ESI and crystallographic data in CIF or other electronic format see DOI: 10.1039/c3cc48914k" href="#fn1">†</a></span>'
        stripped = '<span class="title_heading">Rationale for the sluggish oxidative addition of aryl halides to Au(I)</span>'
        self.assertEqual(strip_rsc_html.clean_html(html), stripped)

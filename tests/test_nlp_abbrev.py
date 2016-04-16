#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_nlp_abbrev
~~~~~~~~~~~~~~~

Test abbreviation detector.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import unittest

from chemdataextractor.doc.document import Document
from chemdataextractor.doc.text import Paragraph
from chemdataextractor.nlp.abbrev import ChemAbbreviationDetector


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestChemAbbreviationDetector(unittest.TestCase):

    def test_abbr1(self):
        """Test the ChemAbbreviationDetector on a simple sentence."""
        ad = ChemAbbreviationDetector()
        self.assertEqual(
            [([u'HDAC'], [u'histone', u'deacetylase'])],
            ad.detect(['as', 'histone', 'deacetylase', '(', 'HDAC', ')', 'inhibitor'])
        )

    def test_abbr2(self):
        """Test the ChemAbbreviationDetector on a simple sentence."""
        ad = ChemAbbreviationDetector()
        self.assertEqual(
            [([u'VPA'], [u'valproic', u'acid'])],
            ad.detect(['The', 'aim', 'of', 'this', 'study', 'was', 'to', 'identify', 'valproic', 'acid', '(', 'VPA', ')'])
        )

    def test_abbr3(self):
        """Test the ChemAbbreviationDetector on a simple sentence."""
        ad = ChemAbbreviationDetector()
        self.assertEqual(
            [(['15-ADON'], ['15-acetyldeoxynivalenol']), (['3-ADON'], ['3-acetyldeoxynivalenol']), (['NIV'], ['nivalenol'])],
            ad.detect(['potencies', 'of', 'DON', ',', '15-acetyldeoxynivalenol', '(', '15-ADON', ')', ',', '3-acetyldeoxynivalenol', '(', '3-ADON', ')', ',', 'fusarenon', 'X', '(', 'FX', ')', ',', 'and', 'nivalenol', '(', 'NIV', ')', 'in'])
        )

    def test_abbr4(self):
        """Test the ChemAbbreviationDetector on a simple sentence."""
        ad = ChemAbbreviationDetector()
        self.assertEqual(
            [(['THF'], ['tetrahydrofuran'])],
            ad.detect(['THF', '=', 'tetrahydrofuran'])
        )

    def test_abbr5(self):
        """Test the ChemAbbreviationDetector on a simple sentence."""
        ad = ChemAbbreviationDetector()
        self.assertEqual(
            [(['THF'], ['tetrahydrofuran'])],
            ad.detect(['THF', '(', 'tetrahydrofuran', ')'])
        )

    def test_abbr6(self):
        """Test the ChemAbbreviationDetector on a simple sentence."""
        ad = ChemAbbreviationDetector()
        self.assertEqual(
            [(['THF'], ['tetrahydrofuran'])],
            ad.detect(['(', 'tetrahydrofuran', ',', 'THF', ')'])
        )

    def test_abbr7(self):
        """Test the ChemAbbreviationDetector on a simple sentence."""
        ad = ChemAbbreviationDetector()
        self.assertEqual(
            [(['NAG'], ['N-acetyl-β-glucosaminidase'])],
            ad.detect(['blood', 'urea', 'nitrogen', ',', 'N-acetyl-β-glucosaminidase', '(', 'NAG', ')', ','])
        )

    def test_equiv1(self):
        """Test the ChemAbbreviationDetector where string equivalent is needed."""
        ad = ChemAbbreviationDetector()
        self.assertEqual(
            [(['CTAB'], ['hexadecyltrimethylammonium', 'bromide'])],
            ad.detect(['was', 'composed', 'of', 'hexadecyltrimethylammonium', 'bromide', '(', 'CTAB', ')', 'and'])
        )

    def test_equiv2(self):
        """Test the ChemAbbreviationDetector where string equivalent is needed."""
        ad = ChemAbbreviationDetector()
        self.assertEqual(
            [(['MeOH'], ['methanol'])],
            ad.detect(['was', 'mostly', 'neutral', 'in', 'methanol', '(', 'MeOH', ')'])
        )

    def test_document(self):
        elements = [
            Paragraph('''The consequences of global change on rivers include altered flow regime, and entrance of
                         compounds that may be toxic to biota. When water is scarce, a reduced dilution capacity may
                         amplify the effects of chemical pollution. Therefore, studying the response of natural
                         communities to compromised water flow and to toxicants is critical for assessing how global
                         change may affect river ecosystems. This work aims to investigate how an episode of drought
                         might influence the response of river biofilms to pulses of triclosan (TCS). The objectives
                         were to assess the separate and combined effects of simulated drought (achieved through
                         drastic flow alteration) and of TCS exposure on biofilms growing in artificial channels.'''),
            Paragraph('''Thus, three-week-old biofilms were studied under four conditions: Control (normal water flow);
                         Simulated Drought (1 week reduced flow+2 days interrupted flow); TCS only (normal water flow
                         plus a 48-h pulse of TCS); and Simulated Drought+TCS. All channels were then left for 2 weeks
                         under steady flow conditions, and their responses and recovery were studied.
                         Several descriptors of biofilms were analyzed before and after each step. Flow reduction and
                         subsequent interruption were found to provoke an increase in extracellular phosphatase
                         activity, bacterial mortality and green algae biomass. The TCS pulses severely affected
                         biofilms: they drastically reduced photosynthetic efficiency, the viability of bacteria and
                         diatoms, and phosphate uptake. Latent consequences evidenced significant combined effects
                         caused by the two stressors.'''),
            Paragraph('''The biofilms exposed only to TCS recovered far better than those
                         subjected to both altered flow and subsequent TCS exposure: the latter suffered more
                         persistent consequences, indicating that simulated drought amplified the toxicity of this
                         compound. This finding has implications for river ecosystems, as it suggests that the toxicity
                         of pollutants to biofilms may be exacerbated following a drought.''')
        ]
        d = Document(*elements)
        self.assertEqual(d.abbreviation_definitions, [([u'TCS'], [u'triclosan'], u'CM')])


if __name__ == '__main__':
    unittest.main()

# -*- coding: utf-8 -*-
"""
test_parse_doi
~~~~~~~~~~~~~~

Test DOI parser.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import unittest

from lxml import etree

from chemdataextractor.doc.text import Sentence
from chemdataextractor.parse.hrms import hrms

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestParseHRMS(unittest.TestCase):
    maxDiff = None

    def do_parse(self, input, expected):
        s = Sentence(input)
        log.debug(s)
        log.debug(s.tagged_tokens)
        result = next(hrms.scan(s.tagged_tokens))[0]
        log.debug(etree.tostring(result, pretty_print=True, encoding='unicode'))
        self.assertEqual(expected, etree.tostring(result, encoding='unicode'))

    def test_hrms1(self):
        s = 'HRMS (ESI) calcd for C34H28N4OP 539.1995 [M + H]+, found 539.1997.'
        output = '<hrms><chemical_structure>C34H28N4OP</chemical_structure></hrms>'
        self.do_parse(s, output)

    def test_hrms2(self):
        s = 'HRMS: 184.0767 [M + Na]+.'
        output = '<hrms/>'
        self.do_parse(s, output)

    def test_hrms3(self):
        s = 'HRMS-ESI (m/z): calcd. for C42H52NO9 [M + NH4]+ 714.3637, found 714.3633.'
        output = '<hrms><chemical_structure>C42H52NO9</chemical_structure></hrms>'
        self.do_parse(s, output)

    def test_hrms4(self):
        s = 'MALDI-HRMS (matrix: HCCA) Calculated for C32H48N4O6: [M + H]+ m/z 585.3607, Found 585.3636.'
        output = '<hrms><chemical_structure>C32H48N4O6</chemical_structure></hrms>'
        self.do_parse(s, output)

    def test_hrms5(self):
        s = 'HRMS (m/z): 827.6005 [M+Na]+ (calcd. for C48H84O9Na: 827.6013). '
        output = '<hrms><chemical_structure>C48H84O9Na</chemical_structure></hrms>'
        self.do_parse(s, output)

    def test_hrms6(self):
        s = 'HRMS [M−H]+ m/z calcd. for C24H32N9+ 446.2781, found 446.2775.'
        output = '<hrms><chemical_structure>C24H32N9+</chemical_structure></hrms>'
        self.do_parse(s, output)

    def test_hrms7(self):
        s = 'DCI-HRMS: m/z 289.0916 [M+H]+; (Calcd for C12H16O8, 288.0845)'
        output = '<hrms><chemical_structure>C12H16O8</chemical_structure></hrms>'
        self.do_parse(s, output)

    def test_hrms8(self):
        s = 'ES-HRMS: m/z 115.0393 [M−H]−; (Calcd for C5H7O3, 116.0473).'
        output = '<hrms><chemical_structure>C5H7O3</chemical_structure></hrms>'
        self.do_parse(s, output)

    def test_hrms9(self):
        s = 'HRMS (ESI) calcd for C27H24N4P 435.1733 [M + H]+, found 435.1738.'
        output = '<hrms><chemical_structure>C27H24N4P</chemical_structure></hrms>'
        self.do_parse(s, output)

    def test_hrms10(self):
        s = 'HRMS (ESI): [M − H]−, found 344.8591. C11H5Br2O3− requires 344.8585.'
        output = '<hrms><chemical_structure>C11H5Br2O3−</chemical_structure></hrms>'
        self.do_parse(s, output)

    def test_hrms11(self):
        s = 'HRMS (ESI): calcd. for C13H11BrO3Na+ [M + Na]+ 316.9789, found 316.9785.'
        output = '<hrms><chemical_structure>C13H11BrO3Na+</chemical_structure></hrms>'
        self.do_parse(s, output)

    def test_hrms12(self):
        s = 'HR-ESI-MS [M − H]− m/z: 447.0854, Calcd. for C21H21O9P (M − H) 447.0923.'
        output = '<hrms><chemical_structure>C21H21O9P</chemical_structure></hrms>'
        self.do_parse(s, output)

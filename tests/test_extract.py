# -*- coding: utf-8 -*-
"""
test_extract
~~~~~~~~~~~~

Test data extraction on small document examples.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import unittest

from chemdataextractor import Document
from chemdataextractor.doc import Heading, Paragraph


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


unittest.util._MAX_LENGTH = 2000


class TestExtract(unittest.TestCase):

    maxDiff = None

    def test_melting_point_heading_salt(self):
        """Test extraction of melting point from a heading and paragraphs. Example taken from patent US06840965B2."""
        d = Document(
            Heading('D. Synthesis of 4-Amino-2-(3-thienyl)phenol Hydrochloride'),
            Paragraph('3 g (13.5 mmoles) of 4-nitro-2-(3-thienyl)phenol was dissolved in 40 mL of ethanol and hydrogenated at 25° C. in the presence of 600 mg of a palladium—active carbon catalyst (10%). After the theoretically required amount of hydrogen had been absorbed, the catalyst was filtered off. Following concentration in a rotary evaporator, the reaction mixture was poured onto 20 mL of cold diethyl ether. The precipitated product was filtered off and dried.'),
            Paragraph('This gave 1.95 g (75% of the theoretical) of 4-amino-2-(3-thienyl)phenol hydrochloride with a melting point of 130-132° C.')

        )
        expected = [
            {'names': ['4-nitro-2-(3-thienyl)phenol']},
            {'names': ['ethanol']},
            {'names': ['palladium']},
            {'names': ['carbon']},
            {'names': ['hydrogen']},
            {'names': ['diethyl ether']},
            {'melting_points': [{'units': '°C', 'value': '130-132'}], 'names': ['4-Amino-2-(3-thienyl)phenol Hydrochloride', '4-amino-2-(3-thienyl)phenol hydrochloride'], 'roles': ['product']}
        ]
        self.assertEqual(expected, d.records.serialize())

    def test_parse_control_character(self):
        """Test control character in text is handled correctly."""
        # The parser doesn't like controls because it uses LXML model so must be XML compatible.
        d = Document(Paragraph('Yielding 2,4,6-trinitrotoluene,\n m.p. 20 \x0eC.'))
        expected = [{'names': ['2,4,6-trinitrotoluene']}]
        self.assertEqual(expected, d.records.serialize())




if __name__ == '__main__':
    unittest.main()

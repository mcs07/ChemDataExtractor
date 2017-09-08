# -*- coding: utf-8 -*-
"""
test_extract
~~~~~~~~~~~~

Test data extraction on small document examples.

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

    def test_title_parse(self):
        """Test heading managed correctly"""
        d = Document(
            Heading('3.2. Experimental Details'),
            Heading('3.2.1. Synthesis of Phosphorus Ylide 5'),
            Paragraph('N-Benzyl-2-chloroacetamide (2): Chloroacetamide 2 was prepared following the procedure described in the literature [23]. To a stirred solution of benzylamine (7.8 mL, 70.8 mmol) in toluene (60 mL) under cooling with ice bath, chloroacetyl chloride (4 g, 35.4 mmol) was slowly added. The reaction mixture was stirred vigorously for 1h at room temperature. The solvent was evaporated under vacuum, the crude reaction was dissolved in dichloromethane (100 mL) and washed with water (3 × 50 mL). The organic layer was dried over anhydrous MgSO4, filtered and the solvent evaporated under vacuum. The product was obtained as a white solid (6.30 g, 97%). m.p. 91–92 °C (93–96 °C from literature) [23]; 1H-NMR (CDCl3) δ 4.11 (s, 2H), 4.50 (d, 2H, J = 6.0 Hz), 6.89 (br s, 1H), 7.26–7.36 (m, 5H, Ar-H).'),
            Paragraph('1-Benzyl-5-(chloromethyl)-1H-tetrazole (3): Compound 3 was prepared by an analogous method to that described in the literature [24]. PCl5 (7.06 g, 33.9 mmol) was added slowly to a solution of N-benzyl-2-chloroacetamide (5.66 g, 30.8 mmol) in toluene (50 mL) under cooling with ice-water bath. The mixture was stirred at room temperature for 2 h, then NaN3 (3.01 g, 46.3 mmol) was added. The reaction mixture was stirred at room temperature for 30 min, water (0.8 mL) was added dropwise and the whole was refluxed for 5 h. After cooling, the reaction mixture was poured into water and extracted with chloroform. The combined organic layers were washed successively with water, NaOH solution 1M and saturated NaCl solution and dried over anhydrous MgSO4. After removal of the solvent, the crude product was purified by flash chromatography (ethyl acetate/hexane (1:2)) affording the tetrazole 3 as light yellow solid (3.47 g, 54%). m.p. 57–59 °C (from diethyl ether) (62–63 °C from literature) [24]; 1H-NMR (CDCl3) δ (ppm) 4.62 (s, 2H), 5.68 (s, 2H), 7.28–7.30 (m, 2H, Ar-H), 7.39–7.40 (m, 3H, Ar-H).')
        )

        print(d.records.serialize())




if __name__ == '__main__':
    unittest.main()

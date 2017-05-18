# -*- coding: utf-8 -*-
"""
test_doc_table
~~~~~~~~~~~~~~

Test the Table Document element.

"""





import logging
import unittest

from chemdataextractor.doc.table import Table, Cell
from chemdataextractor.doc.text import Caption


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestTable(unittest.TestCase):
    """Simple Table instantiation tests."""

    maxDiff = None

    def test_uvvis_table(self):
        """"""
        t = Table(
            caption=Caption('Selected photophysical properties of biarylsubstituted pyrazoles 5–8 and 1-methyl-3,5-diphenylpyrazole (9) at room temperature'),
            headings=[
                [
                    Cell('Compound'),
                    Cell('Absorption maxima λmax,abs (ε) [nm] (L cm−1 mol−1)'),
                    Cell('Emission maxima λmax,em (Φf) [nm] (a.u.)'),
                    Cell('Stokes-shift Δṽ [cm−1]')
                ]
            ],
            rows=[
                [Cell(' 5a '), Cell('273.5 (40 100)'), Cell('357.0 (0.77)'), Cell('9400')],
                [Cell(' 5b '), Cell('268.5 (36 700)'), Cell('359.0 (0.77)'), Cell('8600')],
                [Cell('Coumarin 343'), Cell('263.0 (38 400)'), Cell('344.5 (0.67)'), Cell('9000')],
                [Cell(' 5d '), Cell('281.0 (34 200)'), Cell('351.5 (0.97)'), Cell('7100')],
                [Cell(' 5e '), Cell('285.0 (44 000)'), Cell('382.0 (0.35)'), Cell('8900')],
                [Cell(' 5f '), Cell('289.0 (43 300)'), Cell('363.0 (0.80)'), Cell('7100')],
                [Cell(' 5g '), Cell('285.0 (42 000)'), Cell('343.5 (0.86)'), Cell('6000')],
                [Cell(' 6a '), Cell('283.5 (35 600)'), Cell('344.5 (0.49)'), Cell('6300')],
                [Cell(' 6b '), Cell('267.5 (35 800)'), Cell('338.5 (0.83)'), Cell('7800')],
                [Cell(' 6c '), Cell('286.0 (33 000)'), Cell('347.0 (0.27)'), Cell('6200')],
                [Cell(' 6d '), Cell('306.5 (36 600)'), Cell('384.0 (0.10)'), Cell('6600')],
                [Cell(' 7 '), Cell('288.5 (62 500)'), Cell('367.0 (0.07)'), Cell('7400')],
                [Cell('Compound 8a '), Cell('257.0 (36 300), 293.0 sh (25 000)'), Cell('385.0 (0.41)'), Cell('8200')],
                [Cell(' 8b '), Cell('257.0 (32 000), 296.0 sh (23000)'), Cell('388.0 (0.33)'), Cell('8000')],
                [Cell(' 8c '), Cell('257.0 (27 400), 307.5 (18900)'), Cell('387.0 (0.12)'), Cell('6700')],
                [Cell(' 8d '), Cell('268.5 (29 500)'), Cell('385.0 (0.29)'), Cell('11 300')],
                [Cell('Dye 8e '), Cell('261.5 (39 900), 288.0 sh (29 600), 311.0 sh (20 500)'), Cell('386.5 (0.37)'), Cell('6300')],
                [Cell(' 8f '), Cell('256.5 (27 260), 296.0 (28404)'), Cell('388.5 (0.35)'), Cell('8000')],
                [Cell(' 8g '), Cell('272.5 (39 600)'), Cell('394.0 (0.30)'), Cell('11 300')],
                [Cell(' 8h '), Cell('286.0 (22 900)'), Cell('382.5 (0.33)'), Cell('8800')],
                [Cell(' 9 '), Cell('254.0 (28 800)'), Cell('338.5 (0.40)'), Cell('9800')]]
        )

        gold = [
            {'labels': ['5a'], 'uvvis_spectra': [{'peaks': [{'units': 'nm', 'extinction_units': 'L cm \u2212 1 mol \u2212 1', 'extinction': '40100', 'value': '273.5'}]}], 'quantum_yields': [{'value': '0.77'}]},
            {'labels': ['5b'], 'uvvis_spectra': [{'peaks': [{'units': 'nm', 'extinction_units': 'L cm \u2212 1 mol \u2212 1', 'extinction': '36700', 'value': '268.5'}]}], 'quantum_yields': [{'value': '0.77'}]},
            {'names': ['Coumarin 343'], 'quantum_yields': [{'value': '0.67'}], 'uvvis_spectra': [{'peaks': [{'units': 'nm', 'extinction_units': 'L cm \u2212 1 mol \u2212 1', 'extinction': '38400', 'value': '263.0'}]}]},
            {'labels': ['5d'], 'uvvis_spectra': [{'peaks': [{'units': 'nm', 'extinction_units': 'L cm \u2212 1 mol \u2212 1', 'extinction': '34200', 'value': '281.0'}]}], 'quantum_yields': [{'value': '0.97'}]},
            {'labels': ['5e'], 'uvvis_spectra': [{'peaks': [{'units': 'nm', 'extinction_units': 'L cm \u2212 1 mol \u2212 1', 'extinction': '44000', 'value': '285.0'}]}], 'quantum_yields': [{'value': '0.35'}]},
            {'labels': ['5f'], 'uvvis_spectra': [{'peaks': [{'units': 'nm', 'extinction_units': 'L cm \u2212 1 mol \u2212 1', 'extinction': '43300', 'value': '289.0'}]}], 'quantum_yields': [{'value': '0.80'}]},
            {'labels': ['5g'], 'uvvis_spectra': [{'peaks': [{'units': 'nm', 'extinction_units': 'L cm \u2212 1 mol \u2212 1', 'extinction': '42000', 'value': '285.0'}]}], 'quantum_yields': [{'value': '0.86'}]},
            {'labels': ['6a'], 'uvvis_spectra': [{'peaks': [{'units': 'nm', 'extinction_units': 'L cm \u2212 1 mol \u2212 1', 'extinction': '35600', 'value': '283.5'}]}], 'quantum_yields': [{'value': '0.49'}]},
            {'labels': ['6b'], 'uvvis_spectra': [{'peaks': [{'units': 'nm', 'extinction_units': 'L cm \u2212 1 mol \u2212 1', 'extinction': '35800', 'value': '267.5'}]}], 'quantum_yields': [{'value': '0.83'}]},
            {'labels': ['6c'], 'uvvis_spectra': [{'peaks': [{'units': 'nm', 'extinction_units': 'L cm \u2212 1 mol \u2212 1', 'extinction': '33000', 'value': '286.0'}]}], 'quantum_yields': [{'value': '0.27'}]},
            {'labels': ['6d'], 'uvvis_spectra': [{'peaks': [{'units': 'nm', 'extinction_units': 'L cm \u2212 1 mol \u2212 1', 'extinction': '36600', 'value': '306.5'}]}], 'quantum_yields': [{'value': '0.10'}]},
            {'labels': ['7'], 'uvvis_spectra': [{'peaks': [{'units': 'nm', 'extinction_units': 'L cm \u2212 1 mol \u2212 1', 'extinction': '62500', 'value': '288.5'}]}], 'quantum_yields': [{'value': '0.07'}]},
            {'labels': ['8a'], 'uvvis_spectra': [{'peaks': [{'units': 'nm', 'extinction_units': 'L cm \u2212 1 mol \u2212 1', 'extinction': '36300', 'value': '257.0'}, {'units': 'nm', 'extinction_units': 'L cm \u2212 1 mol \u2212 1', 'shape': 'sh', 'extinction': '25000', 'value': '293.0'}]}], 'quantum_yields': [{'value': '0.41'}]},
            {'labels': ['8b'], 'uvvis_spectra': [{'peaks': [{'units': 'nm', 'extinction_units': 'L cm \u2212 1 mol \u2212 1', 'extinction': '32000', 'value': '257.0'}, {'units': 'nm', 'extinction_units': 'L cm \u2212 1 mol \u2212 1', 'shape': 'sh', 'extinction': '23000', 'value': '296.0'}]}], 'quantum_yields': [{'value': '0.33'}]},
            {'labels': ['8c'], 'uvvis_spectra': [{'peaks': [{'units': 'nm', 'extinction_units': 'L cm \u2212 1 mol \u2212 1', 'extinction': '27400', 'value': '257.0'}, {'units': 'nm', 'extinction_units': 'L cm \u2212 1 mol \u2212 1', 'extinction': '18900', 'value': '307.5'}]}], 'quantum_yields': [{'value': '0.12'}]},
            {'labels': ['8d'], 'uvvis_spectra': [{'peaks': [{'units': 'nm', 'extinction_units': 'L cm \u2212 1 mol \u2212 1', 'extinction': '29500', 'value': '268.5'}]}], 'quantum_yields': [{'value': '0.29'}]},
            {'labels': ['8e'], 'quantum_yields': [{'value': '0.37'}], 'uvvis_spectra': [{'peaks': [{'units': 'nm', 'extinction_units': 'L cm \u2212 1 mol \u2212 1', 'extinction': '39900', 'value': '261.5'}, {'units': 'nm', 'extinction_units': 'L cm \u2212 1 mol \u2212 1', 'shape': 'sh', 'extinction': '29600', 'value': '288.0'}, {'units': 'nm', 'extinction_units': 'L cm \u2212 1 mol \u2212 1', 'shape': 'sh', 'extinction': '20500', 'value': '311.0'}]}]},
            {'labels': ['8f'], 'uvvis_spectra': [{'peaks': [{'units': 'nm', 'extinction_units': 'L cm \u2212 1 mol \u2212 1', 'extinction': '27260', 'value': '256.5'}, {'units': 'nm', 'extinction_units': 'L cm \u2212 1 mol \u2212 1', 'extinction': '28404', 'value': '296.0'}]}], 'quantum_yields': [{'value': '0.35'}]},
            {'labels': ['8g'], 'uvvis_spectra': [{'peaks': [{'units': 'nm', 'extinction_units': 'L cm \u2212 1 mol \u2212 1', 'extinction': '39600', 'value': '272.5'}]}], 'quantum_yields': [{'value': '0.30'}]},
            {'labels': ['8h'], 'uvvis_spectra': [{'peaks': [{'units': 'nm', 'extinction_units': 'L cm \u2212 1 mol \u2212 1', 'extinction': '22900', 'value': '286.0'}]}], 'quantum_yields': [{'value': '0.33'}]},
            {'labels': ['9'], 'uvvis_spectra': [{'peaks': [{'units': 'nm', 'extinction_units': 'L cm \u2212 1 mol \u2212 1', 'extinction': '28800', 'value': '254.0'}]}], 'quantum_yields': [{'value': '0.40'}]},
        ]

        for record in t.records:
            print(record.serialize())

        self.assertEqual(gold, [record.serialize() for record in t.records])

    def test_spectroscopic_table(self):
        """"""
        t = Table(
            caption=Caption('Spectroscopic properties of Coumarins in acetonitrile at 298 K.'),
            headings=[
                [
                    Cell(''),           # Blank  compound heading
                    Cell('λmax (nm)'),
                    Cell('ε (M–1 cm–1)'),
                    Cell('λem (nm)'),
                    Cell('ϕ')
                ]
            ],
            rows=[
                [Cell('Coumarin 343'), Cell('398'), Cell('40 800'), Cell('492'), Cell('0.52')],
                [Cell('C144'), Cell('429'), Cell('9500'), Cell('601'), Cell('N/A')],
                [Cell('Coumarin 34'), Cell('269'), Cell('-'), Cell('435'), Cell('<0.01')],
            ]
        )
        # for record in t.caption.records:
        #     print(record.to_primitive())
        #     print(record.is_contextual)
        gold = [
            {'names': ['Coumarin 343'], 'quantum_yields': [{'type': '\u03d5', 'solvent': 'acetonitrile', 'value': '0.52', 'temperature': '298', 'temperature_units': 'K'}], 'uvvis_spectra': [{'temperature': '298', 'temperature_units': 'K', 'solvent': 'acetonitrile', 'peaks': [{'units': 'nm', 'value': '398'}]}, {'temperature': '298', 'temperature_units': 'K', 'solvent': 'acetonitrile', 'peaks': [{'extinction': '40800', 'extinction_units': 'M \u2013 1 cm \u2013 1'}]} ]},
            {'labels': ['C144'], 'uvvis_spectra': [{'temperature': '298', 'temperature_units': 'K', 'solvent': 'acetonitrile', 'peaks': [{'units': 'nm', 'value': '429'}]}, {'temperature': '298', 'temperature_units': 'K', 'solvent': 'acetonitrile', 'peaks': [{'extinction': '9500', 'extinction_units': 'M \u2013 1 cm \u2013 1'}]}]},
            {'names': ['Coumarin 34'], 'quantum_yields': [{'type': '\u03d5', 'solvent': 'acetonitrile', 'value': '<0.01', 'temperature': '298', 'temperature_units': 'K'}], 'uvvis_spectra': [{'temperature': '298', 'temperature_units': 'K', 'solvent': 'acetonitrile', 'peaks': [{'units': 'nm', 'value': '269'}]}]},
            {'names': ['Coumarins']},
            {'names': ['acetonitrile']}
        ]

        # for record in t.records:
        #     print(record.to_primitive())

        self.assertEqual(gold, [record.serialize() for record in t.records])

if __name__ == '__main__':
    unittest.main()

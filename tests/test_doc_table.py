# -*- coding: utf-8 -*-
"""
test_doc_table
~~~~~~~~~~~~~~

Test the Table Document element.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
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
            {'labels': [u'5a'], 'uvvis_spectra': [{'peaks': [{'units': u'nm', 'extinction_units': u'L cm \u2212 1 mol \u2212 1', 'extinction': u'40100', 'value': u'273.5'}]}], 'quantum_yields': [{'value': u'0.77'}]},
            {'labels': [u'5b'], 'uvvis_spectra': [{'peaks': [{'units': u'nm', 'extinction_units': u'L cm \u2212 1 mol \u2212 1', 'extinction': u'36700', 'value': u'268.5'}]}], 'quantum_yields': [{'value': u'0.77'}]},
            {'names': [u'Coumarin 343'], 'quantum_yields': [{'value': u'0.67'}], 'uvvis_spectra': [{'peaks': [{'units': u'nm', 'extinction_units': u'L cm \u2212 1 mol \u2212 1', 'extinction': u'38400', 'value': u'263.0'}]}]},
            {'labels': [u'5d'], 'uvvis_spectra': [{'peaks': [{'units': u'nm', 'extinction_units': u'L cm \u2212 1 mol \u2212 1', 'extinction': u'34200', 'value': u'281.0'}]}], 'quantum_yields': [{'value': u'0.97'}]},
            {'labels': [u'5e'], 'uvvis_spectra': [{'peaks': [{'units': u'nm', 'extinction_units': u'L cm \u2212 1 mol \u2212 1', 'extinction': u'44000', 'value': u'285.0'}]}], 'quantum_yields': [{'value': u'0.35'}]},
            {'labels': [u'5f'], 'uvvis_spectra': [{'peaks': [{'units': u'nm', 'extinction_units': u'L cm \u2212 1 mol \u2212 1', 'extinction': u'43300', 'value': u'289.0'}]}], 'quantum_yields': [{'value': u'0.80'}]},
            {'labels': [u'5g'], 'uvvis_spectra': [{'peaks': [{'units': u'nm', 'extinction_units': u'L cm \u2212 1 mol \u2212 1', 'extinction': u'42000', 'value': u'285.0'}]}], 'quantum_yields': [{'value': u'0.86'}]},
            {'labels': [u'6a'], 'uvvis_spectra': [{'peaks': [{'units': u'nm', 'extinction_units': u'L cm \u2212 1 mol \u2212 1', 'extinction': u'35600', 'value': u'283.5'}]}], 'quantum_yields': [{'value': u'0.49'}]},
            {'labels': [u'6b'], 'uvvis_spectra': [{'peaks': [{'units': u'nm', 'extinction_units': u'L cm \u2212 1 mol \u2212 1', 'extinction': u'35800', 'value': u'267.5'}]}], 'quantum_yields': [{'value': u'0.83'}]},
            {'labels': [u'6c'], 'uvvis_spectra': [{'peaks': [{'units': u'nm', 'extinction_units': u'L cm \u2212 1 mol \u2212 1', 'extinction': u'33000', 'value': u'286.0'}]}], 'quantum_yields': [{'value': u'0.27'}]},
            {'labels': [u'6d'], 'uvvis_spectra': [{'peaks': [{'units': u'nm', 'extinction_units': u'L cm \u2212 1 mol \u2212 1', 'extinction': u'36600', 'value': u'306.5'}]}], 'quantum_yields': [{'value': u'0.10'}]},
            {'labels': [u'7'], 'uvvis_spectra': [{'peaks': [{'units': u'nm', 'extinction_units': u'L cm \u2212 1 mol \u2212 1', 'extinction': u'62500', 'value': u'288.5'}]}], 'quantum_yields': [{'value': u'0.07'}]},
            {'labels': [u'8a'], 'uvvis_spectra': [{'peaks': [{'units': u'nm', 'extinction_units': u'L cm \u2212 1 mol \u2212 1', 'extinction': u'36300', 'value': u'257.0'}, {'units': u'nm', 'extinction_units': u'L cm \u2212 1 mol \u2212 1', 'shape': u'sh', 'extinction': u'25000', 'value': u'293.0'}]}], 'quantum_yields': [{'value': u'0.41'}]},
            {'labels': [u'8b'], 'uvvis_spectra': [{'peaks': [{'units': u'nm', 'extinction_units': u'L cm \u2212 1 mol \u2212 1', 'extinction': u'32000', 'value': u'257.0'}, {'units': u'nm', 'extinction_units': u'L cm \u2212 1 mol \u2212 1', 'shape': u'sh', 'extinction': u'23000', 'value': u'296.0'}]}], 'quantum_yields': [{'value': u'0.33'}]},
            {'labels': [u'8c'], 'uvvis_spectra': [{'peaks': [{'units': u'nm', 'extinction_units': u'L cm \u2212 1 mol \u2212 1', 'extinction': u'27400', 'value': u'257.0'}, {'units': u'nm', 'extinction_units': u'L cm \u2212 1 mol \u2212 1', 'extinction': u'18900', 'value': u'307.5'}]}], 'quantum_yields': [{'value': u'0.12'}]},
            {'labels': [u'8d'], 'uvvis_spectra': [{'peaks': [{'units': u'nm', 'extinction_units': u'L cm \u2212 1 mol \u2212 1', 'extinction': u'29500', 'value': u'268.5'}]}], 'quantum_yields': [{'value': u'0.29'}]},
            {'labels': [u'8e'], 'quantum_yields': [{'value': u'0.37'}], 'uvvis_spectra': [{'peaks': [{'units': u'nm', 'extinction_units': u'L cm \u2212 1 mol \u2212 1', 'extinction': u'39900', 'value': u'261.5'}, {'units': u'nm', 'extinction_units': u'L cm \u2212 1 mol \u2212 1', 'shape': u'sh', 'extinction': u'29600', 'value': u'288.0'}, {'units': u'nm', 'extinction_units': u'L cm \u2212 1 mol \u2212 1', 'shape': u'sh', 'extinction': u'20500', 'value': u'311.0'}]}]},
            {'labels': [u'8f'], 'uvvis_spectra': [{'peaks': [{'units': u'nm', 'extinction_units': u'L cm \u2212 1 mol \u2212 1', 'extinction': u'27260', 'value': u'256.5'}, {'units': u'nm', 'extinction_units': u'L cm \u2212 1 mol \u2212 1', 'extinction': u'28404', 'value': u'296.0'}]}], 'quantum_yields': [{'value': u'0.35'}]},
            {'labels': [u'8g'], 'uvvis_spectra': [{'peaks': [{'units': u'nm', 'extinction_units': u'L cm \u2212 1 mol \u2212 1', 'extinction': u'39600', 'value': u'272.5'}]}], 'quantum_yields': [{'value': u'0.30'}]},
            {'labels': [u'8h'], 'uvvis_spectra': [{'peaks': [{'units': u'nm', 'extinction_units': u'L cm \u2212 1 mol \u2212 1', 'extinction': u'22900', 'value': u'286.0'}]}], 'quantum_yields': [{'value': u'0.33'}]},
            {'labels': [u'9'], 'uvvis_spectra': [{'peaks': [{'units': u'nm', 'extinction_units': u'L cm \u2212 1 mol \u2212 1', 'extinction': u'28800', 'value': u'254.0'}]}], 'quantum_yields': [{'value': u'0.40'}]},
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

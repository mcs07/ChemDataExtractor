# -*- coding: utf-8 -*-
"""
test_text_chem
~~~~~~~~~~~~~~

Test the text chem package.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import unittest

from chemdataextractor.text.chem import SOLVENT_RE, INCHI_RE, SMILES_RE


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestRegex(unittest.TestCase):

    def test_solvent(self):
        """Test solvent regex."""
        self.assertEqual([u'CH2Cl2'], SOLVENT_RE.findall(u'λmax(CH2Cl2)/nm'))
        self.assertEqual([u'acetonitrile', u'C6H6'], SOLVENT_RE.findall(u'Measured in acetonitrile and C6H6'))
        self.assertEqual([u'd2-dichloromethane'], SOLVENT_RE.findall(u'Spectra in d2-dichloromethane'))
        self.assertEqual([u'isopropanol'], SOLVENT_RE.findall(u'The solvent was isopropanol'))
        self.assertEqual([u'1,2-dichlorobenzene'], SOLVENT_RE.findall(u'Mixed with 1,2-dichlorobenzene.'))
        self.assertEqual([u'CHCl3', u'HCl'], SOLVENT_RE.findall(u'The mixture CHCl3/HCl was added.'))
        self.assertEqual([u'Ethyl acetate', u'Diethyl ether'], SOLVENT_RE.findall(u'Ethyl acetate. Diethyl ether.'))
        self.assertEqual([u'Ethylacetate', u'Diethylether'], SOLVENT_RE.findall(u'Ethylacetate. Diethylether.'))
        self.assertEqual([], SOLVENT_RE.findall(u'[Rh2(dihex)4]2+'))

    def test_inchi(self):
        """Test InChI regex."""
        self.assertFalse(INCHI_RE.match(u'InChI'))
        self.assertFalse(INCHI_RE.match(u'InChI=1S'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C7H4N.Li/c1-2-7-4-3-5-8-6-7;/h3-6H;/q-1;+1'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C9H13BO2S/c1-9(2)6-11-10(12-7-9)8-4-3-5-13-8/h3-5H,6-7H2,1-2H3'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C7H12O/c8-6-7-4-2-1-3-5-7/h6-7H,1-5H2'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/Ca.2H2O.2H2/h;2*1H2;2*1H'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/2BrH.Fe/h2*1H;'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C8H2Br2N2/c9-7-1-5(3-11)6(4-12)2-8(7)10/h1-2H'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C9H10O3/c1-11-8-3-4-9(12-2)7(5-8)6-10/h3-6H,1-2H3'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C8H13NOS/c1-6-11-7-8(1)9-2-4-10-5-3-9/h1H,2-7H2'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C7H10N.BrH/c1-2-8-6-4-3-5-7-8;/h3-7H,2H2,1H3;1H/q+1;/p-1'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C13H9N.C2H7N5/c1-2-6-11-10(5-1)9-14-13-8-4-3-7-12(11)13;3-1(4)7-2(5)6/h1-9H;(H7,3,4,5,6,7)'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C26H56N/c1-5-7-9-11-13-15-17-19-21-23-25-27(3,4)26-24-22-20-18-16-14-12-10-8-6-2/h5-26H2,1-4H3/q+1'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C12H10Si/c1-2-5-10-9(4-1)8-12-11(10)6-3-7-13-12/h1-7,13H,8H2'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C7H10N2.Au/c1-9(2)7-3-5-8-6-4-7;/h3-6H,1-2H3;'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C8H6Cl4/c1-3(2)4-5(9)7(11)8(12)6(4)10/h1-2H3'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/BH3IP/c2-1-3/h1H,3H2'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C6H15N3/c1-2-4-8-9-6-5-7-3-1/h7-9H,1-6H2'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/2C8H5.Ru/c2*1-2-8-6-4-3-5-7-8;/h2*3-7H;/q2*-1;+2'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/HI/h1H/i/hD'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/F5P.FH.H3N/c1-6(2,3,4)5;;/h;1H;1H3'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C10H16/c1-8(2)10-6-4-9(3)5-7-10/h4,10H,1,5-7H2,2-3H3'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/Mo.4O/q;;;2*-1'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/In.N'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/Au.H3P/h;1H3'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/Cd.Hg.Te'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/3CH3.In/h3*1H3;'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/In.3H2O/h;3*1H2/q+3;;;/p-3'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/I.W'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/Pt.H/q+1;'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/p+1/i/hD'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/p+1/i/hH'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/p+1/i/hT'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C5H5N5O/c6-5-9-3-2(4(11)10-5)7-1-8-3/h1H,(H4,6,7,8,9,10,11)'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C2H4ClNO2/c3-1(4)2(5)6/h1H,4H2,(H,5,6)/p+1/t1-/m1/s1'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/H2/h1H/i1+2T'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/CH2Cl2/c2-1-3/h1H2/i1D2'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/H2/h1H/i1+1D'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/H2O4S/c1-5(2,3)4/h(H2,1,2,3,4)/i/hD2'))

    def test_smiles(self):
        self.assertTrue(SMILES_RE.match(u'S=S'))
        self.assertTrue(SMILES_RE.match(u'P1P=P1'))
        self.assertTrue(SMILES_RE.match(u'[V].[Cu+2]'))
        self.assertTrue(SMILES_RE.match(u'O'))
        self.assertTrue(SMILES_RE.match(u'CC1=C(SC=N1)C=CC2=C(NC(SC2)C(C(=O)O)NC(=O)C(=NOC)C3=CSC(=N3)N)C(=O)O'))
        self.assertTrue(SMILES_RE.match(u'C1=CC=C(C=C1)C2=CC=C(C=C2)C3=NN=C(O3)C4=CC=CC=C4'))
        self.assertTrue(SMILES_RE.match(u'CC(=O)OO'))
        self.assertTrue(SMILES_RE.match(u'CCCCCCCC/C=C\CCCCCCCCN'))
        self.assertTrue(SMILES_RE.match(u'C[N+](C)(C)CCCCCC[N+](C)(C)C.[Br-]'))
        self.assertTrue(SMILES_RE.match(u'C([C@H](C(=O)O)N)F'))
        self.assertTrue(SMILES_RE.match(u'[Ru]'))
        self.assertTrue(SMILES_RE.match(u'[S-2].[Cu+2].[Cu+2]'))
        self.assertTrue(SMILES_RE.match(u'[Cd]=[Te]'))
        self.assertTrue(SMILES_RE.match(u'C1C[C@H](OC1)C(=O)O'))
        self.assertTrue(SMILES_RE.match(u'C(=O)(O)[O-].[OH-].[Zn+2]'))
        self.assertTrue(SMILES_RE.match(u'N#N'))
        self.assertTrue(SMILES_RE.match(u'[HH]'))
        self.assertTrue(SMILES_RE.match(u'[Li+].[Li+].[O-][Ti](=O)[O-]'))
        self.assertTrue(SMILES_RE.match(u'[F-]'))
        self.assertTrue(SMILES_RE.match(u'CC(C)[C@@H](C(=O)O)N'))
        self.assertTrue(SMILES_RE.match(u'CC(C)C(C#C)O'))
        self.assertTrue(SMILES_RE.match(u'CCCC#N'))
        self.assertTrue(SMILES_RE.match(u'C(/C=C\O)Cl'))


if __name__ == '__main__':
    unittest.main()


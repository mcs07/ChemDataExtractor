# -*- coding: utf-8 -*-
"""
test_model
~~~~~~~~~~

Test extracted data model.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import unittest

from chemdataextractor.model import Compound, MeltingPoint, UvvisSpectrum, UvvisPeak


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestModel(unittest.TestCase):

    maxDiff = None

    def test_serialize(self):
        """Test model serializes as expected."""
        self.assertEqual(Compound(names=['Coumarin 343']).serialize(), {'names': ['Coumarin 343']})

    def test_is_unidentified(self):
        """Test is_unidentified method returns expected result."""
        self.assertEqual(Compound().is_unidentified, True)
        self.assertEqual(Compound(names=['Coumarin 343']).is_unidentified, False)
        self.assertEqual(Compound(labels=['3a']).is_unidentified, False)
        self.assertEqual(Compound(names=['Coumarin 343'], labels=['3a']).is_unidentified, False)
        self.assertEqual(Compound(melting_points=[MeltingPoint(value='250')]).is_unidentified, True)

    def test_is_contextual(self):
        """Test is_contextual method returns expected result."""
        self.assertEqual(Compound(names=['Coumarin 343']).is_contextual, False)
        self.assertEqual(Compound(melting_points=[MeltingPoint(value='240')]).is_contextual, False)
        self.assertEqual(Compound(melting_points=[MeltingPoint(units='K')]).is_contextual, True)
        self.assertEqual(Compound(melting_points=[MeltingPoint(apparatus='Some apparatus')]).is_contextual, True)
        self.assertEqual(Compound(labels=['3a'], melting_points=[MeltingPoint(apparatus='Some apparatus')]).is_contextual, False)
        self.assertEqual(Compound(uvvis_spectra=[UvvisSpectrum(apparatus='Some apparatus')]).is_contextual, True)
        self.assertEqual(Compound(uvvis_spectra=[UvvisSpectrum(peaks=[UvvisPeak(value='378')])]).is_contextual, False)
        self.assertEqual(Compound(uvvis_spectra=[UvvisSpectrum(peaks=[UvvisPeak(units='nm')])]).is_contextual, True)


if __name__ == '__main__':
    unittest.main()

# -*- coding: utf-8 -*-
"""
test_biblio
~~~~~~~~~~~

Test the biblio package.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import unittest

from chemdataextractor.biblio import BibtexParser, PersonName


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestBibtexParser(unittest.TestCase):

    maxDiff = None

    bib1 = '''@Article{C3CE27013K,
author ="Zakharov, Boris A. and Losev, Evgeniy A. and Boldyreva, Elena V.",
title  ="Polymorphism of {"}glycine-glutaric acid{"} co-crystals: the same phase at low temperatures and high pressures",
journal  ="CrystEngComm",
year  ="2013",
volume  ="15",
issue  ="9",
pages  ="1693-1697",
publisher  ="The Royal Society of Chemistry",
doi  ="10.1039/C3CE27013K",
url  ="http://dx.doi.org/10.1039/C3CE27013K"}
'''

    bib1a = {
        'publisher': 'The Royal Society of Chemistry',
        'doi': '10.1039/C3CE27013K',
        'title': 'Polymorphism of "glycine-glutaric acid" co-crystals: the same phase at low temperatures and high pressures',
        'issue': '9',
        'journal': 'CrystEngComm',
        'author': ['Zakharov, Boris A.', 'Losev, Evgeniy A.', 'Boldyreva, Elena V.'],
        'pages': '1693-1697',
        'volume': '15',
        'link': 'http://dx.doi.org/10.1039/C3CE27013K',
        'year': '2013',
        'type': 'article',
        'id': 'C3CE27013K'
    }

    bib2 = '''@Article{C3RA40330K,
author ="Mutlu, Hatice and Hofsa[German sz ligature}, Robert and Montenegro, Rowena E. and Meier, Michael A. R.",
title  ="Self-metathesis of fatty acid methyl esters: full conversion by choosing the appropriate plant oil",
journal  ="RSC Adv.",
year  ="2013",
volume  ="3",
issue  ="15",
pages  ="4927-4934",
publisher  ="The Royal Society of Chemistry",
doi  ="10.1039/C3RA40330K",
url  ="http://dx.doi.org/10.1039/C3RA40330K"}
'''

    bib2a = {'publisher': 'The Royal Society of Chemistry',
             'doi': '10.1039/C3RA40330K',
             'title': 'Self-metathesis of fatty acid methyl esters: full conversion by choosing the appropriate plant oil',
             'issue': '15',
             'journal': 'RSC Adv.',
             'author': [
                 'Mutlu, Hatice and Hofsa[German sz ligature, Robert',
                 'Montenegro, Rowena E.',
                 'Meier, Michael A. R.'
             ],
             'pages': '4927-4934',
             'volume': '3',
             'link': 'http://dx.doi.org/10.1039/C3RA40330K',
             'year': '2013',
             'type': 'article',
             'id': 'C3RA40330K'
    }

    def test_bib1(self):
        """Test BibTeX example 1."""
        bib = BibtexParser(self.bib1)
        bib.parse()
        self.assertEqual(self.bib1a, bib.records_list[0])

    def test_bib2(self):
        """Test BibTeX example 2."""
        bib = BibtexParser(self.bib2)
        bib.parse()
        self.assertEqual(self.bib2a, bib.records_list[0])

    def test_parse_names(self):
        res = ['Bernd van Linder', 'John-Jules Ch. Meyer', 'Eijkhof, Frank van den']
        self.assertEqual(res, BibtexParser.parse_names('Bernd {van Linder} and {John-Jules Ch.} Meyer and Eijkhof, Frank {v}an {d}en'))
        res = ['John "Jack and Jill" Smith', 'Tom Thompson']
        self.assertEqual(res, BibtexParser.parse_names('John "Jack {and} Jill" Smith and Tom Thompson'))


class TestPersonName(unittest.TestCase):

    def test_names(self):
        """Test person name parser."""
        res = {
            'lastname': 'Smith',
            'nickname': 'Jack and Jill',
            'fullname': 'John "Jack and Jill" Smith',
            'firstname': 'John'
        }
        self.assertEqual(res, dict(PersonName('John "Jack and Jill" Smith')))

        res = {
            'lastname': 'Cierva y Codorn\xedu',
            'prefix': 'de la',
            'fullname': 'Juan de la Cierva y Codorn\xedu',
            'firstname': 'Juan'
        }
        self.assertEqual(res, dict(PersonName('Juan de la Cierva y Codorníu')))

        res = {
            'lastname': 'Beethoven',
            'prefix': 'von',
            'fullname': 'Ludwig von Beethoven',
            'firstname': 'Ludwig'
        }
        self.assertEqual(res, dict(PersonName('Ludwig von Beethoven')))
        self.assertEqual(res, dict(PersonName('von Beethoven, Ludwig')))
        self.assertEqual(res, dict(PersonName('Beethoven, Ludwig von')))

        res = {
            'suffix': 'Jr',
            'firstname': 'George',
            'middlename': 'Oscar',
            'lastname': 'Bluth',
            'nickname': 'Gob',
            'fullname': 'George Oscar "Gob" Bluth Jr'
        }
        self.assertEqual(res, PersonName('George Oscar “Gob” Bluth, Jr.'))
        self.assertEqual(res, PersonName('George Oscar \'Gob\' Bluth, Jr.'))
        self.assertEqual(res, PersonName('George Oscar "Gob" Bluth, Jr.'))

        res = {
            'middlename': 'Paul',
            'lastname': 'Jones',
            'fullname': 'John Paul Jones',
            'firstname': 'John'
        }
        self.assertEqual(res, dict(PersonName('John Paul Jones')))
        self.assertEqual(res, dict(PersonName('Jones, John Paul')))

        res = {
            'lastname': 'Brinch Hansen',
            'fullname': 'Per Brinch Hansen',
            'firstname': 'Per'
        }
        self.assertEqual(res, dict(PersonName('Brinch Hansen, Per')))

        res = {
            'middlename': 'Louis Xavier Joseph',
            'lastname': 'Vallee Poussin',
            'prefix': 'de la',
            'fullname': 'Charles Louis Xavier Joseph de la Vallee Poussin',
            'firstname': 'Charles'
        }
        self.assertEqual(res, dict(PersonName('Charles Louis Xavier Joseph de la Vallee Poussin')))

        res = {
            'lastname': 'Ford',
            'suffix': 'Jr III',
            'firstname': 'Henry',
            'fullname': 'Henry Ford Jr III'
        }
        self.assertEqual(res, dict(PersonName('Henry Ford, Jr., III')))
        self.assertEqual(res, dict(PersonName('Henry Ford Jr. III')))
        self.assertEqual(res, dict(PersonName('Ford, Jr., III, Henry')))

        res = {
            'middlename': 'L',
            'lastname': 'Steele Jr',
            'fullname': 'Guy L Steele Jr',
            'firstname': 'Guy'
        }
        self.assertEqual(res, dict(PersonName('{Steele Jr.}, Guy L.', from_bibtex=True)))
        self.assertEqual(res, dict(PersonName('Guy L. {Steele Jr.}', from_bibtex=True)))

        res = {
            'middlename': 'Fitzgerald',
            'lastname': 'Kennedy',
            'nickname': 'Jack',
            'fullname': 'John Fitzgerald "Jack" Kennedy',
            'firstname': 'John'
        }
        self.assertEqual(res, dict(PersonName('John Fitzgerald "Jack" Kennedy')))

    def test_capitalization(self):
        p = PersonName('juan q. xavier velasquez y garcia', from_bibtex=True)
        self.assertEqual('Juan Q Xavier Velasquez y Garcia', p.fullname)

    def test_equality(self):
        self.assertEqual(PersonName('Henry Ford, Jr., III'), PersonName('Ford, Jr., III, Henry'))
        self.assertEqual(PersonName('Jones, John Paul'), PersonName('John Paul Jones'))

    def test_could_be(self):
        self.assertTrue(PersonName('G. Bluth').could_be(PersonName('George Oscar Bluth Jr.')))
        self.assertFalse(PersonName('G. Bluth Sr.').could_be(PersonName('George Oscar Bluth Jr.')))
        self.assertFalse(PersonName('Oscar Bluth').could_be(PersonName('George Oscar Bluth')))
        self.assertTrue(PersonName('J F K').could_be(PersonName('John Fitzgerald "Jack" Kennedy')))


if __name__ == '__main__':
    unittest.main()

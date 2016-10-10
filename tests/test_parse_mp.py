# -*- coding: utf-8 -*-
"""
test_parse_mp
~~~~~~~~~~~~~

Test melting point parser.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import unittest

from lxml import etree

from chemdataextractor.doc.text import Sentence, Paragraph
from chemdataextractor.parse.mp import mp_phrase


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestParseMp(unittest.TestCase):

    maxDiff = None

    def do_parse(self, input, expected):
        s = Sentence(input)
        log.debug(s)
        log.debug(s.tagged_tokens)
        result = next(mp_phrase.scan(s.tagged_tokens))[0]
        log.debug(etree.tostring(result, pretty_print=True, encoding='unicode'))
        self.assertEqual(expected, etree.tostring(result, encoding='unicode'))

    def test_mp1(self):
        s = 'Colorless solid (81% yield, 74.8 mg, 0.22 mmol); mp 77.2–77.5 °C.'
        expected = '<mp_phrase><mp><value>77.2–77.5</value><units>°C</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_mp2(self):
        s = 'Mp > 280 °C.'
        expected = '<mp_phrase><mp><value>&gt;280</value><units>°C</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_mp3(self):
        s = 'Mp: 105-110 °C'
        expected = '<mp_phrase><mp><value>105-110</value><units>°C</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_mp4(self):
        s = '4-Amino-3-chloro-6-(2,3,4-trifluorophenyl)pyridine-2-carboxylic acid (Compound 67): mp 163-164° C.'
        expected = '<mp_phrase><cem><name>4-Amino-3-chloro-6-(2,3,4-trifluorophenyl)pyridine-2-carboxylic acid</name><label>67</label></cem><mp><value>163-164</value><units>\xb0C</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_mp5(self):
        s = '4-Amino-3-chloro-6-[2,4-dichloro-3-(1-fluoro-1-methylethylphenyl)pyridine-3-carboxylic acid (Compound 127): mp >250° C.'
        expected = '<mp_phrase><cem><name>4-Amino-3-chloro-6-[2,4-dichloro-3-(1-fluoro-1-methylethylphenyl)pyridine-3-carboxylic acid</name><label>127</label></cem><mp><value>&gt;250</value><units>\xb0C</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_mp6(self):
        s = '4-Acetylamino-3-chloro-6-(4-cyano-2,6-difluoro-3-methoxyphenyl)pyridine-2-carboxylic acid, methyl ester: mp 146-147° C.'
        expected = '<mp_phrase><cem><name>4-Acetylamino-3-chloro-6-(4-cyano-2,6-difluoro-3-methoxyphenyl)pyridine-2-carboxylic acid, methyl ester</name></cem><mp><value>146-147</value><units>\xb0C</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_mp7(self):
        s = '3-Bromo-2,6-dichloroaniline: mp 71-72° C.'
        expected = '<mp_phrase><cem><name>3-Bromo-2,6-dichloroaniline</name></cem><mp><value>71-72</value><units>\xb0C</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_mp8(self):
        s = '4-Acetylamino-3-chloro-6-(4-chloro-2-fluoro-3-methoxymethoxy-phenyl)pyridine-2-carboxylic acid, methyl ester (Compound 34) mp 122-123° C.'
        expected = '<mp_phrase><cem><name>4-Acetylamino-3-chloro-6-(4-chloro-2-fluoro-3-methoxymethoxy-phenyl)pyridine-2-carboxylic acid, methyl ester</name><label>34</label></cem><mp><value>122-123</value><units>\xb0C</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_mp9(self):
        s = 'to give 4-acetylamino-3-chloro-6-(4-chloro-2-fluoro-5-methoxyphenyl)pyridine-2-carboxylic acid methyl ester (4.5 g, 0.012 mol): mp 180-182° C.'
        expected = '<mp_phrase><cem><role>to give</role><name>4-acetylamino-3-chloro-6-(4-chloro-2-fluoro-5-methoxyphenyl)pyridine-2-carboxylic acid methyl ester</name></cem><mp><value>180-182</value><units>\xb0C</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_degrees_only(self):
        s = 'm.p. 91°-109°'
        expected = '<mp_phrase><mp><value>91-109</value><units>\xb0</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_afforded(self):
        s = 'afforded bissulfonic acid (102 mg, 41%) as a green solid m.p.>300° C.'
        expected = '<mp_phrase><cem><name>bissulfonic acid</name></cem><mp><value>&gt;300</value><units>\xb0C</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_melting_point_of(self):
        s = 'the product had a melting point of 62-68° C.'
        expected = '<mp_phrase><mp><value>62-68</value><units>\xb0C</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_melting_point_was(self):
        s = 'the melting point was 62-68° C.'
        expected = '<mp_phrase><mp><value>62-68</value><units>\xb0C</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_melting_point(self):
        s = 'melting point 62-68° C.'
        expected = '<mp_phrase><mp><value>62-68</value><units>\xb0C</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_melting_point_colon(self):
        s = 'Melting point: 82-83° C.'
        expected = '<mp_phrase><mp><value>82-83</value><units>\xb0C</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_melting_point_range(self):
        s = 'having a melting point in the range of 125-130° C.'
        expected = '<mp_phrase><mp><value>125-130</value><units>\xb0C</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_m_pt(self):
        s = 'M. pt. 156-158° C.;'
        expected = '<mp_phrase><mp><value>156-158</value><units>\xb0C.</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_of_about(self):
        s = '300 g of carboxyethylmethylphosphinic acid are obtained as a white solid having a melting point of about 95° C'
        expected = '<mp_phrase><cem><name>carboxyethylmethylphosphinic acid</name></cem><mp><value>95</value><units>\xb0C</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_gave(self):
        s = 'under the conditions noted in example 1, gave 1-(3,4-dimethoxyphenyl)-2-(3,4,5-trimethoxyphenyl) ethylene, m.p. 150–152° C'
        expected = '<mp_phrase><cem><name>1-(3,4-dimethoxyphenyl)-2-(3,4,5-trimethoxyphenyl) ethylene</name></cem><mp><value>150\u2013152</value><units>\xb0C</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_gave_label(self):
        s = 'gave 2, m.p. 148° C.;'
        expected = '<mp_phrase><label>2</label><mp><value>148</value><units>\xb0C.</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_give_label(self):
        s = 'to give 3, m.p. 242–244° C.;'
        expected = '<mp_phrase><label>3</label><mp><value>242\u2013244</value><units>\xb0C.</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_bracket_obtained(self):
        s = '(2S,3S)-3-(t-butoxycarbonyl)amino-1,2-epoxy-4-phenylbutane was obtained (mp: 125.6° C.).'
        expected = '<mp_phrase><cem><name>(2S,3S)-3-(t-butoxycarbonyl)amino-1,2-epoxy-4-phenylbutane</name></cem><mp><value>125.6</value><units>\xb0C.</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_bracket(self):
        s = '(2S,3S)-3-(t-butoxycarbonyl)amino-1,2-epoxy-4-phenylbutane (mp: 125.6° C.).'
        expected = '<mp_phrase><cem><name>(2S,3S)-3-(t-butoxycarbonyl)amino-1,2-epoxy-4-phenylbutane</name></cem><mp><value>125.6</value><units>\xb0C.</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_tilde(self):
        s = 'Melting point: 96.8˜101.8° C.'
        expected = '<mp_phrase><mp><value>96.8\u02dc101.8</value><units>\xb0C</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_range_to(self):
        s = 'melting temperature of 203.0 to 207.0° C.'
        expected = '<mp_phrase><mp><value>203.0 to 207.0</value><units>\xb0C</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_melting_at(self):
        s = 'melting at 149-150° C.'
        expected = '<mp_phrase><mp><value>149-150</value><units>\xb0C</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_melting_range(self):
        s = 'Melting Range: 116-118° C.'
        expected = '<mp_phrase><mp><value>116-118</value><units>\xb0C</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_cem_yield(self):
        s = '3-Ethoxymethyl-2-(4-chlorophenyl)imino-2H-chromene (E4): (1.00 g, 64%); m.p.: 84˜86° C., Rf=0.564'
        expected = '<mp_phrase><cem><name>3-Ethoxymethyl-2-(4-chlorophenyl)imino-2H-chromene</name><label>E4</label></cem><mp><value>84\u02dc86</value><units>\xb0C.</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_having(self):
        s = 'to obtain 5 parts of 1-phenyl-3-(4-phenylethynylstyryl)-5-(4-phenylethynylphenyl)pyrazoline having a melting point of 212-214° C.'
        expected = '<mp_phrase><cem><name>1-phenyl-3-(4-phenylethynylstyryl)-5-(4-phenylethynylphenyl)pyrazoline</name></cem><mp><value>212-214</value><units>\xb0C</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_solvent(self):
        s = 'which was crystallised from chloroform-methanol, m.p. 254–256° C.'
        expected = '<mp_phrase><mp><value>254\u2013256</value><units>\xb0C</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_solvent2(self):
        s = 'prepared by recrystallization from hexanes, m.p. 127-129° C.'
        expected = '<mp_phrase><mp><value>127-129</value><units>\xb0C</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_solvent3(self):
        s = 'residual solids in hexanes, m.p. 126-128° C.'
        expected = '<mp_phrase><mp><value>126-128</value><units>\xb0C</units></mp></mp_phrase>'
        self.do_parse(s, expected)

    def test_colon(self):
        s = '3-Cyano-2H-chromene (B1): (2.51 g, 80%); m.p.: 44-45° C.;'
        expected = '<mp_phrase><cem><name>3-Cyano-2H-chromene</name><label>B1</label></cem><mp><value>44-45</value><units>\xb0C.</units></mp></mp_phrase>'
        self.do_parse(s, expected)


class TestParseMpCompound(unittest.TestCase):

    maxDiff = None

    def do_parse(self, input, expected):
        p = Paragraph(input)
        log.debug(p)
        log.debug([r.serialize() for r in p.records])
        self.assertEqual(expected, [r.serialize() for r in p.records])

    def test_mpc1(self):
        s = '4-Amino-3-chloro-6-(2,3,4-trifluorophenyl)pyridine-2-carboxylic acid (Compound 67): mp 163-164° C.'
        expected = [
            {'labels': [u'67'], 'names': [u'4-Amino-3-chloro-6-(2,3,4-trifluorophenyl)pyridine-2-carboxylic acid']},
            {'labels': ['67'], 'melting_points': [{'units': u'\xb0C', 'value': u'163-164'}], 'names': ['4-Amino-3-chloro-6-(2,3,4-trifluorophenyl)pyridine-2-carboxylic acid']}
        ]
        self.do_parse(s, expected)

    def test_mpc2(self):
        s = '3-Bromo-2,6-dichloroaniline: mp 71-72° C.'
        expected = [
            {'names': [u'3-Bromo-2,6-dichloroaniline']},
            {'melting_points': [{'units': u'\xb0C', 'value': u'71-72'}], 'names': ['3-Bromo-2,6-dichloroaniline']}
        ]
        self.do_parse(s, expected)



if __name__ == '__main__':
    unittest.main()

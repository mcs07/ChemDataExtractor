# -*- coding: utf-8 -*-
"""
test_parse_nmr
~~~~~~~~~~~~~~



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

from chemdataextractor.doc.text import Sentence
from chemdataextractor.parse.nmr import nmr

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestParseNmr(unittest.TestCase):

    maxDiff = None

    def do_parse(self, input, expected):
        s = Sentence(input)
        log.debug(s)
        log.debug(s.tagged_tokens)
        result = next(nmr.scan(s.tagged_tokens))[0]
        log.debug(etree.tostring(result, pretty_print=True, encoding='unicode'))
        self.assertEqual(expected, etree.tostring(result, encoding='unicode'))

    def test_nmr1(self):
        s = '1H NMR (300 MHz, CDCl3), 1.00 (t, J = 7.3 Hz, 3H), 1.50 (m, 2H), 1.77 (m, 2H), 2.42 (s, 3H), ' \
            '2.83–2.71 (m, 3H), 6.36 (s, 1H), 7.26 (d, J = 8.7 Hz, 2H), 7.30–7.39 (m, 7H), 7.50 (d, J = 8.2 Hz, 2H), ' \
            '7.54 (d, J = 8.7 Hz, 2H);'
        expected = '<nmr><nucleus>1H</nucleus><frequency><value>300</value><units>MHz</units></frequency><solvent>CDCl3</solvent><peaks><peak><shift>1.00</shift><multiplicity>t</multiplicity><coupling><value>7.3</value><units>Hz</units></coupling><number>3H</number></peak><peak><shift>1.50</shift><multiplicity>m</multiplicity><number>2H</number></peak><peak><shift>1.77</shift><multiplicity>m</multiplicity><number>2H</number></peak><peak><shift>2.42</shift><multiplicity>s</multiplicity><number>3H</number></peak><peak><shift>2.83–2.71</shift><multiplicity>m</multiplicity><number>3H</number></peak><peak><shift>6.36</shift><multiplicity>s</multiplicity><number>1H</number></peak><peak><shift>7.26</shift><multiplicity>d</multiplicity><coupling><value>8.7</value><units>Hz</units></coupling><number>2H</number></peak><peak><shift>7.30–7.39</shift><multiplicity>m</multiplicity><number>7H</number></peak><peak><shift>7.50</shift><multiplicity>d</multiplicity><coupling><value>8.2</value><units>Hz</units></coupling><number>2H</number></peak><peak><shift>7.54</shift><multiplicity>d</multiplicity><coupling><value>8.7</value><units>Hz</units></coupling><number>2H</number></peak></peaks></nmr>'
        self.do_parse(s, expected)

    def test_nmr2(self):
        s = '1H NMR (400 MHz, DMSO) δ 8.34 (s, 1H), 8.10 (d, J = 9.3 Hz, 1H), 7.70 (s, 2H), 3.82–3.65 (m, 1H), ' \
            '1.65–1.37 (m, 4H), 0.83 (t, J = 7.4 Hz, 6H).'
        expected = '<nmr><nucleus>1H</nucleus><frequency><value>400</value><units>MHz</units></frequency><solvent>DMSO</solvent><peaks><peak><shift>8.34</shift><multiplicity>s</multiplicity><number>1H</number></peak><peak><shift>8.10</shift><multiplicity>d</multiplicity><coupling><value>9.3</value><units>Hz</units></coupling><number>1H</number></peak><peak><shift>7.70</shift><multiplicity>s</multiplicity><number>2H</number></peak><peak><shift>3.82\u20133.65</shift><multiplicity>m</multiplicity><number>1H</number></peak><peak><shift>1.65\u20131.37</shift><multiplicity>m</multiplicity><number>4H</number></peak><peak><shift>0.83</shift><multiplicity>t</multiplicity><coupling><value>7.4</value><units>Hz</units></coupling><number>6H</number></peak></peaks></nmr>'
        self.do_parse(s, expected)

    def test_nmr3(self):
        s = '13C NMR (101 MHz, DMSO) δ 164.7, 154.2, 148.5, 125.7, 121.5, 52.0, 26.8 (2C), 10.7 (2C).'
        expected = '<nmr><nucleus>13C</nucleus><frequency><value>101</value><units>MHz</units></frequency><solvent>DMSO</solvent><peaks><peak><shift>164.7</shift></peak><peak><shift>154.2</shift></peak><peak><shift>148.5</shift></peak><peak><shift>125.7</shift></peak><peak><shift>121.5</shift></peak><peak><shift>52.0</shift></peak><peak><shift>26.8</shift><number>2C</number></peak><peak><shift>10.7</shift><number>2C</number></peak></peaks></nmr>'
        self.do_parse(s, expected)

    def test_nmr4(self):
        s = '1H NMR (C6D6, 400 MHz): δ -0.53 (s, 1H), 0.72 (d, 1H, J = 4.0 Hz), 0.98 (s, 1H), 1.58 (s, 15H), ' \
            '1.62 (s, 3H), 1.73 (s, 15H), 1.95 (d, 1H, J = 4.0 Hz), 5.62 (t, 1H, J = 4.0 Hz), 6.00 (t, 1H, J = 4.0 Hz).'
        expected = '<nmr><nucleus>1H</nucleus><solvent>C6D6</solvent><frequency><value>400</value><units>MHz</units></frequency><peaks><peak><shift>-0.53</shift><multiplicity>s</multiplicity><number>1H</number></peak><peak><shift>0.72</shift><multiplicity>d</multiplicity><number>1H</number><coupling><value>4.0</value><units>Hz</units></coupling></peak><peak><shift>0.98</shift><multiplicity>s</multiplicity><number>1H</number></peak><peak><shift>1.58</shift><multiplicity>s</multiplicity><number>15H</number></peak><peak><shift>1.62</shift><multiplicity>s</multiplicity><number>3H</number></peak><peak><shift>1.73</shift><multiplicity>s</multiplicity><number>15H</number></peak><peak><shift>1.95</shift><multiplicity>d</multiplicity><number>1H</number><coupling><value>4.0</value><units>Hz</units></coupling></peak><peak><shift>5.62</shift><multiplicity>t</multiplicity><number>1H</number><coupling><value>4.0</value><units>Hz</units></coupling></peak><peak><shift>6.00</shift><multiplicity>t</multiplicity><number>1H</number><coupling><value>4.0</value><units>Hz</units></coupling></peak></peaks></nmr>'
        self.do_parse(s, expected)

    def test_nmr5(self):
        s = '13C{1H} NMR (C6D6, 125 MHz): δ 10.2, 10.6, 17.4, 38.3, 51.5, 54.2, 60.6, 80.8, 81.0, 88.0, 88.7.'
        expected = '<nmr><nucleus>13C{1H}</nucleus><solvent>C6D6</solvent><frequency><value>125</value><units>MHz</units></frequency><peaks><peak><shift>10.2</shift></peak><peak><shift>10.6</shift></peak><peak><shift>17.4</shift></peak><peak><shift>38.3</shift></peak><peak><shift>51.5</shift></peak><peak><shift>54.2</shift></peak><peak><shift>60.6</shift></peak><peak><shift>80.8</shift></peak><peak><shift>81.0</shift></peak><peak><shift>88.0</shift></peak><peak><shift>88.7</shift></peak></peaks></nmr>'
        self.do_parse(s, expected)

    def test_nmr6(self):
        """With 2D, complicated solvent info."""
        s = '1H NMR (CDCl3 with 0.05% v/v TMS, 400 MHz): δH 7.10 (2H, d, J = 8.9 Hz, H2′ and H6′), ' \
            '7.03-7.07 (3H, m, H3′′, H4′′ and H5′′), 6.83-6.85 (2H, m, H2′′ and H6′′), ' \
            '6.66 (2H, d, J = 8.9 Hz, H3′ and H5′), 6.42 (1H, d, J = 1.8 Hz, H5), 6.26 (1H, d, J = 1.7 Hz, H7), ' \
            '5.18 (1H, s, H1′′′), 5.01 (1H, d, J = 6.6 Hz, H1), 4.52 (1H, s, H2′′′), 4.27 (1H, d, J = 14.2 Hz, H3), ' \
            '4.15 (1H, br d, J = 11.2 Hz, H4′′′), 4.05 (1H, t, J = 11.2 Hz, H3b′′′), 3.88 (1H, J = 14.3, 6.8 Hz, H2), ' \
            '3.86 (3H, s, OCH38), 3.69 (3H, s, OCH34′), 3.64 (3H, s, COOCH32), 3.49 (3H, br s, H5′′′ and H6′′′), ' \
            '3.43-3.47 (1H, overlapped, H3a′′′), 3.45 (3H, s, OCH32′′′).'
        expected = '<nmr><nucleus>1H</nucleus><solvent>CDCl3 with 0.05 % v / v TMS</solvent><frequency><value>400</value><units>MHz</units></frequency><peaks><peak><shift>7.10</shift><number>2H</number><multiplicity>d</multiplicity><coupling><value>8.9</value><units>Hz</units></coupling><assignment>H2\u2032</assignment><assignment>H6\u2032</assignment></peak><peak><shift>7.03-7.07</shift><number>3H</number><multiplicity>m</multiplicity><assignment>H3\u2032\u2032</assignment><assignment>H4\u2032\u2032</assignment><assignment>H5\u2032\u2032</assignment></peak><peak><shift>6.83-6.85</shift><number>2H</number><multiplicity>m</multiplicity><assignment>H2\u2032\u2032</assignment><assignment>H6\u2032\u2032</assignment></peak><peak><shift>6.66</shift><number>2H</number><multiplicity>d</multiplicity><coupling><value>8.9</value><units>Hz</units></coupling><assignment>H3\u2032</assignment><assignment>H5\u2032</assignment></peak><peak><shift>6.42</shift><number>1H</number><multiplicity>d</multiplicity><coupling><value>1.8</value><units>Hz</units></coupling><assignment>H5</assignment></peak><peak><shift>6.26</shift><number>1H</number><multiplicity>d</multiplicity><coupling><value>1.7</value><units>Hz</units></coupling><assignment>H7</assignment></peak><peak><shift>5.18</shift><number>1H</number><multiplicity>s</multiplicity><assignment>H1\u2032\u2032\u2032</assignment></peak><peak><shift>5.01</shift><number>1H</number><multiplicity>d</multiplicity><coupling><value>6.6</value><units>Hz</units></coupling><assignment>H1</assignment></peak><peak><shift>4.52</shift><number>1H</number><multiplicity>s</multiplicity><assignment>H2\u2032\u2032\u2032</assignment></peak><peak><shift>4.27</shift><number>1H</number><multiplicity>d</multiplicity><coupling><value>14.2</value><units>Hz</units></coupling><assignment>H3</assignment></peak><peak><shift>4.15</shift><number>1H</number><multiplicity>br d</multiplicity><coupling><value>11.2</value><units>Hz</units></coupling><assignment>H4\u2032\u2032\u2032</assignment></peak><peak><shift>4.05</shift><number>1H</number><multiplicity>t</multiplicity><coupling><value>11.2</value><units>Hz</units></coupling><assignment>H3b\u2032\u2032\u2032</assignment></peak><peak><shift>3.88</shift><number>1H</number><coupling><value>14.3 , 6.8</value><units>Hz</units></coupling><assignment>H2</assignment></peak><peak><shift>3.86</shift><number>3H</number><multiplicity>s</multiplicity><assignment>OCH38</assignment></peak><peak><shift>3.69</shift><number>3H</number><multiplicity>s</multiplicity><assignment>OCH34\u2032</assignment></peak><peak><shift>3.64</shift><number>3H</number><multiplicity>s</multiplicity><assignment>COOCH32</assignment></peak><peak><shift>3.49</shift><number>3H</number><multiplicity>br s</multiplicity><assignment>H5\u2032\u2032\u2032</assignment><assignment>H6\u2032\u2032\u2032</assignment></peak><peak><shift>3.43-3.47</shift><number>1H</number><note>overlapped</note><assignment>H3a\u2032\u2032\u2032</assignment></peak><peak><shift>3.45</shift><number>3H</number><multiplicity>s</multiplicity><assignment>OCH32\u2032\u2032\u2032</assignment></peak></peaks></nmr>'
        self.do_parse(s, expected)

    def test_nmr7(self):
        """With 2D."""
        s = '13C NMR (CDCl3, 125 MHz): δC 170.6 (s, COCH32), 160.6 (s, C4a), 160.0 (s, C6), 158.8 (s, C4′), ' \
            '157.1 (s, C8), 136.7 (s, C1′′ ), 129.0 (d, C2′ and C6′), 127.8 (d, C2′′, C3′′, C5′′ and C6′′), ' \
            '126.6 (d, C4′′), 126.3 (s, C1′), 112.7 (d, C3′ and C5′), 109.6 (s, C8a), 101.9 (s, C3a), 95.2 (d, C2′′′), ' \
            '94.0 (d, C1′′′), 93.9 (d, C7), 93.4 (s, C8b), 92.9 (d, C5), 79.7 (d, C1), 70.7 (d, C5′′′), ' \
            '68.3 (d, C4′′′), 63.3 (t, C6′′′), 59.0 (t, C3′′′), 55.9 (q, OCH38), 55.1 (q, OCH34′), ' \
            '55.0 (d, C3; q, OCH32′′′), 52.1 (q, COCH32), 50.3 (d, C2).'
        expected = '<nmr><nucleus>13C</nucleus><solvent>CDCl3</solvent><frequency><value>125</value><units>MHz</units></frequency><peaks><peak><shift>170.6</shift><multiplicity>s</multiplicity><assignment>COCH32</assignment></peak><peak><shift>160.6</shift><multiplicity>s</multiplicity><assignment>C4a</assignment></peak><peak><shift>160.0</shift><multiplicity>s</multiplicity><assignment>C6</assignment></peak><peak><shift>158.8</shift><multiplicity>s</multiplicity><assignment>C4\u2032</assignment></peak><peak><shift>157.1</shift><multiplicity>s</multiplicity><assignment>C8</assignment></peak><peak><shift>136.7</shift><multiplicity>s</multiplicity><assignment>C1\u2032\u2032</assignment></peak><peak><shift>129.0</shift><multiplicity>d</multiplicity><assignment>C2\u2032</assignment><assignment>C6\u2032</assignment></peak><peak><shift>127.8</shift><multiplicity>d</multiplicity><assignment>C2\u2032\u2032</assignment><assignment>C3\u2032\u2032</assignment><assignment>C5\u2032\u2032</assignment><assignment>C6\u2032\u2032</assignment></peak><peak><shift>126.6</shift><multiplicity>d</multiplicity><assignment>C4\u2032\u2032</assignment></peak><peak><shift>126.3</shift><multiplicity>s</multiplicity><assignment>C1\u2032</assignment></peak><peak><shift>112.7</shift><multiplicity>d</multiplicity><assignment>C3\u2032</assignment><assignment>C5\u2032</assignment></peak><peak><shift>109.6</shift><multiplicity>s</multiplicity><assignment>C8a</assignment></peak><peak><shift>101.9</shift><multiplicity>s</multiplicity><assignment>C3a</assignment></peak><peak><shift>95.2</shift><multiplicity>d</multiplicity><assignment>C2\u2032\u2032\u2032</assignment></peak><peak><shift>94.0</shift><multiplicity>d</multiplicity><assignment>C1\u2032\u2032\u2032</assignment></peak><peak><shift>93.9</shift><multiplicity>d</multiplicity><assignment>C7</assignment></peak><peak><shift>93.4</shift><multiplicity>s</multiplicity><assignment>C8b</assignment></peak><peak><shift>92.9</shift><multiplicity>d</multiplicity><assignment>C5</assignment></peak><peak><shift>79.7</shift><multiplicity>d</multiplicity><assignment>C1</assignment></peak><peak><shift>70.7</shift><multiplicity>d</multiplicity><assignment>C5\u2032\u2032\u2032</assignment></peak><peak><shift>68.3</shift><multiplicity>d</multiplicity><assignment>C4\u2032\u2032\u2032</assignment></peak><peak><shift>63.3</shift><multiplicity>t</multiplicity><assignment>C6\u2032\u2032\u2032</assignment></peak><peak><shift>59.0</shift><multiplicity>t</multiplicity><assignment>C3\u2032\u2032\u2032</assignment></peak><peak><shift>55.9</shift><multiplicity>q</multiplicity><assignment>OCH38</assignment></peak><peak><shift>55.1</shift><multiplicity>q</multiplicity><assignment>OCH34\u2032</assignment></peak><peak><shift>55.0</shift><multiplicity>d</multiplicity><assignment>C3</assignment><multiplicity>q</multiplicity><assignment>OCH32\u2032\u2032\u2032</assignment></peak><peak><shift>52.1</shift><multiplicity>q</multiplicity><assignment>COCH32</assignment></peak><peak><shift>50.3</shift><multiplicity>d</multiplicity><assignment>C2</assignment></peak></peaks></nmr>'
        self.do_parse(s, expected)

    def test_nmr8(self):
        """d of d multiplicity."""
        s = '1H NMR (D2O, 300 MHz): δ 1.61 (s, 6H), 1.68 (s, 3H), 1.72 (s, 3H), 2.17-1.99 (m, 8H), ' \
            '4.45 (d of d, 2H, JH,H = 6Hz, JP,H = 6Hz), 5.23-5.15 (m, 2H), 5.46 (t, 1H, J = 6Hz).'
        expected = '<nmr><nucleus>1H</nucleus><solvent>D2O</solvent><frequency><value>300</value><units>MHz</units></frequency><peaks><peak><shift>1.61</shift><multiplicity>s</multiplicity><number>6H</number></peak><peak><shift>1.68</shift><multiplicity>s</multiplicity><number>3H</number></peak><peak><shift>1.72</shift><multiplicity>s</multiplicity><number>3H</number></peak><peak><shift>2.17-1.99</shift><multiplicity>m</multiplicity><number>8H</number></peak><peak><shift>4.45</shift><multiplicity>d of d</multiplicity><number>2H</number><coupling><value>6</value><units>Hz</units></coupling><coupling><value>6</value><units>Hz</units></coupling></peak><peak><shift>5.23-5.15</shift><multiplicity>m</multiplicity><number>2H</number></peak><peak><shift>5.46</shift><multiplicity>t</multiplicity><number>1H</number><coupling><value>6</value><units>Hz</units></coupling></peak></peaks></nmr>'
        self.do_parse(s, expected)

    def test_nmr9(self):
        """"""
        s = '31P NMR (D2O, 121.5 MHz): δ −6.56 (d, 1P, JP,P = 21.9 Hz), −9.89 (d, 1P, JP,P = 21.9 Hz).'
        expected = '<nmr><nucleus>31P</nucleus><solvent>D2O</solvent><frequency><value>121.5</value><units>MHz</units></frequency><peaks><peak><shift>\u22126.56</shift><multiplicity>d</multiplicity><number>1P</number><coupling><value>21.9</value><units>Hz</units></coupling></peak><peak><shift>\u22129.89</shift><multiplicity>d</multiplicity><number>1P</number><coupling><value>21.9</value><units>Hz</units></coupling></peak></peaks></nmr>'
        self.do_parse(s, expected)

    def test_nmr10(self):
        """"""
        s = '1H NMR (300 MHz, CDCl3) δ = 3.96 (s, 3H), 6.66 (s, 1H), 7.29–7.54 (m, 8H), 7.66 (d, J = 8.5 Hz, 4H), 7.92 (d, J = 8.5 Hz, 2H).'
        expected = '<nmr><nucleus>1H</nucleus><frequency><value>300</value><units>MHz</units></frequency><solvent>CDCl3</solvent><peaks><peak><shift>3.96</shift><multiplicity>s</multiplicity><number>3H</number></peak><peak><shift>6.66</shift><multiplicity>s</multiplicity><number>1H</number></peak><peak><shift>7.29\u20137.54</shift><multiplicity>m</multiplicity><number>8H</number></peak><peak><shift>7.66</shift><multiplicity>d</multiplicity><coupling><value>8.5</value><units>Hz</units></coupling><number>4H</number></peak><peak><shift>7.92</shift><multiplicity>d</multiplicity><coupling><value>8.5</value><units>Hz</units></coupling><number>2H</number></peak></peaks></nmr>'
        self.do_parse(s, expected)

    def test_nmr11(self):
        """"""
        s = '13C NMR (75 MHz, CDCl3) δ = 37.8 (CH3), 103.4 (CH), 126.0 (CH), 127.1 (CH), 127.4 (CH), 127.5 (CH), 128.7 (CH), 128.87 (CH), 128.90 (4 CH), 130.8 (Cquat), 132.6 (Cquat), 140.4 (Cquat), 141.0 (Cquat), 145.3 (Cquat), 150.3 (Cquat).'
        expected = '<nmr><nucleus>13C</nucleus><frequency><value>75</value><units>MHz</units></frequency><solvent>CDCl3</solvent><peaks><peak><shift>37.8</shift><assignment>CH3</assignment></peak><peak><shift>103.4</shift><assignment>CH</assignment></peak><peak><shift>126.0</shift><assignment>CH</assignment></peak><peak><shift>127.1</shift><assignment>CH</assignment></peak><peak><shift>127.4</shift><assignment>CH</assignment></peak><peak><shift>127.5</shift><assignment>CH</assignment></peak><peak><shift>128.7</shift><assignment>CH</assignment></peak><peak><shift>128.87</shift><assignment>CH</assignment></peak><peak><shift>128.90</shift><number>4</number><assignment>CH</assignment></peak><peak><shift>130.8</shift><assignment>Cquat</assignment></peak><peak><shift>132.6</shift><assignment>Cquat</assignment></peak><peak><shift>140.4</shift><assignment>Cquat</assignment></peak><peak><shift>141.0</shift><assignment>Cquat</assignment></peak><peak><shift>145.3</shift><assignment>Cquat</assignment></peak><peak><shift>150.3</shift><assignment>Cquat</assignment></peak></peaks></nmr>'
        self.do_parse(s, expected)

    def test_nmr12(self):
        """"""
        s = '1H NMR (400 MHz, DMSO-d6): ppm = 2.07 (s, 6H, CH3), 5.40 (s, 2H, CH) 6.90 (d, 4H, J= 8.9 Hz,  CHAr), 7.25-7.38 (m, 10H, CHAr), 7.5 (d, 4H, J= 8.9 Hz, CHAr), 9.42 (s, 2H, NH), 9.73 (s, 2H, NH), 9.98 (s, 2H, NH).'
        expected = '<nmr><nucleus>1H</nucleus><frequency><value>400</value><units>MHz</units></frequency><solvent>DMSO-d6</solvent><peaks><peak><shift>2.07</shift><multiplicity>s</multiplicity><number>6H</number><assignment>CH3</assignment></peak><peak><shift>5.40</shift><multiplicity>s</multiplicity><number>2H</number><assignment>CH</assignment></peak><peak><shift>6.90</shift><multiplicity>d</multiplicity><number>4H</number><coupling><value>8.9</value><units>Hz</units></coupling><assignment>CHAr</assignment></peak><peak><shift>7.25-7.38</shift><multiplicity>m</multiplicity><number>10H</number><assignment>CHAr</assignment></peak><peak><shift>7.5</shift><multiplicity>d</multiplicity><number>4H</number><coupling><value>8.9</value><units>Hz</units></coupling><assignment>CHAr</assignment></peak><peak><shift>9.42</shift><multiplicity>s</multiplicity><number>2H</number><assignment>NH</assignment></peak><peak><shift>9.73</shift><multiplicity>s</multiplicity><number>2H</number><assignment>NH</assignment></peak><peak><shift>9.98</shift><multiplicity>s</multiplicity><number>2H</number><assignment>NH</assignment></peak></peaks></nmr>'
        self.do_parse(s, expected)

    def test_nmr13(self):
        """"""
        s = '1H NMR (CDCl3; δ in ppm): 0.16-0.51 (t, 12H), 1.75-2.21 (m, 8H), 5.16 (s, 2H), 7.00-8.21 (m, 25 Ar—H).'
        expected = '<nmr><nucleus>1H</nucleus><solvent>CDCl3</solvent><peaks><peak><shift>0.16-0.51</shift><multiplicity>t</multiplicity><number>12H</number></peak><peak><shift>1.75-2.21</shift><multiplicity>m</multiplicity><number>8H</number></peak><peak><shift>5.16</shift><multiplicity>s</multiplicity><number>2H</number></peak><peak><shift>7.00-8.21</shift></peak></peaks></nmr>'
        self.do_parse(s, expected)


if __name__ == '__main__':
    unittest.main()

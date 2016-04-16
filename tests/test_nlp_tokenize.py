#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for tokenization."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import unittest

from chemdataextractor.doc.text import Text
from chemdataextractor.nlp.tokenize import WordTokenizer, ChemWordTokenizer, FineWordTokenizer

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestWordTokenizer(unittest.TestCase):
    """Test the standard word tokenizer."""

    maxDiff = None

    def setUp(self):
        self.t = WordTokenizer()

    def test_final_full_stop(self):
        """Test the word tokenizer splits off final full stop only."""
        self.assertEqual(
            ['This', 'is', 'Mr.', 'Hoppy', '\'s', 'tortoise', '.'],
            self.t.tokenize('This is Mr. Hoppy\'s tortoise.')
        )

    def test_full_stop_following(self):
        """Test the word tokenizer splits off final full stop if followed by brackets or quotes."""
        self.assertEqual(
            ['(', 'This', 'is', 'Mr.', 'Hoppy', '\'s', 'tortoise', '.', ')'],
            self.t.tokenize('(This is Mr. Hoppy\'s tortoise.)')
        )
        self.assertEqual(
            ['"', 'This', 'is', 'Mr.', 'Hoppy', '\'s', 'tortoise', '.', '"'],
            self.t.tokenize('"This is Mr. Hoppy\'s tortoise."')
        )
        self.assertEqual(
            ['"', 'This', 'is', 'Mr.', 'Hoppy', '\'s', 'tort.oise', '.', '"'],
            self.t.tokenize('"This is Mr. Hoppy\'s tort.oise."')
        )

    def test_dollar(self):
        """Test the word tokenizer on dollar symbol."""
        self.assertEqual(
            ['On', 'a', '$', '50,000', 'mortgage', 'of', '30', 'years', 'at', '8', 'percent', ',', 'the', 'monthly', 'payment', 'would', 'be', '$', '366.88', '.'],
            self.t.tokenize('On a $50,000 mortgage of 30 years at 8 percent, the monthly payment would be $366.88.')
        )

    def test_quote(self):
        """Test the word tokenizer on quotes."""
        self.assertEqual(
            ['"', 'We', 'beat', 'some', 'pretty', 'good', 'teams', 'to', 'get', 'here', ',', '"', 'Slocum', 'said', '.'],
            self.t.tokenize('"We beat some pretty good teams to get here," Slocum said.')
        )

    def test_brackets_quotes(self):
        """Test the word tokenizer on brackets and quotes."""
        self.assertEqual(
            ['Well', ',', 'we', 'could', 'n\'t', 'have', 'this', 'predictable', ',', 'cliche', '-', 'ridden', ',', '"', 'Touched', 'by', 'an', 'Angel', '"', '(', 'a', 'show', 'creator', 'John', 'Masius', 'worked', 'on', ')', 'wanna-be', 'if', 'she', 'did', 'n\'t', '.'],
            self.t.tokenize('Well, we couldn\'t have this predictable, cliche-ridden, "Touched by an Angel" (a show creator John Masius worked on) wanna-be if she didn\'t.')
        )

    def test_exclamation(self):
        """Test the word tokenizer on exclamation mark."""
        self.assertEqual(
            ['I', 'can', 'not', 'can', 'not', 'work', 'under', 'these', 'conditions', '!'],
            self.t.tokenize('I cannot cannot work under these conditions!')
        )

    def test_digit_comma(self):
        """Test the word tokenizer on commas within numbers."""
        self.assertEqual(
            ['The', 'company', 'spent', '$', '30,000,000', 'last', 'year', '.'],
            self.t.tokenize('The company spent $30,000,000 last year.')
        )

    def test_decimal_number(self):
        """Test the word tokenizer on number containing full stop."""
        self.assertEqual(
            ['It', '\'s',  '2.45',  'cats', 'per', 'mango', '.'],
            self.t.tokenize('It\'s 2.45 cats per mango.')
        )

    def test_phone_number(self):
        """Test the word tokenizer on phone number containing hyphens"""
        self.assertEqual(
            ['Call',  'me',  'at', '02-2348-2192', '.'],
            self.t.tokenize('Call me at 02-2348-2192.')
        )

    def test_percentage(self):
        """Test the word tokenizer on percent sign."""
        self.assertEqual(
            ['The', 'company', 'spent', '40.75', '%', 'of', 'its', 'income', 'last', 'year', '.'],
            self.t.tokenize('The company spent 40.75% of its income last year.')
        )

    def test_colon_time(self):
        """Test the word tokenizer on colon between digits in a time."""
        self.assertEqual(
            ['He', 'arrived', 'at', '3:00', 'pm', '.'],
            self.t.tokenize('He arrived at 3:00 pm.')
        )

    def test_word_colon(self):
        """Test the word tokenizer on colon after word."""
        self.assertEqual(
            ['I', 'bought', 'these', 'items', ':', 'books', ',', 'pencils', ',', 'and', 'pens', '.'],
            self.t.tokenize('I bought these items: books, pencils, and pens.')
        )

    def test_digit_comma_space(self):
        """Test the word tokenizer on comma between digits with a space."""
        self.assertEqual(
            ['Though', 'there', 'were', '150', ',', '100', 'of', 'them', 'were', 'old', '.'],
            self.t.tokenize('Though there were 150, 100 of them were old.')
        )

    def test_digit_comma_multiple(self):
        """Test the word tokenizer on comma at end of digits."""
        self.assertEqual(
            ['There', 'were', '300,000', ',', 'but', 'that', 'was', "n't", 'enough', '.'],
            self.t.tokenize('There were 300,000, but that wasn\'t enough.')
        )

    def test_theyll(self):
        """Test the word tokenizer on the word they'll."""
        self.assertEqual(
            ['They', "'ll", 'save', 'and', 'invest', 'more', '.'],
            self.t.tokenize('They\'ll save and invest more.')
        )

    def test_bracket1(self):
        """Test the word tokenizer on sentence containing brackets."""
        self.assertEqual(
            ['For', 'a', 'few', 'weeks', '(', '>', '24', 'days', ')', '.'],
            self.t.tokenize('For a few weeks (>24 days).')
        )

    def test_contractions(self):
        """Test the word tokenizer on contractions."""
        self.assertEqual(
            ['Lem', 'me', 'in', ',', 'I', 'got', 'ta', 'gim', 'me', 'some', 'things', '.'],
            self.t.tokenize('Lemme in, I gotta gimme some things.')
        )

    def test_url(self):
        """Test the word tokenizer on URL."""
        self.assertEqual(
            ['The', 'address', 'is', 'http://www.chemdataextractor.org'],
            self.t.tokenize('The address is http://www.chemdataextractor.org')
        )

    def test_text_sentence(self):
        """Test tokenization through the Text and Sentence API."""
        t = Text('Hi, my name is Matt. What is your name?', word_tokenizer=WordTokenizer())
        self.assertEqual(
            [['Hi', ',', 'my', 'name', 'is', 'Matt', '.'], ['What', 'is', 'your', 'name', '?']],
            [sent.raw_tokens for sent in t.sentences]
        )


class TestChemTokenizer(unittest.TestCase):
    """Test the chemistry-aware word tokenizer."""

    maxDiff = None

    def setUp(self):
        self.t = ChemWordTokenizer()

    def test_final_full_stop(self):
        """Test the word tokenizer splits off final full stop only."""
        self.assertEqual(
            ['This', 'is', 'Mr.', 'Hoppy', '\'s', 'tortoise', '.'],
            self.t.tokenize('This is Mr. Hoppy\'s tortoise.')
        )

    def test_full_stop_following(self):
        """Test the word tokenizer splits off final full stop if followed by brackets or quotes."""
        self.assertEqual(
            ['(', 'This', 'is', 'Mr.', 'Hoppy', '\'s', 'tortoise', '.', ')'],
            self.t.tokenize('(This is Mr. Hoppy\'s tortoise.)')
        )
        self.assertEqual(
            ['"', 'This', 'is', 'Mr.', 'Hoppy', '\'s', 'tortoise', '.', '"'],
            self.t.tokenize('"This is Mr. Hoppy\'s tortoise."')
        )
        self.assertEqual(
            ['"', 'This', 'is', 'Mr.', 'Hoppy', '\'s', 'tort.oise', '.', '"'],
            self.t.tokenize('"This is Mr. Hoppy\'s tort.oise."')
        )

    def test_dollar(self):
        """Test the word tokenizer on dollar symbol."""
        self.assertEqual(
            ['On', 'a', '$', '50,000', 'mortgage', 'of', '30', 'years', 'at', '8', 'percent', ',', 'the', 'monthly', 'payment', 'would', 'be', '$', '366.88', '.'],
            self.t.tokenize('On a $50,000 mortgage of 30 years at 8 percent, the monthly payment would be $366.88.')
        )

    def test_quote(self):
        """Test the word tokenizer on quotes."""
        self.assertEqual(
            ['"', 'We', 'beat', 'some', 'pretty', 'good', 'teams', 'to', 'get', 'here', ',', '"', 'Slocum', 'said', '.'],
            self.t.tokenize('"We beat some pretty good teams to get here," Slocum said.')
        )

    def test_brackets_quotes(self):
        """Test the word tokenizer on brackets and quotes."""
        self.assertEqual(
            ['Well', ',', 'we', 'could', 'n\'t', 'have', 'this', 'predictable', ',', 'cliche', '-', 'ridden', ',', '"', 'Touched', 'by', 'an', 'Angel', '"', '(', 'a', 'show', 'creator', 'John', 'Masius', 'worked', 'on', ')', 'wanna-be', 'if', 'she', 'did', 'n\'t', '.'],
            self.t.tokenize('Well, we couldn\'t have this predictable, cliche-ridden, "Touched by an Angel" (a show creator John Masius worked on) wanna-be if she didn\'t.')
        )

    def test_exclamation(self):
        """Test the word tokenizer on exclamation mark."""
        self.assertEqual(
            ['I', 'can', 'not', 'can', 'not', 'work', 'under', 'these', 'conditions', '!'],
            self.t.tokenize('I cannot cannot work under these conditions!')
        )

    def test_digit_comma(self):
        """Test the word tokenizer on commas within numbers."""
        self.assertEqual(
            ['The', 'company', 'spent', '$', '30,000,000', 'last', 'year', '.'],
            self.t.tokenize('The company spent $30,000,000 last year.')
        )

    def test_percentage(self):
        """Test the word tokenizer on percent sign."""
        self.assertEqual(
            ['The', 'company', 'spent', '40.75', '%', 'of', 'its', 'income', 'last', 'year', '.'],
            self.t.tokenize('The company spent 40.75% of its income last year.')
        )

    def test_colon_time(self):
        """Test the word tokenizer on colon between digits in a time."""
        self.assertEqual(
            ['He', 'arrived', 'at', '3', ':', '00', 'pm', '.'],
            self.t.tokenize('He arrived at 3:00 pm.')
        )

    def test_word_colon(self):
        """Test the word tokenizer on colon after word."""
        self.assertEqual(
            ['I', 'bought', 'these', 'items', ':', 'books', ',', 'pencils', ',', 'and', 'pens', '.'],
            self.t.tokenize('I bought these items: books, pencils, and pens.')
        )

    def test_digit_comma_space(self):
        """Test the word tokenizer on comma between digits with a space."""
        self.assertEqual(
            ['Though', 'there', 'were', '150', ',', '100', 'of', 'them', 'were', 'old', '.'],
            self.t.tokenize('Though there were 150, 100 of them were old.')
        )

    def test_digit_comma_multiple(self):
        """Test the word tokenizer on comma at end of digits."""
        self.assertEqual(
            ['There', 'were', '300,000', ',', 'but', 'that', 'was', "n't", 'enough', '.'],
            self.t.tokenize('There were 300,000, but that wasn\'t enough.')
        )

    def test_theyll(self):
        """Test the word tokenizer on the word they'll."""
        self.assertEqual(
            ['They', "'ll", 'save', 'and', 'invest', 'more', '.'],
            self.t.tokenize('They\'ll save and invest more.')
        )

    def test_bracket1(self):
        """Test the word tokenizer on sentence containing brackets."""
        self.assertEqual(
            ['For', 'a', 'few', 'weeks', '(', '>', '24', 'days', ')', '.'],
            self.t.tokenize('For a few weeks (>24 days).')
        )

    def test_bracket2(self):
        """Test the word tokenizer on sentence containing brackets."""
        self.assertEqual(
            ['Coumarin', '343', '(', 'C343', ')', 'was', 'added', 'to', 'the', 'mixture', '.'],
            self.t.tokenize('Coumarin 343 (C343) was added to the mixture.')
        )

    def test_bracket3(self):
        """Test the word tokenizer on sentence containing brackets."""
        self.assertEqual(
            ['(', 'Ka', ':', '1.42', '×', '10(10)', 'M-1', 'vs', '1.95', '±', '0.35', '×', '10(10)', 'M-1', ')', 'and', 'increased', '(', '9.9', 'vs', '3.7', '±', '0.4', 'fmol', ')'],
            self.t.tokenize('(Ka: 1.42×10(10) M-1 vs 1.95±0.35×10(10) M-1) and increased (9.9 vs 3.7±0.4 fmol)')
        )

    def test_bracket4(self):
        """Test the word tokenizer on sentence containing chemical name with commas and brackets."""
        self.assertEqual(
            ['Pd-C', 'hydrogenation', 'of', '3,21-diacetoxy-5', 'beta,19-cyclopregna-2,9(11)-diene-4,20-dione', '(', '10', ')'],
            self.t.tokenize('Pd-C hydrogenation of 3,21-diacetoxy-5 beta,19-cyclopregna-2,9(11)-diene-4,20-dione (10)')
        )

    def test_bracket5(self):
        """Test the word tokenizer on sentence containing chemical name with commas and brackets."""
        self.assertEqual(
            ['(2E)-3-[5-(2,3-Dimethoxy-6-methyl-1,4-benzoquinoyl)]-2-nonyl-2-propenoic', 'acid'],
            self.t.tokenize('(2E)-3-[5-(2,3-Dimethoxy-6-methyl-1,4-benzoquinoyl)]-2-nonyl-2-propenoic acid')
        )

    def test_bracket6(self):
        """Test the word tokenizer on sentence containing chemical name with prime and brackets."""
        self.assertEqual(
            ['(2-Amino-3\'-methoxyphenyl)oxanaphthalen-4-one', '(', 'PD', '98059', ')'],
            self.t.tokenize('(2-Amino-3\'-methoxyphenyl)oxanaphthalen-4-one (PD 98059)')
        )

    def test_bracket7(self):
        """Test the word tokenizer on sentence containing chemical name with brackets."""
        self.assertEqual(
            ['The', 'maximum', '(3H)-thymidine', 'incorporation', 'into', 'DNA', '.'],
            self.t.tokenize('The maximum (3H)-thymidine incorporation into DNA.')
        )

    def test_comma1(self):
        """Test the word tokenizer on sentence containing chemical name with commas."""
        self.assertEqual(
            ['With', 'hot', 'acetic', '+', 'p-toluenesulfonic', 'acid', '5', 'underwent', 'rearrangement', 'to', '12-acetoxy-11', 'beta,19-epoxypregn-5-ene-4,20-dione', '(', '8', ')', '.'],
            self.t.tokenize('With hot acetic + p-toluenesulfonic acid 5 underwent rearrangement to 12-acetoxy-11 beta,19-epoxypregn-5-ene-4,20-dione (8).')
        )

    def test_comma2(self):
        """Test the word tokenizer on sentence containing chemical name with commas."""
        self.assertEqual(
            ['N,N-Dimethylformamide', '(', 'DMF', ')', 'was', 'used', 'as', 'solvent', '.'],
            self.t.tokenize('N,N-Dimethylformamide (DMF) was used as solvent.')
        )

    def test_comma3(self):
        """Test the word tokenizer on sentence containing chemical name with commas."""
        self.assertEqual(
            ['1,2-bis(o-aminophenoxy)-ethane-N,N,N\',N\'-tetraacetic', 'acid'],
            self.t.tokenize('1,2-bis(o-aminophenoxy)-ethane-N,N,N\',N\'-tetraacetic acid')
        )

    def test_comma4(self):
        """Test the word tokenizer on sentence containing chemical name with commas."""
        self.assertEqual(
            ['N,N,N\',N\'-tetrakis', '[2-pyridylmethyl]ethylenediamine'],
            self.t.tokenize('N,N,N\',N\'-tetrakis [2-pyridylmethyl]ethylenediamine')
        )

    def test_comma5(self):
        """Test the word tokenizer on sentence containing chemical name with commas."""
        self.assertEqual(
            ['o,o\'-bismyristoyl', 'and', 'α,α\'-dipyridyl'],
            self.t.tokenize('o,o\'-bismyristoyl and α,α\'-dipyridyl')
        )

    def test_comma6(self):
        """Test the word tokenizer on sentence containing chemical name with a prime character."""
        self.assertEqual(
            ['The', 'characteristics', 'of', 'the', 'C(sp,sp2,sp3)', '–', 'H', '⋯', 'F', '–', 'C(sp,sp2,sp3)', 'intermolecular'],
            self.t.tokenize('The characteristics of the C(sp,sp2,sp3)–H⋯F–C(sp,sp2,sp3) intermolecular')
        )

    def test_prime(self):
        """Test the word tokenizer on sentence containing chemical name with a prime character."""
        self.assertEqual(
            ['N,N′-heteroaromatic', 'ancillary', 'ligands'],
            self.t.tokenize('N,N′-heteroaromatic ancillary ligands')
        )

    def test_square_bracket(self):
        """Test the word tokenizer on sentence containing chemical name with square brackets."""
        self.assertEqual(
            ['[Hg(dman)2]', ',', 'with', '[PdCl2(SEt2)2]', 'or', '[{PdCl2(PPh3)}2]'],
            self.t.tokenize('[Hg(dman)2], with [PdCl2(SEt2)2] or [{PdCl2(PPh3)}2]')
        )

    def test_curly_bracket(self):
        """Test the word tokenizer on sentence containing chemical name with curly brackets."""
        self.assertEqual(
            ['bimetallic', 'complexes', ',', '{[Mn(salpn)]2[Fe(CN)5NO]}n', '(', '1', ')', ',', '{[Mn(salpn)(CH3OH)]4[Mn(CN)5NO]}[C(CN)3]·3H2O', '(', '2', ')', ',', '{[Mn(dapsc)][Fe(CN)5NO]·0.5CH3OH·0.25H2O}n', '(', '3', ')', 'and', '{[Mn(salpn)(CH3OH)]4[Fe(CN)5NO]}(ClO4)2·4H2O', '(', '4', ')', ',', 'where', 'salpn2−', '=', 'N,N′-1,3-propylene-bis(salicylideneiminato)', 'dianion', 'and', 'dapsc', '=', '2,6-diacetylpyridine-bis(semicarbazone)'],
            self.t.tokenize('bimetallic complexes, {[Mn(salpn)]2[Fe(CN)5NO]}n (1), {[Mn(salpn)(CH3OH)]4[Mn(CN)5NO]}[C(CN)3]·3H2O (2), {[Mn(dapsc)][Fe(CN)5NO]·0.5CH3OH·0.25H2O}n (3) and {[Mn(salpn)(CH3OH)]4[Fe(CN)5NO]}(ClO4)2·4H2O (4), where salpn2− = N,N′-1,3-propylene-bis(salicylideneiminato) dianion and dapsc = 2,6-diacetylpyridine-bis(semicarbazone)')
        )

    def test_bracket_internal_split(self):
        """Test the word tokenizer on sentence containing token that should be split internally and from brackets."""
        self.assertEqual(
            ['Extensive', 'H', '-', 'bonding', '(', 'F', '⋯', 'H', '–', 'OH', ')', 'links', 'the', 'molecules'],
            self.t.tokenize('Extensive H-bonding (F⋯H–OH) links the molecules')
        )

    def test_colon_chem(self):
        """Test the word tokenizer on chemical name containing colon."""
        self.assertEqual(
            ['Group', '13', 'fluorides', ',', 'MF3·3H2O', '(', 'M', '=', 'Al', ',', 'Ga', 'or', 'In', ')', 'with', '2,2′:6′,2′′-terpyridyl', ',', '2,2′-bipyridyl', 'or', '1,10-phenanthroline', 'under', 'hydrothermal', 'conditions', '(', '180', '°', 'C', '/', '15', 'h', ')'],
            self.t.tokenize('Group 13 fluorides, MF3·3H2O (M = Al, Ga or In) with 2,2′:6′,2′′-terpyridyl, 2,2′-bipyridyl or 1,10-phenanthroline under hydrothermal conditions (180 °C/15 h)')
        )

    def test_positive_charge(self):
        """Test the word tokenizer on chemical name with trailing plus."""
        self.assertEqual(
            ['[⊂Me2N(CH2)2NMe(CH2)2]+', ',', 'with', 'fluorometallate', 'anions'],
            self.t.tokenize('[⊂Me2N(CH2)2NMe(CH2)2]+, with fluorometallate anions')
        )

    def test_bracket_subsequent(self):
        """Test the word tokenizer on chemical name with subsequent (not nested) brackets."""
        self.assertEqual(
            ['The', 'α-ammonium-acylchloride', 'salts', '[NH2(CH2)3CHC(O)Cl][WOCl5]', ',', '1a', ',', 'and', '[MeNH2CH2C(O)Cl][WOCl5]', ',', '1b', '.'],
            self.t.tokenize('The α-ammonium-acylchloride salts [NH2(CH2)3CHC(O)Cl][WOCl5], 1a, and [MeNH2CH2C(O)Cl][WOCl5], 1b.')
        )

    def test_bracket_subsequent2(self):
        """Test the word tokenizer on chemical name with subsequent (not nested) brackets."""
        self.assertEqual(
            ['(N,N)-thingy-(errrm)'],
            self.t.tokenize('(N,N)-thingy-(errrm)')
        )

    def test_bracket_range(self):
        """Test the word tokenizer on a bracketed range."""
        self.assertEqual(
            ['(', 'a', ')', '–', '(', 'c', ')', 'Some', 'things', '.'],
            self.t.tokenize('(a)–(c) Some things.')
        )

    def test_space_colon_digit(self):
        """Test the word tokenizer on an usual spacing of colon."""
        self.assertEqual(
            ['Intensity', 'ratio', 'of', '2', ':', '2', ':', '4', 'and', '54', ':', '18', '.'],
            self.t.tokenize('Intensity ratio of 2 :2 :4 and 54 : 18.')
        )

    def test_quote_apostrophe(self):
        """Test the word tokenizer when a quote is used as an apostrophe."""
        self.assertEqual(
            ['Alzheimer', '\u2019s', 'disease', '(', 'AD', ')', 'was', '‘', 'extremely', '’', 'hard', '‘', 'to', 'diagnose', '.', '’'],
            self.t.tokenize('Alzheimer’s disease (AD) was ‘extremely’ hard ‘to diagnose.’')
        )

    def test_quote_apostrophe2(self):
        """Test the word tokenizer when a quote is used as an apostrophe."""
        self.assertEqual(
            ['Alzheimer', '\u2019s', 'disease', '(', 'AD', ')', 'was', '‘', 'extremely', '’', 'hard', '‘', 'to', 'diagnose', '’', '.'],
            self.t.tokenize('Alzheimer’s disease (AD) was ‘extremely’ hard ‘to diagnose’.')
        )

    def test_quote_apostrophe3(self):
        """Test the word tokenizer when a quote is used as an apostrophe."""
        self.assertEqual(
            ['Alzheimer', '\u2019s', 'disease', '(', 'AD', ')', 'was', '‘', 'extremely', '’', 'hard', '‘', 'to', 'diagnose', '’', ',', 'at', 'the', 'time', '.'],
            self.t.tokenize('Alzheimer’s disease (AD) was ‘extremely’ hard ‘to diagnose’, at the time.')
        )

    def test_apostrophe_quote(self):
        """Test the word tokenizer when an apostrophe is used as a quote."""
        self.assertEqual(
            ["a", "Special", "Issue", "entitled", "'", "Cognitive", "Enhancers", "'", "."],
            self.t.tokenize("a Special Issue entitled 'Cognitive Enhancers'.")
        )

    def test_double_apostrophe_quote(self):
        """Test the word tokenizer when an apostrophe is used as a quote."""
        self.assertEqual(
            ["between", "the", "''", "Schiff", "base", "''", "and"],
            self.t.tokenize("between the ''Schiff base'' and")
        )

    def test_bracketed_url(self):
        """Test the word tokenizer on a bracketed URL."""
        self.assertEqual(
            ['QALIBRA', 'software', '(', 'www.qalibra.eu', ')'],
            self.t.tokenize('QALIBRA software (www.qalibra.eu)')
        )

    def test_symbols(self):
        self.assertEqual(['2', '+', '2', '=', '4'], self.t.tokenize('2+2=4'))
        self.assertEqual(['+', '4', '°', 'C'], self.t.tokenize('+4°C'))
        self.assertEqual(['(', 'H2A', '<-->', 'HA-', '+', 'H+', 'and', 'HA-', '<-->', 'A', '=', '+', 'H+', ')'], self.t.tokenize('(H2A <--> HA- + H+ and HA- <--> A= + H+)'))
        self.assertEqual(['[2+2+2]'], self.t.tokenize('[2+2+2]'))
        self.assertEqual(['95.5', '+/-', '0.2', '%'], self.t.tokenize('95.5 +/- 0.2%'))

    def test_sentence_end(self):
        self.assertEqual(['upon', 'addition', 'of', 'Ni(II)', ';'], self.t.tokenize('upon addition of Ni(II);'))
        self.assertEqual(['upon', 'addition', 'of', 'Ni(II)', '.'], self.t.tokenize('upon addition of Ni(II).'))
        self.assertEqual(['complexes', 'in', 'THF', '(', 'ii', ')', '.'], self.t.tokenize('complexes in THF (ii).'))
        self.assertEqual(['complexes', 'in', 'THF', '(', 'ii', ')', ','], self.t.tokenize('complexes in THF (ii),'))
        self.assertEqual(['measured', 'at', '303', 'K', '.'], self.t.tokenize('measured at 303 K.'))
        self.assertEqual(['Sentence', 'trails', 'off', '…'], self.t.tokenize('Sentence trails off…'))
        self.assertEqual(['Sentence', 'trails', 'off', '...'], self.t.tokenize('Sentence trails off...'))
        self.assertEqual(['in', 'the', 'AUC', '.'], self.t.tokenize('in the AUC.'))
        self.assertEqual(['for', 'lane', 'no.', '11', '.'], self.t.tokenize('for lane no. 11.'))
        self.assertEqual(['under', 'A.', 'M.', '1.5', 'illumination'], self.t.tokenize('under A. M. 1.5 illumination'))
        self.assertEqual(['space', 'group', 'P', '(', 'No.', '2', ')', '.'], self.t.tokenize('space group P (No. 2).'))

    def test_abbreviations(self):
        self.assertEqual(['(', 'ca.', '30', 'mL', ')'], self.t.tokenize('(ca. 30 mL)'))
        self.assertEqual(['Elements', ',', 'e.g.', 'calcium'], self.t.tokenize('Elements, e.g. calcium'))

    def test_more_brackets(self):
        self.assertEqual(['NaOH', '(', 'aq', ')'], self.t.tokenize('NaOH(aq)'))
        self.assertEqual(['HCl', '(', 'g', ')'], self.t.tokenize('HCl(g)'))
        self.assertEqual(['5(g)'], self.t.tokenize('5(g)'))
        self.assertEqual(['a', ')', 'UV', '/', 'vis', 'spectrum', '.'], self.t.tokenize('a) UV/vis spectrum.'))
        self.assertEqual(['a', ')', 'UV', '-', 'vis', 'spectrum', '.'], self.t.tokenize('a) UV-vis spectrum.'))
        self.assertEqual(['(', 'c', ')', '–', '(', 'e', ')'], self.t.tokenize('(c)–(e)'))
        self.assertEqual(['THF', '(', 'i', ')', ',', 'toluene', '(', 'iii', ')'], self.t.tokenize('THF (i), toluene (iii)'))
        self.assertEqual(['buffer', '(', 'pH', '7.4', ')', '.'], self.t.tokenize('buffer (pH 7.4).'))

    def test_multihyphens(self):
        self.assertEqual(['---'], self.t.tokenize('---'))
        self.assertEqual(['–––'], self.t.tokenize('–––'))
        self.assertEqual(['———'], self.t.tokenize('———'))
        self.assertEqual(['−−−'], self.t.tokenize('−−−'))
        self.assertEqual(['--'], self.t.tokenize('--'))
        self.assertEqual(['––'], self.t.tokenize('––'))
        self.assertEqual(['——'], self.t.tokenize('——'))
        self.assertEqual(['−−'], self.t.tokenize('−−'))

    def test_tilde(self):
        self.assertEqual(['a', 'line', 'width', 'of', '\u223c', '3', 'Hz', '.'], self.t.tokenize('a line width of ∼3 Hz.'))
        self.assertEqual(['a', 'line', 'width', 'of', '~', '3', 'Hz', '.'], self.t.tokenize('a line width of ~3 Hz.'))

    def test_slashes(self):
        self.assertEqual(['methanol', '/', 'water'], self.t.tokenize('methanol/water'))
        self.assertEqual(['B3LYP', '/', '6-311G(d,p)'], self.t.tokenize('B3LYP/6-311G(d,p)'))

    def test_iron_states(self):
        self.assertEqual(['Fe(III)'], self.t.tokenize('Fe(III)'))
        self.assertEqual(['Fe(iii)'], self.t.tokenize('Fe(iii)'))
        self.assertEqual(['Fe(3+)'], self.t.tokenize('Fe(3+)'))
        self.assertEqual(['Fe(0)'], self.t.tokenize('Fe(0)'))

    def test_identifiers(self):
        self.assertEqual(['4CN'], self.t.tokenize('4CN'))
        self.assertEqual(['2a'], self.t.tokenize('2a'))

    def test_colons(self):
        self.assertEqual(['ethanol', ':', 'water'], self.t.tokenize('ethanol:water'))
        self.assertEqual(['1', ':', '2'], self.t.tokenize('1:2'))
        self.assertEqual(['1', ':', '2'], self.t.tokenize('1 : 2'))
        self.assertEqual(['(', 'foo', ')', ':', '(', 'bar', ')'], self.t.tokenize('(foo):(bar)'))
        self.assertEqual(['foo', ')', ':', '(', 'bar'], self.t.tokenize('foo):(bar'))
        self.assertEqual(['4:7,10:13-diepoxy[15]annulenone'], self.t.tokenize('4:7,10:13-diepoxy[15]annulenone'))
        self.assertEqual(['9-(5′,5-diphenyl[1,1′:3′,1′′:3′′,1:3,1′′′′-quinquephenyl]-5′′-diyl)-9H-carbazole'], self.t.tokenize('9-(5′,5-diphenyl[1,1′:3′,1′′:3′′,1:3,1′′′′-quinquephenyl]-5′′-diyl)-9H-carbazole'))
        self.assertEqual(['9,9′-(5′-phenyl[1,1′:3′,1′′-terphenyl]-3,5-diyl)bis-9H-carbazole'], self.t.tokenize('9,9′-(5′-phenyl[1,1′:3′,1′′-terphenyl]-3,5-diyl)bis-9H-carbazole'))

    def test_lambda(self):
        self.assertEqual(['lambda5-phosphane'], self.t.tokenize('lambda5-phosphane'))
        self.assertEqual(['λ5-phosphane'], self.t.tokenize('λ5-phosphane'))

    def test_chem_names(self):
        self.assertEqual(['Tetrahydro', 'furan', '(', 'THF', ')'], self.t.tokenize('Tetrahydro furan (THF)'))
        self.assertEqual(['(S)-alanine'], self.t.tokenize('(S)-alanine'))
        self.assertEqual(['D-glucose'], self.t.tokenize('D-glucose'))
        self.assertEqual(['spiro[4.5]decane'], self.t.tokenize('spiro[4.5]decane'))
        self.assertEqual(['β-D-Glucose'], self.t.tokenize('β-D-Glucose'))
        self.assertEqual(['L-alanyl-L-glutaminyl-L-arginyl-O-phosphono-L-seryl-L-alanyl-L-proline'],
                         self.t.tokenize('L-alanyl-L-glutaminyl-L-arginyl-O-phosphono-L-seryl-L-alanyl-L-proline'))
        self.assertEqual(['aluminium(3+)'], self.t.tokenize('aluminium(3+)'))
        self.assertEqual(['1-methyl-2-methylidene-cyclohexane'],
                         self.t.tokenize('1-methyl-2-methylidene-cyclohexane'))

    def test_rings(self):
        self.assertEqual(["2,2':6',2''-Terphenyl-1,1',1''-triol"],
                         self.t.tokenize("2,2':6',2''-Terphenyl-1,1',1''-triol"))
        self.assertEqual(["phenothiazino[3',4':5,6][1,4]oxazino[2,3-i]benzo[5,6][1,4]thiazino[3,2-c]phenoxazine"],
                         self.t.tokenize("phenothiazino[3',4':5,6][1,4]oxazino[2,3-i]benzo[5,6][1,4]thiazino[3,2-c]phenoxazine"))

    def test_saccharide(self):
        self.assertEqual(['beta-D-Glucopyranosyl-(1->4)-D-glucose'], self.t.tokenize('beta-D-Glucopyranosyl-(1->4)-D-glucose'))
        self.assertEqual(['α-D-Glucopyranosyl-(1→4)-β-D-glucopyranose'], self.t.tokenize('α-D-Glucopyranosyl-(1→4)-β-D-glucopyranose'))
        self.assertEqual(['α-L-Fucp-(1→3)-[α-D-Galp-(1→4)]-α-D-Glcp-(1→3)-α-D-GalpOAll'], self.t.tokenize('α-L-Fucp-(1→3)-[α-D-Galp-(1→4)]-α-D-Glcp-(1→3)-α-D-GalpOAll'))
        self.assertEqual(['(1→4)-β-D-Glucan'], self.t.tokenize('(1→4)-β-D-Glucan'))
        self.assertEqual(['((1→2)-α-D-galacto)-(1→4)-β-D-Glucan'], self.t.tokenize('((1→2)-α-D-galacto)-(1→4)-β-D-Glucan'))

    def test_polymer(self):
        self.assertEqual([u"poly(2,2'-diamino-5-hexadecylbiphenyl-3,3'-diyl)"],
                         self.t.tokenize(u"poly(2,2'-diamino-5-hexadecylbiphenyl-3,3'-diyl)"))

    def test_operators(self):
        self.assertEqual(['J', '=', '8.8'], self.t.tokenize('J=8.8'))
        self.assertEqual(['CH2', '=', 'CH2'], self.t.tokenize('CH2=CH2'))
        self.assertEqual(['mL', '×', '3'], self.t.tokenize('mL×3'))
        self.assertEqual(['3', '×'], self.t.tokenize('3×'))
        self.assertEqual(['×', '3'], self.t.tokenize('×3'))
        self.assertEqual(['15', '÷', '3'], self.t.tokenize('15÷3'))
        self.assertEqual(['5', '+', '3'], self.t.tokenize('5+3'))
        self.assertEqual(['ESI+'], self.t.tokenize('ESI+'))
        self.assertEqual(['Ce3+'], self.t.tokenize('Ce3+'))

    def test_stereo(self):
        self.assertEqual(['(+)-chiraline'], self.t.tokenize('(+)-chiraline'))
        self.assertEqual(['(-)-chiraline'], self.t.tokenize('(-)-chiraline'))
        self.assertEqual(['(+-)-chiraline'], self.t.tokenize('(+-)-chiraline'))  # \u002d Hyphen-minus
        self.assertEqual(['(+−)-chiraline'], self.t.tokenize('(+−)-chiraline'))  # \u2212 Minus
        self.assertEqual(['(+/-)-chiraline'], self.t.tokenize('(+/-)-chiraline'))  # \u002d Hyphen-minus
        self.assertEqual(['(+/−)-chiraline'], self.t.tokenize('(+/−)-chiraline'))  # \u2212 Minus
        self.assertEqual(['(±)-chiraline'], self.t.tokenize('(±)-chiraline'))

    def test_hyphen_twice(self):
        self.assertEqual(['cytoplasmic', '-', 'to', '-', 'nuclear'], self.t.tokenize('cytoplasmic-to-nuclear'))
        self.assertEqual(['layer', '-', 'by', '-', 'layer'], self.t.tokenize('layer-by-layer'))
        self.assertEqual(['end', '-', 'of', '-', 'phase'], self.t.tokenize('end-of-phase'))
        self.assertEqual(['oil', '-', 'in', '-', 'water'], self.t.tokenize('oil-in-water'))
        self.assertEqual(['nucleation', '-', 'and', '-', 'growth'], self.t.tokenize('nucleation-and-growth'))
        self.assertEqual(['State', '-', 'of', '-', 'the', '-', 'art'], self.t.tokenize('State-of-the-art'))

    def test_nmr_types(self):
        self.assertEqual(['(13)C', '-', 'NMR'], self.t.tokenize('(13)C-NMR'))
        self.assertEqual(['(1)H', '-', 'NMR'], self.t.tokenize('(1)H-NMR'))
        self.assertEqual(['(31)P', '-', 'NMR'], self.t.tokenize('(31)P-NMR'))
        self.assertEqual(['(19)F', '-', 'NMR'], self.t.tokenize('(19)F-NMR'))
        self.assertEqual(['13C', '-', 'NMR'], self.t.tokenize('13C-NMR'))
        self.assertEqual(['1H', '-', 'NMR'], self.t.tokenize('1H-NMR'))
        self.assertEqual(['31P', '-', 'NMR'], self.t.tokenize('31P-NMR'))
        self.assertEqual(['19F', '-', 'NMR'], self.t.tokenize('19F-NMR'))
        self.assertEqual(['proton', '-', 'NMR'], self.t.tokenize('proton-NMR'))

    def test_bracket_hyphen(self):
        self.assertEqual(['(LBD)-linked'], self.t.tokenize('(LBD)-linked'))
        self.assertEqual(['Fe(IV)', '-', 'oxo-mediated'], self.t.tokenize('Fe(IV)-oxo-mediated'))
        self.assertEqual(['Fe(IV)', '-', 'mediated'], self.t.tokenize('Fe(IV)-mediated'))
        self.assertEqual(['T-bet(-/-)'], self.t.tokenize('T-bet(-/-)'))
        self.assertEqual(['(', 'nano', 'LC', '/', 'nano-ESI-IT-MS', ')'], self.t.tokenize('(nano LC/nano-ESI-IT-MS)'))

    def test_hyphen_nosplit(self):
        self.assertEqual(['1,4-addition'], self.t.tokenize('1,4-addition'))
        self.assertEqual(['1,3\'-substituted'], self.t.tokenize('1,3\'-substituted'))
        self.assertEqual(['3,3′-dianisyl-substituted'], self.t.tokenize('3,3′-dianisyl-substituted'))
        self.assertEqual(['α-substituted'], self.t.tokenize('α-substituted'))
        self.assertEqual(['meta-substituted'], self.t.tokenize('meta-substituted'))
        self.assertEqual(['poly-zwitterion'], self.t.tokenize('poly-zwitterion'))
        self.assertEqual(['1,2-zwitterion'], self.t.tokenize('1,2-zwitterion'))

    def test_element_hyphen(self):
        self.assertEqual(['Fe', '-', 'containing'], self.t.tokenize('Fe-containing'))
        self.assertEqual(['C', '-', 'terminal'], self.t.tokenize('C-terminal'))
        self.assertEqual(['Li', '-', 'ions'], self.t.tokenize('Li-ions'))

    def test_hyphen_split(self):
        self.assertEqual(['hydrocarbon', '-', 'based'], self.t.tokenize('hydrocarbon-based'))
        self.assertEqual(['methicillin', '-', 'resistant'], self.t.tokenize('methicillin-resistant'))
        self.assertEqual(['methicillin', '-', 'resistant', ','], self.t.tokenize('methicillin-resistant,'))
        self.assertEqual(['HPMA', '-', 'based'], self.t.tokenize('HPMA-based'))
        self.assertEqual(['HPMA', '-', 'based', ')'], self.t.tokenize('HPMA-based)'))

    def test_bracket_chem2(self):
        """Test the word tokenizer on chemical name containing brackets."""
        self.assertEqual(
            ['(-)-(5R,8S,8aS)-8-methyl-5-pentyloctahydroindolizine', '(', '8-epi-indolizidine', '209B', ')', '9', 'in', '74', '%', 'yield', '.'],
            self.t.tokenize('(-)-(5R,8S,8aS)-8-methyl-5-pentyloctahydroindolizine (8-epi-indolizidine 209B) 9 in 74% yield.')
        )

    def test_bracket_chem_identifier(self):
        """Test the word tokenizer on chemical identifier with stereo brackets."""
        self.assertEqual(
            ['produced', 'the', 'thiolactam', '(+)-27', 'in', '92', '%', 'yield', '.'],
            self.t.tokenize('produced the thiolactam (+)-27 in 92% yield.')
        )

    def test_minus_hyphen(self):
        """Test the word tokenizer on a minus used as a hyphen."""
        self.assertEqual(
            ['The', 'dose', '−', 'response', 'curve', '.'],
            self.t.tokenize('The dose−response curve.')
        )

    def test_abbreviation_sentence_end(self):
        """Test the word tokenizer on sentence with abbreviation at the end."""
        self.assertEqual(['Chemical', 'Company', 'Ltd.'], self.t.tokenize('Chemical Company Ltd.'))
        self.assertEqual(['Studies', 'in', 'the', 'U.S.'], self.t.tokenize('Studies in the U.S.'))
        self.assertEqual(['the', 'mean', '±', 'S.D.'], self.t.tokenize('the mean ± S.D.'))
        self.assertEqual(['in', 'a', 'beaker', 'at', 'r.t.'], self.t.tokenize('in a beaker at r.t.'))
        self.assertEqual(['Whitaker', 'et', 'al.'], self.t.tokenize('Whitaker et al.'))

    def test_trademarks(self):
        self.assertEqual(['CML', '(', 'TM', ')'], self.t.tokenize('CML(TM)'))
        self.assertEqual(['Apple', '(', 'R', ')'], self.t.tokenize('Apple(R)'))
        self.assertEqual(['IR3535', '(', '®', ')'], self.t.tokenize('IR3535(®)'))
        self.assertEqual(['IR3535', '(', '™', ')'], self.t.tokenize('IR3535(™)'))
        self.assertEqual(['IR3535', '(', 'TM', ')'], self.t.tokenize('IR3535(TM)'))
        self.assertEqual(['IR3535', '(', 'R', ')'], self.t.tokenize('IR3535(R)'))
        self.assertEqual(['IR3535', '®'], self.t.tokenize('IR3535®'))
        self.assertEqual(['IR3535', '™'], self.t.tokenize('IR3535™'))

    def test_ms(self):
        self.assertEqual(['[M+H]+', '1523.86', ',', '[M+2H]2+', '762.43', ',', '[M+3H]3+', '508.62.', 'Observed', ':', '[M+H]+', '1523.20', ',', '[M+2H]2+', '762.45', ',', '[M+3H]3+', '508.70', '.'], self.t.tokenize('[M+H]+ 1523.86, [M+2H]2+ 762.43, [M+3H]3+ 508.62. Observed: [M+H]+ 1523.20, [M+2H]2+ 762.45, [M+3H]3+ 508.70.'))
        # This isn't ideal but can't see any alternative apart from super fine tokenization
        self.assertEqual(['527.3596', '[', 'M', '+', 'H]+', ',', 'C30H47N4O4+'], self.t.tokenize('527.3596 [M + H]+, C30H47N4O4+'))

    def test_quantities(self):
        self.assertEqual(['contamination', 'of', '2', '%', 'Cl2'], self.t.tokenize('contamination of 2% Cl2'))
        self.assertEqual(['Placed', 'at', 'a', 'distance', 'of', '7.2', 'cm', '.'], self.t.tokenize('Placed at a distance of 7.2cm.'))
        self.assertEqual(['Addition', 'of', '~', '1.8', 'mg', 'of', 'CaCO3', '.'], self.t.tokenize('Addition of ~1.8mg of CaCO3.'))
        self.assertEqual(['Recorded', 'in', 'HCl', '(', 'pH', '2', ')', '.'], self.t.tokenize('Recorded in HCl (pH2).'))
        self.assertEqual(['Experienced', 'a', 'pressure', 'of', '160', 'kPa', '.'], self.t.tokenize('Experienced a pressure of 160kPa.'))
        self.assertEqual(['Brought', 'to', 'pH', '10.5', ',', 'gradually', '.'], self.t.tokenize('Brought to pH10.5, gradually.'))
        self.assertEqual(['A', 'volume', 'of', '24', 'cm3', 'was', 'drained', '.'], self.t.tokenize('A volume of 24cm3 was drained.'))
        self.assertEqual(['2', 'M', 'H2SO4', 'was', 'heated', '.'], self.t.tokenize('2M H2SO4 was heated.'))
        self.assertEqual(['The', 'spectrum', 'was', 'recorded', 'at', '10', '°', 'C'], self.t.tokenize('The spectrum was recorded at 10° C'))
        self.assertEqual(['The', 'spectrum', 'was', 'recorded', 'at', '10', '°', 'C'], self.t.tokenize('The spectrum was recorded at 10°C'))
        self.assertEqual(['The', 'spectrum', 'was', 'recorded', 'at', '10', '°', 'C'], self.t.tokenize('The spectrum was recorded at 10 °C'))
        self.assertEqual(['Added', '3.5', 'g', 'and', 'stirred', 'for', '5.5', 's', '.'], self.t.tokenize('Added 3.5g and stirred for 5.5s.'))
        self.assertEqual(['and', '≈', '90', '°'], self.t.tokenize('and ≈90°'))
        self.assertEqual(['B3LYP', '/', '6-31g(d)'], self.t.tokenize('B3LYP/6-31g(d)'))
        self.assertEqual(['N', '1s', 'spectra'], self.t.tokenize('N 1s spectra'))
        self.assertEqual(['In', 'the', '1980s', 'there', 'was'], self.t.tokenize('In the 1980s there was'))
        self.assertEqual(['Produced', 'compounds', '3g', ',', '3l', ',', '3m', 'and', '3n'], self.t.tokenize('Produced compounds 3g, 3l, 3m and 3n'))
        self.assertEqual(['9.66', '(', 'd', ',', '1H', ',', '3J', '=', '5.4', 'Hz', ',', 'H15', ')'], self.t.tokenize('9.66 (d, 1H, 3J = 5.4Hz, H15)'))
        self.assertEqual(['greater', 'than', '3', '×', '10-11', 'mol', 'kg-1', 'or', '2', '×', '10-5', 'mol', 'kg-1'], self.t.tokenize('greater than 3 × 10-11mol kg-1 or 2 × 10-5mol kg-1'))

    def test_linesymbols(self):
        self.assertEqual(['N', '(', '■', ')', ',', 'C2', '(', '●', ')', ',', 'C3', '(', '▲', ')'],
                         self.t.tokenize('N(■), C2(●), C3(▲)'))
        self.assertEqual(['benzaldehyde', '(', '○', ')'], self.t.tokenize('benzaldehyde (○)'))
        self.assertEqual(['6', '(', '--', ')', ',', '1', '(', '----', ')', 'and', '3', '(', '·····', ')'],
                         self.t.tokenize('6 (--), 1 (----) and 3 (·····)'))
        self.assertEqual(['6', '(', '--', ')', ',', '1', '(', '----', ')', 'and', '3', '(', '·····', ')'],
                         self.t.tokenize('6 (--), 1 (----) and 3 (·····)'))

    def test_bracket_chems(self):
        self.assertEqual(['molecules', 'of', 'the', '[NiL2]', 'complex'], self.t.tokenize('molecules of the [NiL2] complex'))
        self.assertEqual(['[Et3NBz][FeIIICl4]'], self.t.tokenize('[Et3NBz][FeIIICl4]'))
        self.assertEqual(['[2PA-Mmim][Tf2N]'], self.t.tokenize('[2PA-Mmim][Tf2N]'))
        self.assertEqual(['[H2O]', '≈', '3000', 'ppm'], self.t.tokenize('[H2O] ≈ 3000 ppm'))
        self.assertEqual(['(', '[Cu+]', '/', '[L]', '=', '3', ')'], self.t.tokenize('([Cu+]/[L] = 3)'))
        self.assertEqual(['(Ph3PO)(Ph3POH)(HSO4)'], self.t.tokenize('(Ph3PO)(Ph3POH)(HSO4)'))
        self.assertEqual(['(', 'iron(III)'], self.t.tokenize('(iron(III)'))

    def test_chem_formula(self):
        self.assertEqual(['(C2H5)4N'], self.t.tokenize('(C2H5)4N'))
        self.assertEqual(['(C2H5)4N'], self.t.tokenize('(C2H5)4N'))
        self.assertEqual(['monomer', '28M-Py2'], self.t.tokenize('monomer 28M-Py2'))
        self.assertEqual(['monomer', '28M-Py2'], self.t.tokenize('monomer 28M-Py2'))
        self.assertEqual(['ratio', 'Ag+', '/', 'nucleoside', 'of', '3', ':', '1'], self.t.tokenize('ratio Ag+/nucleoside of 3:1'))
        self.assertEqual(['[Al(H2L)n]3-'], self.t.tokenize('[Al(H2L)n]3-'))
        self.assertEqual(['[Fe(CN)5(NO)]2-'], self.t.tokenize('[Fe(CN)5(NO)]2-'))
        self.assertEqual(['[Fe(CN)5(NO)]2−'], self.t.tokenize('[Fe(CN)5(NO)]2−'))

    def test_deuterated(self):
        self.assertEqual(['acetone-d6'], self.t.tokenize('acetone-d6'))
        self.assertEqual(['chloroform-d'], self.t.tokenize('chloroform-d'))
        self.assertEqual(['d8-THF'], self.t.tokenize('d8-THF'))
        self.assertEqual(['THF-d8'], self.t.tokenize('THF-d8'))
        self.assertEqual(['d6-DMSO'], self.t.tokenize('d6-DMSO'))
        self.assertEqual(['DMSO-d6'], self.t.tokenize('DMSO-d6'))

    def test_reagents_list(self):
        """Test the word tokenizer on a reagents list."""
        self.assertEqual(
            ['Reagents', ':', '(', 'i', ')', 'H2', '(', '7', 'atm', ')', ',', '10', '%', 'Pd', '/', 'C', ',', 'AcOH', ',', 'rt', ';', '(', 'ii', ')', 'Cl(CH2)3COCl', ',', 'NaOEt', '(', 'cat.', ')', ',', 'CHCl3', ',', 'reflux', ';', '(', 'iii', ')', 'Lawesson', '\'s', 'reagent', ',', '110', '°', 'C', ';'],
            self.t.tokenize('Reagents: (i) H2 (7 atm), 10% Pd/C, AcOH, rt; (ii) Cl(CH2)3COCl, NaOEt (cat.), CHCl3, reflux; (iii) Lawesson\'s reagent, 110°C;')
        )

    def test_abbreviation_definition(self):
        """Test the word tokenizer on chemical abbreviation definition."""
        self.assertEqual(
            ['(', 'ADDP', ':', "1,1'-(azodicarbonyl)dipiperidine", ')'],
            self.t.tokenize('(ADDP: 1,1\'-(azodicarbonyl)dipiperidine)')
        )

    def test_nmr_whitespace_error(self):
        """Test the word tokenizer on NMR isotope missing preceding whitespace."""
        self.assertEqual(['726.1520', '.', '1H', 'NMR'], self.t.tokenize('726.1520.1H NMR'))
        self.assertEqual(['intermediate', '.', '1H', u'NMR'], self.t.tokenize('intermediate.1H NMR'))

    def test_ir_whitespace_error(self):
        """Test things like IR(KBr)."""
        self.assertEqual(['IR', '(', 'KBr', ')'], self.t.tokenize('IR(KBr)'))

    def test_bracket_whitespace_error(self):
        """Test the word tokenizer on bracket whitespace error."""
        self.assertEqual(['7.95', '(', 's', ',', '4H', ')'], self.t.tokenize('7.95(s, 4H)'))
        self.assertEqual(['In', 'Fig.', '5', '(', 'a', ',', 'b', ')'], self.t.tokenize('In Fig. 5(a, b)'))

    def test_chemtext_sentence(self):
        """Test tokenization through the Text and Sentence API."""
        t = Text('Hi, my name is Matt. What is your name?')
        self.assertEqual(
            [['Hi', ',', 'my', 'name', 'is', 'Matt', '.'], ['What', 'is', 'your', 'name', '?']],
            [sent.raw_tokens for sent in t.sentences]
        )

    def test_chemtext_sentence2(self):
        """Test tokenization through the ChemText and Sentence API."""
        t = Text('(Ka: 1.42×10(10) M-1 vs 1.95±0.35×10(10) M-1) and increased (9.9 vs 3.7±0.4 fmol)')
        self.assertEqual(
            [['(', 'Ka', ':', '1.42', '×', '10(10)', 'M-1', 'vs', '1.95', '±', '0.35', '×', '10(10)', 'M-1', ')', 'and', 'increased', '(', '9.9', 'vs', '3.7', '±', '0.4', 'fmol', ')']],
            [sent.raw_tokens for sent in t.sentences]
        )


class TestFineWordTokenizer(unittest.TestCase):
    """Test the fine word tokenizer."""

    maxDiff = None

    def setUp(self):
        self.t = FineWordTokenizer()

    def test_final_full_stop(self):
        """Test the word tokenizer splits off final full stop only."""
        self.assertEqual(
            ['This', 'is', 'Mr.', 'Hoppy', '\'s', 'tortoise', '.'],
            self.t.tokenize('This is Mr. Hoppy\'s tortoise.')
        )

    def test_full_stop_following(self):
        """Test the word tokenizer splits off final full stop if followed by brackets or quotes."""
        self.assertEqual(
            ['(', 'This', 'is', 'Mr.', 'Hoppy', '\'s', 'tortoise', '.', ')'],
            self.t.tokenize('(This is Mr. Hoppy\'s tortoise.)')
        )
        self.assertEqual(
            ['"', 'This', 'is', 'Mr.', 'Hoppy', '\'s', 'tortoise', '.', '"'],
            self.t.tokenize('"This is Mr. Hoppy\'s tortoise."')
        )
        self.assertEqual(
            ['"', 'This', 'is', 'Mr.', 'Hoppy', '\'s', 'tort.oise', '.', '"'],
            self.t.tokenize('"This is Mr. Hoppy\'s tort.oise."')
        )

    def test_dollar(self):
        """Test the word tokenizer on dollar symbol."""
        self.assertEqual(
            ['On', 'a', '$', '50,000', 'mortgage', 'of', '30', 'years', 'at', '8', 'percent', ',', 'the', 'monthly', 'payment', 'would', 'be', '$', '366.88', '.'],
            self.t.tokenize('On a $50,000 mortgage of 30 years at 8 percent, the monthly payment would be $366.88.')
        )

    def test_quote(self):
        """Test the word tokenizer on quotes."""
        self.assertEqual(
            ['"', 'We', 'beat', 'some', 'pretty', 'good', 'teams', 'to', 'get', 'here', ',', '"', 'Slocum', 'said', '.'],
            self.t.tokenize('"We beat some pretty good teams to get here," Slocum said.')
        )

    def test_brackets_quotes(self):
        """Test the word tokenizer on brackets and quotes."""
        self.assertEqual(
            ['Well', ',', 'we', 'could', 'n\'t', 'have', 'this', 'predictable', ',', 'cliche', '-', 'ridden', ',', '"', 'Touched', 'by', 'an', 'Angel', '"', '(', 'a', 'show', 'creator', 'John', 'Masius', 'worked', 'on', ')', 'wan', 'na', '-', 'be', 'if', 'she', 'did', 'n\'t', '.'],
            self.t.tokenize('Well, we couldn\'t have this predictable, cliche-ridden, "Touched by an Angel" (a show creator John Masius worked on) wanna-be if she didn\'t.')
        )

    def test_exclamation(self):
        """Test the word tokenizer on exclamation mark."""
        self.assertEqual(
            ['I', 'can', 'not', 'can', 'not', 'work', 'under', 'these', 'conditions', '!'],
            self.t.tokenize('I cannot cannot work under these conditions!')
        )

    def test_digit_comma(self):
        """Test the word tokenizer on commas within numbers."""
        self.assertEqual(
            ['The', 'company', 'spent', '$', '30,000,000', 'last', 'year', '.'],
            self.t.tokenize('The company spent $30,000,000 last year.')
        )

    def test_percentage(self):
        """Test the word tokenizer on percent sign."""
        self.assertEqual(
            ['The', 'company', 'spent', '40.75', '%', 'of', 'its', 'income', 'last', 'year', '.'],
            self.t.tokenize('The company spent 40.75% of its income last year.')
        )

    def test_colon_time(self):
        """Test the word tokenizer on colon between digits in a time."""
        self.assertEqual(
            ['He', 'arrived', 'at', '3', ':', '00', 'pm', '.'],
            self.t.tokenize('He arrived at 3:00 pm.')
        )

    def test_word_colon(self):
        """Test the word tokenizer on colon after word."""
        self.assertEqual(
            ['I', 'bought', 'these', 'items', ':', 'books', ',', 'pencils', ',', 'and', 'pens', '.'],
            self.t.tokenize('I bought these items: books, pencils, and pens.')
        )

    def test_digit_comma_space(self):
        """Test the word tokenizer on comma between digits with a space."""
        self.assertEqual(
            ['Though', 'there', 'were', '150', ',', '100', 'of', 'them', 'were', 'old', '.'],
            self.t.tokenize('Though there were 150, 100 of them were old.')
        )

    def test_digit_comma_multiple(self):
        """Test the word tokenizer on comma at end of digits."""
        self.assertEqual(
            ['There', 'were', '300,000', ',', 'but', 'that', 'was', "n't", 'enough', '.'],
            self.t.tokenize('There were 300,000, but that wasn\'t enough.')
        )

    def test_theyll(self):
        """Test the word tokenizer on the word they'll."""
        self.assertEqual(
            ['They', "'ll", 'save', 'and', 'invest', 'more', '.'],
            self.t.tokenize('They\'ll save and invest more.')
        )

    def test_bracket1(self):
        """Test the word tokenizer on sentence containing brackets."""
        self.assertEqual(
            ['For', 'a', 'few', 'weeks', '(', '>', '24', 'days', ')', '.'],
            self.t.tokenize('For a few weeks (>24 days).')
        )

    def test_bracket_chems(self):
        self.assertEqual(['molecules', 'of', 'the', '[', 'NiL2', ']', 'complex'], self.t.tokenize('molecules of the [NiL2] complex'))
        self.assertEqual(['[', 'Et3NBz', ']', '[', 'FeIIICl4', ']'], self.t.tokenize('[Et3NBz][FeIIICl4]'))
        self.assertEqual(['[', '2PA', '-', 'Mmim', ']', '[', 'Tf2N', ']'], self.t.tokenize('[2PA-Mmim][Tf2N]'))
        self.assertEqual(['[', 'H2O', ']', '≈', '3000', 'ppm'], self.t.tokenize('[H2O] ≈ 3000 ppm'))
        self.assertEqual(['(', '[', 'Cu', '+', ']', '/', '[', 'L', ']', '=', '3', ')'], self.t.tokenize('([Cu+]/[L] = 3)'))
        self.assertEqual(['(', 'Ph3PO', ')', '(', 'Ph3POH', ')', '(', 'HSO4', ')'], self.t.tokenize('(Ph3PO)(Ph3POH)(HSO4)'))
        self.assertEqual(['(', 'iron', '(', 'III', ')'], self.t.tokenize('(iron(III)'))

    def test_chem_formula(self):
        self.assertEqual(['(', 'C2H5', ')', '4N'], self.t.tokenize('(C2H5)4N'))
        self.assertEqual(['(', 'C2H5', ')', '4N'], self.t.tokenize('(C2H5)4N'))
        self.assertEqual(['monomer', '28M', '-', 'Py2'], self.t.tokenize('monomer 28M-Py2'))
        self.assertEqual(['monomer', '28M', '-', 'Py2'], self.t.tokenize('monomer 28M-Py2'))
        self.assertEqual(['ratio', 'Ag', '+', '/', 'nucleoside', 'of', '3', ':', '1'], self.t.tokenize('ratio Ag+/nucleoside of 3:1'))
        self.assertEqual(['[', 'Al', '(', 'H2L', ')', 'n', ']', '3', '-'], self.t.tokenize('[Al(H2L)n]3-'))
        self.assertEqual(['[', 'Fe', '(', 'CN', ')', '5', '(', 'NO', ')', ']', '2', '-'], self.t.tokenize('[Fe(CN)5(NO)]2-'))
        self.assertEqual(['[', 'Fe', '(', 'CN', ')', '5', '(', 'NO', ')', ']', '2', '−'], self.t.tokenize('[Fe(CN)5(NO)]2−'))

    def test_chem_names(self):
        self.assertEqual(['Tetrahydro', 'furan', '(', 'THF', ')'], self.t.tokenize('Tetrahydro furan (THF)'))
        self.assertEqual(['(', 'S', ')', '-', 'alanine'], self.t.tokenize('(S)-alanine'))
        self.assertEqual(['D', '-', 'glucose'], self.t.tokenize('D-glucose'))
        self.assertEqual(['spiro', '[', '4.5', ']', 'decane'], self.t.tokenize('spiro[4.5]decane'))
        self.assertEqual(['β', '-', 'D', '-', 'Glucose'], self.t.tokenize('β-D-Glucose'))
        self.assertEqual(['L', '-', 'alanyl', '-', 'L', '-', 'glutaminyl', '-', 'L', '-', 'arginyl', '-', 'O', '-', 'phosphono', '-', 'L', '-', 'seryl', '-', 'L', '-', 'alanyl', '-', 'L', '-', 'proline'],
                         self.t.tokenize('L-alanyl-L-glutaminyl-L-arginyl-O-phosphono-L-seryl-L-alanyl-L-proline'))
        self.assertEqual(['aluminium', '(', '3', '+', ')'], self.t.tokenize('aluminium(3+)'))
        self.assertEqual(['1', '-', 'methyl', '-', '2', '-', 'methylidene', '-', 'cyclohexane'],
                         self.t.tokenize('1-methyl-2-methylidene-cyclohexane'))


if __name__ == '__main__':
    unittest.main()

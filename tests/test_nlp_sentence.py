#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for sentence tokenization."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import unittest

from chemdataextractor.doc.text import Text
from chemdataextractor.nlp.tokenize import SentenceTokenizer, ChemSentenceTokenizer


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


# class TestSentenceTokenizer(unittest.TestCase):
#
#     @classmethod
#     def setUpClass(cls):
#         cls.ps = SentenceTokenizer()
#
#     def test_punkt_tokenizer(self):
#         """Test the Punkt Sentence Tokenizer directly."""
#         self.assertEqual(
#             ['This is the first sentence.', 'This is another.', 'This is a third.'],
#             self.ps.tokenize('This is the first sentence. This is another. This is a third.')
#         )
#
#     def test_punkt_initials(self):
#         """Test the Punkt Sentence Tokenizer on full stops after initials in names."""
#         self.assertEqual(
#             ['Punkt knows that the periods in Mr. Smith and Johann S. Bach do not mark sentence boundaries.'],
#             self.ps.tokenize('Punkt knows that the periods in Mr. Smith and Johann S. Bach do not mark sentence boundaries.')
#         )
#
#     def test_punkt_lowercase_start(self):
#         """Test the Punkt Sentence Tokenizer on a lowercase sentence start."""
#         self.assertEqual(
#             ['And sometimes sentences can start with non-capitalized words.', 'i is a good variable name.'],
#             self.ps.tokenize('And sometimes sentences can start with non-capitalized words. i is a good variable name.')
#         )
#
#     def test_punkt_realign_boundaries(self):
#         """Test the Punkt Sentence Tokenizer groups brackets and quotes with the correct sentence."""
#         self.assertEqual(
#             ['(How does it deal with this parenthesis?)', '"It should be part of the previous sentence."', 'OK?'],
#             self.ps.tokenize('(How does it deal with this parenthesis?) "It should be part of the previous sentence." OK?')
#         )
#
#     def test_punkt_tokenizer_span(self):
#         """Test the Punkt Sentence Tokenizer span output."""
#         input = 'This is the first sentence. This is another. This is a third.'
#         spans = self.ps.span_tokenize(input)
#         self.assertEqual([(0, 27), (28, 44), (45, 61)], spans)
#         self.assertEqual(input[spans[1][0]:spans[1][1]], 'This is another.')
#
#     def test_text_sentence(self):
#         """Test sentence tokenization through the Text and Sentence API."""
#         t = Text('Hi, my name is Matt. What is your name?')
#         self.assertEqual(
#             [(0, 20, 'Hi, my name is Matt.'), (21, 39, 'What is your name?')],
#             [(s.start, s.end, s.text) for s in t.sentences]
#         )


class TestChemSentenceTokenizer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ps = ChemSentenceTokenizer()

    def test_punkt_tokenizer(self):
        """Test the Punkt Sentence Tokenizer directly."""
        text = 'This is the first sentence. This is another. This is a third.'
        sents = ['This is the first sentence.', 'This is another.', 'This is a third.']
        self.assertEqual(sents, self.ps.tokenize(text))

    def test_et_al(self):
        """Test the tokenizer handles et al. within a sentence correctly."""
        text = 'Costa et al. reported the growth of HA nanowires due to the chemical potential of an amorphous calcium phosphate solution. This structural feature would make the {001} very sensitive to surrounding growth conditions.'
        sents = [
            'Costa et al. reported the growth of HA nanowires due to the chemical potential of an amorphous calcium phosphate solution.',
            'This structural feature would make the {001} very sensitive to surrounding growth conditions.'
        ]
        self.assertEqual(sents, self.ps.tokenize(text))

    def test_et_al2(self):
        """Test the tokenizer handles et al. abbreviation correctly."""
        text = 'In the field of DSCs, Gratzel et al. demonstrated this for the first time in 2004.'
        sents = ['In the field of DSCs, Gratzel et al. demonstrated this for the first time in 2004.']
        self.assertEqual(sents, self.ps.tokenize(text))

    def test_et_al_end(self):
        """Test the tokenizer handles et al. at the end of a sentence correctly."""
        text = 'This is in agreement with previous observations by Peng et al. It is believed that 1D growth does occur.'
        sents = [
            'This is in agreement with previous observations by Peng et al.',
            'It is believed that 1D growth does occur.'
        ]
        self.assertEqual(sents, self.ps.tokenize(text))

    def test_fig_bracket(self):
        """Test the tokenizer handles bracketed Fig. abbreviation correctly."""
        text = 'The model is in good agreement with the intensity of the peaks observed in the XRD patterns (Fig. 1).'
        sents = ['The model is in good agreement with the intensity of the peaks observed in the XRD patterns (Fig. 1).']
        self.assertEqual(sents, self.ps.tokenize(text))

    def test_eg_et_al(self):
        """Test the tokenizer handles e.g. and et al. abbreviations correctly."""
        text = 'There is a clear linkage to some diseases, e.g. multiple myeloma. Vidler et al. studied the druggability of the different members, but to date there are no PCM studies performed on this family.'
        sents = [
            'There is a clear linkage to some diseases, e.g. multiple myeloma.',
            'Vidler et al. studied the druggability of the different members, but to date there are no PCM studies performed on this family.'
        ]
        self.assertEqual(sents, self.ps.tokenize(text))

    def test_colon(self):
        """Test the tokenizer handles colons correctly."""
        text = 'The authors were able to split this into two types, namely: those involved in absorption and those involved in emission.'
        sents = ['The authors were able to split this into two types, namely: those involved in absorption and those involved in emission.']
        self.assertEqual(sents, self.ps.tokenize(text))

    def test_lowercase_sentence_start(self):
        """Test the tokenizer handles lowercase sentence start correctly."""
        text = 'These regions are positive contributors to overall efficiency. van Westen et al. built on this by including data from 24 new sources.'
        sents = [
            'These regions are positive contributors to overall efficiency.',
            'van Westen et al. built on this by including data from 24 new sources.'
        ]
        self.assertEqual(sents, self.ps.tokenize(text))

    def test_chemtext_sentence(self):
        """Test sentence tokenization through the ChemText and Sentence API."""
        t = Text('These regions are positive contributors to overall efficiency. van Westen et al. built on this by including data from 24 new sources.')
        self.assertEqual(
            [(0, 62, 'These regions are positive contributors to overall efficiency.'), (63, 133, 'van Westen et al. built on this by including data from 24 new sources.')],
            [(s.start, s.end, s.text) for s in t.sentences]
        )


if __name__ == '__main__':
    unittest.main()

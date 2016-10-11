# -*- coding: utf-8 -*-
"""
chemdataextractor.doc.text
~~~~~~~~~~~~~~~~~~~~~~~~~~

Text-based document elements.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from abc import abstractproperty
import logging
import re

import six

from ..model import ModelList
from ..parse.context import ContextParser
from ..parse.cem import ChemicalLabelParser, CompoundHeadingParser, CompoundParser, chemical_name
from ..parse.table import CaptionContextParser
from ..parse.ir import IrParser
from ..parse.mp import MpParser
from ..parse.nmr import NmrParser
from ..parse.uvvis import UvvisParser
from ..nlp.lexicon import ChemLexicon
from ..nlp.cem import CemTagger, IGNORE_PREFIX, IGNORE_SUFFIX, SPECIALS, SPLITS
from ..nlp.abbrev import ChemAbbreviationDetector
from ..nlp.tag import NoneTagger
from ..nlp.pos import ChemCrfPosTagger
from ..nlp.tokenize import ChemSentenceTokenizer, ChemWordTokenizer, regex_span_tokenize
from ..utils import memoized_property
from .element import BaseElement


log = logging.getLogger(__name__)


@six.python_2_unicode_compatible
class BaseText(BaseElement):
    """Abstract base class for a text Document Element."""

    def __init__(self, text, word_tokenizer=None, lexicon=None, abbreviation_detector=None, pos_tagger=None, ner_tagger=None, parsers=None, **kwargs):
        """"""
        if not isinstance(text, six.text_type):
            raise TypeError('Text must be a unicode string')
        super(BaseText, self).__init__(**kwargs)
        self._text = text
        self.word_tokenizer = word_tokenizer if word_tokenizer is not None else self.word_tokenizer
        self.lexicon = lexicon if lexicon is not None else self.lexicon
        self.abbreviation_detector = abbreviation_detector if abbreviation_detector is not None else self.abbreviation_detector
        self.pos_tagger = pos_tagger if pos_tagger is not None else self.pos_tagger
        self.ner_tagger = ner_tagger if ner_tagger is not None else self.ner_tagger
        self.parsers = parsers if parsers is not None else self.parsers

    def __repr__(self):
        return '%s(id=%r, references=%r, text=%r)' % (self.__class__.__name__, self.id, self.references, self._text.encode('utf8'))

    def __str__(self):
        return self._text

    @property
    def text(self):
        """The raw text string for this passage of text."""
        return self._text

    @abstractproperty
    def word_tokenizer(self):
        """The word tokenizer to use."""
        return

    @abstractproperty
    def lexicon(self):
        """The lexicon to use."""
        return

    @abstractproperty
    def pos_tagger(self):
        """The part of speech tagger use."""
        return

    @abstractproperty
    def ner_tagger(self):
        """The named entity recognition tagger to use."""
        return

    @abstractproperty
    def parsers(self):
        """The parsers to use."""
        return

    @abstractproperty
    def tokens(self):
        """Return a list of tokens."""
        return

    @abstractproperty
    def tags(self):
        """Return a list of tags."""
        return

    def serialize(self):
        """Convert Text element to python dictionary."""
        data = {'type': self.__class__.__name__, 'content': self.text}
        return data

    def _repr_html_(self):
        return self.text


class Text(BaseText):
    """A passage of text, comprising one or more sentences."""

    sentence_tokenizer = ChemSentenceTokenizer()
    word_tokenizer = ChemWordTokenizer()
    lexicon = ChemLexicon()
    abbreviation_detector = ChemAbbreviationDetector()
    pos_tagger = ChemCrfPosTagger()  # ChemPerceptronTagger()
    ner_tagger = CemTagger()
    parsers = []

    def __init__(self, text, sentence_tokenizer=None, word_tokenizer=None, lexicon=None, abbreviation_detector=None, pos_tagger=None, ner_tagger=None, parsers=None, **kwargs):
        """"""
        super(Text, self).__init__(text, word_tokenizer=word_tokenizer, lexicon=lexicon, abbreviation_detector=abbreviation_detector, pos_tagger=pos_tagger, ner_tagger=ner_tagger, parsers=None, **kwargs)
        self.sentence_tokenizer = sentence_tokenizer if sentence_tokenizer is not None else self.sentence_tokenizer

    @memoized_property
    def sentences(self):
        """Return a list of Sentences that make up this text passage."""
        sents = []
        spans = self.sentence_tokenizer.span_tokenize(self.text)
        for span in spans:
            sent = Sentence(
                text=self.text[span[0]:span[1]],
                start=span[0],
                end=span[1],
                word_tokenizer=self.word_tokenizer,
                lexicon=self.lexicon,
                abbreviation_detector=self.abbreviation_detector,
                pos_tagger=self.pos_tagger,
                ner_tagger=self.ner_tagger,
                parsers=self.parsers,
                document=self.document
            )
            sents.append(sent)
        return sents

    @property
    def raw_sentences(self):
        """Return a list of sentence strings that make up this text passage."""
        return [sentence.text for sentence in self.sentences]

    @property
    def tokens(self):
        """Return a list of tokens for each sentence in this text passage."""
        return [sent.tokens for sent in self.sentences]

    @property
    def raw_tokens(self):
        """Return a list of tokens for each sentence in this text passage."""
        return [sent.raw_tokens for sent in self.sentences]

    @property
    def pos_tagged_tokens(self):
        """Return a list of (token, tag) tuples for each sentence in this text passage."""
        return [sent.pos_tagged_tokens for sent in self.sentences]

    @property
    def pos_tags(self):
        """Return a list of part of speech tags for each sentence in this text passage."""
        return [sent.pos_tags for sent in self.sentences]

    @memoized_property
    def unprocessed_ner_tagged_tokens(self):
        """Return a list of unprocessed named entity recognition tags for the tokens in this sentence.

        No corrections from abbreviation detection are performed.
        """
        return [sent.unprocessed_ner_tagged_tokens for sent in self.sentences]

    @memoized_property
    def unprocessed_ner_tags(self):
        """Return a list of unprocessed named entity tags for the tokens in this sentence.

        No corrections from abbreviation detection are performed.
        """
        return [sent.unprocessed_ner_tags for sent in self.sentences]

    @property
    def ner_tagged_tokens(self):
        """Return a list of (token, tag) tuples for each sentence in this text passage."""
        return [sent.ner_tagged_tokens for sent in self.sentences]

    @property
    def ner_tags(self):
        """Return a list of part of speech tags for each sentence in this text passage."""
        return [sent.ner_tags for sent in self.sentences]

    @property
    def cems(self):
        """Return a list of part of speech tags for each sentence in this text passage."""
        return [cem for sent in self.sentences for cem in sent.cems]

    @property
    def tagged_tokens(self):
        """Return a list of (token, tag) tuples for each sentence in this text passage."""
        return [sent.tagged_tokens for sent in self.sentences]

    @property
    def tags(self):
        """Return a list of tags for each sentence in this text passage."""
        return [sent.tags for sent in self.sentences]

    @property
    def abbreviation_definitions(self):
        """"""
        return [ab for sent in self.sentences for ab in sent.abbreviation_definitions]

    @property
    def records(self):
        """Return a list of records for this text passage."""
        return ModelList(*[r for sent in self.sentences for r in sent.records])

    def __add__(self, other):
        if type(self) == type(other):
            merged = self.__class__(
                text=self.text + other.text,
                id=self.id or other.id,
                references=self.references + other.references,
                sentence_tokenizer=self.sentence_tokenizer,
                word_tokenizer=self.word_tokenizer,
                lexicon=self.lexicon,
                abbreviation_detector=self.abbreviation_detector,
                pos_tagger=self.pos_tagger,
                ner_tagger=self.ner_tagger,
                parsers=self.parsers
            )
            return merged
        return NotImplemented


class Title(Text):
    parsers = [CompoundParser()]

    def _repr_html_(self):
        return '<h1 class="cde-title">' + self.text + '</h1>'


class Heading(Text):
    parsers = [CompoundHeadingParser(), ChemicalLabelParser()]

    def _repr_html_(self):
        return '<h2 class="cde-title">' + self.text + '</h2>'


class Paragraph(Text):

    parsers = [CompoundParser(), ChemicalLabelParser(), NmrParser(), IrParser(), UvvisParser(), MpParser(), ContextParser()]

    def _repr_html_(self):
        return '<p class="cde-paragraph">' + self.text + '</p>'


class Footnote(Text):

    parsers = [ContextParser(), CaptionContextParser()]

    def _repr_html_(self):
        return '<p class="cde-footnote">' + self.text + '</p>'


class Citation(Text):
    # No tagging in citations
    ner_tagger = NoneTagger()
    abbreviation_detector = False
    # TODO: Citation parser
    # TODO: Store number/label

    def _repr_html_(self):
        return '<p class="cde-citation">' + self.text + '</p>'


class Caption(Text):
    parsers = [CompoundParser(), ChemicalLabelParser(), CaptionContextParser()]

    def _repr_html_(self):
        return '<caption class="cde-caption">' + self.text + '</caption>'


class Sentence(BaseText):
    """A single sentence within a text passage."""

    word_tokenizer = ChemWordTokenizer()
    lexicon = ChemLexicon()
    abbreviation_detector = ChemAbbreviationDetector()
    pos_tagger = ChemCrfPosTagger()  # ChemPerceptronTagger()
    ner_tagger = CemTagger()
    parsers = []

    def __init__(self, text, start=0, end=None, word_tokenizer=None, lexicon=None, abbreviation_detector=None, pos_tagger=None, ner_tagger=None, parsers=None, **kwargs):
        super(Sentence, self).__init__(text, word_tokenizer=word_tokenizer, lexicon=lexicon, abbreviation_detector=abbreviation_detector, pos_tagger=pos_tagger, ner_tagger=ner_tagger, parsers=parsers, **kwargs)
        #: The start index of this sentence within the text passage.
        self.start = start
        #: The end index of this sentence within the text passage.
        self.end = end if end is not None else len(text)

    def __repr__(self):
        return '%s(%r, %r, %r)' % (self.__class__.__name__, self._text.encode('utf8'), self.start, self.end)

    @memoized_property
    def tokens(self):
        """Return a list of token Spans for this sentence."""
        spans = self.word_tokenizer.span_tokenize(self.text)
        toks = [Token(
            text=self.text[span[0]:span[1]],
            start=span[0] + self.start,
            end=span[1] + self.start,
            lexicon=self.lexicon
        ) for span in spans]
        return toks

    @property
    def raw_tokens(self):
        """Return a list of token strings that make up this sentence."""
        return [token.text for token in self.tokens]

    @memoized_property
    def pos_tagged_tokens(self):
        """Return a list of part of speech tags for the tokens in this sentence."""
        # log.debug('Getting pos tags')
        return self.pos_tagger.tag(self.raw_tokens)

    @property
    def pos_tags(self):
        """Return a list of part of speech tags for the tokens in this sentence."""
        return [tag for token, tag in self.pos_tagged_tokens]

    @memoized_property
    def unprocessed_ner_tagged_tokens(self):
        """Return a list of unprocessed named entity recognition tags for the tokens in this sentence.

        No corrections from abbreviation detection are performed.
        """
        # log.debug('Getting unprocessed_ner_tags')
        return self.ner_tagger.tag(self.pos_tagged_tokens)

    @memoized_property
    def unprocessed_ner_tags(self):
        """Return a list of unprocessed named entity tags for the tokens in this sentence.

        No corrections from abbreviation detection are performed.
        """
        return [tag for token, tag in self.unprocessed_ner_tagged_tokens]

    @memoized_property
    def abbreviation_definitions(self):
        """Return a list of (abbreviation, long, ner_tag) tuples."""
        abbreviations = []
        if self.abbreviation_detector:
            # log.debug('Detecting abbreviations')
            ners = self.unprocessed_ner_tags
            for abbr_span, long_span in self.abbreviation_detector.detect_spans(self.raw_tokens):
                abbr = self.raw_tokens[abbr_span[0]:abbr_span[1]]
                long = self.raw_tokens[long_span[0]:long_span[1]]
                # Check if long is entirely tagged as one named entity type
                long_tags = ners[long_span[0]:long_span[1]]
                unique_tags = set([tag[2:] for tag in long_tags if tag is not None])
                tag = long_tags[0][2:] if None not in long_tags and len(unique_tags) == 1 else None
                abbreviations.append((abbr, long, tag))
        return abbreviations

    @memoized_property
    def ner_tagged_tokens(self):
        """"""
        return list(zip(self.raw_tokens, self.ner_tags))

    @memoized_property
    def ner_tags(self):
        """"""
        # log.debug('Getting ner_tags')
        ner_tags = self.unprocessed_ner_tags
        abbrev_defs = self.document.abbreviation_definitions if self.document else self.abbreviation_definitions
        # Ensure abbreviation entity matches long entity
        # TODO: This is potentially a performance bottleneck?
        for i in range(0, len(ner_tags)):
            for abbr, long, ner_tag in abbrev_defs:
                if abbr == self.raw_tokens[i:i+len(abbr)]:
                    old_ner_tags = ner_tags[i:i+len(abbr)]
                    ner_tags[i] = 'B-%s' % ner_tag if ner_tag is not None else None
                    ner_tags[i+1:i+len(abbr)] = ['I-%s' % ner_tag if ner_tag is not None else None] * (len(abbr) - 1)
                    # Remove ner tags from brackets surrounding abbreviation
                    if i > 1 and self.raw_tokens[i-1] == '(':
                        ner_tags[i-1] = None
                    if i < len(self.raw_tokens) - 1 and self.raw_tokens[i+1] == ')':
                        ner_tags[i+1] = None
                    if not old_ner_tags == ner_tags[i:i+len(abbr)]:
                        log.debug('Correcting abbreviation tag: %s (%s): %s -> %s' % (' '.join(abbr), ' '.join(long), old_ner_tags, ner_tags[i:i+len(abbr)]))
        # TODO: Ensure abbreviations in brackets at the end of an entity match are separated and the brackets untagged
        # Hydrogen Peroxide (H2O2)
        # Tungsten Carbide (WC)
        # TODO: Filter off alphanumerics from end (1h) (3) (I)
        # May need more intelligent
        return ner_tags

    @memoized_property
    def cems(self):
        # log.debug('Getting cems')
        spans = []
        # print(self.text.encode('utf8'))
        for result in chemical_name.scan(self.tagged_tokens):
            # parser scan yields (result, startindex, endindex) - we just use the indexes here
            tokens = self.tokens[result[1]:result[2]]
            start = tokens[0].start
            end = tokens[-1].end
            # Adjust boundaries to exclude disallowed prefixes/suffixes
            currenttext = self.text[start-self.start:end-self.start].lower()
            for prefix in IGNORE_PREFIX:
                if currenttext.startswith(prefix):
                    # print('%s removing %s' % (currenttext, prefix))
                    start += len(prefix)
                    break
            for suffix in IGNORE_SUFFIX:
                if currenttext.endswith(suffix):
                    # print('%s removing %s' % (currenttext, suffix))
                    end -= len(suffix)
                    break
            # Adjust boundaries to exclude matching brackets at start and end
            currenttext = self.text[start-self.start:end-self.start]
            for bpair in [('(', ')'), ('[', ']')]:
                if len(currenttext) > 2 and currenttext[0] == bpair[0] and currenttext[-1] == bpair[1]:
                    level = 1
                    for k, char in enumerate(currenttext[1:]):
                        if char == bpair[0]:
                            level += 1
                        elif char == bpair[1]:
                            level -= 1
                        if level == 0 and k == len(currenttext) - 2:
                            start += 1
                            end -= 1
                            break

            currenttext = self.text[start-self.start:end-self.start]

            # Do splits
            split_spans = []
            comps = list(regex_span_tokenize(currenttext, '(-|\+|\)?-to-\(?|···|/|\s)'))
            if len(comps) > 1:
                for split in SPLITS:
                    if all(re.search(split, currenttext[comp[0]:comp[1]]) for comp in comps):
                        # print('%s splitting %s' % (currenttext, [currenttext[comp[0]:comp[1]] for comp in comps]))
                        for comp in comps:
                            span = Span(text=currenttext[comp[0]:comp[1]], start=start+comp[0], end=start+comp[1])
                            # print('SPLIT: %s - %s' % (currenttext, repr(span)))
                            split_spans.append(span)
                        break
                else:
                    split_spans.append(Span(text=currenttext, start=start, end=end))
            else:
                split_spans.append(Span(text=currenttext, start=start, end=end))

            # Do specials
            for split_span in split_spans:
                for special in SPECIALS:
                    m = re.search(special, split_span.text)
                    if m:
                        # print('%s special %s' % (split_span.text, m.groups()))
                        for i in range(1, len(m.groups()) + 1):
                            span = Span(text=m.group(i), start=split_span.start+m.start(i), end=split_span.start+m.end(i))
                            # print('SUBMATCH: %s - %s' % (currenttext, repr(span)))
                            spans.append(span)
                        break
                else:
                    spans.append(split_span)
        return spans

    @memoized_property
    def tags(self):
        """Return combined POS and NER tags."""
        tags = self.pos_tags
        for i, tag in enumerate(self.ner_tags):
            if tag is not None:
                tags[i] = tag
        return tags

    @property
    def tagged_tokens(self):
        return list(zip(self.raw_tokens, self.tags))

    @property
    def records(self):
        """Return a list of records for this sentence."""
        compounds = ModelList()
        seen_labels = set()
        for parser in self.parsers:
            for record in parser.parse(self.tagged_tokens):
                p = record.serialize()
                if not p:  # TODO: Potential performance issues?
                    continue
                # Skip duplicate records
                if record in compounds:
                    continue
                # Skip just labels that have already been seen (bit of a hack)
                if all(k in {'labels', 'roles'} for k in p.keys()) and set(record.labels).issubset(seen_labels):
                    continue
                seen_labels.update(record.labels)
                compounds.append(record)
        return compounds

    def __add__(self, other):
        if type(self) == type(other):
            merged = self.__class__(
                text=self.text + other.text,
                start=self.start,
                end=None,
                id=self.id or other.id,
                references=self.references + other.references,
                word_tokenizer=self.word_tokenizer,
                lexicon=self.lexicon,
                abbreviation_detector=self.abbreviation_detector,
                pos_tagger=self.pos_tagger,
                ner_tagger=self.ner_tagger,
                parsers=self.parsers
            )
            return merged
        return NotImplemented


@six.python_2_unicode_compatible
class Span(object):
    """A text span within a sentence."""

    def __init__(self, text, start, end):
        self.text = text
        """The text content of this span."""
        self.start = start
        """The start offset of this token in the original text."""
        self.end = end
        """The end offset of this token in the original text."""

    def __repr__(self):
        return '%s(%r, %r, %r)' % (self.__class__.__name__, self.text.encode('utf8'), self.start, self.end)

    def __str__(self):
        return self.text

    @property
    def length(self):
        """The offset length of this span in the original text."""
        return self.end - self.start


class Token(Span):
    """A single token within a sentence. Corresponds to a word, character, punctuation etc."""

    def __init__(self, text, start, end, lexicon):
        """"""
        super(Token, self).__init__(text, start, end)
        #: The lexicon for this token.
        self.lexicon = lexicon
        self.lexicon.add(text)

    @property
    def lex(self):
        """The corresponding Lexeme entry in the Lexicon for this token."""
        return self.lexicon[self.text]

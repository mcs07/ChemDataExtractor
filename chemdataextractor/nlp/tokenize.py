# -*- coding: utf-8 -*-
"""
chemdataextractor.nlp.tokenize
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Word and sentence tokenizers.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from abc import ABCMeta, abstractmethod
import logging
import re

import six

from ..text import bracket_level, GREEK
from ..data import load_model


log = logging.getLogger(__name__)


class BaseTokenizer(six.with_metaclass(ABCMeta)):
    """Abstract base class from which all Tokenizer classes inherit.

    Subclasses must implement a ``span_tokenize(text)`` method that returns a list of integer offset tuples that
    identify tokens in the text.

    """

    def tokenize(self, s):
        """Return a list of token strings from the given sentence.

        :param string s: The sentence string to tokenize.
        :rtype: iter(str)
        """
        return [s[start:end] for start, end in self.span_tokenize(s)]

    @abstractmethod
    def span_tokenize(self, s):
        """Return a list of integer offsets that identify tokens in the given sentence.

        :param string s: The sentence string to tokenize.
        :rtype: iter(tuple(int, int))
        """
        return

    def tokenize_sents(self, strings):
        """Apply the ``tokenize`` method to each sentence in ``strings``.

        :param list(str) sentences: A list of sentence strings to tokenize.
        :rtype: iter(iter(str))
        """
        return [self.tokenize(s) for s in strings]

    def span_tokenize_sents(self, strings):
        """Apply the ``span_tokenize`` method to each sentence in ``strings``.

        :param list(str) sentences: A list of sentence strings to tokenize.
        :rtype: iter(iter(tuple(int, int)))
        """
        for s in strings:
            yield list(self.span_tokenize(s))


def regex_span_tokenize(s, regex):
    """Return spans that identify tokens in s split using regex."""
    left = 0
    for m in re.finditer(regex, s, re.U):
        right, next = m.span()
        if right != 0:
            yield left, right
        left = next
    yield left, len(s)


class SentenceTokenizer(BaseTokenizer):
    """Sentence tokenizer that uses the Punkt algorithm by Kiss & Strunk (2006)."""

    model = 'models/punkt_english.pickle'  # This is available from NLTK

    def __init__(self, model=None):
        self.model = model if model is not None else self.model
        self._tokenizer = None
        log.debug('%s: Initializing with %s' % (self.__class__.__name__, self.model))

    def span_tokenize(self, s):
        """Return a list of integer offsets that identify sentences in the given text.

        :param string s: The text to tokenize into sentences.
        :rtype: iter(tuple(int, int))
        """
        if self._tokenizer is None:
            self._tokenizer = load_model(self.model)
        # for debug in tokenizer.debug_decisions(s):
        #     log.debug(format_debug_decision(debug))
        return self._tokenizer.span_tokenize(s)


class ChemSentenceTokenizer(SentenceTokenizer):
    """Sentence tokenizer that uses the Punkt algorithm by Kiss & Strunk (2006), trained on chemistry text."""
    model = 'models/punkt_chem-1.0.pickle'


class WordTokenizer(BaseTokenizer):
    """Standard word tokenizer for generic English text."""
    #: Split before and after these sequences, wherever they occur, unless entire token is one of these sequences
    SPLIT = [
        '----',
        '––––',  # \u2013 en dash
        '————',  # \u2014 em dash
        '<--->',
        '---',
        '–––',  # \u2013 en dash
        '———',  # \u2014 em dash
        '<-->',
        '-->',
        '...',
        '--',
        '––',  # \u2013 en dash
        '——',  # \u2014 em dash
        '``',
        "''",
        '->',
        '<',
        '>',
        '–',  # \u2013 en dash
        '—',  # \u2014 em dash
        '―',  # \u2015 horizontal bar
        '~',  # \u007e Tilde
        '⁓',  # \u2053 Swung dash
        '∼',  # \u223c Tilde operator
        '°',  # \u00b0 Degrees
        ';',
        '@',
        '#',
        '$',
        '£',  # \u00a3
        '€',  # \u20ac
        '%',
        '&',
        '?',
        '!',
        '™',  # \u2122
        '®',  # \u00ae
        '…',  # \u2026
        '⋯',  # \u22ef Mid-line ellipsis
        '†',  # \u2020 Dagger
        '‡',  # \u2021 Double dagger
        '§',  # \u00a7 Section sign
        '¶'   # \u00b6 Pilcrow sign
        '≠',  # \u2260
        '≡',  # \u2261
        '≢',  # \u2262
        '≣',  # \u2263
        '≤',  # \u2264
        '≥',  # \u2265
        '≦',  # \u2266
        '≧',  # \u2267
        '≨',  # \u2268
        '≩',  # \u2269
        '≪',  # \u226a
        '≫',  # \u226b
        '≈',  # \u2248
        '=',
        '÷',  # \u00f7
        '×',  # \u00d7
        '→',  # \u2192
        '⇄',  # \u21c4
        '"',  # \u0022 Quote mark
        '“',  # \u201c
        '”',  # \u201d
        '„',  # \u201e
        '‟',  # \u201f
        '‘',  # \u2018 Left single quote
        # '’',  # \u2019 Right single quote  - Regularly used as an apostrophe, so don't always split
        '‚',  # \u201a Single low quote
        '‛',  # \u201b Single reversed quote
        '`',  # \u0060
        '´',  # \u00b4
        # Primes
        '′',  # \u2032
        '″',  # \u2033
        '‴',  # \u2034
        '‵',  # \u2035
        '‶',  # \u2036
        '‷',  # \u2037
        '⁗',  # \u2057
        # Brackets
        '(',
        '[',
        '{',
        '}',
        ']',
        ')',
        # Slashes
        '/',  # \u002f Solidus
        '⁄',  # \u2044 Fraction slash
        '∕',  # \u2215 Division slash
        # Hyphens and Minuses
        # '-',  # \u002d Hyphen-minus
        '−',  # \u2212 Minus
        '‒',  # \u2012 figure dash
        # '‐',  # \u2010 Hyphen
        # '‐',  # \u2010 Hyphen
        # '‑',  # \u2011 Non-breaking hyphen
        '+',  # \u002b Plus
        '±',  # \u00b1 Plus/Minus
    ]
    #: Split around these sequences unless they are followed by a digit
    SPLIT_NO_DIGIT = [':', ',']
    #: Split after these sequences if they start a word
    SPLIT_START_WORD = ["''", "``", "'"]
    #: Split before these sequences if they end a word
    SPLIT_END_WORD = ["'s", "'m", "'d", "'ll", "'re", "'ve", "n't", "''", "'", "’s", "’m", "’d", "’ll", "’re", "’ve", "n’t", "’", "’’"]
    #: Don't split full stop off last token if it is one of these sequences
    NO_SPLIT_STOP = ['...', 'al.', 'Co.', 'Ltd.', 'Pvt.', 'A.D.', 'B.C.', 'B.V.', 'S.D.', 'U.K.', 'U.S.', 'r.t.']
    #: Split these contractions at the specified index
    CONTRACTIONS = [("cannot", 3), ("d'ye", 1), ("d’ye", 1), ("gimme", 3), ("gonna", 3), ("gotta", 3), ("lemme", 3),
                    ("mor'n", 3), ("mor’n", 3), ("wanna", 3), ("'tis", 2), ("'twas", 2)]
    #: Don't split these sequences.
    NO_SPLIT = {
        'mm-hm', 'mm-mm', 'o-kay', 'uh-huh', 'uh-oh', 'wanna-be'
    }
    #: Don't split around hyphens with these prefixes
    NO_SPLIT_PREFIX = {
        'e', 'a', 'u', 'x', 'agro', 'ante', 'anti', 'arch', 'be', 'bi', 'bio', 'co', 'counter', 'cross', 'cyber',
        'de', 'eco', 'ex', 'extra', 'inter', 'intra', 'macro', 'mega', 'micro', 'mid', 'mini', 'multi', 'neo', 'non',
        'over', 'pan', 'para', 'peri', 'post', 'pre', 'pro', 'pseudo', 'quasi', 're', 'semi', 'sub', 'super', 'tri',
        'ultra', 'un', 'uni', 'vice'
    }
    #: Don't split around hyphens with these suffixes.
    NO_SPLIT_SUFFIX = {
        'esque', 'ette', 'fest', 'fold', 'gate', 'itis', 'less', 'most', '-o-torium', 'rama', 'wise'
    }
    #: Don't split around hyphens if only these characters before or after.
    NO_SPLIT_CHARS = '0123456789,\'"“”„‟‘’‚‛`´′″‴‵‶‷⁗'

    def __init__(self, split_last_stop=True):
        #: Whether to split off the final full stop (unless preceded by NO_SPLIT_STOP). Default True.
        self.split_last_stop = split_last_stop

    def _split_span(self, span, index, length=0):
        """Split a span into two or three separate spans at certain indices."""
        offset = span[1] + index if index < 0 else span[0] + index
        # log.debug([(span[0], offset), (offset, offset + length), (offset + length, span[1])])
        return [(span[0], offset), (offset, offset + length), (offset + length, span[1])]

    def _subspan(self, s, span, nextspan):
        """Recursively subdivide spans based on a series of rules."""
        text = s[span[0]:span[1]]
        lowertext = text.lower()

        # Skip if only a single character or a split sequence
        if span[1] - span[0] < 2 or text in self.SPLIT or text in self.SPLIT_END_WORD or text in self.SPLIT_START_WORD or lowertext in self.NO_SPLIT:
            return [span]

        # Skip if it looks like URL
        if text.startswith('http://') or text.startswith('ftp://') or text.startswith('www.'):
            return [span]

        # Split full stop at end of final token (allow certain characters to follow) unless ellipsis
        if self.split_last_stop and nextspan is None and text not in self.NO_SPLIT_STOP and not text[-3:] == '...':
            if text[-1] == '.':
                return self._split_span(span, -1)
            ind = text.rfind('.')
            if ind > -1 and all(t in '\'‘’"“”)]}' for t in text[ind + 1:]):
                return self._split_span(span, ind, 1)

        # Split off certain sequences at the end of a word
        for spl in self.SPLIT_END_WORD:
            if text.endswith(spl) and len(text) > len(spl) and text[-len(spl) - 1].isalpha():
                return self._split_span(span, -len(spl), 0)

        # Split off certain sequences at the start of a word
        for spl in self.SPLIT_START_WORD:
            if text.startswith(spl) and len(text) > len(spl) and text[-len(spl) - 1].isalpha():
                return self._split_span(span, len(spl), 0)

        # Split around certain sequences
        for spl in self.SPLIT:
            ind = text.find(spl)
            if ind > -1:
                return self._split_span(span, ind, len(spl))

        # Split around certain sequences unless followed by a digit
        for spl in self.SPLIT_NO_DIGIT:
            ind = text.rfind(spl)
            if ind > -1 and (len(text) <= ind + len(spl) or not text[ind + len(spl)].isdigit()):
                return self._split_span(span, ind, len(spl))

        # Characters to split around, but with exceptions
        for i, char in enumerate(text):
            if char == '-':
                before = lowertext[:i]
                after = lowertext[i+1:]
                # By default we split on hyphens
                split = True
                if before in self.NO_SPLIT_PREFIX or after in self.NO_SPLIT_SUFFIX:
                    split = False  # Don't split if prefix or suffix in list
                elif not before.strip(self.NO_SPLIT_CHARS) or not after.strip(self.NO_SPLIT_CHARS):
                    split = False  # Don't split if prefix or suffix entirely consist of certain characters
                if split:
                    return self._split_span(span, i, 1)

        # Split contraction words
        for contraction in self.CONTRACTIONS:
            if lowertext == contraction[0]:
                return self._split_span(span, contraction[1])
        return [span]

    def span_tokenize(self, s):
        """"""
        # First get spans by splitting on all whitespace
        # Includes: \u0020 \u00A0 \u1680 \u180E \u2000 \u2001 \u2002 \u2003 \u2004 \u2005 \u2006 \u2007 \u2008 \u2009 \u200A \u202F \u205F \u3000
        spans = [(left, right) for left, right in regex_span_tokenize(s, '\s+') if not left == right]
        i = 0
        # Recursively split spans according to rules
        while i < len(spans):
            subspans = self._subspan(s, spans[i], spans[i + 1] if i + 1 < len(spans) else None)
            spans[i:i+1] = [subspan for subspan in subspans if subspan[1] - subspan[0] > 0]
            if len(subspans) == 1:
                i += 1
        return spans


class ChemWordTokenizer(WordTokenizer):
    """Word Tokenizer for chemistry text."""

    #: Split before and after these sequences, wherever they occur, unless entire token is one of these sequences
    SPLIT = [
        '----',
        '––––',  # \u2013 en dash
        '————',  # \u2014 em dash
        '<--->',
        '---',
        '–––',  # \u2013 en dash
        '———',  # \u2014 em dash
        '<-->',
        '-->',
        '...',
        '--',
        '––',  # \u2013 en dash
        '——',  # \u2014 em dash
        # '``',
        # "''",
        # '->',  # Don't split around this if occurs within chemical name
        '<',
        # '>',   # Don't split around this if occurs within chemical name
        ').',  # Fix missing whitespace errors
        '.(',  # Fix missing whitespace errors
        '–',  # \u2013 en dash
        '—',  # \u2014 em dash
        '―',  # \u2015 horizontal bar
        '~',  # \u007e Tilde
        '⁓',  # \u2053 Swung dash
        '∼',  # \u223c Tilde operator
        '°',  # \u00b0 Degrees
        # ';',
        '@',
        '#',
        '$',
        '£',  # \u00a3
        '€',  # \u20ac
        '%',
        '&',
        '?',
        '!',
        '™',  # \u2122
        '®',  # \u00ae
        '…',  # \u2026
        '⋯',  # \u22ef Mid-line ellipsis
        '†',  # \u2020 Dagger
        '‡',  # \u2021 Double dagger
        '§',  # \u00a7 Section sign
        '¶'   # \u00b6 Pilcrow sign
        '≠',  # \u2260
        '≡',  # \u2261
        '≢',  # \u2262
        '≣',  # \u2263
        '≤',  # \u2264
        '≥',  # \u2265
        '≦',  # \u2266
        '≧',  # \u2267
        '≨',  # \u2268
        '≩',  # \u2269
        '≪',  # \u226a
        '≫',  # \u226b
        '≈',  # \u2248
        '=',
        '÷',  # \u00f7
        '×',  # \u00d7
        # '→',  # \u2192 # Don't split around this if occurs within chemical name
        '⇄',  # \u21c4
        '"',  # \u0022 Quote mark
        '“',  # \u201c
        '”',  # \u201d
        '„',  # \u201e
        '‟',  # \u201f
        '‘',  # \u2018 Left single quote
        # '’',  # \u2019 Right single quote - Regularly used as an apostrophe, so don't always split
        '‚',  # \u201a Single low quote
        '‛',  # \u201b Single reversed quote
        '`',  # \u0060
        '´',  # \u00b4
        # Primes
        # '′',  # \u2032
        # '″',  # \u2033
        # '‴',  # \u2034
        # '‵',  # \u2035
        # '‶',  # \u2036
        # '‷',  # \u2037
        # '⁗',  # \u2057
        # Brackets
        # '(',
        # '[',
        # '{',
        # '}',
        # ']',
        # ')',
        # Slashes
        # '/',  # \u002f Solidus
        # '⁄',  # \u2044 Fraction slash
        # '∕',  # \u2215 Division slash
        # Hyphens and Minuses
        # '-',  # \u002d Hyphen-minus
        # '−',  # \u2212 Minus
        # '‒',  # \u2012 figure dash
        # '‐',  # \u2010 Hyphen
        # '‑',  # \u2011 Non-breaking hyphen
        # '+',  # \u002b Plus
        # '±',  # \u00b1 Plus/Minus
    ]
    #: Split before these sequences if they end a token
    SPLIT_END = [':', ',', '(TM)', '(R)', '(®)', '(™)', '(■)', '(◼)', '(●)', '(▲)', '(○)', '(◆)', '(▼)', '(⧫)', '(△)', '(◇)', '(▽)', '(⬚)', '(×)', '(□)', '(•)', '’']
    #: Split before these sequences if they end a token, unless preceded by a digit
    SPLIT_END_NO_DIGIT = ['(aq)', '(aq.)', '(s)', '(l)', '(g)']
    #: Don't split around slash when both preceded and followed by these characters
    NO_SPLIT_SLASH = ['+', '-', '−']
    #: Regular expression that matches a numeric quantity with units
    QUANTITY_RE = re.compile(r'^((\d\d\d)g|([-−]?\d+\.\d+|10[-−]\d+)(g|s|m|N|V)([-−]?[1-4])?|(\d*[-−]?\d+\.?\d*)([pnµμm]A|[µμmk]g|[kM]J|m[lL]|[nµμm]?M|[nµμmc]m|kN|[mk]V|[mkMG]?W|[mnpμµ]s|Hz|[Mm][Oo][Ll](e|ar)?s?|k?Pa|ppm|min)([-−]?[1-4])?)$')
    #: Don't split on hyphen if the prefix matches this regular expression
    NO_SPLIT_PREFIX_ENDING = re.compile('(^\(.*\)|^[\d,\'"“”„‟‘’‚‛`´′″‴‵‶‷⁗Α-Ωα-ω]+|ano|ato|azo|boc|bromo|cbz|chloro|eno|fluoro|fmoc|ido|ino|io|iodo|mercapto|nitro|ono|oso|oxalo|oxo|oxy|phospho|telluro|tms|yl|ylen|ylene|yliden|ylidene|ylidyn|ylidyne)$', re.U)
    #: Don't split on hyphen if prefix or suffix match this regular expression
    NO_SPLIT_CHEM = re.compile('([\-α-ω]|\d+,\d+|\d+[A-Z]|^d\d\d?$|acetic|acetyl|acid|acyl|anol|azo|benz|bromo|carb|cbz|chlor|cyclo|ethan|ethyl|fluoro|fmoc|gluc|hydro|idyl|indol|iene|ione|iodo|mercapto|n,n|nitro|noic|o,o|oxalo|oxo|oxy|oyl|onyl|phen|phth|phospho|pyrid|telluro|tetra|tms|ylen|yli|zole|alpha|beta|gamma|delta|epsilon|theta|kappa|lambda|sigma|omega)', re.U | re.I)
    #: Don't split on hyphen if the prefix is one of these sequences
    NO_SPLIT_PREFIX = {
        'e', 'a', 'u', 'x', 'agro', 'ante', 'anti', 'arch', 'be', 'bi', 'bio', 'co', 'counter', 'cross', 'cyber',
        'de', 'eco', 'ex', 'extra', 'inter', 'intra', 'macro', 'mega', 'micro', 'mid', 'mini', 'multi', 'neo', 'non',
        'over', 'pan', 'para', 'peri', 'post', 'pre', 'pro', 'pseudo', 'quasi', 're', 'semi', 'sub', 'super', 'tri',
        'ultra', 'un', 'uni', 'vice',

        'aci', 'adeno', 'aldehydo', 'allo', 'alpha', 'altro', 'ambi', 'aorto', 'arachno', 'as', 'beta', 'bis', 'catena',
        'centi', 'chi', 'chiro', 'circum', 'cis', 'closo', 'colo', 'conjuncto', 'conta', 'contra', 'cortico', 'cosa',
        'counter', 'cran', 'crypto', 'cyclo', 'deca', 'deci', 'delta', 'demi', 'di', 'dis', 'dl', 'eco', 'electro',
        'endo', 'ennea', 'ent', 'epi', 'epsilon', 'erythro', 'eta', 'exo', 'ferro', 'galacto', 'gamma', 'gastro',
        'giga', 'gluco', 'glycero', 'graft', 'gulo', 'hemi', 'hepta', 'hexa', 'homo', 'hydro', 'hypho', 'hypo', 'ideo',
        'idio', 'in', 'infra', 'iota', 'iso', 'judeo', 'kappa', 'keto', 'kis', 'lambda', 'lyxo', 'manno', 'medi',
        'meso', 'meta', 'milli', 'mono', 'mu', 'muco', 'musculo', 'myo', 'nano', 'neuro', 'nido', 'nitro', 'nona',
        'nor', 'novem', 'novi', 'nu', 'octa', 'octi', 'octo', 'omega', 'omicron', 'ortho', 'paleo', 'pelvi', 'penta',
        'pheno', 'phi', 'pi', 'pica', 'pneumo', 'poly', 'preter', 'psi', 'quadri', 'quater', 'quinque', 'recto', 'rho',
        'ribo', 'salpingo', 'scyllo', 'sec', 'sept', 'septi', 'sero', 'sesqui', 'sexi', 'sigma', 'sn', 'soci', 'supra',
        'sur', 'sym', 'syn', 'talo', 'tau', 'tele', 'ter', 'tera', 'tert', 'tetra', 'theta', 'threo', 'trans',
        'triangulo', 'tris', 'uber', 'unsym', 'upsilon', 'veno', 'ventriculo', 'xi', 'xylo', 'zeta',
    }
    #: Split on hyphens followed by one of these sequences
    SPLIT_SUFFIX = {
        'absorption', 'abstinent', 'abstraction', 'abuse', 'accelerated', 'accepting', 'acclimated', 'acclimation',
        'acid', 'activated', 'activation', 'active', 'activity', 'addition', 'adducted', 'adducts', 'adequate',
        'adjusted', 'administrated', 'adsorption', 'affected', 'aged', 'alcohol', 'alcoholic', 'algae', 'alginate',
        'alkaline', 'alkylated', 'alkylation', 'alkyne', 'analogous', 'anesthetized', 'appended', 'armed', 'aromatic',
        'assay', 'assemblages', 'assisted', 'associated', 'atom', 'atoms', 'attenuated', 'attributed', 'backbone',
        'base', 'based', 'bearing', 'benzylation', 'binding', 'biomolecule', 'biotic', 'blocking', 'blood', 'bond',
        'bonded', 'bonding', 'bonds', 'boosted', 'bottle', 'bottled', 'bound', 'bridge', 'bridged', 'buffer',
        'buffered', 'caged', 'cane', 'capped', 'capturing', 'carrier', 'carrying', 'catalysed', 'catalyzed', 'cation',
        'caused', 'centered', 'challenged', 'chelating', 'cleaving', 'coated', 'coating', 'coenzyme', 'competing',
        'competitive', 'complex', 'complexes', 'compound', 'compounds', 'concentration', 'conditioned', 'conditions',
        'conducting', 'configuration', 'confirmed', 'conjugate', 'conjugated', 'conjugates', 'connectivity',
        'consuming', 'contained', 'containing', 'contaminated', 'control', 'converting', 'coordinate', 'coordinated',
        'copolymer', 'copolymers', 'core', 'cored', 'cotransport', 'coupled', 'covered', 'crosslinked', 'cyclized',
        'damaged', 'dealkylation', 'decocted', 'decorated', 'deethylation', 'deficiency', 'deficient', 'defined',
        'degrading', 'demethylated', 'demethylation', 'dendrimer', 'density', 'dependant', 'dependence', 'dependent',
        'deplete', 'depleted', 'depleting', 'depletion', 'depolarization', 'depolarized', 'deprived', 'derivatised',
        'derivative', 'derivatives', 'derivatized', 'derived', 'desorption', 'detected', 'devalued', 'dextran',
        'dextrans', 'diabetic', 'dimensional', 'dimer', 'distribution', 'divalent', 'domain', 'dominated',
        'donating', 'donor', 'dopant', 'doped', 'doping', 'dosed', 'dot', 'drinking', 'driven', 'drug', 'drugs', 'dye',
        'edge', 'efficiency', 'electrodeposited', 'electrolyte', 'elevating', 'elicited', 'embedded', 'emersion',
        'emitting', 'encapsulated', 'encapsulating', 'enclosed', 'enhanced', 'enhancing', 'enriched', 'enrichment',
        'enzyme', 'epidermal', 'equivalents', 'etched', 'ethanolamine', 'evoked', 'exchange', 'excimer', 'excluder',
        'expanded', 'experimental', 'exposed', 'exposure', 'expressing', 'extract', 'extraction', 'fed', 'finger', 'fixed', 'fixing',
        'flanking', 'flavonoid', 'fluorescence', 'formation', 'forming', 'fortified', 'free', 'function',
        'functionalised', 'functionalized', 'functionalyzed', 'fused', 'gas', 'gated', 'generating', 'glucuronidating',
        'glycoprotein', 'glycosylated', 'glycosylation', 'gradient', 'grafted', 'group', 'groups', 'halogen',
        'heterocyclic', 'homologues', 'hydrogel', 'hydrolyzing', 'hydroxylated', 'hydroxylation', 'hydroxysteroid',
        'immersion', 'immobilized', 'immunoproteins', 'impregnated', 'imprinted', 'inactivated', 'increased',
        'increasing', 'incubated', 'independent', 'induce', 'induced', 'inducible', 'inducing', 'induction', 'influx',
        'inhibited', 'inhibitor', 'inhibitory', 'initiated', 'injected', 'insensitive', 'insulin', 'integrated',
        'interlinked', 'intermediate', 'intolerant', 'intoxicated', 'ion', 'ions', 'island', 'isomer', 'isomers',
        'knot', 'label', 'labeled', 'labeling', 'labelled', 'laden', 'lamp', 'laser', 'layer', 'layers', 'lesioned',
        'ligand', 'ligated', 'like', 'limitation', 'limited', 'limiting', 'lined', 'linked', 'linker', 'lipid',
        'lipids', 'lipoprotein', 'liposomal', 'liposomes', 'liquid', 'liver', 'loaded', 'loading', 'locked', 'loss',
        'lowering', 'lubricants', 'luminance', 'luminescence', 'maintained', 'majority', 'making', 'mannosylated',
        'material', 'mediated', 'metabolizing', 'metal', 'metallized', 'methylation', 'migrated', 'mimetic',
        'mimicking', 'mixed', 'mixture', 'mode', 'model', 'modified', 'modifying', 'modulated', 'moiety', 'molecule',
        'monoadducts', 'monomer', 'mutated', 'nanogel', 'nanoparticle', 'nanotube', 'need', 'negative', 'nitrosated',
        'nitrosation', 'nitrosylation', 'nmr', 'noncompetitive', 'normalized', 'nuclear', 'nucleoside', 'nucleosides',
        'nucleotide', 'nucleotides', 'nutrition', 'olefin', 'olefins', 'oligomers', 'omitted', 'only',
        'outcome', 'overload', 'oxidation', 'oxidized', 'oxo-mediated', 'oxygenation', 'page', 'paired', 'pathway',
        'patterned', 'peptide', 'permeabilized', 'permeable', 'phase', 'phospholipids', 'phosphopeptide',
        'phosphorylated', 'pillared', 'placebo', 'planted', 'plasma', 'polymer', 'polymers', 'poor', 'porous',
        'position', 'positive', 'postlabeling', 'precipitated', 'preferring', 'pretreated', 'primed', 'produced',
        'producing', 'production', 'promoted', 'promoting', 'protected', 'protein', 'proteomic', 'protonated',
        'provoked', 'purified', 'radical', 'reacting', 'reaction', 'reactive', 'reagents', 'rearranged', 'receptor',
        'receptors', 'recognition', 'redistribution', 'redox', 'reduced', 'reducing', 'reduction', 'refractory',
        'refreshed', 'regenerating', 'regulated', 'regulating', 'regulatory', 'related', 'release', 'releasing',
        'replete', 'requiring', 'resistance', 'resistant', 'resitant', 'response', 'responsive', 'responsiveness',
        'restricted', 'resulted', 'retinal', 'reversible', 'ribosylated', 'ribosylating', 'ribosylation', 'rich',
        'right', 'ring', 'saturated', 'scanning', 'scavengers', 'scavenging', 'sealed', 'secreting', 'secretion',
        'seeking', 'selective', 'selectivity', 'semiconductor', 'sensing', 'sensitive', 'sensitized', 'soluble',
        'solution', 'solvent', 'sparing', 'specific', 'spiked', 'stabilised', 'stabilized', 'stabilizing', 'stable',
        'stained', 'steroidal', 'stimulated', 'stimulating', 'storage', 'stressed', 'stripped', 'substituent',
        'substituted', 'substitution', 'substrate', 'sufficient', 'sugar', 'sugars', 'supplemented', 'supported',
        'suppressed', 'surface', 'susceptible', 'sweetened', 'synthesizing', 'tagged', 'target', 'telopeptide',
        'terminal', 'terminally', 'terminated', 'termini', 'terminus', 'ternary', 'terpolymer', 'tertiary', 'tested',
        'testes', 'tethered', 'tetrabrominated', 'tolerance', 'tolerant', 'toxicity', 'toxin', 'tracer', 'transfected',
        'transfer', 'transition', 'transport', 'transporter', 'treated', 'treating', 'treatment', 'triggered',
        'turn', 'type', 'unesterified', 'untreated', 'vacancies', 'vacancy', 'variable', 'water', 'yeast', 'yield',
        'zwitterion'
    }

    def _closing_bracket_index(self, text, bpair=('(', ')')):
        """Return the index of the closing bracket that matches the opening bracket at the start of the text."""
        level = 1
        for i, char in enumerate(text[1:]):
            if char == bpair[0]:
                level += 1
            elif char == bpair[1]:
                level -= 1
            if level == 0:
                return i + 1

    def _opening_bracket_index(self, text, bpair=('(', ')')):
        """Return the index of the opening bracket that matches the closing bracket at the end of the text."""
        level = 1
        for i, char in enumerate(reversed(text[:-1])):
            if char == bpair[1]:
                level += 1
            elif char == bpair[0]:
                level -= 1
            if level == 0:
                return len(text) - i - 2

    def _is_number(self, text):
        """Return True if the text is a number."""
        try:
            float(text)
            return True
        except ValueError:
            return False

    def _is_saccharide_arrow(self, before, after):
        """Return True if the arrow is in a chemical name."""
        if (before and after and before[-1].isdigit() and after[0].isdigit() and
            before.rstrip('0123456789').endswith('(') and after.lstrip('0123456789').startswith(')-')):
            return True
        else:
            return False

    def _subspan(self, s, span, nextspan):
        """Recursively subdivide spans based on a series of rules."""
        text = s[span[0]:span[1]]
        lowertext = text.lower()

        # Skip if only a single character or a split sequence
        if span[1] - span[0] < 2 or text in self.SPLIT or text in self.SPLIT_END_WORD or text in self.SPLIT_START_WORD or lowertext in self.NO_SPLIT:
            return [span]

        # Skip if it looks like URL
        if text.startswith('http://') or text.startswith('ftp://') or text.startswith('www.'):
            return [span]

        # Split full stop at end of final token (allow certain characters to follow) unless ellipsis
        if self.split_last_stop and nextspan is None and text not in self.NO_SPLIT_STOP and not text[-3:] == '...':
            if text[-1] == '.':
                return self._split_span(span, -1)
            ind = text.rfind('.')
            if ind > -1 and all(t in '\'‘’"“”)]}' for t in text[ind + 1:]):
                return self._split_span(span, ind, 1)

        # Split off certain sequences at the end of a token
        for spl in self.SPLIT_END:
            if text.endswith(spl) and len(text) > len(spl):
                return self._split_span(span, -len(spl), 0)

        # Split off certain sequences at the end of a word
        for spl in self.SPLIT_END_WORD:
            if text.endswith(spl) and len(text) > len(spl) and text[-len(spl) - 1].isalpha():
                return self._split_span(span, -len(spl), 0)

        # Split off certain sequences at the end of a word
        for spl in self.SPLIT_START_WORD:
            if text.startswith(spl) and len(text) > len(spl) and text[-len(spl) - 1].isalpha():
                return self._split_span(span, len(spl), 0)

        # Split around certain sequences
        for spl in self.SPLIT:
            ind = text.find(spl)
            if ind > -1:
                return self._split_span(span, ind, len(spl))

        # Split around certain sequences unless followed by a digit
        # - We skip this because of difficulty with chemical names.
        # for spl in self.SPLIT_NO_DIGIT:
        #     ind = text.rfind(spl)
        #     if ind > -1 and (len(text) <= ind + len(spl) or not text[ind + len(spl)].isdigit()):
        #         return self._split_span(span, ind, len(spl))

        # Split off certain sequences at the end of a token unless preceded by a digit
        for spl in self.SPLIT_END_NO_DIGIT:
            if text.endswith(spl) and len(text) > len(spl) and not text[-len(spl) - 1].isdigit():
                return self._split_span(span, -len(spl), 0)

        # Regular Bracket at both start and end, break off both provided they correspond
        if text.startswith('(') and text.endswith(')') and self._closing_bracket_index(text) == len(text) - 1:
            return self._split_span(span, 1, len(text)-2)

        # Split things like IR(KBr)
        if text.startswith('IR(') and text.endswith(')'):
            return self._split_span(span, 2, 1)

        # Split things like \d+\.\d+([a-z]+) e.g. UV-vis/IR peaks with bracketed strength/shape
        m = re.match('^(\d+\.\d+|\d{3,})(\([a-z]+\))$', text, re.I)
        if m:
            return self._split_span(span, m.start(2), 1)

        # Split brackets off start and end if the corresponding bracket isn't within token
        for bpair in [('(', ')'), ('{', '}'), ('[', ']')]:
            #level = bracket_level(text, open=[bpair[0]], close=[bpair[1]])
            # Bracket at start, bracketlevel > 0, break it off
            if text.startswith(bpair[0]) and self._closing_bracket_index(text, bpair=bpair) is None:
                return self._split_span(span, 1, 0)
            # Bracket at end, bracketlevel < 0, break it off
            if text.endswith(bpair[1]) and self._opening_bracket_index(text, bpair=bpair) is None:
                return self._split_span(span, -1, 0)

        # TODO: Consider splitting around comma in limited circumstances. Mainly to fix whitespace errors.

        # Characters to split around, but with exceptions
        for i, char in enumerate(text):
            before = text[:i]
            after = text[i+1:]
            if char in {':', ';'}:
                # Split around colon unless it looks like we're in a chemical name
                if not (before and after and after[0].isdigit() and before.rstrip('′\'')[-1].isdigit() and '-' in after) and not (self.NO_SPLIT_CHEM.search(before) and self.NO_SPLIT_CHEM.search(after)):
                    return self._split_span(span, i, 1)
            elif char in {'x', '+', '−'}:
                # Split around x, +, − (\u2212 minus) between two numbers or at start followed by numbers
                if (i == 0 or self._is_number(before)) and self._is_number(after):
                    return self._split_span(span, i, 1)
                # Also plit around − (\u2212 minus) between two letters
                if char == '−' and before and before[-1].isalpha() and after and after[0].isalpha():
                    return self._split_span(span, i, 1)
            elif char == '±':
                # Split around ± unless surrounded by brackets
                if not (before and after and before[-1] == '(' and after[0] == ')'):
                    return self._split_span(span, i, 1)
            elif char == '/':
                # Split around / unless '+/-' or '-/-' etc.
                if not (before and after and before[-1] in self.NO_SPLIT_SLASH and after[0] in self.NO_SPLIT_SLASH):
                    return self._split_span(span, i, 1)
            elif char == '>':
                if not (before and before[-1] == '-'):
                    # Split if preceding is not -
                    return self._split_span(span, i, 1)
                if before and before[-1] == '-':
                    # If preceding is -, split around -> unless in chemical name
                    if not text == '->' and not self._is_saccharide_arrow(before[:-1], after):
                        return self._split_span(span, i-1, 2)
            elif char is '→' and not self._is_saccharide_arrow(before, after):
                # TODO: 'is' should be '=='... this never splits!?
                # Split around → unless in chemical name
                return self._split_span(span, i, 1)
            elif char == '(' and self._is_number(before) and not '(' in after and not ')' in after:
                # Split around open bracket after a number
                return self._split_span(span, i, 1)
            elif char == '-':
                lowerbefore = lowertext[:i]
                lowerafter = lowertext[i+1:]
                # Always split on -of-the- -to- -in- -by- -of- -or- -and- -per- -the-
                if lowerafter[:7] == 'of-the-':
                    return [(span[0], span[0] + i), (span[0] + i, span[0] + i + 1), (span[0] + i + 1, span[0] + i + 3), (span[0] + i + 3, span[0] + i + 4), (span[0] + i + 4, span[0] + i + 7), (span[0] + i + 7, span[0] + i + 8), (span[0] + i + 8, span[1])]
                if lowerafter[:5] in {'on-a-', 'of-a-'}:
                    return [(span[0], span[0] + i), (span[0] + i, span[0] + i + 1), (span[0] + i + 1, span[0] + i + 3), (span[0] + i + 3, span[0] + i + 4), (span[0] + i + 4, span[0] + i + 5), (span[0] + i + 5, span[0] + i + 6), (span[0] + i + 6, span[1])]
                if lowerafter[:3] in {'to-', 'in-', 'by-', 'of-', 'or-', 'on-'}:
                    return [(span[0], span[0] + i), (span[0] + i, span[0] + i + 1), (span[0] + i + 1, span[0] + i + 3), (span[0] + i + 3, span[0] + i + 4), (span[0] + i + 4, span[1])]
                if lowerafter[:4] in {'and-', 'per-', 'the-'}:
                    return [(span[0], span[0] + i), (span[0] + i, span[0] + i + 1), (span[0] + i + 1, span[0] + i + 4), (span[0] + i + 4, span[0] + i + 5), (span[0] + i + 5, span[1])]

                # By default we split on hyphens
                split = True
                if lowerafter == 'nmr':
                    split = True  # Always split NMR off end
                elif bracket_level(text) == 0 and (not bracket_level(after) == 0 or not bracket_level(before) == 0):
                    split = False  # Don't split if within brackets
                elif after and after[0] == '>':
                    split = False  # Don't split if followed by >
                elif lowerbefore in self.NO_SPLIT_PREFIX or lowerafter in self.NO_SPLIT_SUFFIX:
                    split = False  # Don't split if prefix or suffix in list
                elif self.NO_SPLIT_PREFIX_ENDING.search(lowerbefore):
                    split = False  # Don't split if prefix ends with pattern
                elif lowerafter in self.SPLIT_SUFFIX:
                    split = True  # Do split if suffix in list
                elif len(before) <= 1 or len(after) <= 2:
                    split = False  # Don't split if not at least 2 char before and 3 after
                elif self.NO_SPLIT_CHEM.search(lowerbefore) or self.NO_SPLIT_CHEM.search(lowerafter):
                    split = False  # Don't split if prefix or suffix match chem regex
                if split:
                    return self._split_span(span, i, 1)

                # TODO: Errors:
                # [³H]-choline
                # S,S'-...
                # 1,4-di-substituted
                # 11-β - hydroxysteroid
                # Spelt out greek: 11beta - hydroxysteroid
                # ...-N-substituted like 2,5-dimethyl-N-substituted pyrroles
                # 4-(2-Butyl-6,7-dichloro-2-cyclopentyl-indan-1-on-5-yl) oxobutyric acid
                # Adenosine - monophosphate
                # Consistency for amino acids: Arg-Arg and Arg-Arg-Asp... probably always split
                # D,L-α-peptide?
                # N'-formylkynurenine
                # poly(D,L-lactic acid )?
                # poly(methyl metha-acrylate )?
                # Poly(N - alkyl Acrylamide )
                # poly(N - isopropyl acrylamide )
                # R,S - lorazepam
                # S,S - dioxide

        # Split units off the end of a numeric value
        quantity = self.QUANTITY_RE.search(text)
        if quantity:
            return self._split_span(span, len(quantity.group(6) or quantity.group(3) or quantity.group(2)), 0)

        # Split pH off the start of a numeric value
        if text.startswith('pH') and self._is_number(text[2:]):
            return self._split_span(span, 2, 0)

        # Split contraction words
        for contraction in self.CONTRACTIONS:
            if lowertext == contraction[0]:
                return self._split_span(span, contraction[1])

        if nextspan:
            nexttext = s[nextspan[0]:nextspan[1]]
            # Split NMR isotope whitespace errors (joined with previous sentence full stop)
            if nexttext == 'NMR':
                ind = text.rfind('.')
                if ind > -1 and text[ind + 1:] in {'1H', '13C', '15N', '31P', '19F', '11B', '29Si', '170', '73Ge', '195Pt', '33S', '13C{1H}'}:
                    return self._split_span(span, ind, 1)


        return [span]


class FineWordTokenizer(WordTokenizer):
    """Word Tokenizer that also split around hyphens and all colons."""
    #: Split before and after these sequences, wherever they occur, unless entire token is one of these sequences
    SPLIT = [
        '----',
        '––––',  # \u2013 en dash
        '————',  # \u2014 em dash
        '<--->',
        '---',
        '–––',  # \u2013 en dash
        '———',  # \u2014 em dash
        '<-->',
        '-->',
        '...',
        '--',
        '––',  # \u2013 en dash
        '——',  # \u2014 em dash
        '``',
        "''",
        '->',
        '<',
        '>',
        '–',  # \u2013 en dash
        '—',  # \u2014 em dash
        '―',  # \u2015 horizontal bar
        '~',  # \u007e Tilde
        '⁓',  # \u2053 Swung dash
        '∼',  # \u223c Tilde operator
        '°',  # \u00b0 Degrees
        ';',
        '@',
        '#',
        '$',
        '£',  # \u00a3
        '€',  # \u20ac
        '%',
        '&',
        '?',
        '!',
        '™',  # \u2122
        '®',  # \u00ae
        '…',  # \u2026
        '⋯',  # \u22ef Mid-line ellipsis
        '†',  # \u2020 Dagger
        '‡',  # \u2021 Double dagger
        '§',  # \u00a7 Section sign
        '¶'   # \u00b6 Pilcrow sign
        '≠',  # \u2260
        '≡',  # \u2261
        '≢',  # \u2262
        '≣',  # \u2263
        '≤',  # \u2264
        '≥',  # \u2265
        '≦',  # \u2266
        '≧',  # \u2267
        '≨',  # \u2268
        '≩',  # \u2269
        '≪',  # \u226a
        '≫',  # \u226b
        '≈',  # \u2248
        '=',
        '÷',  # \u00f7
        '×',  # \u00d7
        '→',  # \u2192
        '⇄',  # \u21c4
        '"',  # \u0022 Quote mark
        '“',  # \u201c
        '”',  # \u201d
        '„',  # \u201e
        '‟',  # \u201f
        '‘',  # \u2018 Left single quote
        '’',  # \u2019 Right single quote
        '‚',  # \u201a Single low quote
        '‛',  # \u201b Single reversed quote
        '`',  # \u0060
        '´',  # \u00b4
        # Primes
        '′',  # \u2032
        '″',  # \u2033
        '‴',  # \u2034
        '‵',  # \u2035
        '‶',  # \u2036
        '‷',  # \u2037
        '⁗',  # \u2057
        # Brackets
        '(',
        '[',
        '{',
        '}',
        ']',
        ')',
        # Slashes
        '/',  # \u002f Solidus
        '⁄',  # \u2044 Fraction slash
        '∕',  # \u2215 Division slash
        # Hyphens and Minuses
        '-',  # \u002d Hyphen-minus
        '−',  # \u2212 Minus
        '‒',  # \u2012 figure dash
        '‐',  # \u2010 Hyphen
        '‑',  # \u2011 Non-breaking hyphen
        '+',  # \u002b Plus
        '±',  # \u00b1 Plus/Minus
        ':',
    ]
    #: Split before these sequences if they end a token
    SPLIT_NO_DIGIT = [',']
    NO_SPLIT = {}
    #: Don't split around hyphens with these prefixes
    NO_SPLIT_PREFIX = {}
    #: Don't split around hyphens with these suffixes.
    NO_SPLIT_SUFFIX = {}

    def _subspan(self, s, span, nextspan):
        """Recursively subdivide spans based on a series of rules."""

        # Split on boundaries between greek and non-greek
        text = s[span[0]:span[1]]
        for i, char in enumerate(text):
            if i < len(text) - 1:
                nextchar = text[i + 1]
                if (char in GREEK and nextchar not in GREEK) or (char not in GREEK and nextchar in GREEK):
                    return [(span[0], span[0] + i + 1), (span[0] + i + 1, span[1])]

        # Perform all normal WordTokenizer splits
        return super(FineWordTokenizer, self)._subspan(s,span, nextspan)

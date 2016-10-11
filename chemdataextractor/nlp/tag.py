#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
chemdataextractor.nlp.tag
~~~~~~~~~~~~~~~~~~~~~~~~~

Tagger implementations. Used for part-of-speech tagging and named entity recognition.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from abc import ABCMeta, abstractmethod
from collections import defaultdict
import io
import logging
import pickle
import random
import re

import dawg
import pycrfsuite
import six

from ..data import load_model, find_data
from .lexicon import Lexicon


log = logging.getLogger(__name__)


class BaseTagger(six.with_metaclass(ABCMeta)):
    """Abstract tagger class from which all taggers inherit.

    Subclasses must implement a ``tag()`` method.
    """

    @abstractmethod
    def tag(self, tokens):
        """Return a list of (token, tag) tuples for the given list of token strings.

        :param list(str) tokens: The list of tokens to tag.
        :rtype: list(tuple(str, str))
        """
        return

    def tag_sents(self, sentences):
        """Apply the ``tag`` method to each sentence in ``sentences``."""
        return [self.tag(s) for s in sentences]

    def evaluate(self, gold):
        """Evaluate the accuracy of this tagger using a gold standard corpus.

        :param list(list(tuple(str, str))) gold: The list of tagged sentences to score the tagger on.
        :returns: Tagger accuracy value.
        :rtype: float
        """
        tagged_sents = self.tag_sents([w for (w, t) in sent] for sent in gold)
        gold_tokens = sum(gold, [])
        test_tokens = sum(tagged_sents, [])
        accuracy = float(sum(x == y for x, y in six.moves.zip(gold_tokens, test_tokens))) / len(test_tokens)
        return accuracy


class NoneTagger(BaseTagger):
    """Tag every token with None."""

    def tag(self, tokens):
        """"""
        return [(token, None) for token in tokens]


class RegexTagger(BaseTagger):
    """Regular Expression Tagger."""

    # TODO: I think NLTK RegexTagger has recently been improved to be more like this, so maybe we can just remove this?
    # We aren't actually using this anywhere because the regex ability in parsers is more flexible...
    # But may be useful for users that want an easy way to override some other tagger?

    #: Regular expression patterns in (regex, tag) tuples.
    patterns = [
        (r'^-?[0-9]+(.[0-9]+)?$', 'CD'),   # cardinal numbers
        (r'(The|the|A|a|An|an)$', 'AT'),   # articles
        (r'.*able$', 'JJ'),                # adjectives
        (r'.*ness$', 'NN'),                # nouns formed from adjectives
        (r'.*ly$', 'RB'),                  # adverbs
        (r'.*s$', 'NNS'),                  # plural nouns
        (r'.*ing$', 'VBG'),                # gerunds
        (r'.*ed$', 'VBD'),                 # past tense verbs
        (r'.*', 'NN')                      # nouns (default)
    ]

    #: The lexicon to use
    lexicon = Lexicon()

    def __init__(self, patterns=None, lexicon=None):
        """

        :param list(tuple(string, string)) patterns: List of (regex, tag) pairs.
        """
        self.patterns = patterns if patterns is not None else self.patterns
        self.regexes = [(re.compile(pattern, re.I | re.U), tag) for pattern, tag in self.patterns]
        self.lexicon = lexicon if lexicon is not None else self.lexicon
        log.debug('%s: Initializing with %s patterns' % (self.__class__.__name__, len(self.patterns)))

    def tag(self, tokens):
        """Return a list of (token, tag) tuples for a given list of tokens."""
        tags = []
        for token in tokens:
            normalized = self.lexicon[token].normalized
            for regex, tag in self.regexes:
                if regex.match(normalized):
                    tags.append((token, tag))
                    break
            else:
                tags.append((token, None))
        return tags


class AveragedPerceptron(object):
    """Averaged Perceptron implementation.

    Based on implementation by Matthew Honnibal, released under the MIT license.

    See more:
        http://spacy.io/blog/part-of-speech-POS-tagger-in-python/
        https://github.com/sloria/textblob-aptagger
    """

    def __init__(self):
        # Each feature gets its own weight vector, so weights is a dict-of-dicts
        self.weights = {}
        self.classes = set()
        # The accumulated values, for the averaging. Keyed by feature/class tuples
        self._totals = defaultdict(int)
        # The last time the feature was changed, for the averaging. Keyed by feature/class tuples
        self._tstamps = defaultdict(int)
        # Number of instances seen
        self.i = 0

    def predict(self, features):
        """Dot-product the features and current weights and return the best label."""
        scores = defaultdict(float)
        for feat in features:
            if feat not in self.weights:
                continue
            weights = self.weights[feat]
            for label, weight in weights.items():
                scores[label] += weight
        # Do a secondary alphabetic sort, for stability
        return max(self.classes, key=lambda label: (scores[label], label))

    def update(self, truth, guess, features):
        """Update the feature weights."""
        def upd_feat(c, f, w, v):
            param = (f, c)
            self._totals[param] += (self.i - self._tstamps[param]) * w
            self._tstamps[param] = self.i
            self.weights[f][c] = w + v

        self.i += 1
        if truth == guess:
            return None
        for f in features:
            weights = self.weights.setdefault(f, {})
            upd_feat(truth, f, weights.get(truth, 0.0), 1.0)
            upd_feat(guess, f, weights.get(guess, 0.0), -1.0)
        return None

    def average_weights(self):
        """Average weights from all iterations."""
        for feat, weights in self.weights.items():
            new_feat_weights = {}
            for clas, weight in weights.items():
                param = (feat, clas)
                total = self._totals[param]
                total += (self.i - self._tstamps[param]) * weight
                averaged = round(total / float(self.i), 3)
                if averaged:
                    new_feat_weights[clas] = averaged
            self.weights[feat] = new_feat_weights
        return None

    def save(self, path):
        """Save the pickled model weights."""
        with io.open(path, 'wb') as fout:
            return pickle.dump(dict(self.weights), fout)

    def load(self, path):
        """Load the pickled model weights."""
        with io.open(path, 'rb') as fin:
            self.weights = pickle.load(fin)


class ApTagger(six.with_metaclass(ABCMeta, BaseTagger)):
    """Greedy Averaged Perceptron tagger, based on implementation by Matthew Honnibal, released under the MIT license.

     See more:
         http://spacy.io/blog/part-of-speech-POS-tagger-in-python/
         https://github.com/sloria/textblob-aptagger

     """

    START = ['-START-', '-START2-']
    lexicon = Lexicon()
    clusters = False

    def __init__(self, model=None, lexicon=None, clusters=None):
        """"""
        self.perceptron = AveragedPerceptron()
        self.tagdict = {}
        self.classes = set()
        self.model = model if model is not None else self.model
        self.lexicon = lexicon if lexicon is not None else self.lexicon
        self.clusters = clusters if clusters is not None else self.clusters
        log.debug('%s: Initializing with %s' % (self.__class__.__name__, self.model))

    def tag(self, tokens):
        """Return a list of (token, tag) tuples for a given list of tokens."""
        # Lazy load model first time we tag
        if not self.classes:
            self.load(self.model)
        prev, prev2 = self.START
        tags = []
        for i, token in enumerate(tokens):
            tag = self.tagdict.get(token)
            if not tag:
                features = self._get_features(i, tokens, prev, prev2)
                tag = self.perceptron.predict(features)
            tags.append((token, tag))
            prev2 = prev
            prev = tag
        return tags

    def train(self, sentences, nr_iter=5):
        """Train a model from sentences.

        :param sentences: A list of sentences, each of which is a list of (token, tag) tuples.
        :param nr_iter: Number of training iterations.
        """
        self._make_tagdict(sentences)
        self.perceptron.classes = self.classes
        for iter_ in range(nr_iter):
            c = 0
            n = 0
            for sentence in sentences:
                prev, prev2 = self.START
                context = [t[0] for t in sentence]
                for i, (token, tag) in enumerate(sentence):
                    guess = self.tagdict.get(token)
                    if not guess:
                        feats = self._get_features(i, context, prev, prev2)
                        guess = self.perceptron.predict(feats)
                        self.perceptron.update(tag, guess, feats)
                    prev2 = prev
                    prev = guess
                    c += guess == tag
                    n += 1
            random.shuffle(sentences)
            log.debug('Iter %s: %s/%s=%s' % (iter_, c, n, (float(c) / n) * 100))
        self.perceptron.average_weights()

    def save(self, f):
        """Save pickled model to file."""
        return pickle.dump((self.perceptron.weights, self.tagdict, self.classes, self.clusters), f, protocol=pickle.HIGHEST_PROTOCOL)

    def load(self, model):
        """Load pickled model."""
        self.perceptron.weights, self.tagdict, self.classes, self.clusters = load_model(model)
        self.perceptron.classes = self.classes

    @abstractmethod
    def _get_features(self, i, context, prev, prev2):
        """Map tokens into a feature representation."""
        pass

    def _make_tagdict(self, sentences):
        """Make a tag dictionary for single-tag words."""
        counts = defaultdict(lambda: defaultdict(int))
        for sent in sentences:
            for word, tag in sent:
                counts[word][tag] += 1
                self.classes.add(tag)
        freq_thresh = 20
        ambiguity_thresh = 0.97
        for word, tag_freqs in counts.items():
            tag, mode = max(tag_freqs.items(), key=lambda item: item[1])
            n = sum(tag_freqs.values())
            # Don't add rare words to the tag dictionary, only add quite unambiguous words
            if n >= freq_thresh and (float(mode) / n) >= ambiguity_thresh:
                self.tagdict[word] = tag


class CrfTagger(BaseTagger):
    """Tagger that uses Conditional Random Fields (CRF)."""
    lexicon = Lexicon()
    clusters = False

    #: Parameters to pass to training algorithm. See http://www.chokkan.org/software/crfsuite/manual.html
    params = {
        # These parameters are valid for the default LBFGS training algorithm. Change if using another.
        'c1': 1.0,  # Coefficient for L1 regularization (OWL-QN). Default 0.
        'c2': 0.001,  # Coefficient for L2 regularization. Default 1.
        'max_iterations': 50,  # The maximum number of iterations for L-BFGS optimization. Default INT_MAX.
        'feature.possible_transitions': False,  # Force to generate all possible transition features. Default False.
        'feature.possible_states': False,  # Force to generate all possible state features. Default False.
        # 'feature.minfreq' : 2, # The minimum frequency of features. Default 0.
        # 'epsilon' :  # Epsilon for testing the convergence of the objective. Default 0.00001.
    }

    def __init__(self, model=None, lexicon=None, clusters=None, params=None):
        """"""
        self.model = model if model is not None else self.model
        self.lexicon = lexicon if lexicon is not None else self.lexicon
        self.clusters = clusters if clusters is not None else self.clusters
        self.params = params if params is not None else self.params
        self._tagger = pycrfsuite.Tagger()
        self._loaded_model = False

    def load(self, model):
        log.debug('Loading %s' % model)
        self._tagger.open(find_data(model))
        self._loaded_model = True

    def tag(self, tokens):
        """Return a list of ((token, tag), label) tuples for a given list of (token, tag) tuples."""
        # Lazy load model first time we tag
        if not self._loaded_model:
            self.load(self.model)
        features = [self._get_features(tokens, i) for i in range(len(tokens))]
        labels = self._tagger.tag(features)
        tagged_sent = list(zip(tokens, labels))
        return tagged_sent

    def train(self, sentences, model):
        """Train the CRF tagger using CRFSuite.

        :params sentences: Annotated sentences.
        :params model: Path to save pickled model.
        """
        trainer = pycrfsuite.Trainer(verbose=True)
        trainer.set_params(self.params)
        for sentence in sentences:
            tokens, labels = zip(*sentence)
            features = [self._get_features(tokens, i) for i in range(len(tokens))]
            trainer.append(features, labels)
        trainer.train(model)
        self.load(model)


class DictionaryTagger(BaseTagger):
    """Dictionary Tagger. Tag tokens based on inclusion in a DAWG."""

    #: The lexicon to use.
    lexicon = Lexicon()
    #: DAWG model file path.
    model = None
    #: Entity tag. Matches will be tagged like 'B-CM' and 'I-CM' according to IOB scheme. TODO: Optional no B/I?
    entity = 'CM'
    #: Delimiters that define where matches are allowed to start or end.
    delimiters = re.compile(r'(^.|\b|\s|\W|.$)')
    #: Whether dictionary matches are case sensitive.
    case_sensitive = False

    def __init__(self, words=None, model=None, entity=None, case_sensitive=None, lexicon=None):
        """

        :param list(list(string)) words: list of words, each of which is a list of tokens.
        """
        self._dawg = dawg.CompletionDAWG()
        self.model = model if model is not None else self.model
        self.entity = entity if entity is not None else self.entity
        self.case_sensitive = case_sensitive if case_sensitive is not None else self.case_sensitive
        self.lexicon = lexicon if lexicon is not None else self.lexicon
        self._loaded_model = False
        if words is not None:
            self.build(words)

    def load(self, model):
        """Load pickled DAWG from disk."""
        self._dawg.load(find_data(model))
        self._loaded_model = True

    def save(self, path):
        """Save pickled DAWG to disk."""
        self._dawg.save(path)

    def build(self, words):
        """Construct dictionary DAWG from tokenized words."""
        words = [self._normalize(tokens) for tokens in words]
        self._dawg = dawg.CompletionDAWG(words)
        self._loaded_model = True

    def _normalize(self, tokens):
        """Normalization transform to apply to both dictionary words and input tokens."""
        if self.case_sensitive:
            return ' '.join(self.lexicon[t].normalized for t in tokens)
        else:
            return ' '.join(self.lexicon[t].lower for t in tokens)

    def tag(self, tokens):
        """Return a list of (token, tag) tuples for a given list of tokens."""
        if not self._loaded_model:
            self.load(self.model)
        tags = [None] * len(tokens)
        norm = self._normalize(tokens)
        length = len(norm)
        # A set of allowed indexes for matches to start or end at
        delims = [0] + [i for span in [m.span() for m in self.delimiters.finditer(norm)] for i in span] + [length]
        # Token indices
        token_at_index = []
        for i, t in enumerate(tokens):
            token_at_index.extend([i] * (len(self.lexicon[t].normalized) + 1))
        start_i = 0
        end_i = 1
        matches = {}
        next_start = end_i
        # TODO: This could be a little more efficient by skipping indexes forward to next delim points.
        while True:
            current = norm[start_i:end_i]
            if self._dawg.has_keys_with_prefix(current):
                # print('%s:%s:%s' % (start_i, end_i, current))
                # If the current span is in the dawg, and isn't followed by an alphanumeric character
                if current in self._dawg and start_i in delims and end_i in delims:
                    # print(current)
                    # Subsequent longer matches with same start_i will overwrite values in matches dict
                    matches[start_i] = (start_i, end_i, current)
                    # We can skip forward to after this match next time we increment start_i
                    next_start = end_i
                # Increment end_i provided we aren't already at the end of the input
                if end_i < length:
                    end_i += 1
                    continue
            # Increment start_i provided we aren't already at the end of the input
            start_i = next_start
            if start_i >= length - 1:
                break
            end_i = start_i + 1
            next_start = end_i
        # Apply matches as tags to the relevant tokens
        for start_i, end_i, current in matches.values():
            start_token = token_at_index[start_i]
            end_token = token_at_index[end_i]
            # Possible for match to start in 'I' token from prev match. Merge matches by not overwriting to 'B'.
            if not tags[start_token] == 'I-%s' % self.entity:
                tags[start_token] = 'B-%s' % self.entity
            tags[start_token+1:end_token+1] = ['I-%s' % self.entity] * (end_token - start_token)
        tokentags = list(zip(tokens, tags))
        return tokentags

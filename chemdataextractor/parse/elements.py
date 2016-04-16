# -*- coding: utf-8 -*-
"""
chemdataextractor.parse.elements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Parser elements.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import collections
import copy
import logging
import re

from lxml.builder import E
import six
import types


class ParseException(Exception):
    """Exception thrown by a ParserElement when it doesn't match input."""

    def __init__(self, tokens, i=0, msg=None, element=None):
        self.i = i
        self.msg = msg
        self.tokens = tokens
        self.element = element

    @classmethod
    def wrap(cls, parse_exception):
        return cls(parse_exception.tokens, parse_exception.loc, parse_exception.msg, parse_exception.element)

    def __str__(self):
        return ('%s (at token %d)' % (self.msg, self.i)).encode('utf8')



log = logging.getLogger(__name__)


XML_SAFE_TAGS = {
    '-LRB-': 'LRB',
    '-RRB-': 'RRB',
    '.': 'STOP',
    ',': 'COMMA',
    ':': 'COLON',
    '$': 'DOLLAR',
    '``': 'LQUOTE',
    '\'\'': 'RQUOTE',
    'PRP$': 'PRPPOS',
    'WP$': 'WPPOS',
    None: 'NONE'
}


def safe_name(name):
    """Make name safe for use in XML output."""
    return XML_SAFE_TAGS.get(name, name)


class BaseParserElement(object):
    """Abstract base parser element class."""

    def __init__(self):
        self.name = None
        self.actions = []
        self.streamlined = False

    def set_action(self, *fns):
        self.actions = fns
        return self

    def add_action(self, *fns):
        self.actions += fns
        return self

    def copy(self):
        new = copy.copy(self)
        new.actions = self.actions[:]
        return new

    def set_name(self, name):
        new = self.copy()
        new.name = name
        return new

    def scan(self, tokens, max_matches=six.MAXSIZE, overlap=False):
        """"""
        if not self.streamlined:
            self.streamline()
        matches = 0
        i = 0
        length = len(tokens)
        while i < length and matches < max_matches:
            try:
                results, next_i = self.parse(tokens, i)
            except ParseException as err:
                i += 1
            else:
                if next_i > i:
                    matches += 1
                    if len(results) == 1:
                        results = results[0]
                    yield results, i, next_i
                    if overlap:
                        i += 1
                    else:
                        i = next_i
                else:
                    i += 1

    def parse(self, tokens, i, actions=True):
        start = i
        try:
            result, i = self._parse_tokens(tokens, i, actions)
        except IndexError:
            raise ParseException(tokens, i, 'IndexError', self)
        if actions:
            for action in self.actions:
                action_result = action(tokens, start, result)
                if action_result is not None:
                    result = action_result
        return result, i

    def try_parse(self, tokens, i):
        return self.parse(tokens, i, actions=False)[1]

    def _parse_tokens(self, tokens, i, actions=True):
        """Implemented by subclasses. """
        # TODO: abstractmethod?
        return None, i

    def streamline(self):
        self.streamlined = True
        return self

    def __add__(self, other):
        if isinstance(other, six.text_type):
            other = Word(other)
        if not isinstance(other, BaseParserElement):
            # raise?
            return None
        return And([self, other])

    def __radd__(self, other):
        if isinstance(other, six.text_type):
            other = Word(other)
        if not isinstance(other, BaseParserElement):
            # raise?
            return None
        return other + self

    def __or__(self, other):
        if isinstance(other, six.text_type):
            other = Word(other)
        if not isinstance(other, BaseParserElement):
            return None
        return First([self, other])

    def __ror__(self, other):
        if isinstance(other, six.text_type):
            other = Word(other)
        if not isinstance(other, BaseParserElement):
            return None
        return other | self

    def __xor__(self, other):
        if isinstance(other, six.text_type):
            other = Word(other)
        if not isinstance(other, BaseParserElement):
            return None
        return Or([self, other])

    def __rxor__(self, other):
        if isinstance(other, six.text_type):
            other = Word(other)
        if not isinstance(other, BaseParserElement):
            return None
        return other ^ self

    # def __and__(self, other):
    #     if isinstance(other, six.text_type):
    #         other = Word(other)
    #     if not isinstance(other, BaseParserElement):
    #         return None
    #     return Each([self, other])
    #
    # def __rand__(self, other):
    #     if isinstance(other, six.text_type):
    #         other = Word(other)
    #     if not isinstance(other, BaseParserElement):
    #         return None
    #     return other & self

    def __invert__(self):
        return Not(self)

    def __call__(self, name):
        return self.set_name(name)

    def hide(self):
        return Hide(self)


class Any(BaseParserElement):
    """Always match a single token."""

    def _parse_tokens(self, tokens, i, actions=True):
        return [E(self.name or safe_name(tokens[i][1]), tokens[i][0])], i + 1


class Word(BaseParserElement):
    """Match token text exactly."""

    def __init__(self, match):
        super(Word, self).__init__()
        self.match = match

    def _parse_tokens(self, tokens, i, actions=True):
        token_text = tokens[i][0]
        if token_text == self.match:
            return [E(self.name or safe_name(tokens[i][1]), token_text)], i + 1
        raise ParseException(tokens, i, 'Expected %s, got %s' % (self.match, token_text), self)


class Tag(BaseParserElement):
    """Match tag exactly."""

    def __init__(self, match):
        super(Tag, self).__init__()
        self.match = match

    def _parse_tokens(self, tokens, i, actions=True):
        token = tokens[i]
        if token[1] == self.match:
            return [E(self.name or safe_name(token[1]), token[0])], i + 1
        raise ParseException(tokens, i, 'Expected %s, got %s' % (self.match, token[1]), self)


class IWord(Word):
    """Case-insensitive match token text."""

    def __init__(self, match):
        super(IWord, self).__init__(match.lower())

    def _parse_tokens(self, tokens, i, actions=True):
        token_text = tokens[i][0]
        if token_text.lower() == self.match:
            return [E(self.name or safe_name(tokens[i][1]), tokens[i][0])], i + 1
        raise ParseException(tokens, i, 'Expected %s, got %s' % (self.match, tokens[i][0]), self)


class Regex(BaseParserElement):
    """Match token text with regular expression."""

    def __init__(self, pattern, flags=0, group=None):
        super(Regex, self).__init__()
        if isinstance(pattern, six.string_types):
            self.regex = re.compile(pattern, flags)
            self.pattern = pattern
        else:
            self.regex = pattern
            self.pattern = pattern.pattern
        self.group = group

    def _parse_tokens(self, tokens, i, actions=True):
        token_text = tokens[i][0]
        result = self.regex.search(token_text)
        if result:
            text = tokens[i][0] if self.group is None else result.group(self.group)
            return [E(self.name or safe_name(tokens[i][1]), text)], i + 1
        raise ParseException(tokens, i, 'Expected %s, got %s' % (self.pattern, token_text), self)


class Start(BaseParserElement):
    """Match at start of tokens."""

    def __init__(self):
        super(Start, self).__init__()

    def _parse_tokens(self, tokens, i, actions=True):
        if i != 0:
            raise ParseException(tokens, i, 'Expected start of tokens', self)
        return [], i


class End(BaseParserElement):
    """Match at end of tokens."""

    def __init__(self):
        super(End, self).__init__()

    def _parse_tokens(self, tokens, i, actions=True):
        if i < len(tokens):
            raise ParseException(tokens, i, 'Expected end of tokens', self)
        return [], i


class ParseExpression(BaseParserElement):
    """Abstract class for combining and post-processing parsed tokens."""

    def __init__(self, exprs):
        super(ParseExpression, self).__init__()
        if isinstance(exprs, types.GeneratorType):
            exprs = list(exprs)
        if isinstance(exprs, six.text_type):
            self.exprs = [Word(exprs)]
        elif isinstance(exprs, collections.Sequence):
            if all(isinstance(expr, six.text_type) for expr in exprs):
                exprs = map(Word, exprs)
            self.exprs = list(exprs)
        # else:
        #     try:
        #         self.exprs = list(exprs)
        #     except TypeError:
        #         self.exprs = [exprs]

    def __getitem__(self, i):
        return self.exprs[i]

    def append(self, other):
        self.exprs.append(other)
        return self

    def copy(self):
        ret = super(ParseExpression, self).copy()
        ret.exprs = [e.copy() for e in self.exprs]
        return ret

    def streamline(self):
        super(ParseExpression, self).streamline()
        for e in self.exprs:
            e.streamline()
        # collapse nested exprs from e.g. And(And(And(a, b), c), d) to And(a,b,c,d)
        if len(self.exprs) == 2:
            other = self.exprs[0]
            if isinstance(other, self.__class__) and not other.actions and other.name is None:
                self.exprs = other.exprs[:] + [self.exprs[1]]
            other = self.exprs[-1]
            if isinstance(other, self.__class__) and not other.actions and other.name is None:
                self.exprs = self.exprs[:-1] + other.exprs[:]
        return self


class And(ParseExpression):
    """Match all in the given order."""

    def __init__(self, exprs):
        super(And, self).__init__(exprs)

    def _parse_tokens(self, tokens, i, actions=True):
        results = []
        for e in self.exprs:
            exprresults, i = e.parse(tokens, i)
            if exprresults is not None:
                results.extend(exprresults)
        return ([E(self.name, *results)] if self.name else results), i

    def __iadd__(self, other):
        if isinstance(other, six.text_type):
            other = Word(other)
        return self.append(other)


class Or(ParseExpression):
    """Match the longest."""

    def _parse_tokens(self, tokens, i, actions=True):
        furthest_exception_i = -1
        furthest_match_i = -1
        furthest_exception = None
        for e in self.exprs:
            try:
                end_i = e.try_parse(tokens, i)
            except ParseException as err:
                if err.i > furthest_exception_i:
                    furthest_exception = err
                    furthest_exception_i = err.i
            except IndexError:
                if len(tokens) > furthest_exception_i:
                    furthest_exception = ParseException(tokens, len(tokens), '', self)
                    furthest_exception_i = len(tokens)
            else:
                if end_i > furthest_match_i:
                    furthest_match_i = end_i
                    furthest_match = e

        if furthest_match_i < 0:
            if furthest_exception is not None:
                raise furthest_exception
            else:
                raise ParseException(tokens, i, 'No alternatives match', self)

        # If a name is assigned to an Or, it replaces the name of the contained result
        if self.name:
            furthest_match = furthest_match.set_name(self.name)

        result, result_i = furthest_match.parse(tokens, i, actions=actions)
        # if self.name:
        #     result.tag = self.name
        return result, result_i

    def __ixor__(self, other):
        if isinstance(other, six.text_type):
            other = Word(other)
        return self.append(other)


class First(ParseExpression):
    """Match the first."""

    def __init__(self, exprs):
        super(First, self).__init__(exprs)

    def _parse_tokens(self, tokens, i, actions=True):
        furthest_i = -1
        furthest_exception = None
        for e in self.exprs:
            try:
                result, result_i = e.parse(tokens, i, actions=True)
                # If a name is assigned to a First, it replaces the name of the contained result
                if self.name:
                    for e in result:
                        e.tag = self.name
                return result, result_i
            except ParseException as err:
                if err.i > furthest_i:
                    furthest_exception = err
                    furthest_i = err.i
        else:
            if furthest_exception is not None:
                raise furthest_exception
            else:
                raise ParseException(tokens, i, 'No alternatives match', self)

    def __ior__(self, other):
        if isinstance(other, six.text_type):
            other = Word(other)
        return self.append(other)


class ParseElementEnhance(BaseParserElement):
    """Abstract class for combining and post-processing parsed tokens."""

    def __init__(self, expr):
        super(ParseElementEnhance, self).__init__()
        if isinstance(expr, six.text_type):
            expr = Word(expr)
        self.expr = expr

    def _parse_tokens(self, tokens, i, actions=True):
        if self.expr is not None:
            return self.expr.parse(tokens, i)
        else:
            raise ParseException('', i, 'Error', self)

    def streamline(self):
        super(ParseElementEnhance, self).streamline()
        if self.expr is not None:
            self.expr.streamline()
        return self


class FollowedBy(ParseElementEnhance):
    """Check ahead if matches."""

    def _parse_tokens(self, tokens, i, actions=True):
        self.expr.try_parse(tokens, i)
        return [], i


class Not(ParseElementEnhance):
    """Check ahead to disallow a match with the given parse expression."""

    def _parse_tokens(self, tokens, i, actions=True):
        try:
            self.expr.try_parse(tokens, i)
        except (ParseException, IndexError):
            pass
        else:
            raise ParseException(tokens, i, 'Encountered disallowed token', self)
        return [], i


class ZeroOrMore(ParseElementEnhance):
    """Optional repetition of zero or more of the given expression."""

    def _parse_tokens(self, tokens, i, actions=True):
        results = []
        try:
            results, i = self.expr.parse(tokens, i, actions)
            while 1:
                start_i = i
                tmpresults, i = self.expr.parse(tokens, start_i, actions)
                if tmpresults:
                    results.extend(tmpresults)
        except (ParseException, IndexError):
            pass
        return ([E(self.name, *results)] if self.name else results), i


class OneOrMore(ParseElementEnhance):
    """Repetition of one or more of the given expression."""

    def _parse_tokens(self, tokens, i, actions=True):
        # must be at least one
        results, i = self.expr.parse(tokens, i, actions)
        try:
            while 1:
                start_i = i
                tmpresults, i = self.expr.parse(tokens, start_i, actions)
                if tmpresults:
                    results.extend(tmpresults)
        except (ParseException, IndexError):
            pass
        return ([E(self.name, *results)] if self.name else results), i


class Optional(ParseElementEnhance):

    def __init__(self, expr):
        super(Optional, self).__init__(expr)

    def _parse_tokens(self, tokens, i, actions=True):
        results = []
        try:
            results, i = self.expr.parse(tokens, i, actions)
        except (ParseException, IndexError):
            pass
        return results, i


class Group(ParseElementEnhance):
    """"""

    def _parse_tokens(self, tokens, i, actions=True):
        results, i = self.expr.parse(tokens, i, actions)
        return ([E(self.name, *results)] if self.name else results), i


class SkipTo(ParseElementEnhance):

    def __init__(self, expr, include=False):
        super(SkipTo, self).__init__(expr)
        self.include = include

    def _parse_tokens(self, tokens, i, actions=True):
        start_i = i
        tokens_length = len(tokens)
        while i <= tokens_length:
            try:
                self.expr.parse(tokens, i, actions=False)
                results = [E(safe_name(t[1]), t[0]) for t in tokens[start_i:i]]
                if self.include:
                    match_result, i = self.expr.parse(tokens, i, actions)
                    if match_result:
                        results.extend(match_result)
                return results, i
            except (ParseException, IndexError):
                i += 1
        raise ParseException(tokens, i, '', self)


class Hide(ParseElementEnhance):
    """Converter for ignoring the results of a parsed expression."""

    def _parse_tokens(self, tokens, i, actions=True):
        results, i = super(Hide, self)._parse_tokens(tokens, i)
        return [], i

    def hide(self):
        return self


# Abbreviations
W = Word
I = IWord
R = Regex
T = Tag
H = Hide

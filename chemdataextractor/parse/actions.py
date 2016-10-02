# -*- coding: utf-8 -*-
"""
chemdataextractor.parse.actions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Actions to perform during parsing.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import re

from lxml.builder import E
from lxml.etree import strip_tags

from ..text import HYPHENS


log = logging.getLogger(__name__)


def flatten(tokens, start, result):
    """Replace all child results with their text contents."""
    for e in result:
        strip_tags(e, '*')
    return result


def join(tokens, start, result):
    """Join tokens into a single string with spaces between."""
    texts = []
    if len(result) > 0:
        for e in result:
            for child in e.iter():
                if child.text is not None:
                    texts.append(child.text)
        return [E(result[0].tag, ' '.join(texts))]


def merge(tokens, start, result):
    """Join tokens into a single string with no spaces."""
    texts = []
    if len(result) > 0:
        for e in result:
            for child in e.iter():
                if child.text is not None:
                    texts.append(child.text)
        return [E(result[0].tag, ''.join(texts))]


def strip_stop(tokens, start, result):
    """Remove trailing full stop from tokens."""
    for e in result:
        for child in e.iter():
            if child.text.endswith('.'):
                child.text = child.text[:-1]
    return result


def fix_whitespace(tokens, start, result):
    """Fix whitespace around hyphens and commas. Can be used to remove whitespace tokenization artefacts."""
    for e in result:
        for child in e.iter():
            child.text = child.text.replace(' , ', ', ')
            for hyphen in HYPHENS:
                child.text = child.text.replace(' %s ' % hyphen, '%s' % hyphen)
            child.text = re.sub(r'- (.) -', r'-\1-', child.text)
    return result

# -*- coding: utf-8 -*-
"""
chemdataextractor.text
~~~~~~~~~~~~~~~~~~~~~~

Tools for processing text.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import re
import unicodedata

from bs4 import UnicodeDammit


#: Control characters.
CONTROLS = {'\u0001', '\u0002', '\u0003', '\u0004', '\u0005', '\u0006', '\u0007', '\u0008'}

#: Hyphen and dash characters.
HYPHENS = {
    '-',  # \u002d Hyphen-minus
    '‐',  # \u2010 Hyphen
    '‑',  # \u2011 Non-breaking hyphen
    '⁃',  # \u2043 Hyphen bullet
    '‒',  # \u2012 figure dash
    '–',  # \u2013 en dash
    '—',  # \u2014 em dash
    '―',  # \u2015 horizontal bar
}

#: Minus characters.
MINUSES = {
    '-',  # \u002d Hyphen-minus
    '−',  # \u2212 Minus
    '－',  # \uff0d Full-width Hyphen-minus
    '⁻',  # \u207b Superscript minus
}

#: Plus characters.
PLUSES = {
    '+',  # \u002b Plus
    '＋',  # \uff0b Full-width Plus
    '⁺',  # \u207a Superscript plus
}

#: Slash characters.
SLASHES = {
    '/',  # \u002f Solidus
    '⁄',  # \u2044 Fraction slash
    '∕',  # \u2215 Division slash
}

#: Tilde characters.
TILDES = {
    '~',  # \u007e Tilde
    '˜',  # \u02dc Small tilde
    '⁓',  # \u2053 Swung dash
    '∼',  # \u223c Tilde operator
    '∽',  # \u223d Reversed tilde
    '∿',  # \u223f Sine wave
    '〜',  # \u301c Wave dash
    '～',  # \uff5e Full-width tilde
}

#: Apostrophe characters.
APOSTROPHES = {
    "'",  # \u0027
    '’',  # \u2019
    '՚',  # \u055a
    'Ꞌ',  # \ua78b
    'ꞌ',  # \ua78c
    '＇',  # \uff07
}

#: Single quote characters.
SINGLE_QUOTES = {
    "'",  # \u0027
    '‘',  # \u2018
    '’',  # \u2019
    '‚',  # \u201a
    '‛',  # \u201b

}

#: Double quote characters.
DOUBLE_QUOTES = {
    '"',  # \u0022
    '“',  # \u201c
    '”',  # \u201d
    '„',  # \u201e
    '‟',  # \u201f
}

#: Accent characters.
ACCENTS = {
    '`',  # \u0060
    '´',  # \u00b4
}

#: Prime characters.
PRIMES = {
    '′',  # \u2032
    '″',  # \u2033
    '‴',  # \u2034
    '‵',  # \u2035
    '‶',  # \u2036
    '‷',  # \u2037
    '⁗',  # \u2057
}

#: Quote characters, including apostrophes, single quotes, double quotes, accents and primes.
QUOTES = APOSTROPHES | SINGLE_QUOTES | DOUBLE_QUOTES | ACCENTS | PRIMES

#: Uppercase and lowercase greek letters.
GREEK = {
    'Α',  # \u0391
    'Β',  # \u0392
    'Γ',  # \u0393
    'Δ',  # \u0394
    'Ε',  # \u0395
    'Ζ',  # \u0396
    'Η',  # \u0397
    'Θ',  # \u0398
    'Ι',  # \u0399
    'Κ',  # \u039a
    'Λ',  # \u039b
    'Μ',  # \u039c
    'Ν',  # \u039d
    'Ξ',  # \u039e
    'Ο',  # \u039f
    'Π',  # \u03a0
    'Ρ',  # \u03a1
    'Σ',  # \u03a3
    'Τ',  # \u03a4
    'Υ',  # \u03a5
    'Φ',  # \u03a6
    'Χ',  # \u03a7
    'Ψ',  # \u03a8
    'Ω',  # \u03a9
    'α',  # \u03b1
    'β',  # \u03b2
    'γ',  # \u03b3
    'δ',  # \u03b4
    'ε',  # \u03b5
    'ζ',  # \u03b6
    'η',  # \u03b7
    'θ',  # \u03b8
    'ι',  # \u03b9
    'κ',  # \u03ba
    'λ',  # \u03bb
    'μ',  # \u03bc
    'ν',  # \u03bd
    'ξ',  # \u03be
    'ο',  # \u03bf
    'π',  # \u03c0
    'ρ',  # \u03c1
    'σ',  # \u03c3
    'τ',  # \u03c4
    'υ',  # \u03c5
    'φ',  # \u03c6
    'χ',  # \u03c7
    'ψ',  # \u03c8
    'ω',  # \u03c9
}

#: Names of greek letters spelled out as words.
GREEK_WORDS = {
    'Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta', 'Iota', 'Kappa', 'Lambda', 'Mu', 'Nu', 'Xi',
    'Omicron', 'Pi', 'Rho', 'Sigma', 'Tau', 'Upsilon', 'Phi', 'Chi', 'Psi', 'Omega', 'alpha', 'beta', 'gamma', 'delta',
    'epsilon', 'zeta', 'eta', 'theta', 'iota', 'kappa', 'lamda', 'mu', 'nu', 'xi', 'omicron', 'pi', 'rho', 'sigma',
    'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega'
}

#: Words that should not be capitalized in titles.
SMALL = {
    'a', 'an', 'and', 'as', 'at', 'but', 'by', 'en', 'for', 'if', 'in', 'of', 'on', 'or', 'the', 'to', 'v', 'v', 'via',
    'vs', 'vs'
}

#: Words that should not be capitalized in names.
NAME_SMALL = {
    'abu', 'bon', 'bin', 'da', 'dal', 'de', 'del', 'der', 'de', 'di', u'dí', 'ibn', 'la', 'le', 'san', 'st', 'ste',
    'van', 'vel', 'von', 'y'
}

# This isn't every possible TLD, just the most common, to avoid false positives.
TLDS = {
    'aero', 'asia', 'biz', 'cat', 'com', 'coop', 'edu', 'eu', 'gov', 'info', 'int', 'jobs', 'mil', 'mobi', 'museum',
    'name', 'net', 'org', 'pro', 'tel', 'travel', 'xxx', 'ad', 'as', 'ar', 'au', 'br', 'bz', 'ca', 'cc', 'cd', 'co',
    'ch', 'cn', 'de', 'dj', 'es', 'fr', 'fm', 'it', 'io', 'jp', 'la', 'ly', 'me', 'ms', 'nl', 'no', 'nu', 'ru', 'sc',
    'se', 'sr', 'su', 'tk', 'tv', 'uk', 'us', 'ws'
}

#: A variety of numbers, spelled out as words.
NUMBERS = {
    'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve',
    'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen', 'twenty', 'thirty', 'forty',
    'fifty', 'sixty', 'seventy', 'eighty', 'ninety', 'hundred', 'thousand', 'million', 'billion', 'trillion'
}

#: Regular expression that matches email addresses.
EMAIL_RE = re.compile(r'([\w\-\.\+%]+@(\w[\w\-]+\.)+[\w\-]+)', re.I | re.U)
#: Regular expression that matches DOIs.
DOI_RE = re.compile(r'^10\.\d{4,9}/[-\._;()/:A-Z0-9]+$', re.U)
#: Regular expression that matches ISSNs.
ISSN_RE = re.compile(r'^\d{4}-\d{3}[\dX]$', re.U)


def get_encoding(input_string, guesses=None, is_html=False):
    """Return the encoding of a byte string. Uses bs4 UnicodeDammit.

    :param string input_string: Encoded byte string.
    :param list[string] guesses: (Optional) List of encoding guesses to prioritize.
    :param bool is_html: Whether the input is HTML.
    """
    converted = UnicodeDammit(input_string, override_encodings=[guesses] if guesses else [], is_html=is_html)
    return converted.original_encoding


def levenshtein(s1, s2, allow_substring=False):
    """Return the Levenshtein distance between two strings.

    The Levenshtein distance (a.k.a "edit difference") is the number of characters that need to be substituted,
    inserted or deleted to transform s1 into s2.

    Setting the `allow_substring` parameter to True allows s1 to be a
    substring of s2, so that, for example, "hello" and "hello there" would have a distance of zero.

    :param string s1: The first string
    :param string s2: The second string
    :param bool allow_substring: Whether to allow s1 to be a substring of s2
    :returns: Levenshtein distance.
    :rtype int
    """
    len1, len2 = len(s1), len(s2)
    lev = []
    for i in range(len1 + 1):
        lev.append([0] * (len2 + 1))
    for i in range(len1 + 1):
        lev[i][0] = i
    for j in range(len2 + 1):
        lev[0][j] = 0 if allow_substring else j
    for i in range(len1):
        for j in range(len2):
            lev[i + 1][j + 1] = min(lev[i][j + 1] + 1, lev[i + 1][j] + 1, lev[i][j] + (s1[i] != s2[j]))
    return min(lev[len1]) if allow_substring else lev[len1][len2]


def bracket_level(text, open={'(', '[', '{'}, close={')', ']', '}'}):
    """Return 0 if string contains balanced brackets or no brackets."""
    level = 0
    for c in text:
        if c in open:
            level += 1
        elif c in close:
            level -= 1
    return level


def is_punct(text):
    for char in text:
        if not unicodedata.category(char).startswith('P'):
            return False
    else:
        return True


def is_ascii(text):
    for char in text:
        if ord(char) >= 128:
            return False
    else:
        return True


def like_url(text):
    if len(text) < 1:
        return False
    if text.startswith('http://'):
        return True
    elif text.startswith('www.') and len(text) >= 5:
        return True
    if len(text) < 2 or text[0] == '.' or text[-1] == '.' or '.' not in text:
        return False
    tld = text.rsplit('.', 1)[1].split(':', 1)[0]
    if tld.endswith('/'):
        return True
    if tld.isalpha() and tld in TLDS:
        return True
    return False


def like_number(text):
    text = text.replace(',', '').replace('.', '')
    if text.isdigit():
        return True
    if text.count('/') == 1:
        num, denom = text.split('/')
        if like_number(num) and like_number(denom):
            return True
    if text in NUMBERS:
        return True
    return False


def word_shape(text):
    prev_m = ''
    seq = 0
    shape = []
    for c in text:
        if c.isdigit():
            m = 'd'  # Digits
        elif c in GREEK:
            m = 'g'  # Greek letters
        elif c.isalpha():
            m = 'X' if c.isupper() else 'x'  # Uppercase or lowercase alphabetical
        elif c in QUOTES:
            m = "'"  # Quotes and apostrophes
        elif c in {':', ';'}:
            m = ':'  # Colons and semicolons
        elif c in {'!', '?', '.'}:
            m = '.'  # Sentence ends
        elif c in {'(', '[', '{', ')', ']', '}'}:
            m = 'b'  # Brackets
        elif c in {'°', '%'}:
            m = 'u'  # units
        elif c in {'■', '◼', '●', '▲', '○', '◆', '▼', '⧫', '△', '◇', '▽', '⬚', '□'}:
            m = 'l'  # list markers
        elif c in {',', '$', '&', '-'}:
            m = c  # Stay the same
        else:
            m = '*'  # Everything else, symbols etc: {'=', '+', '*', '_', '|', '@', '×', '÷', '±', '<', '≤', '>', '≥', '≦', '≡', '≅', '≈', '≃', '≲', '→', '←', '⇄', '≪', '≫', '↔', '≠', '∝', '∈', '⇌', '⇋', '⋯', '~', '·', '•', '√', '⊃', '∑', '∏', '®', '∞', '∂', '∫', '∇', '∧', '⟨', '⟩'}
        if m == prev_m:
            seq += 1
        else:
            seq = 0
            prev_m = m
        if seq < 3:
            shape.append(m)
    return ''.join(shape)

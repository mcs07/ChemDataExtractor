# -*- coding: utf-8 -*-
"""
chemdataextractor.cli.dict
~~~~~~~~~~~~~~~~~~~~~~~~~~

Commands for building a dictionary-based chemical named entity recognizer.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import re
import sys

import click
from ..nlp.lexicon import ChemLexicon
from ..nlp.tokenize import ChemWordTokenizer

from ..nlp.tag import DictionaryTagger
from ..nlp.cem import CsDictCemTagger, CiDictCemTagger, STOPLIST, STOP_SUB, STOP_TOKENS


try:
    from html import unescape
except ImportError:
    from six.moves.html_parser import HTMLParser
    unescape = HTMLParser().unescape


NG_RE = re.compile('([\[\(](\d\d?CI|USAN|r?INN|BAN|JAN|USP)(\d\d?CI|USAN|r?INN|BAN|JAN|USP|[:\-,]|spanish|latin)*[\)\]])+$', re.I | re.U)
START_RE = re.compile('^(anhydrous|elemental|amorphous|conjugated|colloidal|activated) ', re.I | re.U)
END_RE = re.compile('[\[\(]((crude )?product|substance|solution|anhydrous|derivative|analog|salt|modified|discontinued|injectable|anesthetic|pharmaceutical|natural|nonionic|european|ester|dye|tablets?|mineral|VAN|hydrolyzed)[\)\]]$', re.I | re.U)
RATIO_RE = re.compile('[\[\(]((\d\d?)(:(\d\d?|\?|\d\.\d))+)[\)\]]$', re.I | re.U)
NUM_END_RE = re.compile(' (\d+)$', re.U)
ALPHANUM_END_RE = re.compile(' ([A-Za-z]\d*)$', re.U)
BRACKET_RE = re.compile('^\(([^\(\)]+)\)$', re.I | re.U)

GREEK_WORDS = {
    'Alpha': 'Α',  # \u0391
    'Beta': 'Β',  # \u0392
    'Gamma': 'Γ',  # \u0393
    'Delta': 'Δ',  # \u0394
    'Epsilon': 'Ε',  # \u0395
    'Zeta': 'Ζ',  # \u0396
    'Eta': 'Η',  # \u0397
    'Theta': 'Θ',  # \u0398
    'Iota': 'Ι',  # \u0399
    'Kappa': 'Κ',  # \u039a
    'Lambda': 'Λ',  # \u039b
    'Mu': 'Μ',  # \u039c
    'Nu': 'Ν',  # \u039d
    'Xi': 'Ξ',  # \u039e
    'Omicron': 'Ο',  # \u039f
    'Pi': 'Π',  # \u03a0
    'Rho': 'Ρ',  # \u03a1
    'Sigma': 'Σ',  # \u03a3
    'Tau': 'Τ',  # \u03a4
    'Upsilon': 'Υ',  # \u03a5
    'Phi': 'Φ',  # \u03a6
    'Chi': 'Χ',  # \u03a7
    'Psi': 'Ψ',  # \u03a8
    'Omega': 'Ω',  # \u03a9
    'alpha': 'α',  # \u03b1
    'beta': 'β',  # \u03b2
    'gamma': 'γ',  # \u03b3
    'delta': 'δ',  # \u03b4
    'epsilon': 'ε',  # \u03b5
    'zeta': 'ζ',  # \u03b6
    'eta': 'η',  # \u03b7
    'theta': 'θ',  # \u03b8
    'iota': 'ι',  # \u03b9
    'kappa': 'κ',  # \u03ba
    'lambda': 'λ',  # \u03bb
    'mu': 'μ',  # \u03bc
    'nu': 'ν',  # \u03bd
    'xi': 'ξ',  # \u03be
    'omicron': 'ο',  # \u03bf
    'pi': 'π',  # \u03c0
    'rho': 'ρ',  # \u03c1
    'sigma': 'σ',  # \u03c3
    'tau': 'τ',  # \u03c4
    'upsilon': 'υ',  # \u03c5
    'phi': 'φ',  # \u03c6
    'chi': 'χ',  # \u03c7
    'psi': 'ψ',  # \u03c8
    'omega': 'ω',  # \u03c9
}

UNAMBIGUOUS_GREEK_WORDS = {
    'Alpha': 'Α',  # \u0391
    'Beta': 'Β',  # \u0392
    'Gamma': 'Γ',  # \u0393
    'Delta': 'Δ',  # \u0394
    'Epsilon': 'Ε',  # \u0395
    'Kappa': 'Κ',  # \u039a
    'Lambda': 'Λ',  # \u039b
    'Sigma': 'Σ',  # \u03a3
    'Upsilon': 'Υ',  # \u03a5
    'Omega': 'Ω',  # \u03a9
    'alpha': 'α',  # \u03b1
    'beta': 'β',  # \u03b2
    'gamma': 'γ',  # \u03b3
    'delta': 'δ',  # \u03b4
    'epsilon': 'ε',  # \u03b5
    'kappa': 'κ',  # \u03ba
    'lambda': 'λ',  # \u03bb
    'sigma': 'σ',  # \u03c3
    'upsilon': 'υ',  # \u03c5
    'omega': 'ω',  # \u03c9
}

DOT_GREEK_RE = re.compile('\.(%s)\.' % '|'.join(re.escape(s) for s in GREEK_WORDS.keys()), re.U)
GREEK_RE = re.compile('([\daA\W]|^)(%s)([\d\W]|$)' % '|'.join(re.escape(s) for s in GREEK_WORDS.keys()), re.U)
UNAMBIGUOUS_GREEK_RE = re.compile('(%s)' % '|'.join(re.escape(s) for s in UNAMBIGUOUS_GREEK_WORDS.keys()), re.U)


@click.group(name='dict')
@click.pass_context
def dict_cli(ctx):
    """Chemical dictionary commands."""
    pass


def _process_name(name):
    """Fix issues with Jochem names."""

    # Unescape HTML entities
    name = unescape(name)

    # Remove bracketed stuff on the end
    name = NG_RE.sub('', name).strip()  # Nomenclature groups
    name = END_RE.sub('', name).strip(', ')  # Words
    name = RATIO_RE.sub('', name).strip(', ')  # Ratios

    # Remove stuff off start
    name = START_RE.sub('', name).strip()

    # Remove balanced start and end brackets if none in between
    name = BRACKET_RE.sub('\g<1>', name)

    # Un-invert CAS style names
    comps = name.split(', ')
    if len(comps) == 2:
        if comps[1].endswith('-'):
            name = comps[0]
            name = '%s%s' % (comps[1], name)
    elif len(comps) > 2:
        name = comps[0]
        for i in range(1, len(comps)):
            if comps[i].endswith('-'):
                name = '%s%s' % (comps[i], name)
            else:
                name = '%s %s' % (name, comps[i])
    return name


def _filter_name(name):
    """Filter words when adding to Dictionary. Return True if name should be added."""
    # Remove if length 3 or less
    if len(name) <= 3:
        return False
    # Remove if starts with IL-
    if name.startswith('IL-'):
        return False
    lowname = name.lower()
    # Remove if contains certain sequences
    if any(c in lowname for c in STOP_SUB):
        return False
    # Remove if (case-insensitive) exact match to stoplist
    if lowname in STOPLIST:
        return False
    comps = re.split('[ -]', lowname)
    # Remove if just single character + digits separated by spaces or hyphens (or the word compound)
    if all(c.isdigit() or len(c) == 1 or c == 'compound' for c in comps):
        return False
    # Remove if 3 or fewer letters with 2 or fewer digits
    if len(comps) == 2 and len(comps[0]) <= 3 and comps[0].isalpha() and len(comps[1]) <= 3 and comps[1].isdigit():
        return False
    # Remove if just greek characters and numbrs
    if re.match('^[Α-Ωα-ω0-9]+$', name):
        return False
    # Filter registry numbers? No real size benefit in DAWG.
    # if REG_RE.search(name):
    #     keep = False
    # Handle this at the token level
    # if name.endswith(' derivative') or name.endswith(' analog') or name.endswith(' solution'):
    #     keep = False
    # Filter this after matching and expanding boundaries
    # if name.startswith('-') or name.endswith('-'):
    #     keep = False
    # Filter this after matching and expanding boundaries
    # if not bracket_level(name) == 0:
    #     print(name)
    return True


def _filter_tokens(tokens):
    """"""
    keep = True
    for token in tokens:
        if token in STOP_TOKENS:
            keep = False
    return keep


def _get_variants(name):
    """Return variants of chemical name."""
    names = [name]
    oldname = name
    # Map greek words to unicode characters
    if DOT_GREEK_RE.search(name):
        wordname = name
        while True:
            m = DOT_GREEK_RE.search(wordname)
            if m:
                wordname = wordname[:m.start(1)-1] + m.group(1) + wordname[m.end(1)+1:]
            else:
                break
        symbolname = name
        while True:
            m = DOT_GREEK_RE.search(symbolname)
            if m:
                symbolname = symbolname[:m.start(1)-1] + GREEK_WORDS[m.group(1)] + symbolname[m.end(1)+1:]
            else:
                break
        names = [wordname, symbolname]
    else:
        while True:
            m = GREEK_RE.search(name)
            if m:
                name = name[:m.start(2)] + GREEK_WORDS[m.group(2)] + name[m.end(2):]
            else:
                break
        while True:
            m = UNAMBIGUOUS_GREEK_RE.search(name)
            if m:
                name = name[:m.start(1)] + GREEK_WORDS[m.group(1)] + name[m.end(1):]
            else:
                break
        if not name == oldname:
            names.append(name)
    newnames = []
    for name in names:
        # If last word \d+, add variants with hyphen and no space preceding
        if NUM_END_RE.search(name):
            newnames.append(NUM_END_RE.sub('-\g<1>', name))
            newnames.append(NUM_END_RE.sub('\g<1>', name))
        # If last word [A-Za-z]\d* add variants with hyphen preceding.
        if ALPHANUM_END_RE.search(name):
            newnames.append(ALPHANUM_END_RE.sub('-\g<1>', name))
    names.extend(newnames)
    return names


tokenizer = ChemWordTokenizer(split_last_stop=False)


def _make_tokens(name):
    """"""
    tokenized_names = []
    name = _process_name(name)
    if _filter_name(name):
        for name in _get_variants(name):
            if _filter_name(name):
                tokens = tokenizer.tokenize(name)
                if _filter_tokens(tokens):
                    tokenized_names.append(tokens)
    #print(tokenized_names)
    return tokenized_names


@dict_cli.command()
@click.argument('jochem', type=click.File('r', encoding='utf8'))
@click.option('--output', '-o', type=click.File('w', encoding='utf8'), help='Dictionary file.', default=sys.stdout)
@click.option('--csoutput', '-c', type=click.File('w', encoding='utf8'), help='Case-sensitive dictionary file.', default=sys.stdout)
@click.pass_obj
def prepare_jochem(ctx, jochem, output, csoutput):
    """Process and filter jochem file to produce list of names for dictionary."""
    click.echo('chemdataextractor.dict.prepare_jochem')
    for i, line in enumerate(jochem):
        print('JC%s' % i)
        if line.startswith('TM '):
            if line.endswith('	@match=ci\n'):
                for tokens in _make_tokens(line[3:-11]):
                    output.write(' '.join(tokens))
                    output.write('\n')
            else:
                for tokens in _make_tokens(line[3:-1]):
                    csoutput.write(' '.join(tokens))
                    csoutput.write('\n')


@dict_cli.command()
@click.argument('include', type=click.File('r', encoding='utf8'))
@click.option('--output', '-o', type=click.File('w', encoding='utf8'), help='Output file.', default=sys.stdout)
@click.pass_obj
def prepare_include(ctx, include, output):
    """Process and filter include file to produce list of names for dictionary."""
    click.echo('chemdataextractor.dict.prepare_include')
    for i, line in enumerate(include):
        print('IN%s' % i)
        for tokens in _make_tokens(line.strip()):
            output.write(' '.join(tokens))
            output.write('\n')


@dict_cli.command()
@click.argument('inputs', type=click.File('r', encoding='utf8'), nargs=-1)
@click.option('--output', help='Output model file.', required=True)
@click.option('--cs/--no-cs', help='Whether case-sensitive.', default=False)
@click.pass_obj
def build(ctx, inputs, output, cs):
    """Build chemical name dictionary."""
    click.echo('chemdataextractor.dict.build')
    dt = DictionaryTagger(lexicon=ChemLexicon(), case_sensitive=cs)
    names = []
    for input in inputs:
        for line in input:
            tokens = line.split()
            names.append(tokens)
    dt.build(words=names)
    dt.save(output)


@dict_cli.command()
@click.argument('model', required=True)
@click.option('--cs/--no-cs', default=False)
@click.option('--corpus', '-c', type=click.File('r', encoding='utf8'), required=True)
@click.option('--output', '-o', type=click.File('w', encoding='utf8'), help='Output file.', default=sys.stdout)
@click.pass_obj
def tag(ctx, model, cs, corpus, output):
    """Tag chemical entities and write CHEMDNER annotations predictions file."""
    click.echo('chemdataextractor.dict.tag')
    tagger = CsDictCemTagger(model=model) if cs else CiDictCemTagger(model=model)
    for line in corpus:
        sentence = []
        goldsentence = []
        for t in line.split():
            token, tag = t.rsplit('/', 1)
            goldsentence.append((token, tag))
            sentence.append(token)
        if sentence:
            tokentags = tagger.tag(sentence)
            for i, tokentag in enumerate(tokentags):
                goldtokentag = goldsentence[i]
                if goldtokentag[1] not in {'B-CM', 'I-CM'} and tokentag[1] in {'B-CM', 'I-CM'}:
                    print(line)
                    print(tokentag[0])

            output.write(' '.join('/'.join(tokentag) for tokentag in tagger.tag(sentence)))
            output.write('\n')
        else:
            output.write('\n')

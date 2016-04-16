# -*- coding: utf-8 -*-
"""
chemdataextractor.biblio.person
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tools for parsing people's names from strings into various name components.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import re
import string

from ..text import QUOTES
from ..text.latex import latex_to_unicode


ORCID_RE = re.compile(r'^\d{4}-\d{4}-\d{4}-\d{4}$')


TITLES = {
    'ms', 'miss', 'mrs', 'mr', 'master', 'dr', 'doctor', 'prof', 'professor', 'sir', 'dame', 'madam', 'madame',
    'mademoiselle', 'monsieur', 'lord', 'lady', 'rev', 'reverend', 'fr', 'father', 'brother', 'sister', 'pastor',
    'cardinal', 'abbot', 'abbess', 'friar', 'mother', 'bishop', 'archbishop', 'priest', 'priestess', 'pope', 'vicar',
    'chaplain', 'saint', 'deacon', 'archdeacon', 'rabbi', 'ayatollah', 'imam', 'pres', 'president', 'gov', 'governor',
    'rep', 'representative', 'sen', 'senator', 'minister', 'chancellor', 'cllr', 'councillor', 'secretary', 'speaker',
    'alderman', 'delegate', 'mayor', 'ambassador', 'prefect', 'premier', 'envoy', 'provost', 'coach', 'principal',
    'king', 'queen', 'prince', 'princess', 'royal', 'majesty', 'highness', 'rt', 'duke', 'duchess', 'archduke',
    'archduchess', 'marquis', 'marquess', 'marchioness', 'earl', 'count', 'countess', 'viscount', 'viscountess',
    'baron', 'baroness', 'sheikh', 'emperor', 'empress', 'tsar', 'tsarina', 'uncle', 'auntie', 'aunt', 'atty',
    'attorney', 'advocate', 'judge', 'solicitor', 'barrister', 'comptroller', 'sheriff', 'registrar', 'treasurer',
    'associate', 'assistant', 'honorable', 'honourable', 'deputy', 'vice', 'executive', 'his', 'her', 'private',
    'corporal', 'sargent', 'seargent', 'officer', 'major', 'captain', 'commander', 'lieutenant', 'colonel', 'general',
    'chief', 'admiral', 'pilot', 'resident', 'surgeon', 'nurse', 'col', 'capt', 'cpt', 'maj', 'cpl', 'ltc', 'sgt',
    'pfc', 'sfc', 'mg', 'bg', 'ssgt', 'ltcol', 'majgen', 'gen', 'ltgen', 'sgtmaj', 'bgen', 'lcpl', '2ndlt', '1stlt',
    'briggen', '1stsgt', 'pvt', '2lt', '1lt', 'ens', 'lt', 'adm', 'vadm', 'cpo', 'mcpo', 'mcpoc', 'scpo', 'radm(lh)',
    'radm(uh)', 'ltg'
}

PREFIXES = {
    'abu', 'bon', 'bin', 'da', 'dal', 'de', 'del', 'der', 'de', 'di', 'dí', 'ibn', 'la', 'le', 'san', 'st', 'ste',
    'van', 'vel', 'von'
}

SUFFIXES = {
    'Esq', 'Esquire', 'Bt', 'Btss', 'Jr', 'Sr', '2', 'I', 'II', 'III', 'IV', 'V', 'CLU', 'ChFC', 'CFP', 'MP', 'MSP',
    'MEP', 'AM', 'MLA', 'QC', 'KC', 'PC', 'SCJ', 'MHA', 'MNA', 'MPP', 'VC', 'GC', 'KBE', 'CBE', 'MBE', 'DBE', 'GBE',
    'OBE', 'MD', 'PhD', 'DBEnv', 'DConstMgt', 'DREst', 'EdD', 'DPhil', 'DLitt', 'DSocSci', 'EngD', 'DD', 'LLD', 'DProf',
    'BA', 'BSc', 'LLB', 'BEng', 'MBChB', 'MA', 'MSc', 'MSci', 'MPhil', 'MArch', 'MMORSE', 'MMath', 'MMathStat',
    'MPharm', 'MSt', 'MRes', 'MEng', 'MChem', 'MSocSc', 'MMus', 'LLM', 'BCL', 'MPhys', 'MComp', 'MAcc', 'MFin', 'MBA',
    'MPA', 'MEd', 'MEnt', 'MCGI', 'MGeol', 'MLitt', 'MEarthSc', 'MClinRes', 'MJur', 'FdA', 'FdSc', 'FdEng', 'PgD',
    'PgDip', 'PgC', 'PgCert', 'DipHE', 'OND', 'CertHE', 'RA', 'FRCP', 'FRSC', 'FRSA', 'FRCS', 'FMedSci', 'AMSB',
    'MSB', 'FSB', 'FBA', 'FBCS', 'FCPS', 'FGS', 'FREng', 'FRS', 'FRAeS', 'FRAI', 'FRAS', 'MRCP', 'MRCS', 'MRCA', 'FRCA',
    'MRCGP', 'FRCGP', 'MRSC', 'MRPharmS', 'FRPharmS', 'FZS', 'FRES', 'CBiol', 'CChem', 'CEng', 'CMath', 'CPhys', 'CSci'
}

SUFFIXES_LOWER = {suf.lower() for suf in SUFFIXES}

NOT_SUFFIX = {'I.', 'V.'}


# Make attributes instead of dict style.
# Parse from string as a class method.
# Mutable attributes that can be set via constructor or modified at any time.
# to_dict, to_json method?


class PersonName(dict):
    """Class for parsing a person's name into its constituent parts.

    Parses a name string into title, firstname, middlename, nickname, prefix, lastname, suffix.

    Example usage:

        p = PersonName('von Beethoven, Ludwig')

    PersonName acts like a dict:

        print p
        print p['firstname']
        print json.dumps(p)

    Name components can also be access as attributes:

        print p.lastname

    Instances can be reused by setting the name property:

        p.name = 'Henry Ford Jr. III'
        print p

    Two PersonName objects are equal if every name component matches exactly. For fuzzy matching, use the `could_be`
    method. This returns True for names that are not explicitly inconsistent.

    This class was written with the intention of parsing BibTeX author names, so name components enclosed within curly
    brackets will not be split.

    """

    # Useful info at  http://nwalsh.com/tex/texhelp/bibtx-23.html

    # Issues:
    # - Prefix 'ben' is recognised as middlename. Could distinguish 'ben' and 'Ben'?
    # - Multiple word first names like "Emma May" or "Billy Joe" aren't supported

    def __init__(self, fullname=None, from_bibtex=False):
        """Initialize with a name string.

        :param fullname: A person name as a string.

        """
        super(PersonName, self).__init__()
        self._from_bibtex = from_bibtex
        self.fullname = fullname

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.fullname)

    def __str__(self):
        return dict.__repr__(self)

    def could_be(self, other):
        """Return True if the other PersonName is not explicitly inconsistent."""
        # TODO: Some suffix and title differences should be allowed
        if type(other) is not type(self):
            return NotImplemented
        if self == other:
            return True
        for attr in ['title', 'firstname', 'middlename', 'nickname', 'prefix', 'lastname', 'suffix']:
            if attr not in self or attr not in other:
                continue
            puncmap = dict((ord(char), None) for char in string.punctuation)
            s = self[attr].lower().translate(puncmap)
            o = other[attr].lower().translate(puncmap)
            if s == o:
                continue
            if attr in {'firstname', 'middlename', 'lastname'}:
                if (({len(comp) for comp in s.split()} == {1} and [el[0] for el in o.split()] == s.split()) or
                        ({len(comp) for comp in o.split()} == {1} and [el[0] for el in s.split()] == o.split())):
                    continue
            return False
        return True

    @property
    def fullname(self):
        return self.get('fullname', '')

    @fullname.setter
    def fullname(self, fullname):
        self.clear()
        self._parse(fullname)

    def __getattr__(self, name):
        if name in {'title', 'firstname', 'middlename', 'nickname', 'prefix', 'lastname', 'suffix'}:
            return self.get(name)
        else:
            raise AttributeError

    def _is_title(self, t):
        """Return true if t is a title."""
        return t.lower().replace('.', '') in TITLES

    def _is_prefix(self, t):
        """Return true if t is a prefix."""
        return t.lower().replace('.', '') in PREFIXES

    def _is_suffix(self, t):
        """Return true if t is a suffix."""
        return t not in NOT_SUFFIX and (t.replace('.', '') in SUFFIXES or t.replace('.', '') in SUFFIXES_LOWER)

    def _tokenize(self, comps):
        """Split name on spaces, unless inside curly brackets or quotes."""
        ps = []
        for comp in comps:
            ps.extend([c.strip(' ,') for c in re.split(r'\s+(?=[^{}]*(?:\{|$))', comp)])
        return [p for p in ps if p]

    def _clean(self, t, capitalize=None):
        """Convert to normalized unicode and strip trailing full stops."""
        if self._from_bibtex:
            t = latex_to_unicode(t, capitalize=capitalize)
        t = ' '.join([el.rstrip('.') if el.count('.') == 1 else el for el in t.split()])
        return t

    def _strip(self, tokens, criteria, prop, rev=False):
        """Strip off contiguous tokens from the start or end of the list that meet the criteria."""
        num = len(tokens)
        res = []
        for i, token in enumerate(reversed(tokens) if rev else tokens):
            if criteria(token) and num > i + 1:
                res.insert(0, tokens.pop()) if rev else res.append(tokens.pop(0))
            else:
                break
        if res:
            self[prop] = self._clean(' '.join(res))
        return tokens

    def _parse(self, fullname):
        """Perform the parsing."""
        n = ' '.join(fullname.split()).strip(',')
        if not n:
            return
        comps = [p.strip() for p in n.split(',')]
        if len(comps) > 1 and not all([self._is_suffix(comp) for comp in comps[1:]]):
            vlj = []
            while True:
                vlj.append(comps.pop(0))
                if not self._is_suffix(comps[0]):
                    break
            ltokens = self._tokenize(vlj)
            ltokens = self._strip(ltokens, self._is_prefix, 'prefix')
            ltokens = self._strip(ltokens, self._is_suffix, 'suffix', True)
            self['lastname'] = self._clean(' '.join(ltokens), capitalize='name')
        tokens = self._tokenize(comps)
        tokens = self._strip(tokens, self._is_title, 'title')
        if not 'lastname' in self:
            tokens = self._strip(tokens, self._is_suffix, 'suffix', True)
        voni = []
        end = len(tokens) - 1
        if not 'prefix' in self:
            for i, token in enumerate(reversed(tokens)):
                if self._is_prefix(token):
                    if (i == 0 and end > 0) or (not 'lastname' in self and not i == end):
                        voni.append(end - i)
                else:
                    if (i == 0 and 'lastname' in self) or voni:
                        break
        if voni:
            if not 'lastname' in self:
                self['lastname'] = self._clean(' '.join(tokens[voni[0]+1:]), capitalize='name')
            self['prefix'] = self._clean(' '.join(tokens[voni[-1]:voni[0]+1]))
            tokens = tokens[:voni[-1]]
        else:
            if not 'lastname' in self:
                self['lastname'] = self._clean(tokens.pop(), capitalize='name')
        if tokens:
            self['firstname'] = self._clean(tokens.pop(0), capitalize='name')
        if tokens:
            nicki = []
            for i, token in enumerate(tokens):
                if token[0] in QUOTES:
                    for j, token2 in enumerate(tokens[i:]):
                        if token2[-1] in QUOTES:
                            nicki = range(i, i+j+1)
                            break
            if nicki:
                self['nickname'] = self._clean(' '.join(tokens[nicki[0]:nicki[-1]+1]).strip(''.join(QUOTES)),
                                                     capitalize='name')
                tokens[nicki[0]:nicki[-1]+1] = []
        if tokens:
            self['middlename'] = self._clean(' '.join(tokens), capitalize='name')
        namelist = []
        for attr in ['title', 'firstname', 'middlename', 'nickname', 'prefix', 'lastname', 'suffix']:
            if attr in self:
                namelist.append('"%s"' % self[attr] if attr == 'nickname' else self[attr])
        self['fullname'] = ' '.join(namelist)

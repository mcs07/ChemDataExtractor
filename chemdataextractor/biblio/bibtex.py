# -*- coding: utf-8 -*-
"""
chemdataextractor.biblio.bibtex
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

BibTeX parser.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from collections import OrderedDict
import json
import re

from ..text.latex import latex_to_unicode


class BibtexParser(object):
    """A class for parsing a BibTeX string into JSON or a python data structure.

    Example usage:

        with open(example.bib, 'r') as f:
            bib = BibtexParser(f.read())
            bib.parse()
            print bib.records_list
            print bib.json
    """

    def __init__(self, data, **kwargs):
        """Initialize BibtexParser with data.

        Optional metadata passed as keyword arguments will be included in the JSON output.
        e.g. collection, label, description, id, owner, created, modified, source

        Example usage:

            bib = BibtexParser(data, created=unicode(datetime.utcnow()), owner='mcs07')

        """
        self.data = data
        self.meta = kwargs
        self._token = None
        self.token_type = None
        self._tokens = re.compile(r'([^\s"\'#%@{}()=,]+|\s|"|\'|#|%|@|{|}|\(|\)|=|,)').finditer(self.data)
        self.mode = None
        self.definitions = {}
        self.records = OrderedDict()

        # Key name normalizations
        self.keynorms = {
            u'keyw': u'keyword',
            u'keywords': u'keyword',
            u'authors': u'author',
            u'editors': u'editor',
            u'url': u'link',
            u'urls': u'link',
            u'links': u'link',
            u'subjects': u'subject'
        }

    def _next_token(self, skipws=True):
        """Increment _token to the next token and return it."""
        self._token = next(self._tokens).group(0)
        return self._next_token() if skipws and self._token.isspace() else self._token

    def parse(self):
        """Parse self.data and store the parsed BibTeX to self.records."""
        while True:
            try:
                # TODO: If self._next_token() == '%' skip to newline?
                if self._next_token() == '@':
                    self._parse_entry()
            except StopIteration:
                break

    def _parse_entry(self):
        """Parse an entry."""
        entry_type = self._next_token().lower()
        if entry_type == 'string':
            self._parse_string()
        elif entry_type not in ['comment', 'preamble']:
            self._parse_record(entry_type)

    def _parse_string(self):
        """Parse a string entry and store the definition."""
        if self._next_token() in ['{', '(']:
            field = self._parse_field()
            if field:
                self.definitions[field[0]] = field[1]

    def _parse_record(self, record_type):
        """Parse a record."""
        if self._next_token() in ['{', '(']:
            key = self._next_token()
            self.records[key] = {
                u'id': key,
                u'type': record_type.lower()
            }
            if self._next_token() == ',':
                while True:
                    field = self._parse_field()
                    if field:
                        k, v = field[0], field[1]
                        if k in self.keynorms:
                            k = self.keynorms[k]
                        if k == 'pages':
                            v = v.replace(' ', '').replace('--', '-')
                        if k == 'author' or k == 'editor':
                            v = self.parse_names(v)
                        # Recapitalizing the title generally causes more problems than it solves
                        # elif k == 'title':
                        #     v = latex_to_unicode(v, capitalize='title')
                        else:
                            v = latex_to_unicode(v)
                        self.records[key][k] = v
                    if self._token != ',':
                        break

    def _parse_field(self):
        """Parse a Field."""
        name = self._next_token()
        if self._next_token() == '=':
            value = self._parse_value()
            return name, value

    def _parse_value(self):
        """Parse a value. Digits, definitions, and the contents of double quotes or curly brackets."""
        val = []
        while True:
            t = self._next_token()
            if t == '"':
                brac_counter = 0
                while True:
                    t = self._next_token(skipws=False)
                    if t == '{':
                        brac_counter += 1
                    if t == '}':
                        brac_counter -= 1
                    if t == '"' and brac_counter <= 0:
                        break
                    else:
                        val.append(t)
            elif t == '{':
                brac_counter = 0
                while True:
                    t = self._next_token(skipws=False)
                    if t == '{':
                        brac_counter += 1
                    if t == '}':
                        brac_counter -= 1
                    if brac_counter < 0:
                        break
                    else:
                        val.append(t)
            elif re.match(r'\w', t):
                val.extend([self.definitions.get(t, t), ' '])
            elif t.isdigit():
                val.append([t, ' '])
            elif t == '#':
                pass
            else:
                break

        value = ' '.join(''.join(val).split())
        return value

    @classmethod
    def parse_names(cls, names):
        """Parse a string of names separated by "and" like in a BibTeX authors field."""
        names = [latex_to_unicode(n) for n in re.split(r'\sand\s(?=[^{}]*(?:\{|$))', names) if n]
        return names

    @property
    def size(self):
        """Return the number of records parsed."""
        return len(self.records)

    @property
    def records_list(self):
        """Return the records as a list of dictionaries."""
        return list(self.records.values())

    @property
    def metadata(self):
        """Return metadata for the parsed collection of records."""
        auto = {u'records': self.size}
        auto.update(self.meta)
        return auto

    @property
    def json(self):
        """Return a list of records as a JSON string. Follows the BibJSON convention."""
        return json.dumps(OrderedDict([('metadata', self.metadata), ('records', self.records.values())]))


def parse_bibtex(data):
    bib = BibtexParser(data)
    bib.parse()
    return bib.records_list


# TODO: Improvements to BibTexParser
# - Initialize with options, then pass text to .parse method to reuse an instance?
# - Initialize with a single entry, and have attributes that correspond to the bibtex fields?
# - Have a classmethod that takes text containing multiple entries, then returns a list of instances
# - Have a list wrapper class that allows serialization of all at once?

# TODO: BibtexWriter - write python dict or BibJSON to BibTeX

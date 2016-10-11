# -*- coding: utf-8 -*-
"""
chemdataextractor.doc.document
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Document model.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from abc import ABCMeta, abstractproperty
import collections
import io
import json
import logging

import six

from .text import Paragraph, Citation, Footnote, Heading, Title
from .table import Table
from .figure import Figure
from ..errors import ReaderError
from ..model import ModelList
from ..text import get_encoding


log = logging.getLogger(__name__)


@six.python_2_unicode_compatible
class BaseDocument(six.with_metaclass(ABCMeta, collections.Sequence)):
    """Abstract base class for a Document."""

    def __repr__(self):
        return '<%s: %s elements>' % (self.__class__.__name__, len(self))

    def __str__(self):
        return '<%s: %s elements>' % (self.__class__.__name__, len(self))

    def __getitem__(self, index):
        return self.elements[index]

    def __len__(self):
        return len(self.elements)

    @abstractproperty
    def elements(self):
        """Return a list of document elements."""
        return []

    @abstractproperty
    def records(self):
        """Chemical records that have been parsed from this Document."""
        return []


class Document(BaseDocument):
    """"""

    def __init__(self, *elements):
        """"""
        self._elements = []
        for element in elements:
            # Convert raw text to Paragraph elements
            if isinstance(element, six.text_type):
                element = Paragraph(element)
            elif isinstance(element, six.binary_type):
                # Try guess encoding if byte string
                encoding = get_encoding(element)
                log.warn('Guessed bytestring encoding as %s. Use unicode strings to avoid this warning.', encoding)
                element = Paragraph(element.decode(encoding))
            element.document = self
            self._elements.append(element)
        log.debug('%s: Initializing with %s elements' % (self.__class__.__name__, len(self.elements)))

    @classmethod
    def from_file(cls, f, fname=None, readers=None):
        if isinstance(f, six.string_types):
            f = io.open(f, 'rb')
        if not fname and hasattr(f, 'name'):
            fname = f.name
        return cls.from_string(f.read(), fname=fname, readers=readers)

    @classmethod
    def from_string(cls, fstring, fname=None, readers=None):
        if readers is None:
            from ..reader import DEFAULT_READERS
            readers = DEFAULT_READERS
        for reader in readers:
            # Skip reader if we don't think it can read file
            if not reader.detect(fstring, fname=fname):
                continue
            try:
                d = reader.readstring(fstring)
                log.debug('Parsed document with %s' % reader.__class__.__name__)
                return d
            except ReaderError:
                pass
        raise ReaderError('Unable to read document')

    @property
    def elements(self):
        """Return a list of document elements."""
        return self._elements

    # TODO: memoized_property?
    @property
    def records(self):
        records = ModelList()
        contextual_records = []
        head_def_record = None
        head_def_record_i = None
        last_product_record = None
        title_record = None
        for i, el in enumerate(self.elements):
            last_id_record = None

            # Save title compound
            if isinstance(el, Title):
                el_records = el.records
                if len(el_records) == 1 and el_records[0].is_id_only:
                    title_record = el_records[0]
            
            # Reset head_def_record unless consecutive heading with no records
            if isinstance(el, Heading) and head_def_record is not None:
                if not (i == head_def_record_i + 1 and len(el.records) == 0):
                    head_def_record = None
                    head_def_record_i = None

            # Paragraph with single sentence with single ID record considered a head_def_record like heading
            if isinstance(el, Paragraph) and len(el.sentences) == 1:
                el_records = el.records
                if len(el_records) == 1 and el_records[0].is_id_only:
                    head_def_record = el_records[0]
                    head_def_record_i = i
            elif isinstance(el, Paragraph) and len(el.sentences) > 0 and not (head_def_record_i == i - 1 and isinstance(self.elements[i - 1], Heading)):
                # head_def_record from first sentence in Paragraph with single ID record unless right after heading with previous head_def_record
                first_sent_records = el.sentences[0].records
                if len(first_sent_records) == 1 and first_sent_records[0].is_id_only:
                    sent_record = first_sent_records[0]
                    if sent_record.labels or (sent_record.names and len(sent_record.names[0]) > len(el.sentences[0].text) / 2):
                        head_def_record = sent_record
                        head_def_record_i = i

            for record in el.records:
                # Keep track of the most recent record with labels
                if isinstance(el, Paragraph) and record.labels:
                    last_id_record = record
                # Keep track of the most recent 'product' record
                if 'product' in record.roles:
                    last_product_record = record
                if isinstance(el, Heading) and (record.labels or record.names):
                    head_def_record = record
                    head_def_record_i = i

                    # If 2 consecutive headings with compound ID, merge in from previous
                    if i > 0 and isinstance(self.elements[i - 1], Heading):
                        prev = self.elements[i - 1]
                        if (len(el.records) == 1 and record.is_id_only and len(prev.records) == 1 and
                                prev.records[0].is_id_only and not (record.labels and prev.records[0].labels) and
                                not (record.names and prev.records[0].names)):
                            record.names.extend(prev.records[0].names)
                            record.labels.extend(prev.records[0].labels)
                            record.roles.extend(prev.records[0].roles)

                if record.is_unidentified:
                    if record.is_contextual:
                        # Add contextual record to a list of all from the document for later merging
                        contextual_records.append(record)
                        continue
                    else:
                        # print(record.serialize())
                        # We have property values but no names or labels... try merge those from previous
                        if isinstance(el, Paragraph) and (head_def_record or last_product_record or last_id_record or title_record):
                            # head_def_record from heading takes priority if the heading directly precedes the paragraph ( NOPE: or the last_id_record has no name)
                            if head_def_record_i and head_def_record_i + 1 == i: # or (last_id_record and not last_id_record.names)):
                                if head_def_record:
                                    record.names = head_def_record.names
                                    record.labels = head_def_record.labels
                                    record.roles = head_def_record.roles
                                elif last_id_record:
                                    record.names = last_id_record.names
                                    record.labels = last_id_record.labels
                                    record.roles = last_id_record.roles
                                elif last_product_record:
                                    record.names = last_product_record.names
                                    record.labels = last_product_record.labels
                                    record.roles = last_product_record.roles
                                elif title_record:
                                    record.names = title_record.names
                                    record.labels = title_record.labels
                                    record.roles = title_record.roles
                            else:
                                if last_id_record:
                                    record.names = last_id_record.names
                                    record.labels = last_id_record.labels
                                    record.roles = last_id_record.roles
                                elif head_def_record:
                                    record.names = head_def_record.names
                                    record.labels = head_def_record.labels
                                    record.roles = head_def_record.roles
                                elif last_product_record:
                                    record.names = last_product_record.names
                                    record.labels = last_product_record.labels
                                    record.roles = last_product_record.roles
                                elif title_record:
                                    record.names = title_record.names
                                    record.labels = title_record.labels
                                    record.roles = title_record.roles
                        else:
                            # Consider continue here to filter records missing name/label...
                            pass
                records.append(record)

        for record in records:
            for contextual_record in contextual_records:
                record.merge_contextual(contextual_record)

        for record in records:
            for short, long, entity in self.abbreviation_definitions:
                if entity == 'CM':
                    name = ' '.join(long)
                    abbrev = ' '.join(short)
                    if name in record.names and not abbrev in record.names:
                        record.names.append(abbrev)
                    if abbrev in record.names and not name in record.names:
                        record.names.append(name)

        # Merge records with any shared name/label
        len_l = len(records)
        i = 0
        while i < (len_l - 1):
            for j in range(i + 1, len_l):
                r = records[i]
                other_r = records[j]

                # Strip whitespace and lowercase to compare names
                rnames_std = {''.join(n.split()).lower() for n in r.names}
                onames_std = {''.join(n.split()).lower() for n in other_r.names}

                # Clashing labels, don't merge
                if len(set(r.labels) - set(other_r.labels)) > 0 and len(set(other_r.labels) - set(r.labels)) > 0:
                    continue

                if any(n in rnames_std for n in onames_std) or any(l in r.labels for l in other_r.labels):
                    records.pop(j)
                    records.pop(i)
                    records.append(r.merge(other_r))
                    len_l -= 1
                    i -= 1
                    break
            i += 1
        return records

    def get_element_with_id(self, id):
        """Return the element with the specified ID."""
        # Should we maintain a hashmap of ids to make this more efficient? Probably overkill.
        # TODO: Elements can contain nested elements (captions, footnotes, table cells, etc.)
        return next((el for el in self.elements if el.id == id), None)

    @property
    def figures(self):
        """Return all Figure Elements in this Document."""
        return [el for el in self.elements if isinstance(el, Figure)]

    @property
    def tables(self):
        """Return all Table Elements in this Document."""
        return [el for el in self.elements if isinstance(el, Table)]

    @property
    def citations(self):
        """Return all Citation Elements in this Document."""
        return [el for el in self.elements if isinstance(el, Citation)]

    @property
    def footnotes(self):
        """Return all Footnote Elements in this Document."""
        # TODO: Elements (e.g. Tables) can contain nested Footnotes
        return [el for el in self.elements if isinstance(el, Footnote)]

    @property
    def headings(self):
        """Return all Heading Elements in this Document."""
        return [el for el in self.elements if isinstance(el, Heading)]

    @property
    def paragraphs(self):
        """Return all Paragraph Elements in this Document."""
        return [el for el in self.elements if isinstance(el, Paragraph)]

    @property
    def captioned_elements(self):
        """Return all Captioned Elements in this Document."""
        return [el for el in self.elements if isinstance(el, BaseCaptionedElement)]

    @property
    def abbreviation_definitions(self):
        """"""
        return [ab for el in self.elements for ab in el.abbreviation_definitions]

    @property
    def ner_tags(self):
        """"""
        return [n for el in self.elements for n in el.ner_tags]

    @property
    def cems(self):
        """"""
        return list(set([n for el in self.elements for n in el.cems]))

    def serialize(self):
        """Convert Document to python dictionary."""
        # Serialize fields to a dict
        elements = []
        for element in self.elements:
            elements.append(element.serialize())
        data = {'type': 'document', 'elements': elements}
        return data

    def to_json(self, *args, **kwargs):
        """Convert Document to JSON string."""
        return json.dumps(self.serialize(), *args, **kwargs)

    def _repr_html_(self):
        html_lines = ['<div class="cde-document">']
        for element in self.elements:
            html_lines.append(element._repr_html_())
        html_lines.append('</div>')
        return '\n'.join(html_lines)


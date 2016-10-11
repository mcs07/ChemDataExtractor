# -*- coding: utf-8 -*-
"""
chemdataextractor.doc.element
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Document elements.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from abc import ABCMeta, abstractproperty
import json

import six


@six.python_2_unicode_compatible
class BaseElement(six.with_metaclass(ABCMeta)):
    """Abstract base class for a Document Element."""

    def __init__(self, document=None, references=None, id=None):
        """If part of a Document, an Element should be initialized with a reference to its containing Document."""
        #: The containing Document
        self._document = document
        self.id = id
        self.references = references if references is not None else []

    def __repr__(self):
        return '<%s>' % (self.__class__.__name__,)

    def __str__(self):
        return '<%s>' % (self.__class__.__name__,)

    @property
    def document(self):
        return self._document

    @document.setter
    def document(self, document):
        # Subclasses may need to override this and also assign the document to sub-elements
        self._document = document
        # If we have problems with garbage collection, use a weakref to document to avoid circular references:
        # try:
        #     self._document = weakref.proxy(document)
        # except TypeError:
        #     self._document = document

    @abstractproperty
    def records(self):
        """Chemical records that have been parsed from this Element."""
        return []

    # @abstractmethod  # TODO: Put this back?
    # def serialize(self):
    #     """Convert Element to python dictionary."""
    #     return []

    def to_json(self, *args, **kwargs):
        """Convert Element to JSON string."""
        return json.dumps(self.serialize(), *args, **kwargs)


@six.python_2_unicode_compatible
class CaptionedElement(BaseElement):
    """Document Element with a caption."""

    def __init__(self, caption, label=None, **kwargs):
        """If part of a Document, an Element should be initialized with a reference to its containing Document."""
        super(CaptionedElement, self).__init__(**kwargs)
        self.caption = caption
        self.label = label

    def __repr__(self):
        return '%s(id=%r, references=%r, caption=%r)' % (self.__class__.__name__, self.id, self.references, self.caption.text.encode('utf8'))

    def __str__(self):
        return self.caption.text

    @property
    def document(self):
        return self._document

    @document.setter
    def document(self, document):
        self._document = document
        self.caption.document = document

    @property
    def records(self):
        """Chemical records that have been parsed from this Element."""
        # This just passes the caption records. Subclasses may wish to extend this.
        return self.caption.records

    @property
    def abbreviation_definitions(self):
        """"""
        return self.caption.abbreviation_definitions

    @property
    def ner_tags(self):
        """Return a list of part of speech tags for each sentence in this text passage."""
        # TODO: Delete this method?
        return self.caption.ner_tags

    @property
    def cems(self):
        """Return a list of chemical entity mentions for this element."""
        return self.caption.cems

    def serialize(self):
        """Convert Text element to python dictionary."""
        data = {'type': self.__class__.__name__, 'caption': self.caption.serialize()}
        return data

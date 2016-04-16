# -*- coding: utf-8 -*-
"""
chemdataextractor.reader.plaintext
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import re

import six

from ..doc.document import Document
from .base import BaseReader
from ..text import get_encoding


class PlainTextReader(BaseReader):
    """Read plain text and split into Paragraphs based on newline patterns."""

    def detect(self, fstring, fname=None):
        """Have a stab at most files."""
        if fname is not None and '.' in fname:
            extension = fname.rsplit('.', 1)[1]
            if extension in {'pdf', 'html', 'xml'}:
                return False
        return True

    def parse(self, fstring):
        if isinstance(fstring, six.binary_type):
            fstring = fstring.decode(get_encoding(fstring))
        para_strings = [p.strip() for p in re.split(r'\r\n[ \t]*\r\n|\r[ \t]*\r|\n[ \t]*\n', fstring)]
        return Document(*para_strings)

# -*- coding: utf-8 -*-
"""
chemdataextractor.biblio
~~~~~~~~~~~~~~~~~~~~~~~~

Tools for dealing with bibliographic information.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .bibtex import BibtexParser, parse_bibtex
from .person import PersonName
from .xmp import XmpParser, parse_xmp

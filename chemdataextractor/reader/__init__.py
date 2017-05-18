# -*- coding: utf-8 -*-
"""
chemdataextractor.reader
~~~~~~~~~~~~~~~~~~~~~~~~

Reader classes that read a file and produce a ChemDataExtractor Document object.

"""






from .acs import AcsHtmlReader
from .cssp import CsspHtmlReader
from .markup import HtmlReader, XmlReader
from .pdf import PdfReader
from .plaintext import PlainTextReader
from .rsc import RscHtmlReader
from .nlm import NlmXmlReader
from .uspto import UsptoXmlReader


DEFAULT_READERS = [
    AcsHtmlReader(),
    RscHtmlReader(),
    NlmXmlReader(),
    UsptoXmlReader(),
    CsspHtmlReader(),
    XmlReader(),
    HtmlReader(),
    PdfReader(),
    PlainTextReader(),
]

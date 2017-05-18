# -*- coding: utf-8 -*-
"""
chemdataextractor.errors
~~~~~~~~~~~~~~~~~~~~~~~~

Error classes for ChemDataExtractor.

"""







class ChemDataExtractorError(Exception):
    """Base ChemDataExtractor exception."""
    pass


class ReaderError(ChemDataExtractorError):
    """Raised when a reader is unable to read a document."""


class ModelNotFoundError(ChemDataExtractorError):
    """Raised when a model file could not be found."""

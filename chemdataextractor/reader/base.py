# -*- coding: utf-8 -*-
"""
chemdataextractor.reader.base
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



"""





from abc import ABCMeta, abstractmethod

import six


class BaseReader(six.with_metaclass(ABCMeta)):
    """All Document Readers should implement a parse method."""

    def detect(self, fstring, fname=None):
        """Quickly check if this reader can parse the input. Reader subclasses should override this.

        Used to quickly skip attempting to parse when trying different readers. If in doubt, return True, and then
        raise ReaderError in the parse method if it fails.
        """
        return True

    @abstractmethod
    def parse(self, fstring):
        """Parse the input and return a Document. Raises ReaderError if the parse fails."""
        pass

    def read(self, f):
        """Read a file-like object and return a Document."""
        return self.parse(f.read())

    def readstring(self, fstring):
        """Read a file string and return a Document."""
        return self.parse(fstring)

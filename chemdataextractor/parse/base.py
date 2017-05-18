# -*- coding: utf-8 -*-
"""
chemdataextractor.parse.base
~~~~~~~~~~~~~~~~~~~~~~~~~~~~



"""





from abc import abstractproperty, abstractmethod
import logging

log = logging.getLogger(__name__)


class BaseParser(object):
    """"""

    @abstractproperty
    def root(self):
        pass

    @abstractmethod
    def interpret(self, result, start, end):
        pass

    def parse(self, tokens):
        for result in self.root.scan(tokens):
            for model in self.interpret(*result):
                yield model

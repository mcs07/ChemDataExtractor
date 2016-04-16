# -*- coding: utf-8 -*-
"""
chemdataextractor.parse.base
~~~~~~~~~~~~~~~~~~~~~~~~~~~~



:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
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

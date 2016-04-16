# -*- coding: utf-8 -*-
"""
chemdataextractor.parse.nmr
~~~~~~~~~~~~~~~~~~~~~~~~~~~

NMR text parser.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import re

from ..utils import first
from ..model import Compound, MeltingPoint
from .actions import merge
from .base import BaseParser
from .elements import W, I, R, Optional


log = logging.getLogger(__name__)

prefix = (R('^m\.?p\.?$', re.I) | I('melting') + I('point')).hide() + Optional(W('='))

delim = R('^[:;\.]$')

temp_range = (Optional(R('^[\-–−]$')) + (R('^[\+\-–−]?\d+(\.\d+)?[\-–−]\d+(\.\d+)?$') | (R('^[\+\-–−]?\d+(\.\d+)?$') + R('^[\-–−~]$') + R('^[\+\-–−]?\d+(\.\d+)?$'))))('value').add_action(merge)
temp_value = (Optional(R('^[~∼\<\>]$')) + Optional(R('^[\-–−]$')) + R('^[\+\-–−]?\d+(\.\d+)?$'))('value').add_action(merge)
temp = (temp_range | temp_value)('value')


units = (W('°') + R('[CFK]') | W('K'))('units').add_action(merge)

mp = (prefix + Optional(delim).hide() + temp + units)('mp')


class MpParser(BaseParser):
    """"""
    root = mp

    def interpret(self, result, start, end):
        yield Compound({
            'melting_points': [
                MeltingPoint({
                    'value': first(result.xpath('./value/text()')),
                    'units': first(result.xpath('./units/text()')),
                })
            ]
        })

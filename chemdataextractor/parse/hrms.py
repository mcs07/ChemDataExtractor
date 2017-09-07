# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re

from .base import BaseParser
from .elements import OneOrMore, R, Optional, ZeroOrMore, Not
from ..model import Compound, HRMS
from ..utils import first
from .actions import merge

not_separator = '[^\.;,]$'
separator = '[\.;,]'
chem_sign = '[\+\-‐‑⁃‒–—―−－⁻]'
number = R('^\d+(\.\d+)?$')
chemical_name = R('^(([A-Z][a-z]?\d*|\((?:[^()]*(?:\(.*\))?[^()]*)+\)\d+)+' + chem_sign + '?)$', min_size=5)
# obtained from https://stackoverflow.com/questions/23602175/regex-for-parsing-chemical-formulas
chemical_structure_start = (R('(calcd|calculated)' + separator + '?', flags=re.IGNORECASE) | R('^for' + separator + '?', flags=re.IGNORECASE))
chemical_structure = (ZeroOrMore(chemical_structure_start + R(not_separator)).hide() + (chemical_name('chemical_structure')) + Optional(R(separator)).hide())
# compound = (R('^\[') + ZeroOrMore(R('\.+')) + R('\]')).add_action(merge)('compound')

# theoretical = (Optional(W('calcd') + W('for')).hide() + number('mass') + compound)('theoretical')
# experimental = (Optional(W('found')).hide() + number('mass'))('experimental')
exceptions = ((number | R(chem_sign + '$') | R(u'((^found|^\d+)' + separator + '?)$', flags=re.IGNORECASE)) + Optional(R(separator))).hide()

hrms = (R('HRMS').hide() + ZeroOrMore(chemical_structure | exceptions | R(not_separator).hide()))('hrms')


class HRMSParser(BaseParser):
    """"""
    root = hrms

    def __init__(self):
        pass

    def interpret(self, result, start, end):
        h = HRMS(
            chemical_structure=first(result.xpath('./chemical_structure/text()'))
        )
        c = Compound()
        c.hrms.append(h)

        yield c

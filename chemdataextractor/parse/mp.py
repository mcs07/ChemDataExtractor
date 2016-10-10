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

from chemdataextractor.parse.cem import cem, chemical_label, lenient_chemical_label, solvent_name
from chemdataextractor.parse.common import lbrct, dt, rbrct
from ..utils import first
from ..model import Compound, MeltingPoint
from .actions import merge, join
from .base import BaseParser
from .elements import W, I, R, Optional, Any, OneOrMore, Not, ZeroOrMore

log = logging.getLogger(__name__)

prefix = Optional(I('a')).hide() + (R('^m\.?pt?\.?$', re.I) | I('melting') + Optional((I('point') | I('temperature')| I('range'))) | R('^m\.?$', re.I) + R('^pt?\.?$', re.I)).hide() + Optional(W('=') | I('of') | I('was') | I('is') | I('at')).hide() + Optional(I('in') + I('the') + I('range') + Optional(I('of')) | I('about')).hide()

delim = R('^[:;\.,]$')

units = (W('°') + Optional(R('^[CFK]\.?$')) | W('K\.?'))('units').add_action(merge)

joined_range = R('^[\+\-–−]?\d+(\.\d+)?[\-–−~∼˜]\d+(\.\d+)?$')('value').add_action(merge)
spaced_range = (R('^[\+\-–−]?\d+(\.\d+)?$') + Optional(units).hide() + (R('^[\-–−~∼˜]$') + R('^[\+\-–−]?\d+(\.\d+)?$') | R('^[\+\-–−]\d+(\.\d+)?$')))('value').add_action(merge)
to_range = (R('^[\+\-–−]?\d+(\.\d+)?$') + Optional(units).hide() + (I('to') + R('^[\+\-–−]?\d+(\.\d+)?$') | R('^[\+\-–−]\d+(\.\d+)?$')))('value').add_action(join)
temp_range = (Optional(R('^[\-–−]$')) + (joined_range | spaced_range | to_range))('value').add_action(merge)
temp_value = (Optional(R('^[~∼˜\<\>]$')) + Optional(R('^[\-–−]$')) + R('^[\+\-–−]?\d+(\.\d+)?$'))('value').add_action(merge)
temp = (temp_range | temp_value)('value')

mp = (prefix + Optional(delim).hide() + temp + units)('mp')


bracket_any = lbrct + OneOrMore(Not(mp) + Not(rbrct) + Any()) + rbrct

solvent_phrase = (R('^(re)?crystalli[sz](ation|ed)$', re.I) + (I('with') | I('from')) + cem | solvent_name)
cem_mp_phrase = (Optional(solvent_phrase).hide() + Optional(cem) + Optional(I('having')).hide() + Optional(delim).hide() + Optional(bracket_any).hide() + Optional(delim).hide() + Optional(lbrct) + mp + Optional(rbrct))('mp_phrase')
to_give_mp_phrase = ((I('to') + (I('give') | I('afford') | I('yield') | I('obtain')) | I('affording') | I('afforded') | I('gave') | I('yielded')).hide() + Optional(dt).hide() + (cem | chemical_label | lenient_chemical_label) + ZeroOrMore(Not(mp) + Not(cem) + Any()).hide() + mp)('mp_phrase')
obtained_mp_phrase = ((cem | chemical_label) + (I('is') | I('are') | I('was')).hide() + (I('afforded') | I('obtained') | I('yielded')).hide() + ZeroOrMore(Not(mp) + Not(cem) + Any()).hide() + mp)('mp_phrase')

mp_phrase = cem_mp_phrase | to_give_mp_phrase | obtained_mp_phrase


class MpParser(BaseParser):
    """"""
    root = mp_phrase

    def interpret(self, result, start, end):
        compound = Compound(
            melting_points=[
                MeltingPoint(
                    value=first(result.xpath('./mp/value/text()')),
                    units=first(result.xpath('./mp/units/text()'))
                )
            ]
        )
        cem_el = first(result.xpath('./cem'))
        if cem_el is not None:
            compound.names = cem_el.xpath('./name/text()')
            compound.labels = cem_el.xpath('./label/text()')
        yield compound

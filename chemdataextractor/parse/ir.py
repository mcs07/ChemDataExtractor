# -*- coding: utf-8 -*-
"""
chemdataextractor.parse.ir
~~~~~~~~~~~~~~~~~~~~~~~~~~

IR spectrum text parser.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import re

from lxml.builder import E

from ..model import Compound, IrSpectrum, IrPeak
from .base import BaseParser
from ..utils import first
from .actions import join, merge, strip_stop
from .common import hyphen
from .elements import W, I, T, R, Optional, ZeroOrMore, OneOrMore, Not
from .cem import chemical_name


log = logging.getLogger(__name__)


def extract_units(tokens, start, result):
    """Extract units from bracketed after nu"""
    for e in result:
        for child in e.iter():
            if 'cm−1' in child.text:
                return [E('units', 'cm−1')]
    return []


delim = R('^[;:,\./]$').hide()

# Not really just solvent, also nujol suspension, pellet, or ATR
ir_solvent = (I('KBr') | I('ATR') | I('neat') | I('NaCl') | I('CaF2') | I('AgCl') | I('CsI')) + Optional(I('pellet'))

solvent = (ir_solvent | chemical_name)('solvent').add_action(join)

units = Optional(W('/')).hide() + (
    R('^\[?cm[-–−‒]?1\]?$') |
    W('cm') + R('^[-–−‒]$') + W('1')
)('units').add_action(merge)


value_range = ((R('^\d{,2}[ ,]?\d{3}(\.\d+)?[\-–−‒]\d{,2}[ ,]?\d{3}(\.\d+)?$') | (R('^\d{,2}[ ,]?\d{3}(\.\d+)?$') + R('^[\-–−‒]$') + R('^\d{,2}[ ,]?\d{3}(\.\d+)?$'))))('value').add_action(merge)
value = R('^\d{,2}[ ,]?\d{3}(\.\d+)?\.?$')('value').add_action(strip_stop)

strength = R('^(m|medium|w|weak|s|strong|n|narrow|b|broad|sh|sharp)$', re.I)('strength') + Optional(I('peak')).hide()

bond = OneOrMore(Not(W(')')) + (T('B-CM') | T('I-CM') | T('JJ') | T('NN') | T('NNP') | T('NNS') | T('HYPH') | T('CD') | T('LS') | T('CC')))('bond').add_action(join)

peak_meta_options = strength | bond

peak_meta = W('(').hide() + peak_meta_options + ZeroOrMore(delim + peak_meta_options) + W(')').hide()

nu = (R('^[vνυ]̃?(max)?(\(cm−1\))?$') + Optional(W('max')) + Optional(W('='))).add_action(extract_units)

spectrum_meta = W('(').hide() + (units | solvent | nu) + ZeroOrMore(delim + (units | solvent | nu)) + W(')').hide()


insolvent = T('IN') + solvent

ir_type = (Optional(W('FT') + hyphen) + R('^(FT-?)?IR|FT-?IS|IR-ATR$') + Optional(hyphen + W('ATR')))('type').add_action(merge)

prelude = (ir_type | R('^[vνυ]max$').hide()) + Optional(I('data')) + Optional(insolvent) + ZeroOrMore(spectrum_meta) + Optional(delim) + Optional(nu) + Optional(delim) + Optional(units)

peak = ((value_range | value) + Optional(peak_meta))('peak')

peaks = (peak + ZeroOrMore(ZeroOrMore(delim | W('and')).hide() + peak))('peaks')


ir = (prelude + peaks + Optional(delim) + Optional(units))('ir')


class IrParser(BaseParser):
    """"""
    root = ir

    def interpret(self, result, start, end):
        c = Compound()
        i = IrSpectrum(
            solvent=first(result.xpath('./solvent/text()'))
        )
        units = first(result.xpath('./units/text()'))
        for peak_result in result.xpath('./peaks/peak'):
            ir_peak = IrPeak(
                value=first(peak_result.xpath('./value/text()')),
                units=units,
                strength=first(peak_result.xpath('./strength/text()')),
                bond=first(peak_result.xpath('./bond/text()'))
            )
            i.peaks.append(ir_peak)
        c.ir_spectra.append(i)
        yield c

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

import copy
import logging
import re


from ..model import Compound, NmrSpectrum, NmrPeak
from ..utils import first
from .actions import join, merge, strip_stop, fix_whitespace
from .base import BaseParser
from .common import cc, equals
from .cem import chemical_name, nmr_solvent
from .elements import W, I, T, R, Optional, ZeroOrMore, SkipTo, OneOrMore, Not, Group

log = logging.getLogger(__name__)


number = R('^\d+(\.\d+)?$')

nucleus = (
    W('1H') | W('13C') | W('15N') | W('31P') | W('19F') | W('11B') | W('29Si') | W('17O') | W('73Ge') | W('195Pt') |
    W('33S') | W('13C{1H}') | W('13C{1H') + W('}') | W('H1') | W('C13') | W('N15') | W('P31') | W('F19') | W('B11') |
    W('Si29') | W('Ge73') | W('Pt195') | W('S33')
)('nucleus').add_action(merge)

nmr_name = R('^N\.?M\.?R\.?\(?$', re.I).hide()

nmr_name_with_nucleus = R('^(1H|13C)N\.?M\.?R\.?\(?$', re.I, group=1)('nucleus')

frequency = (number('value') + R('^M?Hz$')('units'))('frequency')

delim = R('^[;:,\./]$').hide()

solvent = ((nmr_solvent | chemical_name) + Optional((R('^(\+|&|and)$') | cc) + (nmr_solvent | chemical_name)) + Optional(SkipTo(R('^([;:,\.\)]|at)$'))) + Optional(Optional(delim) + I('solvent').hide()))('solvent').add_action(join).add_action(fix_whitespace)

temp_value = (Optional(R('^[~∼\<\>]$')) + Optional(R('^[\-–−]$')) + R('^[\+\-–−]?\d+(\.\d+)?$'))('value').add_action(merge)
temp_word = (I('room') + R('^temp(erature)?$') | R('^r\.?t\.?$', re.I))('value').add_action(join)
temp_units = (W('°') + R('[CFK]') | W('K'))('units').add_action(merge)
temperature = Optional(I('at').hide()) + Group((temp_value + temp_units) | temp_word)('temperature')


def fix_nmr_peak_whitespace_error(tokens, start, result):
    """"""
    new_result = []
    for e in result:
        shift = e.find('shift')
        if ',' in shift.text:
            for peak_text in shift.text.split(','):
                new_e = copy.deepcopy(e)
                new_e.find('shift').text = peak_text
                new_result.append(new_e)
        else:
            new_result.append(e)
    return new_result


def strip_delta(tokens, start, result):
    """"""
    for e in result:
        for child in e.iter():
            if child.text.startswith('δ'):
                child.text = child.text[1:]
    return result

shift_range = (Optional(R('^[\-–−‒]$')) + (R('^δ?[\+\-–−‒]?\d+(\.+\d+)?[\-–−‒]\d+(\.+\d+)?\.?$') | (R('^[\+\-–−‒]?\d+(\.+\d+)?$') + R('^[\-–−‒]$') + R('^[\+\-–−‒]?\d+(\.+\d+)?\.?$'))))('shift').add_action(merge)
shift_value = (Optional(R('^[\-–−‒]$')) + R('^δ?[\+\-–−‒]?\d+(\.+\d+)?\.?$'))('shift').add_action(merge)
shift_error = (Optional(R('^[\-–−‒]$')) + R('^δ?[\+\-–−‒]?\d+(\.+\d+)?,\d+(\.+\d+)?\.?$'))('shift').add_action(merge)
shift = (shift_range | shift_value | shift_error).add_action(strip_stop).add_action(strip_delta)

split = R('^(br?)?(s|S|d|D|t|T|q|Q|quint|sept|m|M|dd|ddd|dt|td|tt|br|bs|sb|h|ABq|broad|singlet|doublet|triplet|qua(rtet)?|quintet|septet|multiplet|multiple|peaks)$')
multiplicity = (OneOrMore(split) + Optional(W('of') + split))('multiplicity').add_action(join)

coupling_value = (number + ZeroOrMore(R('^[,;&]$') + number + Not(W('H'))))('value').add_action(join)
coupling = ((R('^\d?J([HCNPFD\d,]*|cis|trans)$') + Optional(R('^[\-–−‒]$') + R('^[HCNPF\d]$')) + Optional('=')).hide() + coupling_value + Optional(W('Hz')('units')) + ZeroOrMore(R('^[,;&]$').hide() + coupling_value + W('Hz')('units')))('coupling')

number = (R('^\d+(\.\d+)?[HCNPF]\.?$') | (R('^\d+(\.\d+)?$') + R('^[HCNPF]\.?$')))('number').add_action(merge)

assignment_options = (OneOrMore(R('([CNHOPS\-–−‒=]+\d*[A-Za-z]?′*)+') | chemical_name | R('^(C?quat\.?|Ac|Ar|Ph|linker|bridge)$')) + Optional(W('×') + R('^\d+$')))('assignment').add_action(join)
assignment = Optional(R('^\d{1,2}$')('number') + Optional(W('×')).hide()) + (assignment_options + ZeroOrMore(T('CC').hide() + assignment_options))

note = (W('overlapped') | (W('×') + R('^\d+$')))('note').add_action(join)

peak_meta_options = multiplicity | coupling | number | assignment | note
peak_meta = W('(').hide() + peak_meta_options + ZeroOrMore(ZeroOrMore(delim) + peak_meta_options) + Optional(delim) + W(')').hide()

delta = (R('^[δd][HCNPF]?$') + Optional(equals)).hide()
ppm = Optional(R('^[(\[]$')) + Optional(I('in')) + I('ppm') + Optional(R('^[)\]]$'))

spectrum_meta = Optional(W('(').hide()) + (frequency | solvent | delta | temperature) + ZeroOrMore(Optional(delim) + (frequency | solvent | I('ppm') | delta | temperature)) + Optional(temperature) + Optional(W(')').hide())

prelude_options = spectrum_meta | delta | delim | ppm.hide() | equals.hide()
prelude = ((nucleus + Optional(R('^[\-–−‒]$')).hide() + nmr_name | nmr_name_with_nucleus) + ZeroOrMore(prelude_options)) | (R('^δ[HC]?$')('nucleus') + spectrum_meta + ZeroOrMore(prelude_options))

peak = Optional(delta) + (shift + Not(R('^M?Hz$')) + Optional(ppm).hide() + Optional(peak_meta))('peak').add_action(fix_nmr_peak_whitespace_error)
peaks = (peak + ZeroOrMore(ZeroOrMore(delim | W('and')).hide() + peak))('peaks')

nmr = (prelude + peaks)('nmr')


class NmrParser(BaseParser):
    """"""

    root = nmr

    def __init__(self):
        pass

    def interpret(self, result, start, end):

        c = Compound()

        n = NmrSpectrum(
            nucleus=first(result.xpath('./nucleus/text()')),
            solvent=first(result.xpath('./solvent/text()')),
            frequency=first(result.xpath('./frequency/value/text()')),
            frequency_units=first(result.xpath('./frequency/units/text()')),
            temperature=first(result.xpath('./temperature/value/text()')),
            temperature_units=first(result.xpath('./temperature/units/text()'))
        )

        for peak_result in result.xpath('./peaks/peak'):
            nmr_peak = NmrPeak(
                shift=first(peak_result.xpath('./shift/text()')),
                multiplicity=first(peak_result.xpath('./multiplicity/text()')),
                coupling=first(peak_result.xpath('./coupling/value/text()')),
                coupling_units=first(peak_result.xpath('./coupling/units/text()')),
                number=first(peak_result.xpath('./number/text()')),
                assignment=first(peak_result.xpath('./assignment/text()'))
            )
            n.peaks.append(nmr_peak)

        c.nmr_spectra.append(n)
        yield c

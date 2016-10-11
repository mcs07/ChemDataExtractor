# -*- coding: utf-8 -*-
"""
chemdataextractor.parse.context
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Parser for sentences that provide contextual information, such as apparatus, solvent, and temperature.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import re

from .common import optdelim, hyphen, slash
from ..utils import first
from ..parse.base import BaseParser
from ..model import Compound, QuantumYield, NmrSpectrum, UvvisSpectrum, IrSpectrum, MeltingPoint, FluorescenceLifetime
from .actions import join, merge, fix_whitespace
from .cem import chemical_name
from .elements import I, T, R, W, ZeroOrMore, Optional, Group, OneOrMore, Any, Not

log = logging.getLogger(__name__)

dt = T('DT')

quantum_yield = (W('PLQY') | Optional(I('fluorescence') | I('luminescence') | I('photoluminescence') | I('emission')) + I('quantum') + I('yield') + Optional(optdelim + W('PLQY') + optdelim))('quantum_yield').add_action(join)
nmr = (W('NMR') | (I('nuclear') + I('magnetic') + I('resonance')) | W('1H') | W('13C'))('nmr').add_action(join)
uvvis = (I('UV') + (hyphen | slash) + R('^vis(ible)?$', re.I) + Optional(R('^abs(or[bp]tion)?$')))('uvvis').add_action(join).add_action(fix_whitespace)
ir = (R('^(FT-?)?IR|FT-?IS$'))('ir').add_action(join)
mp = (I('melting') + I('points'))('melting_point').add_action(join)
pp = (I('photophysical') + (I('measurements') | I('properties')))('photophysical_properties').add_action(join)
measurement = Group(quantum_yield | nmr | uvvis | ir | mp | pp)('measurement')

result_noun = I('data') | I('results') | I('experiments') | I('spectra')

verb = W('measured') | W('recorded') | W('collected') | W('taken') | W('acquired') | W('obtained') | W('run') | (W('carried') + W('out') | W('performed')) # | T('VBN')

apparatus_type = R('^\d{2,}$') + W('MHz')
brands = I('HORIBA') + I('Jobin') + I('Yvon') | I('Hitachi') | I('Bruker') | I('Cary') | I('Jeol') | I('PerkinElmer') | I('Agilent') | I('Shimadzu') | I('Varian')
models = I('FluoroMax-4') | I('F-7000') | I('AVANCE') | I('Digital') | R('\d\d\d+') | I('UV–vis-NIR') | I('Mercury') | I('Avatar') | I('thermonicolet') | I('pulsed') | I('Fourier') | I('transform')
instrument = I('spectrofluorimeter') | I('spectrophotometer') | Optional(I('fluorescence')) + I('spectrometer') | Optional(I('nmr')) + I('workstation') | W('NMR') | I('instrument') | I('spectrometer')
apparatus = (ZeroOrMore(T('JJ')) + Optional(apparatus_type) + OneOrMore(T('NNP') | T('NN') | brands) + ZeroOrMore(T('NNP') | T('NN') | T('HYPH') | T('CD') | brands | models) + Optional(instrument))('apparatus').add_action(join).add_action(fix_whitespace)
apparatus_blacklist = R('^(following|usual|equation|standard|accepted|method)$', re.I)
apparatus_phrase = (W('with') | W('using') | W('on')).hide() + Optional(dt).hide() + Not(apparatus_blacklist) + apparatus

temp_value = (Optional(R('^[~∼\<\>]$')) + Optional(R('^[\-–−]$')) + R('^[\+\-–−]?\d+(\.\d+)?$') + Optional(W('±') + R('^\d+(\.\d+)?$')))('value').add_action(merge)
temp_range = (Optional(R('^[\-–−]$')) + (R('^[\+\-–−]?\d+(\.\d+)?[\-–−]\d+(\.\d+)?$') | (R('^[\+\-–−]?\d+(\.\d+)?$') + R('^[\-–−]$') + R('^[\+\-–−]?\d+(\.\d+)?$'))))('value').add_action(merge)
temp_word = (I('room') + R('^temp(erature)?$') | R('^r\.?t\.?$', re.I))('value').add_action(join)
temp = (temp_range | temp_value)('value')
temp_units = (W('°') + R('[CFK]') | W('K'))('units').add_action(merge)
temperature_phrase = Optional(I('at').hide()) + Group((temp + temp_units) | temp_word)('temperature')

solvent_phrase = (I('in').hide() + chemical_name)('solvent')

standard = (ZeroOrMore(T('JJ')) + OneOrMore(T('NNP') | T('NN') | T('HYPH') | T('CD') | T('B-CM') | T('I-CM')))('standard').add_action(join).add_action(fix_whitespace)
standard_phrase = (W('with') | W('using')).hide() + Optional(dt).hide() + standard + (ZeroOrMore(W('as') | dt) + Optional(T('JJ')) + I('standard')).hide()

context_phrase = Group(measurement + optdelim + Optional(result_noun).hide() + Optional(T('VBD')).hide() + ZeroOrMore(Not(verb) + Any()).hide() + verb.hide() + OneOrMore(standard_phrase | apparatus_phrase | temperature_phrase | solvent_phrase | Any().hide()))('context_phrase')

# TODO: Multiple measurements, multiple apparatus.
# TODO: 'respectively' phrase


class ContextParser(BaseParser):
    """"""
    root = context_phrase

    def __init__(self):
        pass

    def interpret(self, result, start, end):
        c = Compound()
        context = {
            'apparatus': first(result.xpath('./apparatus/text()')),
            'solvent': first(result.xpath('./solvent/name/text()'))
        }
        measurement = result.xpath('./measurement/*[1]')[0]

        if not measurement.tag == 'melting_point':
            context['temperature'] = first(result.xpath('./temperature/value/text()'))
            context['temperature_units'] = first(result.xpath('./temperature/units/text()'))

        if measurement.tag == 'photophysical_properties':
            c.quantum_yields.append(QuantumYield(**context))
            c.fluorescence_lifetimes.append(FluorescenceLifetime(**context))
            c.uvvis_spectra.append(UvvisSpectrum(**context))
        if measurement.tag == 'quantum_yield':
            c.quantum_yields.append(QuantumYield(**context))
        if measurement.tag == 'melting_point':
            c.melting_points.append(MeltingPoint(**context))
        if measurement.tag == 'nmr':
            c.nmr_spectra.append(NmrSpectrum(**context))
        if measurement.tag == 'uvvis':
            c.uvvis_spectra.append(UvvisSpectrum(**context))
        if measurement.tag == 'ir':
            c.ir_spectra.append(IrSpectrum(**context))
        yield c

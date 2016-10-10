# -*- coding: utf-8 -*-
"""
chemdataextractor.parse.uvvis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

UV-vis text parser.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import re

from ..model import Compound, UvvisSpectrum, UvvisPeak
from .common import hyphen
from .base import BaseParser
from ..utils import first
from .actions import strip_stop
from .elements import W, I, T, R, Optional, ZeroOrMore, OneOrMore
from .cem import chemical_name


log = logging.getLogger(__name__)


delim = R('^[;:,\./]$').hide()

solvent = chemical_name('solvent')
units = Optional(W('/')).hide() + W('nm')('units')
value = R('^\d{3,4}(\.\d+)?\.?$')('value').add_action(strip_stop)
shape = R('^(m|medium|w|weak|s|strong|n|narrow|b|broad|sh|sharp)$', re.I)('shape') + Optional(I('peak')).hide()
peak_meta_options = shape
peak_meta = W('(').hide() + peak_meta_options + ZeroOrMore(delim + peak_meta_options) + W(')').hide()
insolvent = T('IN') + solvent
uvvis_abs_title = (
    I('absorption') + R('max(ima)?') |
    R('^λ(a(bs)?|max)$') + ZeroOrMore(R('^a?max$', re.I) | R('abs(or[bp]tion)?', re.I) | I('a') | W(',')) |
    W('λ$') + OneOrMore(R('^a?max$', re.I) | R('abs(or[bp]tion)?', re.I) | I('a') | W(',')) |
    R('uv([-/]?vis)?', re.I) |
    I('UV') + hyphen + R('^vis(ible)?$', re.I) + Optional(R('^abs(or[bp]tion)?$'))
)
prelude = uvvis_abs_title.hide() + Optional(delim) + Optional(I('data')) + Optional(insolvent) + Optional(delim) + Optional(units)
peak = (value + Optional(peak_meta))('peak')
peaks = (peak + ZeroOrMore(ZeroOrMore(delim | W('and')).hide() + peak))('peaks')
uvvis = (prelude + peaks + Optional(delim) + Optional(units) + Optional(insolvent))('uvvis')


class UvvisParser(BaseParser):
    """"""
    root = uvvis

    def interpret(self, result, start, end):
        c = Compound()
        u = UvvisSpectrum(
            solvent=first(result.xpath('./solvent/text()'))
        )
        units = first(result.xpath('./units/text()'))
        for peak_result in result.xpath('./peaks/peak'):
            uvvis_peak = UvvisPeak(
                value=first(peak_result.xpath('./value/text()')),
                units=units,
                shape=first(peak_result.xpath('./shape/text()'))
            )
            u.peaks.append(uvvis_peak)
        c.uvvis_spectra.append(u)
        yield c

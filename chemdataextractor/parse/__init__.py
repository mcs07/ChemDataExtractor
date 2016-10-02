# -*- coding: utf-8 -*-
"""
chemdataextractor.parse
~~~~~~~~~~~~~~~~~~~~~~~

Parse text using rule-based grammars.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .actions import join, merge, strip_stop, fix_whitespace
from .elements import W, I, R, T, H
from .elements import Any, Word, Tag, IWord, Regex, Start, End, Hide, Not
from .elements import And, Or, First, ZeroOrMore, OneOrMore, Optional, Group, SkipTo

from .cem import CompoundParser, ChemicalLabelParser, CompoundHeadingParser
from .context import ContextParser
from .ir import IrParser
from .mp import MpParser
from .nmr import NmrParser
from .table import CompoundHeadingParser, SolventHeadingParser, UvvisAbsDisallowedHeadingParser, SolventInHeadingParser
from .table import TempInHeadingParser, SolventCellParser, CompoundCellParser, UvvisEmiHeadingParser
from .table import UvvisAbsHeadingParser, ExtinctionHeadingParser, IrHeadingParser, IrCellParser
from .table import QuantumYieldHeadingParser, QuantumYieldCellParser, UvvisEmiCellParser, UvvisAbsCellParser
from .table import ExtinctionCellParser, UvvisAbsEmiQuantumYieldHeadingParser, UvvisAbsEmiQuantumYieldCellParser
from .table import UvvisEmiQuantumYieldHeadingParser, UvvisEmiQuantumYieldCellParser, FluorescenceLifetimeHeadingParser
from .table import FluorescenceLifetimeCellParser, MeltingPointHeadingParser, MeltingPointCellParser
from .table import ElectrochemicalPotentialHeadingParser, ElectrochemicalPotentialCellParser, CaptionContextParser
from .uvvis import UvvisParser

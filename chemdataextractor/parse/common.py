# -*- coding: utf-8 -*-
"""
chemdataextractor.parse.common
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Common parser elements.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import re

from .elements import W, T, R, Optional


log = logging.getLogger(__name__)

# Part-of-Speech Tags
nn = T('NN')
iin = T('IN')  # in is a reserved keyword in python
nnp = T('NNP')
dt = T('DT')
nns = T('NNS')
jj = T('JJ')
comma = T(',')
stop = T('.')
cd = T('CD')
rb = T('RB')
vbd = T('VBD')
vb = T('VB')
cc = T('CC')
vbn = T('VBN')
vbz = T('VBZ')
prp = T('PRP')
vbg = T('VBG')
to = T('TO')
vbp = T('VBP')
hyph = T('HYPH')
md = T('MD')
pos = T('POS')
prpd = T('PRP$')
dollar = T('$')
startquote = T('``')
endquote = T('\'\'')
colon = T(':')
wdt = T('WDT')
jjr = T('JJR')
rp = T('RP')
nnps = T('NNPS')
wp = T('WP')
wrb = T('WRB')
rbr = T('RBR')
jjs = T('JJS')
rrb = T('-RRB-')
lrb = T('-LRB-')
ex = T('EX')
rbs = T('RBS')
pdt = T('PDT')
sym = T('SYM')
fw = T('FW')
wpd = T('WP$')
uh = T('UH')
ls = T('LS')
nfp = T('NFP')
afx = T('AFX')

# Chemical entities
bcm = T('B-CM')
icm = T('I-CM')

# Roman numerals 1-9
roman_numeral = R('^(I|II|III|IV|V|VI|VII|VIII|IX|XI|XII|XIII|XIV)$', re.I)

# Punctuation delimiter that is hidden
delim = R('^[,:;\.\[\]\(\)\{\}/]$').hide()
optdelim = Optional(delim)

# CEM: optdelim = Optional(R('^[;:,\.\(\)]$').hide())
# cont: delim = Optional(R('^[;:,\.\(\)]$').hide())
# MP: delim = R('^[:;\.]$')
# IR: delim = R('^[;:,\./]$').hide()
# NMR: delim = R('^[;:,\.]$').hide()
# table: delims = ZeroOrMore(R('^[,;\[\]\(\)\{\}/]$'))

# Brackets. (Note that these could be tagged other than LRB/RRB e.g. as part of CM entity)
lbrct = W('(').hide()
rbrct = W(')').hide()

# All hyphen and minus characters. Probably more robust than the hyph POS tag.
hyphen = R('^[\-‐‑⁃‒–—―−－⁻]$')

# All quote and apostrophe characters
quote = R('^[\'’՚Ꞌꞌ＇‘’‚‛"“”„‟`´’‘]$')

slash = W('/')

# Symbols
degree = W('°')
times = W('×')
lmbda = W('λ')
epsilon = W('ε')
equals = W('=')

# -*- coding: utf-8 -*-
"""
chemdataextractor.parse.cem
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Chemical entity mention parser elements.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import re
from lxml import etree

from ..model import Compound
from .actions import join, fix_whitespace
from .common import roman_numeral, cc, nnp, hyph, nns, nn, cd, ls, optdelim, bcm, icm, rbrct, lbrct, sym, jj, hyphen, quote, \
    dt
from .base import BaseParser
from .elements import I, R, W, T, ZeroOrMore, Optional, Not, Group, End, Start, OneOrMore, Any

log = logging.getLogger(__name__)


alphanumeric = R('^(d-)?(\d{1,2}[A-Za-z]{1,2}[′″‴‶‷⁗]?)(-d)?$')

numeric = R('^\d{1,3}$')

letter_number = R('^(H\d)?[LSNM]{1,2}\d\d?$')

# Blacklist to truncate chemical mentions where tags continue on incorrectly
cm_blacklist = (W('in') | W(':') + R('^m\.?p\.?$', re.I) | W(':') + Any() + R('^N\.?M\.?R\.?\(?$', re.I))

exclude_prefix = Start() + (lbrct + roman_numeral + rbrct + Not(hyphen) | (R('^\d{1,3}(\.\d{1,3}(\.\d{1,3}(\.\d{1,3})?)?)?$') + Not(hyphen)) | (I('stage') | I('step') | I('section') | I('part')) + (alphanumeric | numeric | roman_numeral | R('^[A-Z]$')))

# Tagged chemical mentions - One B-CM tag followed by zero or more I-CM tags.
cm = (exclude_prefix.hide() + OneOrMore(Not(cm_blacklist) + icm)) | (bcm + ZeroOrMore(Not(cm_blacklist) + icm))

comma = (W(',') | T(',')).hide()
colon = (W(':') | T(':')).hide()

# Prefixes to include in the name
include_prefix = Not(bcm) + R('^(deuterated|triflated|butylated|brominated|acetylated|twisted)$', re.I)

label_type = (Optional(I('reference') | I('comparative')) + R('^(compound|ligand|chemical|dye|derivative|complex|example|intermediate|product|formulae?|preparation)s?$', re.I))('role').add_action(join) + Optional(colon).hide()

synthesis_of = ((I('synthesis') | I('preparation') | I('production') | I('data')) + (I('of') | I('for')))('role').add_action(join)

to_give = (I('to') + (I('give') | I('yield') | I('afford')) | I('afforded') | I('affording') | I('yielded'))('role').add_action(join)

label_blacklist = R('^(31P|[12]H|[23]D|15N|14C|[4567890]\d+)$')

prefixed_label = R('^(cis|trans)-((d-)?(\d{1,2}[A-Za-z]{0,2}[′″‴‶‷⁗]?)(-d)?|[LS]\d\d?)$')

#: Chemical label. Very permissive - must be used in context to avoid false positives.
strict_chemical_label = Not(label_blacklist) + (alphanumeric | roman_numeral | letter_number | prefixed_label)('label')

lenient_chemical_label = numeric('label') | R('^([A-Z]\d{1,3})$')('label') | strict_chemical_label

chemical_label = ((label_type + lenient_chemical_label + ZeroOrMore((T('CC') | comma) + lenient_chemical_label)) | (Optional(label_type.hide()) + strict_chemical_label + ZeroOrMore((T('CC') | comma) + strict_chemical_label)))

#: Chemical label with a label type before
chemical_label_phrase1 = (Optional(synthesis_of) + label_type + lenient_chemical_label + ZeroOrMore((T('CC') | comma) + lenient_chemical_label))
#: Chemical label with synthesis of before
chemical_label_phrase2 = (synthesis_of + Optional(label_type) + lenient_chemical_label + ZeroOrMore((T('CC') | comma) + lenient_chemical_label))
# Chemical label with to give/afforded etc. before, and some restriction after.
chemical_label_phrase3 = (to_give + Optional(dt) + Optional(label_type) + lenient_chemical_label + Optional(lbrct + OneOrMore(Not(rbrct) + Any()) + rbrct).hide() + (End() | I('as') | colon | comma).hide())

chemical_label_phrase = Group(chemical_label_phrase1 | chemical_label_phrase2 | chemical_label_phrase3)('chemical_label_phrase')
# TODO: "Compound 3a-c" - in parser expand out into multiple compounds

element_name = R('^(actinium|aluminium|aluminum|americium|antimony|argon|arsenic|astatine|barium|berkelium|beryllium|bismuth|bohrium|boron|bromine|cadmium|caesium|calcium|californium|carbon|cerium|cesium|chlorine|chromium|cobalt|copernicium|copper|curium|darmstadtium|dubnium|dysprosium|einsteinium|erbium|europium|fermium|flerovium|fluorine|francium|gadolinium|gallium|germanium|hafnium|hassium|helium|holmium|hydrargyrum|hydrogen|indium|iodine|iridium|iron|kalium|krypton|lanthanum|laIrencium|lithium|livermorium|lutetium|magnesium|manganese|meitnerium|mendelevium|mercury|molybdenum|natrium|neodymium|neon|neptunium|nickel|niobium|nitrogen|nobelium|osmium|oxygen|palladium|phosphorus|platinum|plumbum|plutonium|polonium|potassium|praseodymium|promethium|protactinium|radium|radon|rhenium|rhodium|roentgenium|rubidium|ruthenium|rutherfordium|samarium|scandium|seaborgium|selenium|silicon|silver|sodium|stannum|stibium|strontium|sulfur|tantalum|technetium|tellurium|terbium|thallium|thorium|thulium|tin|titanium|tungsten|ununoctium|ununpentium|ununseptium|ununtrium|uranium|vanadium|Iolfram|xenon|ytterbium|yttrium|zinc|zirconium)$', re.I)

#: Mostly unambiguous element symbols
element_symbol = R('^(Ag|Au|Br|Cd|Cl|Cu|Fe|Gd|Ge|Hg|Mg|Pb|Pd|Pt|Ru|Sb|Si|Sn|Ti|Xe|Zn|Zr)$')

#: Registry number patterns
registry_number = R('^BRN-?\d+$') | R('^CHEMBL-?\d+$') | R('^GSK-?\d{3-7}$') | R('^\[?(([1-9]\d{2,7})|([5-9]\d))-\d\d-\d\]?$')

#: Amino acid abbreviations. His removed, too ambiguous
amino_acid = R('^((Ala|Arg|Asn|Asp|Cys|Glu|Gln|Gly|Ile|Leu|Lys|Met|Phe|Pro|Ser|Thr|Trp|Tyr|Val)-?)+$')

amino_acid_name = (
    R('^(histidine|isoleucine|leucine|lysine|methionine|phenylalanine|threonine|tryptophan|valine|selenocysteine|serine|tyrosine|alanine|arginine|asparagine|cysteine|glutamine|glycine|proline)$', re.I) |
    I('aspartic') + I('acid') | I('glutamic') + I('acid')
)

#: Chemical formula patterns
formula = (
    R('^C\(?\d{1,3}\)?(([HNOP]|Cl)\(?\d\d?\)?)+(\(?\d?[\+\-]\d?\)?)?$') |
    R('^((\(?\d{2,3}\)?)?(Fe|Ti|Mg|Ru|Cd|Se)\(?(\d\d?|[IV]+)?\)?((O|Hg)\(?\d?\d?\)?)?)+(\(?\d?[\+\-]\d?\)?)?$') |
    R('(NaOH|CaCl\d?\d?|EtOH|EtAc|MeOH|CF\d|C\d?\d?H\d\d?)+$') |
    R('(NO\d|BH4|Ca\(2\+\)|Ti\(0\)2|\(CH3\)2CHOH|\(CH3\)2CO|\(CH3\)2NCOH|C2H5CN|CH2ClCH2Cl|CH3C6H5|CH3CN|CH3CO2H|CH3COCH3|CH3COOH|CH3NHCOH|CH3Ph|CH3SOCH3|Cl2CH2|ClCH2CH2Cl)') |
    R('^(\(CD3\)2CO|\(CDCl2\)2|C6D6|C2D5CN|CD2Cl2|CD3CN|CD3COCD3|CD3OD|CD3SOCD3|CDCl3|CH3OD|D2O|EtOD|MeOD)$') |
    R('^[\[\{\(].*(NH\d|H2O|NO\d|C\d?H\d|C–H|NBu4|CF3|CD3|CO2|[bp]i?py|\(CO\)|\d,\d[\'′]?-|BF4|PF6|Cl\d|Fe\d|Ph\d).*[\]\}\)]$') |
    R('^[\[\{\(]{1,2}(Ru|Ph|Py|Cu|Ir|Pt|Et\d).*[\]\}\)]$') |
    R('^(GABA|NO|\(\d\)H|KCl)$')
)

solvent_formula = (
    W('CCl4') | W('(CH3)2CHOH') | W('(CH3)2CO') | W('(CH3)2NCOH') | W('C2H4Cl2') | W('C2H5CN') | W('C2H5OH') |
    W('C5H5N') | W('C6H12') | W('C6H14') | W('C6H5CH3') | W('C6H5Cl') | W('C6H6') | W('C7H8') | W('CH2Cl2') |
    W('CH2ClCH2Cl') | W('CH3C6H5') | W('CH3Cl') | W('CH3CN') | W('CH3CO2H') | W('CH3COCH3') | W('CH3COOH') |
    W('CH3NHCOH') | W('CH3NO2') | W('CH3OH') | W('CH3Ph') | W('CH3SOCH3') | W('CHCl2') | W('CHCl3') | W('Cl2CH2') |
    W('ClCH2CH2Cl')
)

# Over-tokenized variants first, useful for matching in tables with fine tokenizer
nmr_solvent = (
    I('THF') + W('-') + I('d8') | I('d8') + W('-') + I('THF') | I('acetone') + W('-') + I('d6') |
    I('d6') + W('-') + I('acetone') | I('chloroform') + W('-') + I('d') | I('d') + W('-') + I('chloroform') |
    I('methanol') + W('-') + I('d4') | I('d4') + W('-') + I('methanol') | I('pyridine') + W('-') + I('d5') |
    I('d5') + W('-') + I('pyridine') | I('DMSO') + W('-') + I('d6') | I('d6') + W('-') + I('DMSO') |
    I('dimethylsulfoxide') + W('-') + I('d6') | I('d6') + W('-') + I('dimethylsulfoxide') |
    W('MeOH') + W('-') + I('d4') | I('d4') + W('-') + W('MeOH') | I('benzene-d6') + W('-') + I('d6') |
    I('d6') + W('-') + I('benzene') | I('d2') + W('-') + I('tetrachloroethane') |
    I('tetrachloroethane') + W('-') + I('d2') |

    I('(CD3)2CO') | I('(CDCl2)2') | I('C6D6') | I('C2D5CN') | I('CD2Cl2') | I('CD3CN') | I('CD3COCD3') | I('CD3OD') |
    I('CD3SOCD3') | I('CDCl3') | I('CH3OD') | I('D2O') | W('EtOD') | W('MeOD') | I('THF-d8') | I('d8-THF') |
    I('acetone-d6') | I('d6-acetone') | I('chloroform-d') | I('d-chloroform') | I('methanol-d4') | I('d4-methanol') |
    I('pyridine-d5') | I('d5-pyridine') | I('DMSO-d6') | I('d6-DMSO') | I('dimethylsulfoxide-d6') | W('C7D8') |
    I('d6-dimethylsulfoxide') | W('MeOH-d4') | W('d4-MeOH') | I('DMSO') | I('benzene-d6') | I('d6-benzene') |
    I('1,1,2,2-tetrachloroethane-d2') | I('tetrachloroethane-d2') | I('d2-tetrachloroethane')

)

#: Solvent names.
other_solvent = (
    I('1-butanol') | I('1-butylimidazole') | I('1-cyclohexanol') | I('1-decanol') | I('1-heptanol') | I('1-hexanol') |
    I('1-methylethyl') + I('acetate') | I('1-octanol') | I('1-pentanol') | I('1-phenylethanol') | I('1-propanol') |
    I('1-undecanol') | I('1,1,1-trifluoroethanol') | I('1,1,1,3,3,3-hexafluoro-2-propanol') |
    I('1,1,1,3,3,3-hexafluoropropan-2-ol') | I('1,1,2-trichloroethane') | I('1,2-c2h4cl2') | I('1,2-dichloroethane') |
    I('1,2-dimethoxyethane') | I('1,2-dimethylbenzene') | I('1,2-ethanediol') | I('1,2,4-trichlorobenzene') |
    I('1,4-dimethylbenzene') | I('1,4-dioxane') | I('2-(n-morpholino)ethanesulfonic') + I('acid') | I('2-butanol') |
    I('2-butanone') | I('2-me-thf') | I('2-methf') | I('2-methoxy-2-methylpropane') |
    I('2-methyl') + I('tetrahydrofuran') | I('2-methylpentane') | I('2-methylpropan-1-ol') | I('2-methylpropan-2-ol') |
    I('2-methyltetrahydrofuran') | I('2-proh') | I('2-propanol') | I('2-propyl') + I('acetate') | I('2-pyrrolidone') |
    I('2,2,2-trifluoroethanol') | I('2,2,4-trimethylpentane') | I('2Me-THF') | I('2MeTHF') | I('3-methyl-pentane') |
    I('4-methyl-1,3-dioxolan-2-one') | I('acetic') + I('acid') | I('aceto-nitrile') | I('acetone') | I('acetonitrile') |
    I('acetononitrile') | I('AcOEt') | I('AcOH') | I('AgNO3') | I('aniline') | I('anisole') | I('benzene') |
    I('benzonitrile') | I('benzyl') + I('alcohol') | I('bromoform') | I('Bu2O') | I('Bu4NBr') | I('Bu4NClO4') |
    I('Bu4NPF6') | I('BuCN') | I('BuOH') | I('butan-1-ol') | I('butan-2-ol') | I('butan-2-one') | I('butane') |
    I('butanol') | I('butanone') | I('butene') | I('butyl') + I('acetate') | I('butyl') + I('acetonitrile') |
    I('butyl') + I('alcohol') | I('butyl') + I('amine') | I('butyl') + I('chloride') | I('butyl') + I('imidazole') |
    I('butyronitrile') | I('c-hexane') | I('carbon') + I('disulfide') | I('carbon') + I('tetrachloride') |
    I('chlorobenzene') | I('chloroform') | I('chloromethane') | I('chlorotoluene') | I('CHX') | I('cumene') |
    I('cyclohexane') | I('cyclohexanol') | I('cyclopentyl') + I('methyl') + I('ether') | I('DCE') | I('DCM') | I('decalin') |
    I('decan-1-ol') | I('decane') | I('decanol') | I('DEE') | I('di-isopropyl') + I('ether') |
    I('di-n-butyl') + I('ether') | I('di-n-hexyl') + I('ether') | I('dibromoethane') | I('dibutoxymethane') |
    I('dibutyl') + I('ether') | I('dichloro-methane') | I('dichlorobenzene') | I('dichloroethane') |
    I('dichloromethane') | I('diethoxymethane') | I('diethyl') + I('carbonate') | I('diethyl') + I('ether') |
    I('diethylamine') | I('diethylether') | I('diglyme') | I('dihexyl') + I('ether') | I('diiodomethane') |
    I('diisopropyl') + I('ether') | I('diisopropylamine') | I('dimethoxyethane') | I('dimethoxymethane') |
    I('dimethyl') + I('acetamide') | I('dimethyl') + I('acetimide') | I('dimethyl') + I('benzene') |
    I('dimethyl') + I('carbonate') | I('dimethyl') + I('ether') | I('dimethyl') + I('formamide') |
    I('dimethyl') + I('sulfoxide') | I('dimethylacetamide') | I('dimethylbenzene') | I('dimethylformamide') |
    I('dimethylformanide') | I('dimethylsulfoxide') | I('dioctyl') + I('sodium') + I('sulfosuccinate') | I('dioxane') |
    I('dioxolane') | I('dipropyl') + I('ether') | I('DMAc') | I('DMF') | I('DMSO') | I('Et2O') | I('EtAc') |
    I('EtAcO') | I('EtCN') | I('ethane') + I('diol') | I('ethane-1,2-diol') | I('ethanol') |
    I('ethyl') + I('(S)-2-hydroxypropanoate') | I('ethyl') + I('acetate') | I('ethyl') + I('benzoate') |
    I('ethyl') + I('formate') | I('ethyl') + I('lactate') | I('ethyl') + I('propionate') | I('ethylacetamide') |
    I('ethylacetate') | I('ethylene') + I('carbonate') | I('ethylene') + I('glycol') | I('ethyleneglycol') |
    I('ethylhexan-1-ol') | I('EtOAc') | I('EtOH') | I('eucalyptol') | I('F3-ethanol') | I('F3-EtOH') | I('formamide') |
    I('formic') + I('acid') | I('glacial') + I('acetic') + I('acid') | I('glycerol') | I('H2O') | I('H2O2') |
    I('H2SO4') | I('HBF4') | I('HCl') | I('HClO4') | I('HCO2H') | I('HCONH2') | I('heptan-1-ol') |
    I('heptane') | I('heptanol') | I('heptene') | I('HEX') | I('hexadecylamine') | I('hexafluoroisopropanol') |
    I('hexafluoropropanol') | I('hexan-1-ol') | I('hexane') | I('hexanes') | I('hexanol') | I('hexene') |
    I('hexyl') + I('ether') | I('HFIP') | I('HFP') | I('HNO3') | I('hydrochloric') + I('acid') |
    I('hydrogen') + I('peroxide') | I('iodobenzene') | I('isohexane') | I('isooctane') | I('isopropanol') |
    I('isopropyl') + I('benzene') | I('KBr') | I('LiCl') | I('ligroine') | I('limonene') | I('Me-THF') | I('Me2CO') |
    I('MeCN') | I('MeCO2Et') | I('MeNO2') | I('MeOH') | I('mesitylene') | I('methanamide') | I('methanol') |
    I('MeTHF') | I('methoxybenzene') | I('methoxyethylamine') | I('methyl') + I('acetamide') |
    I('methyl') + I('acetoacetate') | I('methyl') + I('benzene') | I('methyl') + I('butane') |
    I('methyl') + I('cyclohexane') | I('methyl') + I('ethyl') + I('ketone') | I('methyl') + I('formamide') |
    I('methyl') + I('formate') | I('methyl') + I('isobutyl') + I('ketone') | I('methyl') + I('laurate') |
    I('methyl') + I('methanoate') | I('methyl') + I('naphthalene') | I('methyl') + I('pentane') |
    I('methyl') + I('propan-1-ol') | I('methyl') + I('propan-2-ol') | I('methyl') + I('propionate') |
    I('methyl') + I('pyrrolidin-2-one') | I('methyl') + I('pyrrolidine') | I('methyl') + I('pyrrolidinone') |
    I('methyl') + I('t-butyl') + I('ether') | I('methyl') + I('tetrahydrofuran') | I('methyl-2-pyrrolidone') |
    I('methylbenzene') | I('methylcyclohexane') | I('methylene') + I('chloride') | I('methylformamide') |
    I('methyltetrahydrofuran') | I('MIBK') | I('morpholine') | I('mTHF') | I('n-butanol') |
    I('n-butyl') + I('acetate') | I('n-decane') | I('n-heptane') | I('n-HEX') | I('n-hexane') | I('n-methylformamide') |
    I('n-methylpyrrolidone') | I('n-nonane') | I('n-octanol') | I('n-pentane') | I('n-propanol') |
    I('n,n-dimethylacetamide') | I('n,n-dimethylformamide') | I('n,n-DMF') | I('Na2SO4') | I('NaCl') | I('NaClO4') |
    I('NaHCO3') | I('NaOH') | I('nBu4NBF4') | I('nitric') + I('acid') | I('nitrobenzene') | I('nitromethane') |
    I('nonane') | I('nujol') | I('o-dichlorobenzene') | I('o-xylene') | I('octan-1-ol') | I('octane') | I('octanol') |
    I('octene') | I('ODCB') | I('p-xylene') | I('pentan-1-ol') | I('pentane') | I('pentanol') | I('pentanone') |
    I('pentene') | I('PeOH') | I('perchloric') + I('acid') | I('PhCH3') | I('PhCl') | I('PhCN') | I('phenoxyethanol') |
    I('phenyl') + I('acetylene') | I('Phenyl') + I('ethanol') | I('phenylamine') | I('phenylethanolamine') |
    I('phenylmethanol') | I('PhMe') | I('phosphate') | I('phosphate') + I('buffered') + I('saline') | I('pinane') |
    I('piperidine') | I('polytetrafluoroethylene') | I('potassium') + I('bromide') |
    I('potassium') + I('phosphate') + I('buffer') | I('PrCN') | I('PrOH') | I('propan-1-ol') | I('propan-2-ol') |
    I('propane') | I('propane-1,2-diol') | I('propane-1,2,3-triol') | I('propanol') | I('propene') |
    I('propionic') + I('acid') | I('propionitrile') | I('propyl') + I('acetate') | I('propyl') + I('amine') |
    I('propylene') + I('carbonate') | I('propylene') + I('glycol') | I('pyridine') | I('pyrrolidone') | I('quinoline') |
    I('silver') + I('nitrate') | I('SNO2') | I('sodium') + I('chloride') | I('sodium') + I('hydroxide') |
    I('sodium') + I('perchlorate') | I('sulfuric') + I('acid') | I('t-butanol') | I('TBABF4') | I('TBAF') | I('TBAH') |
    I('TBAOH') | I('TBAP') | I('TBAPF6') | I('TEAP') | I('TEOA') | I('tert-butanol') | I('tert-butyl') + I('alcohol') |
    I('tetrabutylammonium') + I('hexafluorophosphate') | I('tetrabutylammonium') + I('hydroxide') |
    I('tetrachloroethane') | I('tetrachloroethylene') | I('tetrachloromethane') | I('tetrafluoroethylene') |
    I('tetrahydrofuran') | I('tetralin') | I('tetramethylsilane') | I('tetramethylurea') | I('tetrapiperidine') |
    I('TFA') | I('TFE') | I('THF') | I('tin') + I('dioxide') | I('titanium') + I('dioxide') | I('toluene') |
    I('tri-n-butyl') + I('phosphate') | I('triacetate') | I('triacetin') | I('tribromomethane') |
    I('tributyl') + I('phosphate') | I('trichlorobenzene') | I('trichloroethene') | I('trichloromethane') |
    I('triethyl') + I('amine') | I('triethyl') + I('phosphate') | I('triethylamine') |
    I('trifluoroacetic') + I('acid') | I('trifluoroethanol') | I('trimethyl') + I('benzene') |
    I('trimethyl') + I('pentane') | I('tris') | I('undecan-1-ol') | I('undecanol') | I('valeronitrile') | I('water') |
    I('xylene') | I('xylol') |

    I('[nBu4N][BF4]') | I('BCN') | I('ACN') | I('BTN') | I('BHDC') | I('AOT') | I('DMA') | I('Triton X-100') |
    I('MOPS') | I('TX-100') | I('H2O') + I('+') + I('TX') | I('H2O-Triton X') | I('MES') | I('HDA') | I('PIPES') |
    I('heavy') + I('water') | I('IPA') | I('KPB') | I('MCH') | I('NPA') | I('NMP') | I('PBS') | I('HEPES') |
    I('SDS') | I('TBP') | I('TEA')
)
# Potentially problematic solvent names at the end above...

solvent_name_options = (nmr_solvent | solvent_formula | other_solvent)
solvent_name = (Optional(include_prefix) + solvent_name_options)('name').add_action(join).add_action(fix_whitespace)

chemical_name_options = (
    cm | element_name | element_symbol | registry_number | amino_acid | amino_acid_name | formula
)
chemical_name = (Optional(include_prefix) + chemical_name_options)('name').add_action(join).add_action(fix_whitespace)

# Label phrase structures
# label_type delim? label delim? chemical_name ZeroOrMore(delim cc label delim? chemical_name)

label_name_cem = (chemical_label + optdelim + chemical_name)('cem')
labelled_as = (R('^labell?ed$') + W('as')).hide()
optquote = Optional(quote.hide())

label_before_name = Optional(synthesis_of | to_give) + label_type + optdelim + label_name_cem + ZeroOrMore(optdelim + cc + optdelim + label_name_cem)

likely_abbreviation = (Optional(include_prefix + Optional(hyphen)) + R('^([A-Z]{2,6}(\-[A-Z]{1,6})?|[A-Z](\-[A-Z]{2,6}))$'))('name').add_action(join).add_action(fix_whitespace)

name_with_optional_bracketed_label = (Optional(synthesis_of | to_give) + chemical_name + Optional(lbrct + Optional(labelled_as + optquote) + (chemical_label | lenient_chemical_label | likely_abbreviation) + optquote + rbrct))('cem')

# Lenient name match that should be used with stricter surrounding context
lenient_name = OneOrMore(Not(rbrct) + (bcm | icm | jj | nn | nnp | nns | hyph | cd | ls | W(',')))('name').add_action(join).add_action(fix_whitespace)

# Very lenient name and label match, with format like "name (Compound 3)"
lenient_name_with_bracketed_label = (Start() + Optional(synthesis_of) + lenient_name + lbrct + label_type.hide() + lenient_chemical_label + rbrct)('cem')

# chemical name with a comma in it that hasn't been tagged.
name_with_comma_within = Start() + Group(Optional(synthesis_of) + (cm + W(',') + cm + Not(cm) + Not(I('and')))('name').add_action(join).add_action(fix_whitespace))('cem')

# to_give_bracketed_label = to_give + lenient_name  # TODO: Come back to this

# TODO: Currently ensuring roles are captured from text preceding cem/cem_phrase ... abstract out the 'to_give"

cem = (lenient_name_with_bracketed_label | label_before_name | name_with_comma_within | name_with_optional_bracketed_label)

cem_phrase = Group(cem)('cem_phrase')

r_equals = R('^[R]$') + W('=') + OneOrMore(Not(rbrct) + (bcm | icm | nn | nnp | nns | hyph | cd | ls))
of_table = (I('of') | I('in')) + Optional(dt) + I('table')

bracketed_after_name = Optional(comma) + lbrct + Optional(labelled_as + optquote) + (chemical_label | lenient_chemical_label | likely_abbreviation) + optquote + Optional(Optional(comma) + r_equals | of_table) + rbrct
comma_after_name = comma + Optional(labelled_as + optquote) + (chemical_label | likely_abbreviation)

compound_heading_ending = (Optional(comma) + ((lbrct + (chemical_label | lenient_chemical_label | lenient_name) + Optional(Optional(comma) + r_equals | of_table) + rbrct) | chemical_label) + Optional(R('^[:;]$')).hide() | comma + (chemical_label | lenient_chemical_label)) + Optional(W('.')) + End()

# Section number, to allow at the start of a heading
section_no = Optional(I('stage') | I('step') | I('section') | I('part')) + (T('CD') | R('^\d{1,3}(\.\d{1,3}(\.\d{1,3}(\.\d{1,3})?)?)?$') | (Optional(lbrct) + roman_numeral + rbrct))

compound_heading_style1 = Start() + Optional(section_no.hide()) + Optional(synthesis_of) + OneOrMore(Not(compound_heading_ending) + (bcm | icm | jj | nn | nnp | nns | hyph | sym | cd | ls | W(',')))('name').add_action(join).add_action(fix_whitespace) + compound_heading_ending + End()
compound_heading_style2 = chemical_name + Optional(bracketed_after_name)
compound_heading_style3 = synthesis_of + (lenient_name | chemical_name) + Optional(bracketed_after_name | comma_after_name)  # Possibly redundant?
compound_heading_style4 = label_type + lenient_chemical_label + ZeroOrMore((T('CC') | comma) + lenient_chemical_label) + (lenient_name | chemical_name) + Optional(bracketed_after_name | comma_after_name)
# TODO: Capture label type in output

compound_heading_phrase = Group(compound_heading_style1 | compound_heading_style2 | compound_heading_style3 | compound_heading_style4 | chemical_label)('cem')


def standardize_role(role):
    """Convert role text into standardized form."""
    role = role.lower()
    if any(c in role for c in {'synthesis', 'give', 'yield', 'afford', 'product', 'preparation of'}):
        return 'product'
    return role


class CompoundParser(BaseParser):
    """Chemical name possibly with an associated label."""

    root = cem_phrase

    def interpret(self, result, start, end):
        # TODO: Parse label_type into label model object
        for cem_el in result.xpath('./cem'):
            c = Compound(
                names=cem_el.xpath('./name/text()'),
                labels=cem_el.xpath('./label/text()'),
                roles=[standardize_role(r) for r in cem_el.xpath('./role/text()')]
            )
            yield c


class ChemicalLabelParser(BaseParser):
    """Chemical label occurrences with no associated name."""

    root = chemical_label_phrase

    def interpret(self, result, start, end):
        roles = [standardize_role(r) for r in result.xpath('./role/text()')]
        for label in result.xpath('./label/text()'):
            yield Compound(labels=[label], roles=roles)


class CompoundHeadingParser(BaseParser):
    """Better matching of abbreviated names in dedicated compound headings."""

    root = compound_heading_phrase

    def interpret(self, result, start, end):
        roles = [standardize_role(r) for r in result.xpath('./role/text()')]
        labels = result.xpath('./label/text()')
        if len(labels) > 1:
            for label in labels:
                yield Compound(labels=[label], roles=roles)
            for name in result.xpath('./name/text()'):
                yield Compound(names=[name], roles=roles)
        else:
            yield Compound(
                names=result.xpath('./name/text()'),
                labels=labels,
                roles=roles
            )

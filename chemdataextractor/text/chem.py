# -*- coding: utf-8 -*-
"""
chemdataextractor.text.chem
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Chemistry text handling tools.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re

from . import bracket_level

# All chemical element names.
# Includes both aluminium and aluminum, both tungsten and wolfram, and some former names (plumbum, hydrargyrum).
ELEMENTS = {
    'actinium', 'aluminium', 'aluminum', 'americium', 'antimony', 'argon', 'arsenic', 'astatine', 'barium', 'berkelium',
    'beryllium', 'bismuth', 'bohrium', 'boron', 'bromine', 'cadmium', 'caesium', 'calcium', 'californium', 'carbon',
    'cerium', 'cesium', 'chlorine', 'chromium', 'cobalt', 'copernicium', 'copper', 'curium', 'darmstadtium', 'dubnium',
    'dysprosium', 'einsteinium', 'erbium', 'europium', 'fermium', 'flerovium', 'fluorine', 'francium', 'gadolinium',
    'gallium', 'germanium', 'gold', 'hafnium', 'hassium', 'helium', 'holmium', 'hydrargyrum', 'hydrogen', 'indium',
    'iodine', 'iridium', 'iron', 'kalium', 'krypton', 'lanthanum', 'lawrencium', 'lead', 'lithium', 'livermorium',
    'lutetium', 'magnesium', 'manganese', 'meitnerium', 'mendelevium', 'mercury', 'molybdenum', 'natrium', 'neodymium',
    'neon', 'neptunium', 'nickel', 'niobium', 'nitrogen', 'nobelium', 'osmium', 'oxygen', 'palladium', 'phosphorus',
    'platinum', 'plumbum', 'plutonium', 'polonium', 'potassium', 'praseodymium', 'promethium', 'protactinium', 'radium',
    'radon', 'rhenium', 'rhodium', 'roentgenium', 'rubidium', 'ruthenium', 'rutherfordium', 'samarium', 'scandium',
    'seaborgium', 'selenium', 'silicon', 'silver', 'sodium', 'stannum', 'stibium', 'strontium', 'sulfur', 'tantalum',
    'technetium', 'tellurium', 'terbium', 'thallium', 'thorium', 'thulium', 'tin', 'titanium', 'tungsten', 'ununoctium',
    'ununpentium', 'ununseptium', 'ununtrium', 'uranium', 'vanadium', 'wolfram', 'xenon', 'ytterbium', 'yttrium',
    'zinc', 'zirconium'
}

ELEMENT_SYMBOLS = {
    'Ac', 'Ag', 'Al', 'Am', 'Ar', 'As', 'At', 'Au', 'B', 'Ba', 'Be', 'Bh', 'Bi', 'Bk', 'Br', 'C', 'Ca', 'Cd', 'Ce',
    'Cf', 'Cl', 'Cm', 'Cn', 'Co', 'Cr', 'Cs', 'Cu', 'Db', 'Ds', 'Dy', 'Er', 'Es', 'Eu', 'F', 'Fe', 'Fl', 'Fm', 'Fr',
    'Ga', 'Gd', 'Ge', 'H', 'He', 'Hf', 'Hg', 'Ho', 'Hs', 'I', 'In', 'Ir', 'K', 'Kr', 'La', 'Li', 'Lr', 'Lu', 'Lv', 'Md',
    'Mg', 'Mn', 'Mo', 'Mt', 'N', 'Na', 'Nb', 'Nd', 'Ne', 'Ni', 'No', 'Np', 'O', 'Os', 'P', 'Pa', 'Pb', 'Pd', 'Pm', 'Po',
    'Pr', 'Pt', 'Pu', 'Ra', 'Rb', 'Re', 'Rf', 'Rg', 'Rh', 'Rn', 'Ru', 'S', 'Sb', 'Sc', 'Se', 'Sg', 'Si', 'Sm', 'Sn',
    'Sr', 'Ta', 'Tb', 'Tc', 'Te', 'Th', 'Ti', 'Tl', 'Tm', 'U', 'Uuo', 'Uup', 'Uus', 'Uut', 'V', 'W', 'Xe', 'Y', 'Yb',
    'Zn', 'Zr'
}

# Formula regex?
# ((A[cglmrstu]|B[aehikr]?|C[adeflmnorsu]?|D[bsy]|E[rsu]|F[elmr]?|G[ade]|H[efgos]?|I[nr]?|Kr?|L[airuv]|M[dgnot]|N[abdeiop]?|Os?|P[abdmortu]?|R[abefghnu]|S[bcegimnr]?|T[abcehilm]|U|V|W|Xe|Yb?|Z[nr])\d?\d?)+

# Common solvent names.
# Use SOLVENT_RE for proper matching of solvent names.
SOLVENTS = {
    '(CD3)2CO', '(CDCl2)2', '(CH3)2CHOH', '(CH3)2CO', '(CH3)2NCOH', '[nBu4N][BF4]', '1-butanol',
    '1-butylimidazole', '1-cyclohexanol', '1-decanol', '1-heptanol', '1-hexanol', '1-methylethyl acetate',
    '1-octanol', '1-pentanol', '1-phenylethanol', '1-propanol', '1-undecanol', '1,1,1-trifluoroethanol',
    '1,1,1,3,3,3-hexafluoro-2-propanol', '1,1,1,3,3,3-hexafluoropropan-2-ol', '1,1,2-trichloroethane',
    '1,2-c2h4cl2', '1,2-dichloroethane', '1,2-dimethoxyethane', '1,2-dimethylbenzene', '1,2-ethanediol',
    '1,2,4-trichlorobenzene', '1,4-dimethylbenzene', '1,4-dioxane', '2-(n-morpholino)ethanesulfonic acid',
    '2-butanol', '2-butanone', '2-me-thf', '2-methf', '2-methoxy-2-methylpropane', '2-methyl tetrahydrofuran',
    '2-methylpentane', '2-methylpropan-1-ol', '2-methylpropan-2-ol', '2-methyltetrahydrofuran', '2-proh',
    '2-propanol', '2-propyl acetate', '2-pyrrolidone', '2,2,2-trifluoroethanol', '2,2,4-trimethylpentane',
    '2Me-THF', '2MeTHF', '3-methyl-pentane', '4-methyl-1,3-dioxolan-2-one', 'acetic acid', 'aceto-nitrile',
    'acetone', 'acetonitrile', 'acetononitrile', 'ACN', 'AcOEt', 'AcOH', 'AgNO3', 'aniline', 'anisole', 'AOT',
    'BCN', 'benzene', 'benzonitrile', 'benzyl alcohol', 'BHDC', 'bromoform', 'BTN', 'Bu2O', 'Bu4NBr',
    'Bu4NClO4', 'Bu4NPF6', 'BuCN', 'BuOH', 'butan-1-ol', 'butan-2-ol', 'butan-2-one', 'butane', 'butanol',
    'butanone', 'butene', 'butyl acetate', 'butyl acetonitrile', 'butyl alcohol', 'butyl amine',
    'butyl chloride', 'butyl imidazole', 'butyronitrile', 'c-hexane', 'C2D5CN', 'C2H4Cl2', 'C2H5CN', 'C2H5OH',
    'C5H5N', 'C6D6', 'C6H12', 'C6H14', 'C6H5CH3', 'C6H5Cl', 'C6H6', 'C7D8', 'C7H8', 'carbon disulfide',
    'carbon tetrachloride', 'CCl4', 'CD2Cl2', 'CD3CN', 'CD3COCD3', 'CD3OD', 'CD3SOCD3', 'CDCl3', 'CH2Cl2',
    'CH2ClCH2Cl', 'CH3C6H5', 'CH3Cl', 'CH3CN', 'CH3CO2H', 'CH3COCH3', 'CH3COOH', 'CH3NHCOH', 'CH3NO2',
    'CH3OD', 'CH3OH', 'CH3Ph', 'CH3SOCH3', 'CHCl2', 'CHCl3', 'chlorobenzene', 'chloroform', 'chloromethane',
    'chlorotoluene', 'CHX', 'Cl2CH2', 'ClCH2CH2Cl', 'cumene', 'cyclohexane', 'cyclohexanol', 'cyclopentyl methyl ether',
    'D2O', 'DCE', 'DCM', 'decalin', 'decan-1-ol', 'decane', 'decanol', 'DEE', 'di-isopropyl ether',
    'di-n-butyl ether', 'di-n-hexyl ether', 'dibromoethane', 'dibutoxymethane', 'dibutyl ether',
    'dichloro-methane', 'dichlorobenzene', 'dichloroethane', 'dichloromethane', 'diethoxymethane',
    'diethyl carbonate', 'diethyl ether', 'diethylamine', 'diethylether', 'diglyme', 'dihexyl ether',
    'diiodomethane', 'diisopropyl ether', 'diisopropylamine', 'dimethoxyethane', 'dimethoxymethane',
    'dimethyl acetamide', 'dimethyl acetimide', 'dimethyl benzene', 'dimethyl carbonate', 'dimethyl ether',
    'dimethyl formamide', 'dimethyl sulfoxide', 'dimethylacetamide', 'dimethylbenzene', 'dimethylformamide',
    'dimethylformanide', 'dimethylsulfoxide', 'dioctyl sodium sulfosuccinate', 'dioxane', 'dioxolane',
    'dipropyl ether', 'DMA', 'DMAc', 'DMF', 'DMSO', 'Et2O', 'EtAc', 'EtAcO', 'EtCN', 'ethane diol',
    'ethane-1,2-diol', 'ethanol', 'ethyl (S)-2-hydroxypropanoate', 'ethyl acetate', 'ethyl benzoate',
    'ethyl formate', 'ethyl lactate', 'ethyl propionate', 'ethylacetamide', 'ethylacetate', 'ethylene carbonate',
    'ethylene glycol', 'ethyleneglycol', 'ethylhexan-1-ol', 'EtOAc', 'EtOD', 'EtOH', 'eucalyptol', 'F3-ethanol',
    'F3-EtOH', 'formamide', 'formic acid', 'glacial acetic acid', 'glycerol', 'H2O', 'H2O + TX', 'H2O-Triton X',
    'H2O2', 'H2SO4', 'HBF4', 'HCl', 'HClO4', 'HCO2H', 'HCONH2', 'HDA', 'heavy water', 'HEPES', 'heptan-1-ol',
    'heptane', 'heptanol', 'heptene', 'HEX', 'hexadecylamine', 'hexafluoroisopropanol', 'hexafluoropropanol',
    'hexan-1-ol', 'hexane', 'hexanes', 'hexanol', 'hexene', 'hexyl ether', 'HFIP,', 'HFP', 'HNO3',
    'hydrochloric acid', 'hydrogen peroxide', 'iodobenzene', 'IPA', 'isohexane', 'isooctane', 'isopropanol',
    'isopropyl benzene', 'KBr', 'KPB', 'LiCl', 'ligroine', 'limonene', 'MCH', 'Me-THF', 'Me2CO', 'MeCN',
    'MeCO2Et', 'MeNO2', 'MeOD', 'MeOH', 'MES', 'mesitylene', 'methanamide', 'methanol', 'MeTHF',
    'methoxybenzene', 'methoxyethylamine', 'methyl acetamide', 'methyl acetoacetate', 'methyl benzene',
    'methyl butane', 'methyl cyclohexane', 'methyl ethyl ketone', 'methyl formamide', 'methyl formate',
    'methyl isobutyl ketone', 'methyl laurate', 'methyl methanoate', 'methyl naphthalene', 'methyl pentane',
    'methyl propan-1-ol', 'methyl propan-2-ol', 'methyl propionate', 'methyl pyrrolidin-2-one',
    'methyl pyrrolidine', 'methyl pyrrolidinone', 'methyl t-butyl ether', 'methyl tetrahydrofuran',
    'methyl-2-pyrrolidone', 'methylbenzene', 'methylcyclohexane', 'methylene chloride', 'methylformamide',
    'methyltetrahydrofuran', 'MIBK', 'morpholine', 'mTHF', 'n-butanol', 'n-butyl acetate', 'n-decane',
    'n-heptane', 'n-HEX', 'n-hexane', 'n-methylformamide', 'n-methylpyrrolidone', 'n-nonane', 'n-octanol',
    'n-pentane', 'n-propanol', 'n,n-dimethylacetamide', 'n,n-dimethylformamide', 'n,n-DMF', 'Na2SO4', 'NaCl',
    'NaClO4', 'NaHCO3', 'NaOH', 'nBu4NBF4', 'nitric acid', 'nitrobenzene', 'nitromethane', 'NMP', 'nonane',
    'NPA', 'nujol', 'o-dichlorobenzene', 'o-xylene', 'octan-1-ol', 'octane', 'octanol', 'octene', 'ODCB',
    'p-xylene', 'PBS', 'pentan-1-ol', 'pentane', 'pentanol', 'pentanone', 'pentene', 'PeOH', 'perchloric acid',
    'PhCH3', 'PhCl', 'PhCN', 'phenoxyethanol', 'phenyl acetylene', 'Phenyl ethanol', 'phenylamine',
    'phenylethanolamine', 'phenylmethanol', 'PhMe', 'phosphate', 'phosphate buffered saline', 'pinane',
    'piperidine', 'polytetrafluoroethylene', 'potassium bromide', 'potassium phosphate buffer', 'PrCN', 'PrOH',
    'propan-1-ol', 'propan-2-ol', 'propane', 'propane-1,2-diol', 'propane-1,2,3-triol', 'propanol', 'propene',
    'propionic acid', 'propionitrile', 'propyl acetate', 'propyl amine', 'propylene carbonate',
    'propylene glycol', 'pyridine', 'pyrrolidone', 'quinoline', 'SDS', 'silver nitrate', 'SNO2',
    'sodium chloride', 'sodium hydroxide', 'sodium perchlorate', 'sulfuric acid', 't-butanol', 'TBABF4', 'TBAF',
    'TBAH', 'TBAOH', 'TBAP', 'TBAPF6', 'TBP', 'TEA', 'TEAP', 'TEOA', 'tert-butanol', 'tert-butyl alcohol',
    'tetrabutylammonium hexafluorophosphate', 'tetrabutylammonium hydroxide', 'tetrachloroethane',
    'tetrachloroethylene', 'tetrachloromethane', 'tetrafluoroethylene', 'tetrahydrofuran', 'tetralin',
    'tetramethylsilane', 'tetramethylurea', 'tetrapiperidine', 'TFA', 'TFE', 'THF', 'THF-d8', 'tin dioxide',
    'titanium dioxide', 'toluene', 'tri-n-butyl phosphate', 'triacetate', 'triacetin', 'tribromomethane',
    'tributyl phosphate', 'trichlorobenzene', 'trichloroethene', 'trichloromethane', 'triethyl amine',
    'triethyl phosphate', 'triethylamine', 'trifluoroacetic acid', 'trifluoroethanol', 'trifluoroethanol ',
    'trimethyl benzene', 'trimethyl pentane', 'tris', 'Triton X-100', 'TX-100', 'undecan-1-ol', 'undecanol',
    'valeronitrile', 'water', 'xylene', 'xylol'
}

# Common chemical name prefixes
PREFIXES = {'iso', 'tert', 'sec', 'ortho', 'meta', 'para', 'meso'}

# A regular expression that matches common solvents.
SOLVENT_RE = re.compile(r'(?:^|\b)(?:(?:%s|d\d?\d?|[\dn](?:,[\dn]){0,3}|[imnoptDLRS])-?)?(?:%s)(?:-d\d?\d?)?(?=$|\b)'
                        % ('|'.join(re.escape(s) for s in PREFIXES),
                           '|'.join(re.escape(s).replace(r'\ ', r'[\s\-]?') for s in SOLVENTS)), re.I)

# Regular expressions for validating chemical identifiers
CAS_RE = re.compile(r'^\d{1,7}-\d\d-\d$')   # TODO: Should be  (([1-9]\d{2,5})|([5-9]\d))-\d\d-\d
INCHIKEY_RE = re.compile(r'^[A-Z]{14}-[A-Z]{10}-[A-Z\d]$')
INCHI_RE = re.compile(r'^(InChI=)?1S?\/(p\+1|\d*[a-ik-z][a-ik-z\d\.]*(\/c[\d\-*(),;]+)?(\/h[\d\-*h(),;]+)?)(\/[bmpqst][\d\-\.+*,;?m]*|\/i[hdt\d\-+*,;]*(\/h[hdt\d]+)?|\/r[a-ik-z\d]+(\/c[\d\-*(),;]+)?(\/h[\d\-*h(),;]+)?|\/f[a-ik-z\d\.]*(\/h[\d\-*h(),;]+)?)*$', re.I)
SMILES_RE = re.compile(r'^([BCNOPSFIbcnosp*]|Cl|Br|\[\d*(%(e)s|se|as|\*)(@+([THALSPBO]\d+)?)?(H\d?)?([\-+]+\d*)?(:\d+)?\])'
                       r'([BCNOPSFIbcnosp*]|Cl|Br|\[\d*(%(e)s|se|as|\*)(@+([THALSPBO]\d+)?)?(H\d?)?([\-+]+\d*)?(:\d+)?\]|'
                       r'[\-=#$:\\/\(\)%%\.+\d])*$' % {'e': '|'.join(ELEMENT_SYMBOLS)})


def extract_inchis(s):
    """Return a list of InChI identifiers extracted from the string."""
    return [t for t in s.split() if INCHI_RE.match(t)]


def extract_inchikeys(s):
    """Return a list of InChIKey identifiers extracted from the string."""
    return [t for t in s.split() if INCHIKEY_RE.match(t)]


def extract_cas(s):
    """Return a list of CAS identifiers extracted from the string."""
    return [t for t in s.split() if CAS_RE.match(t)]


def extract_smiles(s):
    """Return a list of SMILES identifiers extracted from the string."""
    # TODO: This still gets a lot of false positives.
    smiles = []
    for t in s.split():
        if len(t) > 2 and SMILES_RE.match(t) and not t.endswith('.') and bracket_level(t) == 0:
            smiles.append(t)
    return smiles

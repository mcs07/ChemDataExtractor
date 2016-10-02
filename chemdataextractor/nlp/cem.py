# -*- coding: utf-8 -*-
"""
chemdataextractor.nlp.cem
~~~~~~~~~~~~~~~~~~~~~~~~~

Named entity recognition (NER) for Chemical entity mentions (CEM).

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import re

from ..text import bracket_level
from .lexicon import ChemLexicon
from .tag import BaseTagger, CrfTagger, DictionaryTagger


log = logging.getLogger(__name__)


#: Token endings to ignore when considering stopwords and deriving spans
IGNORE_SUFFIX = [
    # Many of these are now unnecessary due to tokenization improvements, but not much harm in leaving them here.
    '-', '\'s', '-activated', '-adequate', '-affected', '-anesthetized', '-based', '-binding', '-boosted', '-cane',
    '-conditioned', '-containing', '-covered', '-deficient', '-dependent', '-derived', '-electrolyte', '-enriched',
    '-exposed', '-flanking', '-free', '-fused', '-gated', '-glucuronosyltransferases', '-increasing', '-induced',
    '-inducible', '-l-tyrosine', '-labeled', '-lesioned', '-loaded', '-mediated', '-patterned', '-primed', '-reducing',
    '-regulated', '-releasing', '-resistant', '-response', '-rich', '-s-transferase', '-sensitive', '-soluble',
    '-stimulated', '-stressed', '-supplemented', '-terminal', '-transferase', '-treated', '-type', '-blood',
    '-specific', '-like', '-elicited', '-stripped', '-transfer', '-conjugate', '-coated', '-producing', '-oxidized',
    '-associated', '-related', '-converting', '-ligand', '-on-glass', '-seeking', '-hydrolyzing', '-o-deethylase',
    '-deethylase', '-o-depentylase', '-depentylase', '-n-demethylase', '-demethylase', '-o-methyltransferase',
    '-c-oxidase', '-oxidase', '-n-biosidase', '-biosidase', '-immunoproteins', '-spiked', '-lowering', '-page',
    '-depletion', '-formation', '-dealkylation', '-deethylation', '-alkylation', '-ribosylation', '-production',
    '-demethylation', '-oxidation', '-transition', '-glycosylation', '-zwitterion', '-benzylation', '-reduction',
    '-oxygenation', '-nitrosylation', '-evoked', '-mutated', '-doped', '-aged', '-increased', '-triggered', '-linked',
    '-fixed', '-injected', '-contaminated', '-depleted', '-enhanced', '-stained', '-modified', '-fed', '-demethylated',
    '-catalyzed', '-etched', '-labelled', '-conjugated', '-pretreated', '-ribosylated', '-phosphorylated', '-reduced',
    '-bonded', '-stabilised', '-crosslinked', '-mannosylated', '-capped', '-supported', '-initiated', '-integrated',
    '-accelerated', '-encapsulated', '-untreated', '-expanded', '-coupled', '-terminated', '-assisted',
    '-permeabilized', '-resulted', '-alkylated', '-functionalized', '-contained', '-buffered', '-caused', '-cyclized',
    '-substituted', '-modulated', '-inhibited', '-centered', '-promoted', '-confirmed', '-provoked', '-dominated',
    '-limited', '-challenged', '-tetrabrominated', '-unesterified', '-refreshed', '-bottled', '-protonated',
    '-incubated', '-tagged', '-damaged', '-bridged', '-maintained', '-impregnated', '-metabolizing', '-deprived',
    '-insensitive', '-dendrimer', '-receptor', '-tolerant', '-influx', '-administrated', '-requiring', '-permeable',
    '-transport', '-intoxicated', '-overload', '-derivatives', '-derivative', '-sweetened', '-transporter', '-bound',
    '-extract', '-bonding', '-bond', '-trna', '-redistribution', '-copolymers', '-copolymer', '-appended',
    '-susceptible', '-transfected', '-bearing', '-regenerating', '-induction', '-conducting', '-decorated',
    '-encapsulating', '-consuming', '-bridge', '-dependence', '-Pdots', '-only', '-carrying', '-treating', '-isomerase',
    '-ion', '-ions', '-coordinated', '-saturated', '-sparing', '-enclosed', '-stabilized', '-polymer', '-yeast',
    '-making', '-porous', '-independent', '-metallized', '-attenuated', '-liquid', '-caged', '-deficiency', '-sensing',
    '-recognition', '-responsiveness', '-embedded', '-connectivity', '-abuse', '-chelating', '-decocted', '-forming',
    '-nutrition', '-scavenging', '-preferring', '-mimicking', '-drugs', '-drug', '-lubricants', '-adsorption',
    '-ligated', '-detected', '-responsive', '-reacting', '-defined', '-capturing', '-group', '-abstinent', '-paired',
    '-devalued', '-need', '-cellulose', '-atpase', '-inactivated', '-β-glucosaminidase', '-glucosaminidase', '-dosed',
    '-imprinted', '-precipitated', '-monoadducts', '-vacancies', '-vacancy', '-attributed', '-depolarization',
    '-depolarized', '-liver', '-testes', '-reversible', '-active', '-reactive', '-dextran', '-fixing', '-synthesizing',
    '-inhibitory', '-cleaving', '-positive', '-activity', '-fluorescence', '-regulating', '-NPs', '-scanning',
    '-water', '-nmr', '-limiting', '-refractory', '-knot', '-variable', '-biomolecule', '-backbone', '-exchange',
    '-donating', '-coating', '-hydrogenase', '-hydrogenases', '-intolerant', '-deplete', '-poor', '-loading',
    '-enrichment', '-elevating', '-resitant', '-stabilizing', '-pathway', '-fortified', '-adjusted',
    '-restricted', '-dependant', '-locked', '-normalized', '-aromatic', '-hydroxylation', '-intermediate',
    '-6-phosphatase', '-phosphatase', '-linker', '-proteomic', '-mimetic', '-lipid', '-radical', '-receptors',
    '-substrate', '-conjugates', '-promoting', '-dye', '-functionalyzed', '-catalysed', '-reductase', '-QDs',
    '-complexes', '-placebo', '-transferases', '-alginate', '-competing', '-depleting', '-sensitized',
    '-protein', '-regulatory', '-target', '-toxin', '-yield', '-planted', '-produced', '-derivatized', '-secreting',
    '-modifying', '-DNA', '-bonds', '-assemblages', '-exposure', '-negative', '-sealed', '-atom', '-atoms',
    '-abstraction', '-concentration', '-doping', '-competitive', '-acclimation', '-acclimated', '-interlinked',
    '-suppressed', '-postlabeling', '-labeling', '-diabetic', '-omitted', '-sufficient', '-generating', '-terminus',
    '-adducts', '-compound', '-compounds', '-γ-lyase', '-γ-synthase', '-lyase', '-synthase', '-inhibitor',
    '-protected', '-multiwall', '-stripping', '-plasma', '-evolving'
]

#: Token beginnings to ignore when considering stopwords and deriving spans
IGNORE_PREFIX = [
    'fluorophore-', 'low-', 'high-', 'single-', 'odd-', 'non-', 'high-', 'cross-', 'cellulose-', 'anti-', '-multiwall',
    'globular-', 'plasma-', 'hybrid-', 'protein-', 'explicit-', 'cation-', 'water-', 'through-', 'starch-', 'rigid-',
    'conjugated-', 'photoactivatable-', 'alginate-', 'nano-', 'dye-', 'ligand-', 'enzyme-', 'platelet-', 'photo-',
    'total-', 'drug-', 'nanoparticle-', 'nanomaterial-', 'inter-', 'ion-', 'post-', 'one-'
]

#: Final tokens to remove from entity matches
STRIP_END = [
    'groups', 'group', 'colloidal', 'dyes', 'dye', 'products', 'product', 'substances', 'substance', 'solution',
    'derivatives', 'derivative', 'analog', 'salts', 'salt', 'minerals', 'mineral', 'anesthetic', 'tablet', 'tablets',
    'preparation', 'atoms', 'atom', 'monomers', 'monomer', 'nanoparticles', 'nanoparticle', 'radicals', 'radical',
    'dendrimers', 'dendrimer', 'ions', 'ion', 'particles', 'particle', 'anion', 'cation', 'foam', 'cellulose',
    'dextran', '(', 'dust', 'herbicide', 'disease', 'diseases', 'and', 'or', ';', ',', '.'
]

#: First tokens to remove from entity matches
STRIP_START = [
    'anhydrous', 'elemental', 'amorphous', 'conjugated', 'colloidal', 'activated', 'water-soluble', 'total',
    'superparamagnetic', 'molecular', 'high-density', 'synthetic', 'low-density', 'long-chain', 'fused', 'radioactive',
    'reduced', 'anatase', 'dextran', ')', 'trisubstituted', 'deposited', 'herbicide', 'antagonist', 'agonist', 'and',
    'or', 'metallic', 'embryotoxic', 'monoclinic'
]

#: Disallowed tokens in chemical entity mentions (discard if any single token has exact case-insensitive match)
STOP_TOKENS = {
    'gene', 'inhibitor', 'genetical', 'human', 'recombinant', 'recombination', 'adenovirus', 'bovine', 'chicken',
    'sheep', 'pig', 'horse', 'mammalian', 'salmon', 'cytochrome', 'glycoprotein', 'genevrier', 'novartis', 'visfarm',
    'bristol-myers', 'squibb', 'allphar', 'bioniche', 'bipharma', 'chauvin', 'merck', 'procter', 'roche',
    'glaxo', 'glaxosmithkline', 'pfizer', 'ciba-geigy', 'interpharm', 'bayer', 'astrazeneca', 'aventis', 'behringer',
    'ratiopharm', 'pharmacia', 'apotex', 'novopharm', 'alpharma', 'schering', 'genzyme', 'aldrich', 'wiskott',
    'crossref', 'chemistry', '10.1039', '10.1021', '10.1186', 'doi', 'january', 'february', 'march', 'april', 'june',
    'july', 'august', 'september', 'october', 'november', 'december', 'esi', '†', '§', 'london', 'paris', 'tokyo',
    'york', 'angeles', 'francisco', 'berlin', 'bristol', 'southampton', 'edinburgh', 'chicago', 'cambridge', 'oxford',
    'parameters', 'volume', 'dielectric', 'cm–1', 'measurements', 'studies', 'imaging', 'ccdc', 'sigma-aldrich',
    'scientifique', 'china', 'fig.', 'approach', 'colored', 'isbn', 'having', 'background', 'method', 'methods',
    'results', 'discussion', 'introduction', 'conclusion', 'conclusions', 'prior', 'technical', 'nano-beads',
    'nanobeads', 'test', 'production', 'priority', 'claim', 'claims', 'journal', 'journals', 'letters', 'phenomena',
    'article', 'articles', 'ethical', 'guidelines', 'editor', 'editors', 'profile', 'editorial', 'masthead', 'citing',
    'download', 'citation', 'members', 'privacy', 'policy', 'help', 'chemworx', 'biochemistry', 'energy', 'more',
    'syntheticpage', 'contact', 'fluorochem', '.cdx', '.sk2', 'email', 'affiliation', 'affiliations', 'bibtex',
    'medline', 'marinlit', 'chemspider', 'permissions', 'ekins', 'edit', 'links', 'link', 'english', 'italiano',
    'esperanto', 'español', 'wikimedia', 'upload', 'file', 'account', 'personal', 'navigation', 'menu', 'external',
    'references', 'safety', 'pharmacology', 'coffee', 'research', 'bibliography', 'tobacco', 'palestine', 'doctrine',
    'napoleon', 'azərbaycanca', 'euskara', 'latviešu', 'nordfriisk', 'नेपाल भाषा', 'children', 'overdose', 'chocolate',
    'systematic', 'google', 'literature', 'books', 'docking', 'chromatography', 'libraries', 'retention', 'index',
    'danielle', 'claire', 'rachel', 'zhang', 'linkedin', 'magazine', 'america', 'ireland',

}

#: Disallowed substrings in chemical entity mentions (only used when filtering to construct the dictionary?)
STOP_SUB = {
    'botulinum', 'plasminogen', 'necrosis', 'exciton', 'glucan', 'fibroblast', 'follicle', 'natriuretic', 'luteinizing',
    'insulin', 'platelet', 'glucagon', 'activating factor', 'necrosis factor', 'growth factor', ' with ', ' brand of ',
    'transcription factor', ' oil', 'oil of ', ', ', '?', '!', '\\', '|', '@', ';', '%', 'stimulating factor',
    'coagulation factor', 'neurofilament', 'freund', 'anticodon', 'neuropeptide', 'intercellular', 'gene-related',
    'selectin', 'reactive', 'interleukin', 'gramicidin', 'melanin', 'corticotropin', 'corticotrophin',
    'adrenocorticotropic', 'hemoglobin', 'concanavalin', 'factor ', 'releasing factor', 'regulator', 'transmembrane',
    'conductance', 'interferon'
}

#: Disallowed chemical entity mentions (discard if exact case-insensitive match)
STOPLIST = {
    'gold', 'lead', 'yellow', 'epidermal growth factor', 'pristine', 'transdermal patch', 'olive oil', 'groundnut oil',
    'telomerase', 'transdermal patch', 'cascade', 'agar', 'distilled water', 'water', 'alpha-actinin-4', 'iberiotoxin',
    'alginate', 'pancreatin', 'starch', 'iκbα', 'insulin', 'cetuximab', 'il-2', 'serum albumin', 'discover', 'glycine',
    'roundup', 'balance', 'glycogen', 'epidermal growth factor (egf)', 'polysaccharide', 'ginseng', 'hemoglobin',
    'hydroxypropylcellulose', 'advantage', 'petroleum ether', 'gypsum', 'light yellow', 'cadmium chloride (cdcl2)',
    'histone', 'absolute ethanol', 'activated charcoal', 'puerarin', 'total bilirubin', 'collagenase', 'capmul',
    'cremophor el', 'ubiquitin', 'glp-1', 'glucagon-like peptide-1', 'vinegar', 'accelerate', 'Nucleophosmin',
    'deionized water', 'betula', 'pectin', 'pectins', 'furosemide', 'bumetanide', 'teac', 'dept', 'plumbago',
    'cytochrome c', 'ndma', 'ultimate', 'triticum', 'ubiquinone', 'artemisinin', 'cytochrome p450', 'parkin', 'proton',
    'elevate', 'lime', 'corn oil', 'hydrogel', 'activin', 'amylin', 'raven', 'nerve agent', 'collagen', 'gradual',
    'probiotic', 'akron', 'spotlight', 'meta-analysis', 'osteopontin', 'integrin', 'glycoproteins', 'classic',
    'silence', 'first sign', 'compendium', 'prothrombin', 'blood coagulation factor x', 'advance', 'insular',
    'tarragon', 'mutagen', 'agarose', 'glycoprotein', 'maintain a', 'inhalable', 'adrenocorticotropic hormone',
    'cyclin d1', 'cyclin d3', 'chitosan', 'cellulose', 'betaine', 'thromboplastin', 'thrombin',
    'factor x', 'plasminogen', 'exciton', 'growth hormone', 'placental growth hormone', 'aprotinin', 'glucans',
    'latex particles', 'piper', 'corticotropin', 'dixon', 'bengal', 'fret-capture', 'intense blue', 'singlet oxygen',
    'oil-in-water', 'water-in-oil', 'protio', 'crotoxin', 'oil', 'cocktail', 'nodular', 'interceptor', 'fibrinogen',
    'dams', 'lotion', 'consist', 'mascot', 'radio', 'prep', 'ac187', 'pima', 'biopterin', 'dalteparin', 'enoxaparin',
    'lmwh', 'angiotensinogen', 'revolution', 'trails', 'am1', 'xanthium', 'ω', 'noxa', 'sepharose', 'melanin', 'ricin',
    'trypsinogen', 'conserve', 'preview', 'barrels', 'hemozoin', 'recruit', 'dragon', 'acacia', 'homogentisate',
    'triangle', 'vortex', 'reconcile', 'aversion', 'ubr2', 'calcitonin', 'samp', 'xanthan', 'ascophyllum', 'vicilin',
    'maltodextrin', 's100', 'maltodextrin', 'spme', 'p300', 'p450', 'hyaluronidase', 'osteocalcin', 'm41.4', 'genesis',
    'tnfα', 'herceptin', 'laba', 'teriparatide', 'rutile', 'harness', 'hyperoxia', 'adalimumab',
    'cholecystokinin', 'counter', 'acth', 'raptor', 'comet', 'regulon', 'erythropoietin', 'dextran', 'metallothionein',
    'perna', 'carotenoids', 'carotenoid', 'propolis', 'amylose', 'amylopectin', 'ovalbumin', 'ovomucoid', 'gelatin',
    'gemini', 'imperator', 'rubber', 'pak1', 'eristostatin', 'heparin', 'dynorphins', 'dynorphin', 'concise',
    'antitussive', 'maneb', 'foxo1', 'octadecaneuropeptide', 'oligonucleotide', 'prolactin', 'cocktail', 'carotene',
    'pgc1α', 'hyaluronan', 'nucleophosmin', 'thyroglobulin', 'carrageenan', 'abbott', 'chymotrypsin', 'excel',
    'polyubiquitin', 'gelatine', 'carboxymethylcellulose', 'urokinase', 'invader', 'belatacept', 'ferritin', 'casein',
    'taxus', 'proopiomelanocortin', 'capture', 'chitosan', 'cellulose', 'betaine', 'thromboplastin', 'thrombin',
    'aprotinin', 'xyloglucan', 'glucans', 'piper', 'corticotropin', 'dixon', 'bengal', 'protio', 'δr(1)', 'crotoxin',
    'amphiregulin', 'fulfill', 'scpa', 'freedom', 'hemopexin', 'transferrin', 'chemokine', 'pegsunercept',
    'iscu', 'auroxanthin', 'vanilla', 'spectrin', 'caprine', 'picrate', 'fucoidan', 'talin', 'polypeptide', 'mag2',
    'mag2\'s', 'ethylcellulose', 'calcined', 'interferon', 'b13', 'mibc', 'inulin', 'trastuzumab', 'aurora', 'trypsin',
    'cubes', 'pampa', 'actomyosin', 'bevacizumab', 'avastin', 'cd3(+)', 'collagens', 'n17', 'agcg', 'cd2+', 'cd4+',
    'cd2', 'horizon', 'denosumab', 'fgf2', 'campaign', 'authority', 'danshen', 'dinucleotide', 'momentum', 'botox',
    'epoetin', 'adipsin', 'glycerin', 'curcuma', 'alum', 'bile', 'fibroin', 'octreotide', 'pursuit', 'elastin',
    'elastomers', 'shellac', 'dash', 'sp1', 'exotoxin', 'icatibant', 'glucomannan', 'vas1', 'bacteriorhodopsin',
    'saline', 'emotion', 'surpass', 'angiotensin', 'hydroxyethylcellulose', 'rifle', 'chamomile', 'keratin',
    'synacthen', 'lignin', 'd250', 'carrageenin', 'lama', 'maba', 'pink', 'lady', 'fenugreek', 'mannan', 'mustard',
    'cellulase', 'cornstarch', 'thioredoxin', 'persian', 'cultivate', 'scot', 'agglutinin', 'ta98', 'rock', 'pc12',
    'metric', 'ferredoxin', 'adrenodoxin', 'glycopeptide', 'benchmark', 'aopp', 'fractal', 'cd3ε', 'perk', 'dihydro',
    'relaxant', 'clin', 'hemocyanin', 'gleevec', 'ltb4', 'pla2', 'arsenal', 'lignocellulose', 'pat4', 'chitin',
    'resovist', 'hypo', 'coral', 'supreme', 'sv2', 'methylcellulose', 'honey', 'squalamine', 'arabinogalactan', 'mega',
    'steel', 'resilin', 'percolate', 'avicel', 'methemoglobin', 'methb', 'lrp1', 'lats', 'opium', 'cd68', 'valiant',
    'hydroxypropylmethylcellulose', 'pseudo', 'carbomer', 'gallery', 'silicone', 'atpγs', 'pc1', 'murabutide', 'dnase',
    '(gaba)ergic', 'hmqc', 'amitraz', 'indigo', 'gtpγs', 'thioredoxins', 'exenatide', 'hairy', 'sunshine', 'star',
    'spme', 'maltodextrin', 's100', 'vicilin', 'ascophyllum', '[h2o2]', 'xanthan', 'samp', 'calcitonin', 'ubr2',
    'aversion', 'reconcile', 'vortex', 'triangle', 'homogentisate', 'acacia', 'dragon', 'recruit', 'hemozoin',
    'barrels', 'preview', 'conserve', 'trypsinogen', 'ricin', 'melanin', 'sepharose', 'noxa', 'ω', 'xanthium', 'trails',
    'revolution', 'angiotensinogen', 'igaba', 'pullulan', 'lmwh', 'enoxaparin', 'fenton', 'meta', 'active carbon',
    'alamethicin', 'bionic', 'dynorphin', 'anterior pituitary hormone', 'gonadotropin releasing hormone',
    'follicle-stimulating hormone', 'adrenocorticotrophic hormone', 'luteinizing hormone', 'luteinising hormone',
    'parathyroid hormone', 'anterior pituitary hormone', 'gonadotropin releasing hormone',
    'adrenocorticotropic hormone', 'thyroid stimulating hormone', 'corticotrophin-releasing hormone',
    'antidiuretic hormone', 'titan', 'anion', 'ion', 'counter-anion', 'counter-ion', 'polypeptide', 'scopolamine',
    'stainless steel', 'danshen', 'cholera toxin', 'thymosin β4', 'sesame oil', 'blood sugar', 'liposomal doxorubicin',
    'fusarium toxin', 'chondroitin sulfate', 'silybum marianum', 'milk thistle', 'amorphous silica',
    'dna double strand', 'cadherin 11', 'conjugated linoleic acid', 'reduced hemoglobin', 'citrus pectin',
    'double stranded dna', 'a chlorophyll', 'flaxseed oil', 'linseed oil', 'peppermint oil', 'clathrin heavy chain',
    'avicel ph101', 'insulin glargine', 'mustard oil', 'chondroitin sulphate', 'provitamin a', 'white light',
    'tea polyphenol', 'dermatan sulfate', 'water vapor', 'clove oil', 'heparan sulfate', 'neurokinin a',
    'polystyrene latex', 'schisandra chinensis', 'gum arabic', 'linseed oils', 'hydroxypropyl methylcellulose',
    'part 2', 'partially hydrolyzed polyacrylamide', 'oil red', 'amorphous carbon', 'microcrystalline cellulose',
    'castor oil', 'peptide e', 'darbepoetin alfa', 'epoetin beta', 'epoetin alfa', 'factor iia', 'natural rubber',
    'xanthan gum', 'aromatic amine', 'uranyl nitrate', 'conjugated estrogens', 'shiga toxin', 'wheat starch',
    'psychogenic', 'glucagon', 'c-peptide', 'zymosan', 'vertex', 'turpentine', 'turmeric', 'c-reactive protein',
    'caramel', 'corn starch', 'contest', 'cont', 'double-stranded dna', 'emerald', 'eminent', 'endurance', 'benet',
    'doyle', 'adept', 'alliance', 'spiegel', 'dial', 'dorm', 'elon', 'vasal', 'orion', 'wander', 'synthol', 'dibs',
    'bide', 'arena', 'musk', 'warf', 'alpen', 'happy', 'baron', 'quench', 'accent', 'zest', 'orphan', 'ural', 'snip',
    'bridal', 'arrow', 'essex', 'dwell', 'diana', 'tops', 'slam', 'soda', 'poly', 'polygon', 'crest', 'minus', 'legend',
    'atrium', 'tara', 'tunic', 'trim', 'citizen', 'brace', 'mighty', 'strike', 'triumph', 'avenge', 'magnum', 'salute',
    'lance', 'cutlass', 'lancer', 'vanquish', 'summit', 'edge', 'ravage', 'tough', 'clout', 'versed', 'banner', 'orbit',
    'radar', 'tilt', 'epic', 'turbo', 'austin', 'raiser', 'racer', 'vengeance', 'commando', 'morph', 'raid', 'joker',
    'cannon', 'command', 'patrol', 'snap', 'halt', 'procure', 'octave', 'tackle', 'stanza', 'verdict', 'empire',
    'peon', 'beret', 'vigil', 'assure', 'sprinkle', 'clipper', 'parlay', 'finale', 'ignite', 'liberty', 'chopper',
    'sceptre', 'pivot', 'assert', 'dagger', 'stalker', 'touchdown', 'brigade', 'spotless', 'facet', 'punch', 'sanction',
    'daren', 'gallant', 'cinch', 'grasp', 'splendor', 'dorado', 'rally', 'storm', 'icon', 'karate', 'sirius', 'alto',
    'centurion', 'prism', 'battalion', 'manage', 'cameo', 'volley', 'elite', 'canopy', 'shogun', 'finish', 'mandate',
    'visor', 'dividend', 'titus', 'limber', 'safari', 'vishnu', 'sultan', 'melody', 'compass', 'flint', 'prosper',
    'jumbo', 'marksman', 'headline', 'olympus', 'granite', 'allay', 'redskin', 'clay', 'butter', 'belt', 'apolar',
    'retard', 'pensive', 'probate', 'tranquil', 'match', 'android', 'paraffin', 'vaseline', 'goon', 'mist', 'peace',
    'scuffle', 'surfer', 'whack', 'rogue', 'senna', 'restful', 'tabloid', 'ecstasy', 'kelp', 'redux', 'leader',
    'pledge', 'squad', 'sentry', 'cola', 'flake', 'flex', 'bazooka', 'bernice', 'blizzard', 'blow', 'bump', 'candy',
    'carrie', 'caviar', 'cecil', 'charlie', 'coca', 'cola', 'coke', 'heaven', 'hell', 'kokan', 'snort', 'toke',
    'toot', 'snow', 'crack', 'emblem', 'fore', 'oliver', 'pride', 'brake', 'sonar', 'talon', 'maya', 'sophia', 'millie',
    'estate', 'blazer', 'latex', 'tomahawk', 'embark', 'apron', 'subdue', 'saffron', 'prowl', 'stomp', 'diane',
    'redeem', 'confront', 'comfort', 'artist', 'mirage', 'brass', 'expand', 'escort', 'curb', 'recoil', 'anna',
    'bishop', 'sword', 'sonata', 'smear', 'staple', 'tell', 'merlin', 'whip', 'amen', 'apex', 'beast', 'yellows',
    'smack', 'crap', 'harry', 'junk', 'rufus', 'stuff', 'rival', 'vermin', 'snip', 'monarch', 'flair', 'paladin',
    'rugby', 'fortress', 'zodiac', 'stipend', 'equity', 'terminator', 'tara', 'jolt', 'sniper', 'rampart', 'amaze',
    'briton', 'tsar', 'regent', 'admire', 'merit', 'calypso', 'chess', 'endeavour', 'calibre', 'aero', 'citation',
    'combat', 'scourge', 'enforcer', 'hydro', 'tindal', 'applaud', 'adage', 'marshal', 'marshall', 'posse', 'stim',
    'relax', 'quark', 'joust', 'crank', 'dolly', 'rotate', 'tattoo', 'crunch', 'glut', 'pirate', 'sherpa', 'pylon',
    'ripcord', 'ammo', 'barricade', 'demon', 'colt', 'drago', 'fury', 'mustang', 'concord', 'ambush', 'corsair',
    'dragnet', 'kestrel', 'outflank', 'picket', 'pounce', 'kudos', 'lasso', 'scout', 'baroque', 'aria', 'borneo',
    'dart', 'dreamer', 'hocus', 'pegasus', 'morpho', 'polo', 'anon', 'henna', 'lawson', 'malo', 'bloom', 'carol',
    'moment', 'tonal', 'duet', 'solo', 'commodore', 'matador', 'grenade', 'saber', 'crackdown', 'suspend', 'herald',
    'tame', 'smash', 'barrage', 'miracle', 'crossbow', 'vacate', '∑pcbs', 'anti-stress', 'aqua',
    'activated carbon', 'bantu', 'barstar', 'barnase', 'barnase-barstar', 'bishop-kirtman', 'bromelain',
    'bromelia', 'calcitonin', 'carob', 'cocoa butter', 'complement proteins', 'metal-oxide', 'complement proteins',
    'waters', 'aldrich', 'wang', 'xylan', 'transfer rna', 'tough', 'torpedo', 'saccharum', 'saccharina', 'ifn-γ',
    'igf-1', 'starches', 'btx-a', 'bont/a', 'exendin-4', 'snap-25', 'liraglutide', 'tsst-1', 'neuropeptide y',
    'hyaluronic acid', 'il-11', 'phycocyanin', 'gm-csf', 'papp-a', 'moesin', 'endothelin-1', 'adma', 'dm-10', 'ghrp-2',
    'dnase-i', 'phaseolin', 'e-selectin', 'iκb-α', 'protein hydrolysate', 'interferon-γ', 'omalizumab',
    'dextran sulfate sodium', 'avicel cl611', 'diurnal', 'phosphor', 'chorionic gonadotropin', 'orphanin fq', 'ccl3',
    'potato starch', 'protide', 'm1-glucuronide', 'bacp-2', 'glucophage', 'fly ash', 'galanin', '1,3-dpma', 'gst-p(+)',
    'angiotensin i', 'ndp-α-msh', '1,5-dpma', 'nociceptin', 'lipoteichoic acid', 'ifn-gamma', 'actinin-4',
    'margarine', 'cyclones', 'motilin', 'metallothioneins', 'h3n2', 'ip-10', 'chondroitin', 'concanavalin a',
    'p-selectin', 'se-selectin', 'natalizumab', 'kollidon', 'mpo-anca', 'gypsum fibrosum', 'α-msh', 'k-12', 'gana',
    'af-2', 'brs-3-ap', 't-pa', 'rgd peptide', 'ccl3(-/-)', 'α-lactalbumin', 'e-ssa', 'ifn-β', 'ziconotide', 'inas',
    'heat pre', 'an-152', 'chorionic gonadotrophin', 'radixin', 'protanal', 'bloc', 'mops', 'guardian', 'orange',
    'pser-stat3', 'molybdate', 'galsulfase', 'reticulin', 'pyrethrum', 'nociceptin', 'growth hormone releasing hormone',
    'nor-1', 'protamine', 'lipid a', 'ribonucleic acid', 'hirudin', 'c-15', 'sephadex lh-20', 'pro-opiomelanocortin',
    'nida', 'tenax', 'cochineal', 'b-dna', 'arac', 'poly(a)-poly(t)', 'tm-74', 'factor v', 'e3330', 'flonase',
    'defibrotide', 'salix', 'interferon-gamma', 'desmethyl-olanzapine', 'pc-12', 'dpma', 'cope-bd', 'textile', 'ddds',
    'tace', 'lignins', 'gramicidin a', 'il10', 'substance p', 'poloxamer', '12mg', 'flue gas', 'isomaltosaccharide',
    'vinca', 'actinin-4', 'il12', 'siamycin', 'naglazyme', 'bnp-32', 'tea catechin', 'gastrin', 'fp-2', 'somatostatine',
    'dot-silica', 'alpha-t', 'fetal hemoglobin', 'dextrin', 'mica', '5\'-amp', 't-47', 'vinculin', 'lsopc', '3ps',
    '3 ps', 'lead ion', 'french green', 'mg-1', 'rosin', 'rice starch', 'nexus', 'factor vii', 'eculizumab', 'methocel',
    'hydrolyzed polyacrylamide', 'glide', 'hyalgan', 'synvisc', 'octanol-air', 'furfural-water', '90th', 'poly(i:c)',
    'gsno', 'mtcc', 't140', 'sephadex g-75', 'valosin-containing protein', 'deoxyribonucleic acid', 'jasmonate',
    'peony', 'menopur', 'daclizumab', 'gluten proteins', 'the-7', 'microdots', 'b(+)', 'β-endorphin', 'amberlite',
    'supra', 'β-nf', 'optimizer', 'orbit', 'spirit', 'rhombic', 'green tea leaves', 'alum', 'a', 'about', 'again',
    'all', 'almost', 'also', 'although', 'always', 'among', 'an', 'and', 'another', 'any', 'are', 'as', 'at', 'be',
    'because', 'been', 'before', 'being', 'between', 'both', 'but', 'by', 'can', 'could', 'did', 'do', 'does', 'done',
    'due', 'during', 'each', 'either', 'enough', 'especially', 'etc', 'for', 'found', 'from', 'further', 'had', 'has',
    'have', 'having', 'here', 'how', 'however', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'itself', 'just', 'kg',
    'km', 'made', 'mainly', 'make', 'may', 'mg', 'might', 'ml', 'mm', 'most', 'mostly', 'must', 'nearly', 'neither',
    'no', 'nor', 'obtained', 'of', 'often', 'on', 'our', 'overall', 'perhaps', 'pmid', 'quite', 'rather', 'really',
    'regarding', 'seem', 'seen', 'several', 'should', 'show', 'showed', 'shown', 'shows', 'significantly', 'since',
    'so', 'some', 'such', 'than', 'that', 'the', 'their', 'theirs', 'them', 'then', 'there', 'therefore', 'these',
    'they', 'this', 'those', 'through', 'thus', 'to', 'upon', 'use', 'used', 'using', 'various', 'very', 'was', 'we',
    'were', 'what', 'when', 'which', 'while', 'with', 'within', 'without', 'would', 'alcoholic', 'streptavidin',
    'urea nitrogen', 'molten', 'fructose corn syrup', 'human serum albumin', 'Ω127', 'vitamin', 'vitamins',
    'test mixture', 'prothrombinase', 'terpolymer', 'methods', 'section', 'reactivity', 'safety', 'method',
    'experimental', 'discussion', 'synthesis', 'experimental procedures', 'general experimental', 'introduction',
    'results', 'reactions', 'stability', 'multiple', 'crystallography', 'compound', 'syntheses', 'crystal',
    'conclusion', 'references', 'charged', 'nucleotide', 'candidate molecules', 'heteroatoms', 'solvent', 'preparation',
    'formulation', 'omega', 'mol', 'res', 'log in', 'heterocyclic', 'organometallic', 'organometallics', 'nucleobase',
    'organometalloidal', 'acs nano', 'acs omega', 'acs mobile', 'mobile site', 'new titles', 'x close', 'press',

    # Removed: 'gaba', 'gaba(a)', 'alcohol', 'oxide', 'ccl4', 'sugar',
}

#: Regular expressions that define disallowed chemical entity mentions. Note: the entity text is passed as lowercase.
STOP_RES = [
    '^(http|ftp)://',  # URL
    '\.(com|uk|eu|org|net)$',  # URL
    '^\d{4}-\d{3}[\dx]$',  # ISSN
    '^[\w\-\.\+%]{4,} @ \w[\w\-\.]+\.(com?|edu|gov|ac)(\.[\w\-\.]+)?$',  # email
    '^[\d,:\- ]*\d{4,}[\d,:\- ]*$',  # numbers
    '\d{3,} , \d{3,}',  # numbers
    '(\d\d+\.\d+|\d\.\d\d+)',  # numbers
    '\d and \d',  # numbers
    '^(\[\d+\]\s*)+$',  # numbers
    '^\d+$',  # numbers
    '= \d',  # numbers
    '^\+?\d[ \d-]$',  # phone numbers
    'cm-1',  # units
    '^(compound|ligand|chemical|dye|derivative|complex|example|intermediate|product|formulae?)s? [a-z\d]{1,3}',  # labels
    '(b3lyp|31g\(d,p\)|td-dft)',
    'et al\.?$',
    '^(ep|wo|us)\s*\d\s*\d\d[\d\s]*([AB]\d)?($|\s*and)',  # patent numbers
    '^(pre|post)-\d\d\d\d',  # common mistake
    '\d ml$',  # properties
    '\.(png|gif|jpg|txt|html|docx?|xlsx?)$',  # File extensions
    '^(tel|fax)\s*:?\s*\+?\s*\d',  # phone numbers
]

#: Regular expressions defining collections of words that should be split if joined by hyphens or -to-
SPLITS = [
    '^(actinium|aluminium|aluminum|americium|antimony|argon|arsenic|astatine|barium|berkelium|beryllium|bismuth|bohrium|boron|bromine|cadmium|caesium|calcium|californium|carbon|cerium|cesium|chlorine|chromium|cobalt|copernicium|copper|curium|darmstadtium|dubnium|dysprosium|einsteinium|erbium|europium|fermium|flerovium|fluorine|francium|gadolinium|gallium|germanium|gold|hafnium|hassium|helium|holmium|hydrargyrum|hydrogen|indium|iodine|iridium|iron|kalium|krypton|lanthanum|lawrencium|lead|lithium|livermorium|lutetium|magnesium|manganese|meitnerium|mendelevium|mercury|molybdenum|natrium|neodymium|neon|neptunium|nickel|niobium|nitrogen|nobelium|osmium|oxygen|palladium|phosphorus|platinum|plumbum|plutonium|polonium|potassium|praseodymium|promethium|protactinium|radium|radon|rhenium|rhodium|roentgenium|rubidium|ruthenium|rutherfordium|samarium|scandium|seaborgium|selenium|silicon|silver|sodium|stannum|stibium|strontium|sulfur|tantalum|technetium|tellurium|terbium|thallium|thorium|thulium|tin|titanium|tungsten|ununoctium|ununpentium|ununseptium|ununtrium|uranium|vanadium|wolfram|xenon|ytterbium|yttrium|zinc|zirconium)$',
    '^(Ag|Al|Ar|Au|Br|Cd|Cl|Co|Cu|Fe|Gd|Ge|Hg|Kr|Li|Mg|Na|Ne|Ni|Pb|Pd|Pt|Ru|Sb|Si|Sn|Ti|Xe|Zn|Zr|Zn)$',
    '^(iodide|triiodide|nitrite|nitrate)$',
    '^(graphane|graphene|carbon|silica|glucose)$',
    '^(sugar|phospate)$',
    '^(azide|alkyne|alkene|alkane)$',
    '^(arginine|cysteine|glycine|aspartic acid|glutamate|dopamine|serotonin|acetone|methanol|ethanol|EtOH|MeOH|AcOEt|melatonin|leucine|alanine|histidine|isoleucine|lysine|threonine|tryptophan|nicotine|gentamicin|ATP|FITC|biotin|tamoxifen|catechin|asparagine)$',
    '^(Ala|Arg|Asn|Asp|Cys|Glu|Gln|Gly|His|Ile|Leu|Lys|Met|Phe|Pro|Ser|Thr|Trp|Tyr|Val)(?:\(?\d+\)?)?$',
    '^(\(?1\)?H|\(?1[45]\)?N|\(?1[234]\)?C|\(?19\)?F)$',
    '^(F|Cl|Zn[OS]|H\(?2\)?O(\(?2\)?)?|Ni\(OH\)\(?2\)?|(NiF|SnO|TiO|NO)\(?2\)?|(Al|Y|Fe)\(?2\)?O\(?3\)?|CaCO\(?3\)?)$',
    '^(ester|amide)$'
]

# Special case boundary adjustments (only used for cems output)
SPECIALS = [
    '(?:^|-)([CONS])-\w+ases?$',
    '(?:^|-)(S)-(sulfonates?)$',
    '^(GABA)-(benzodiazepine|A)$',
    '^(ZnO|Au|Ag)-NPs?$',  # Nanoparticles
    '^(UDP)-.+ase$',  # UDP-enzyme
    '^(UDP)-(.+)$',  # UDP-other
    '^(N|S)-(?:acetyl|nitros|hydroxyl)(?:ation|ated)$',
    '^-(NO2|CH3|F|Cl|Br|OH)$',  # Remove leading dash
    '^(.+)[²³]?⁺$',  # Remove trailing superscript plus \u207a
    '^δ(\([^\(]+\).+)$',  # Remove leading δ \u03b4 but keep opening bracket if the closing bracket is within name
    '^δ\((.+)\)?$',  # Otherwise remove leading δ \u03b4 and opening bracket
    '^(Ala|Arg|Asn|Asp|Cys|Glu|Gln|Gly|His|Ile|Leu|Lys|Met|Phe|Pro|Ser|Thr|Trp|Tyr|Val)-?\(?\d+\)?$',
    '^(\w{4,})(?:\)?-to-\(?|\+)(\w{4,})$',
    '^(.+)(?:-| )(?:linker|activated|gated|mediated|containing|doped|labeled|coated|enriched|catalyzed|modified|···)(?:-| )(.+)$',
    '^(.+)\s?···\s?(.+)$',
    '^(.+[A-Z])\+([A-Z].+)$',  # Split on plus surrounded by uppercase alpha
    '^([^\(\)]+\w)\+(\w[^\(\)]+)$',  # Split on plus surrounded by any letter or number provided no brackets
    '^(.+\(\d+[A-Za-z]*\)) and (.+)$',  # Split on bracketed alphanumeric label followed by and
    '^(.+)\.$',  # Trim off final punctuation

    #'^((?:.* )acid)-(.+)$',
    # TODO: Slash-separated names? ', ' separated? ' and ' separated? Probably have a min length limit
]


class CiDictCemTagger(DictionaryTagger):
    """Case-insensitive CEM dictionary tagger."""
    lexicon = ChemLexicon()
    model = 'models/cem_dict-1.0.pickle'


class CsDictCemTagger(DictionaryTagger):
    """Case-sensitive CEM dictionary tagger."""
    lexicon = ChemLexicon()
    model = 'models/cem_dict_cs-1.0.pickle'
    case_sensitive = True


class CrfCemTagger(CrfTagger):
    """"""
    model = 'models/cem_crf_chemdner_cemp-1.0.pickle'
    lexicon = ChemLexicon()
    clusters = True

    params = {
        'c1': 1.0,  # Coefficient for L1 regularization (OWL-QN). Default 0.
        'c2': 0.001,  # Coefficient for L2 regularization. Default 1.
        'max_iterations': 200,  # The maximum number of iterations for L-BFGS optimization. Default INT_MAX.
        'feature.possible_transitions': False,  # Force to generate all possible transition features. Default False.
        'feature.possible_states': False,  # Force to generate all possible state features. Default False.
    }

    def _get_features(self, tokens, i):
        """"""
        token, tag = tokens[i]
        w = self.lexicon[token]
        features = [
            'w.shape=%s' % w.shape,
            'w.normalized=%s' % w.normalized,
            'w.lower=%s' % w.lower,
            'w.length=%s' % w.length,
            'w.digit_count=%s' % w.digit_count,
            'w.upper_count=%s' % w.upper_count,
            'w.lower_count=%s' % w.lower_count,
            'w.tag=%s' % tag,
        ]
        if w.like_number:
            features.append('w.like_number')
        elif w.is_punct:
            features.append('w.is_punct')
        elif w.like_url:
            features.append('w.like_url')
        else:
            features.extend([
                'w.suffix1=%s' % w.lower[-1:],
                'w.suffix2=%s' % w.lower[-2:],
                'w.suffix3=%s' % w.lower[-3:],
                'w.suffix4=%s' % w.lower[-4:],
                'w.suffix5=%s' % w.lower[-5:],
                'w.prefix1=%s' % w.lower[:1],
                'w.prefix2=%s' % w.lower[:2],
                'w.prefix3=%s' % w.lower[:3],
                'w.prefix4=%s' % w.lower[:4],
                'w.prefix5=%s' % w.lower[:5],
            ])
            if w.is_alpha:
                features.append('w.is_alpha')
            elif w.is_hyphenated:
                features.append('w.is_hyphenated')
            if w.is_upper:
                features.append('w.is_upper')
            elif w.is_lower:
                features.append('w.is_lower')
            elif w.is_title:
                features.append('w.is_title')
        if self.clusters and w.cluster:
            features.extend([
                'w.cluster4=%s' % w.cluster[:4],
                'w.cluster6=%s' % w.cluster[:6],
                'w.cluster10=%s' % w.cluster[:10],
                'w.cluster20=%s' % w.cluster[:20],
            ])
        # Add features for previous tokens if present
        if i > 0:
            p1token, p1tag = tokens[i-1]
            p1 = self.lexicon[p1token]
            features.extend([
                'p1.lower=%s' % p1.lower,
                'p1.shape=%s' % p1.shape,
                'p1.tag=%s' % p1tag,
            ])
            if not (p1.like_number or p1.is_punct or p1.like_url):
                features.append('p1:suffix3=%s' % p1.lower[-3:])
            if self.clusters and p1.cluster:
                features.extend([
                    'p1.cluster4=%s' % p1.cluster[:4],
                    'p1.cluster6=%s' % p1.cluster[:6],
                    'p1.cluster10=%s' % p1.cluster[:10],
                    'p1.cluster20=%s' % p1.cluster[:20],
                ])
            if i > 1:
                p2token, p2tag = tokens[i-2]
                p2 = self.lexicon[p2token]
                features.extend([
                    'p2.lower=%s' % p2.lower,
                    'p2.shape=%s' % p2.shape,
                    'p2.tag=%s' % p2tag,
                ])
                if self.clusters and p2.cluster:
                    features.extend([
                        'p2.cluster4=%s' % p2.cluster[:4],
                        'p2.cluster6=%s' % p2.cluster[:6],
                        'p2.cluster10=%s' % p2.cluster[:10],
                        'p2.cluster20=%s' % p2.cluster[:20],
                    ])
        # Add features for next tokens if present
        end = len(tokens) - 1
        if i < end:
            n1token, n1tag = tokens[i+1]
            n1 = self.lexicon[n1token]
            features.extend([
                'n1.lower=%s' % n1.lower,
                'n1.shape=%s' % n1.shape,
                'n1.tag=%s' % n1tag,
            ])
            if not (n1.like_number or n1.is_punct or n1.like_url):
                features.append('n1.suffix3=%s' % n1.lower[-3:])
            if self.clusters and n1.cluster:
                features.extend([
                    'n1.cluster4=%s' % n1.cluster[:4],
                    'n1.cluster6=%s' % n1.cluster[:6],
                    'n1.cluster10=%s' % n1.cluster[:10],
                    'n1.cluster20=%s' % n1.cluster[:20],
                ])
            if i < end - 1:
                n2token, n2tag = tokens[i+2]
                n2 = self.lexicon[n2token]
                features.extend([
                    'n2.lower=%s' % n2.lower,
                    'n2.shape=%s' % n2.shape,
                    'n2.tag=%s' % n2tag,
                ])
                if self.clusters and n2.cluster:
                    features.extend([
                        'n2.cluster4=%s' % n2.cluster[:4],
                        'n2.cluster6=%s' % n2.cluster[:6],
                        'n2.cluster10=%s' % n2.cluster[:10],
                        'n2.cluster20=%s' % n2.cluster[:20],
                    ])
        if i == 0:
            features.append('-firsttoken-')
        elif i == 1:
            features.append('-secondtoken-')
        elif i == end - 1:
            features.append('-secondlasttoken-')
        elif i == end:
            features.append('-lasttoken-')
        return features


class CemTagger(BaseTagger):
    """Return the combined output of a number of chemical entity taggers."""

    #: The individual chemical entity taggers to use.
    taggers = [CrfCemTagger(), CiDictCemTagger(), CsDictCemTagger()]
    lexicon = ChemLexicon()

    def _in_stoplist(self, entity):
        """Return True if the entity is in the stoplist."""
        for suffix in IGNORE_SUFFIX:
            if entity.endswith(suffix):
                entity = entity[:-len(suffix)]
        for prefix in IGNORE_PREFIX:
            if entity.startswith(prefix):
                entity = entity[len(prefix):]
        if entity in STOPLIST:
            return True
        # log.debug('Entity: %s', entity)
        for stop_re in STOP_RES:
            if re.search(stop_re, entity):
                log.debug('Killed: %s', entity)
                return True

    def tag(self, tokens):
        """Run individual chemical entity mention taggers and return union of matches, with some postprocessing."""
        # Combine output from individual taggers
        tags = [None] * len(tokens)
        just_tokens = [t[0] for t in tokens]
        for tagger in self.taggers:
            tag_gen = tagger.tag(tokens) if isinstance(tagger, CrfCemTagger) else tagger.tag(just_tokens)
            for i, (token, newtag) in enumerate(tag_gen):
                if newtag == 'I-CM' and not (i == 0 or tag_gen[i - 1][1] not in {'B-CM', 'I-CM'}):
                    tags[i] = 'I-CM'  # Always overwrite I-CM
                elif newtag == 'B-CM' and tags[i] is None:
                    tags[i] = 'B-CM'  # Only overwrite B-CM over None
        # Postprocess the combined output
        for i, tag in enumerate(tags):
            token, pos = tokens[i]
            lex = self.lexicon[token]
            nexttag = tags[i+1] if i < len(tags) - 1 else None
            # Trim disallowed first tokens
            if tag == 'B-CM' and lex.lower in STRIP_START:
                tags[i] = None
                if nexttag == 'I-CM':
                    tags[i+1] = 'B-CM'
            # Trim disallowed final tokens
            if nexttag is None and lex.lower in STRIP_END:
                tags[i] = None
        # Filter certain entities
        for i, tag in enumerate(tags):
            token, pos = tokens[i]
            if tag == 'B-CM':
                entity_tokens = [self.lexicon[token].lower]
                end_i = i + 1
                for j, subsequent in enumerate(tags[i+1:]):
                    if subsequent == 'I-CM':
                        end_i += 1
                        entity_tokens.append(self.lexicon[tokens[i+j+1][0]].lower)
                    else:
                        break

                # Fix combined '1H NMR' on end  # TODO: Also 13C, etc.?
                if len(entity_tokens) > 2 and entity_tokens[-1] == 'nmr' and entity_tokens[-2] == '1h':
                    tags[end_i-2] = 'B-CM'
                    tags[end_i-1] = None
                    entity_tokens = entity_tokens[:-2]

                entity = ' '.join(entity_tokens)
                if any(e in STOP_TOKENS for e in entity_tokens) or self._in_stoplist(entity):
                    tags[i:end_i] = [None] * (end_i - i)
                else:
                    bl = bracket_level(entity)
                    # Try and add on brackets in neighbouring tokens if they form part of the name
                    # TODO: Check bracket type matches before adding on
                    if bl == 1 and len(tokens) > end_i and bracket_level(tokens[end_i][0]) == -1:
                        #print('BLADJUST: %s - %s' % (entity, tokens[end_i][0]))
                        tags[end_i] = 'I-CM'
                    elif bl == -1 and i > 0 and bracket_level(tokens[i-1][0]) == 1:
                        #print('BLADJUST: %s - %s' % (tokens[i-1][0], entity))
                        tags[i-1] = 'B-CM'
                        tags[i] = 'I-CM'
                    elif not bracket_level(entity) == 0:
                        # Filter entities that overall don't have balanced brackets
                        tags[i:end_i] = [None] * (end_i - i)
                    else:
                        # Remove bracketed alphanumeric from end
                        if len(entity_tokens) >= 4 and entity_tokens[-1] == ')' and entity_tokens[-3] == '(':
                            if re.match('^(\d{1,2}[A-Za-z]?|I|II|III|IV|V|VI|VII|VIII|IX)$', entity_tokens[-2]):
                                log.debug('Removing %s from end of CEM', entity_tokens[-2])
                                tags[end_i-3:end_i] = [None, None, None]
        tokentags = zip(tokens, tags)
        return tokentags

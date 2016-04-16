# -*- coding: utf-8 -*-
"""
chemdataextractor.nlp.pos
~~~~~~~~~~~~~~~~~~~~~~~~~

Part-of-speech tagging.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging

from .lexicon import ChemLexicon
from .tag import ApTagger, CrfTagger


log = logging.getLogger(__name__)


#: Complete set of POS tags. Ordered by decreasing frequency in WSJ corpus.
TAGS = [
    'NN',  # NN : 174028
    'IN',  # IN : 132241
    'NNP',  # NNP : 115653
    'DT',  # DT : 101067
    'NNS',  # NNS : 74257
    'JJ',  # JJ : 71238
    ',',  # , : 60488
    '.',  # . : 48689
    'CD',  # CD : 47449
    'RB',  # RB : 40004
    'VBD',  # VBD : 37236
    'VB',  # VB : 32781
    'CC',  # CC : 29607
    'VBN',  # VBN : 26807
    'VBZ',  # VBZ : 26335
    'PRP',  # PRP : 21368
    'VBG',  # VBG : 18693
    'TO',  # TO : 16252
    'VBP',  # VBP : 15370
    'HYPH',  # HYPH : 14789
    'MD',  # MD : 12010
    'POS',  # POS : 10844
    'PRP$',  # PRP$ : 10252
    '$',  # $ : 9217
    '``',  # `` : 8879
    '\'\'',  # '' : 8649
    ':',  # : : 6074
    'WDT',  # WDT : 5824
    'JJR',  # JJR : 4370
    'RP',  # RP : 3509
    'NNPS',  # NNPS : 3186
    'WP',  # WP : 2885
    'WRB',  # WRB : 2629
    'RBR',  # RBR : 2189
    'JJS',  # JJS : 2129
    '-RRB-',  # -RRB- : 1689
    '-LRB-',  # -LRB- : 1672
    'EX',  # EX : 1094
    'RBS',  # RBS : 946
    'PDT',  # PDT : 504
    'SYM',  # SYM : 379
    'FW',  # FW : 279
    'WP$',  # WP$ : 219
    'UH',  # UH : 127
    'LS',  # LS : 102
    'NFP',  # NFP : 14
    'AFX',  # AFX : 4
]


class ApPosTagger(ApTagger):
    """Greedy Averaged Perceptron POS tagger trained on WSJ corpus.

    """
    model = 'models/pos_ap_wsj_nocluster-1.0.pickle'
    clusters = False

    def _get_features(self, i, context, prev, prev2):
        """Map tokens into a feature representation."""
        w = self.lexicon[context[i]]
        features = [
            'bias',
            'w:shape=%s' % w.shape,
            'w:lower=%s' % w.lower,
            'p1:tag=%s' % prev,
            'p2:tag=%s' % prev2,
            'p1:tag+w:lower=%s+%s' % (prev, w.lower),
            'p1:tag+p2:tag=%s+%s' % (prev, prev2),
        ]
        if w.like_number:
            features.append('w:like_number')
        elif w.is_punct:
            features.append('w:is_punct')
        elif w.like_url:
            features.append('w:like_url')
        else:
            features.extend([
                'w:suffix2=%s' % w.lower[-2:],
                'w:suffix3=%s' % w.lower[-3:],
                'w:suffix4=%s' % w.lower[-4:],
                'w:suffix5=%s' % w.lower[-5:],
                'w:prefix1=%s' % w.lower[:1],
                'w:prefix2=%s' % w.lower[:2],
                'w:prefix3=%s' % w.lower[:3],
            ])
            if w.is_alpha:
                features.append('w:is_alpha')
            elif w.is_hyphenated:
                features.append('w:is_hyphenated')
            if w.is_upper:
                features.append('w:is_upper')
            elif w.is_lower:
                features.append('w:is_lower')
            elif w.is_title:
                features.append('w:is_title')
        if self.clusters and w.cluster:
            features.extend([
                'w:cluster4=%s' % w.cluster[:4],
                'w:cluster6=%s' % w.cluster[:6],
                'w:cluster10=%s' % w.cluster[:10],
                'w:cluster20=%s' % w.cluster[:20],
            ])
        # Add features for previous tokens if present
        if i > 0:
            p1 = self.lexicon[context[i-1]]
            features.extend([
                'p1:lower=%s' % p1.lower,
                'p1:shape=%s' % p1.shape,
            ])
            if not (p1.like_number or p1.is_punct or p1.like_url):
                features.append('p1:suffix3=%s' % p1.lower[-3:])
            if self.clusters and p1.cluster:
                features.extend([
                    'p1:cluster4=%s' % p1.cluster[:4],
                    'p1:cluster6=%s' % p1.cluster[:6],
                    'p1:cluster10=%s' % p1.cluster[:10],
                    'p1:cluster20=%s' % p1.cluster[:20],
                ])
            if i > 1:
                p2 = self.lexicon[context[i-2]]
                features.extend([
                    'p2:lower=%s' % p2.lower,
                    'p2:shape=%s' % p2.shape,
                ])
                if self.clusters and p2.cluster:
                    features.extend([
                        'p2:cluster4=%s' % p2.cluster[:4],
                        'p2:cluster6=%s' % p2.cluster[:6],
                        'p2:cluster10=%s' % p2.cluster[:10],
                        'p2:cluster20=%s' % p2.cluster[:20],
                    ])
        # Add features for next tokens if present
        end = len(context) - 1
        if i < end:
            n1 = self.lexicon[context[i+1]]
            features.extend([
                'n1:lower=%s' % n1.lower,
                'n1:shape=%s' % n1.shape
            ])
            if not (n1.like_number or n1.is_punct or n1.like_url):
                features.append('n1:suffix3=%s' % n1.lower[-3:])
            if self.clusters and n1.cluster:
                features.extend([
                    'n1:cluster4=%s' % n1.cluster[:4],
                    'n1:cluster6=%s' % n1.cluster[:6],
                    'n1:cluster10=%s' % n1.cluster[:10],
                    'n1:cluster20=%s' % n1.cluster[:20],
                ])
            if i < end - 1:
                n2 = self.lexicon[context[i+2]]
                features.extend([
                    'n2:lower=%s' % n2.lower,
                    'n2:shape=%s' % n2.shape
                ])
                if self.clusters and n2.cluster:
                    features.extend([
                        'n2:cluster4=%s' % n2.cluster[:4],
                        'n2:cluster6=%s' % n2.cluster[:6],
                        'n2:cluster10=%s' % n2.cluster[:10],
                        'n2:cluster20=%s' % n2.cluster[:20],
                    ])
        # Add position features
        if i == 0:
            features.append('-firsttoken-')
        elif i == 1:
            features.append('-secondtoken-')
        elif i == end - 1:
            features.append('-secondlasttoken-')
        elif i == end:
            features.append('-lasttoken-')
        return features


class ChemApPosTagger(ApPosTagger):
    """Greedy Averaged Perceptron POS tagger trained on both WSJ and GENIA corpora.

    Uses features based on word clusters from chemistry text.
    """
    model = 'models/pos_ap_wsj_genia-1.0.pickle'
    lexicon = ChemLexicon()
    clusters = True


class CrfPosTagger(CrfTagger):
    """"""
    model = 'models/pos_crf_wsj_nocluster-1.0.pickle'
    clusters = False

    def _get_features(self, tokens, i):
        """"""
        token = tokens[i]
        w = self.lexicon[token]
        features = [
            'w.shape=%s' % w.shape,
            # 'w.normalized=%s' % w.normalized,
            'w.lower=%s' % w.lower,
            'w.length=%s' % w.length,
        ]
        if w.like_number:
            features.append('w.like_number')
        elif w.is_punct:
            features.append('w.is_punct')
        # elif w.like_url:
        #     features.append('w.like_url')
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
            p1token = tokens[i-1]
            p1 = self.lexicon[p1token]
            features.extend([
                'p1.lower=%s' % p1.lower,
                'p1.lower=%s+w.lower=%s' % (p1.lower, w.lower),
                'p1.shape=%s' % p1.shape,
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
                p2token = tokens[i-2]
                p2 = self.lexicon[p2token]
                features.extend([
                    'p2.lower=%s' % p2.lower,
                    'p2.lower=%s+p1.lower=%s' % (p2.lower, p1.lower),
                    'p2.lower=%s+p1.lower=%s+w.lower=%s' % (p2.lower, p1.lower, w.lower),
                    'p2.shape=%s' % p2.shape,
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
            n1token = tokens[i+1]
            n1 = self.lexicon[n1token]
            features.extend([
                'n1.lower=%s' % n1.lower,
                'w.lower=%s+n1.lower=%s' % (w.lower, n1.lower),
                'n1.shape=%s' % n1.shape,
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
                n2token = tokens[i+2]
                n2 = self.lexicon[n2token]
                features.extend([
                    'n2.lower=%s' % n2.lower,
                    'n1.lower=%s+n2.lower=%s' % (n1.lower, n2.lower),
                    'w.lower=%s+n1.lower=%s+n2.lower=%s' % (w.lower, n1.lower, n2.lower),
                    'n2.shape=%s' % n2.shape,
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


class ChemCrfPosTagger(CrfPosTagger):
    """"""
    model = 'models/pos_crf_wsj_genia-1.0.pickle'
    lexicon = ChemLexicon()
    clusters = True

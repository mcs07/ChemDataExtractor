# -*- coding: utf-8 -*-
"""
chemdataextractor.nlp.corpus
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tools for reading and writing text corpora.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import gc

from nltk.corpus import ChunkedCorpusReader, TaggedCorpusReader, PlaintextCorpusReader, BracketParseCorpusReader
from nltk.corpus.reader.util import read_line_block, tagged_treebank_para_block_reader
from nltk.tokenize import RegexpTokenizer


class LazyCorpusLoader(object):
    """Derived from NLTK LazyCorpusLoader."""
    def __init__(self, name, reader_cls, *args, **kwargs):
        from nltk.corpus.reader.api import CorpusReader
        assert issubclass(reader_cls, CorpusReader)
        self.__name = self.__name__ = name
        self.__reader_cls = reader_cls
        self.__args = args
        self.__kwargs = kwargs

    def __load(self):
        # Find the corpus root directory.
        corpus = self.__reader_cls(*self.__args, **self.__kwargs)
        args, kwargs = self.__args, self.__kwargs
        name, reader_cls = self.__name, self.__reader_cls
        self.__dict__ = corpus.__dict__
        self.__class__ = corpus.__class__

        def _unload(self):
            lazy_reader = LazyCorpusLoader(name, reader_cls, *args, **kwargs)
            self.__dict__ = lazy_reader.__dict__
            self.__class__ = lazy_reader.__class__
            gc.collect()

        self._unload = _make_bound_method(_unload, self)

    def __getattr__(self, attr):
        if attr == '__bases__':
            raise AttributeError("LazyCorpusLoader object has no attribute '__bases__'")
        self.__load()
        return getattr(self, attr)

    def __repr__(self):
        return '<%s in %r (not loaded yet)>' % (self.__reader_cls.__name__, '.../corpora/'+self.__name)

    def _unload(self):
        pass


def _make_bound_method(func, self):
    """Magic for creating bound methods (used for _unload)."""
    class Foo(object):
        def meth(self): pass
    f = Foo()
    bound_method = type(f.meth)
    try:
        return bound_method(func, self, self.__class__)
    except TypeError: # python3
        return bound_method(func, self)


def _read_chemdner_line_block(stream):
    toks = []
    for i in range(20):
        line = stream.readline()
        if not line: return toks
        pmid, title, abstract = line.split('\t')
        toks.append(title.strip())
        toks.append(abstract.strip())
    return toks

#: Entire WSJ corpus (English News Text Treebank: Penn Treebank Revised, LDC2015T13)
wsj = LazyCorpusLoader(
    'wsj_training',
    BracketParseCorpusReader,
    'data/eng_news_txt_tbnk-ptb_revised/data/penntree',
    r'\d\d/wsj_.*\.tree',
    encoding='ascii'
)

#: WSJ corpus sections 0-18 (English News Text Treebank: Penn Treebank Revised, LDC2015T13)
wsj_training = LazyCorpusLoader(
    'wsj_training',
    BracketParseCorpusReader,
    'data/eng_news_txt_tbnk-ptb_revised/data/penntree',
    r'(00|01|02|03|04|05|06|07|08|09|10|11|12|13|14|15|16|17|18)/wsj_.*\.tree',
    encoding='ascii'
)

#: WSJ corpus sections 19-21 (English News Text Treebank: Penn Treebank Revised, LDC2015T13)
wsj_development = LazyCorpusLoader(
    'wsj_development',
    BracketParseCorpusReader,
    'data/eng_news_txt_tbnk-ptb_revised/data/penntree',
    r'(19|20|21)/wsj_.*\.tree',
    encoding='ascii'
)

#: WSJ corpus sections 22-24 (English News Text Treebank: Penn Treebank Revised, LDC2015T13)
wsj_evaluation = LazyCorpusLoader(
    'wsj_evaluation',
    BracketParseCorpusReader,
    'data/eng_news_txt_tbnk-ptb_revised/data/penntree',
    r'(22|23|24)/wsj_.*\.tree',
    encoding='ascii'
)

#: WSJ corpus sections 0-18 (treebank2)
treebank2_training = LazyCorpusLoader(
    'treebank2_training',
    ChunkedCorpusReader,
    'data/wsj-pos-training',
    r'wsj_.*\.pos',
    sent_tokenizer=RegexpTokenizer(r'(?<=/\.)\s*(?![^\[]*\])', gaps=True),
    para_block_reader=tagged_treebank_para_block_reader, encoding='ascii'
)

#: WSJ corpus sections 19-21 (treebank2)
treebank2_development = LazyCorpusLoader(
    'treebank2_development',
    ChunkedCorpusReader,
    'data/wsj-pos-development',
    r'wsj_.*\.pos',
    sent_tokenizer=RegexpTokenizer(r'(?<=/\.)\s*(?![^\[]*\])', gaps=True),
    para_block_reader=tagged_treebank_para_block_reader, encoding='ascii'
)

#: WSJ corpus sections 22-24 (treebank2)
treebank2_evaluation = LazyCorpusLoader(
    'treebank2_evaluation',
    ChunkedCorpusReader,
    'data/wsj-pos-evaluation',
    r'wsj_.*\.pos',
    sent_tokenizer=RegexpTokenizer(r'(?<=/\.)\s*(?![^\[]*\])', gaps=True),
    para_block_reader=tagged_treebank_para_block_reader, encoding='ascii'
)

#: First 80% of GENIA POS-tagged corpus
genia_training = LazyCorpusLoader(
    'genia_training',
    TaggedCorpusReader,
    'data/genia-pos-training',
    'genia-pos-training.txt',
    word_tokenizer=RegexpTokenizer(r'\n', gaps=True),
    sent_tokenizer=RegexpTokenizer('====================\n', gaps=True)
)

#: Last 20% of GENIA POS-tagged corpus
genia_evaluation = LazyCorpusLoader(
    'genia_evaluation',
    TaggedCorpusReader,
    'data/genia-pos-evaluation',
    'genia-pos-evaluation.txt',
    word_tokenizer=RegexpTokenizer(r'\n', gaps=True),
    sent_tokenizer=RegexpTokenizer('====================\n', gaps=True)
)

medpost = LazyCorpusLoader(
    'medpost',
    TaggedCorpusReader,
    'data/medpost',
    'tag_.+\.pos',
)

medpost_training = LazyCorpusLoader(
    'medpost_training',
    TaggedCorpusReader,
    'data/medpost-pos-training',
    'medpost-pos-training.txt',
)

medpost_evaluation = LazyCorpusLoader(
    'medpost_evaluation',
    TaggedCorpusReader,
    'data/medpost-pos-evaluation',
    'medpost-pos-evaluation.txt',
)

cde_tokensc = LazyCorpusLoader(
    'cde_tokensc',
    PlaintextCorpusReader,
    'data/cde-tokens',
    'cde-tokens-norm.txt',
    word_tokenizer=RegexpTokenizer(r' ', gaps=True),
    sent_tokenizer=RegexpTokenizer('\n', gaps=True),
    para_block_reader=read_line_block
)

chemdner_training = LazyCorpusLoader(
    'chemdner_training',
    PlaintextCorpusReader,
    'data/cde-ner',
    'training.txt',
    word_tokenizer=RegexpTokenizer(r' ', gaps=True),
    sent_tokenizer=RegexpTokenizer('\n', gaps=True),
    para_block_reader=_read_chemdner_line_block
)



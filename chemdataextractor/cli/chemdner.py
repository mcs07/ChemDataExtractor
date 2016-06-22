# -*- coding: utf-8 -*-
"""
chemdataextractor.cli.chemdner
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Command line tools for dealing with CHEMDNER corpus.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from collections import defaultdict
import sys

import click
import six

from ..doc.document import Document
from ..doc.text import Title, Paragraph


@click.group(name='chemdner')
@click.pass_context
def chemdner_cli(ctx):
    """CHEMDNER commands."""
    pass


@chemdner_cli.command()
@click.argument('annotations', type=click.File('r', encoding='utf8'), required=True)
@click.option('--gout', '-g', type=click.File('w', encoding='utf8'), help='Gold annotations output.', required=True)
@click.pass_obj
def prepare_gold(ctx, annotations, gout):
    """Prepare bc-evaluate gold file from annotations supplied by CHEMDNER."""
    click.echo('chemdataextractor.chemdner.prepare_gold')
    for line in annotations:
        pmid, ta, start, end, text, category = line.strip().split('\t')
        gout.write('%s\t%s:%s:%s\n' % (pmid, ta, start, end))


@chemdner_cli.command()
@click.argument('input', type=click.File('r', encoding='utf8'), required=True)
@click.option('--annotations', '-a', type=click.File('r', encoding='utf8'), required=True)
@click.option('--tout', '-t', type=click.File('w', encoding='utf8'), help='Token/POS/IOB file.', required=True)
@click.option('--lout', '-l', type=click.File('w', encoding='utf8'), help='Token/IOB file.', required=True)
@click.pass_obj
def prepare_tokens(ctx, input, annotations, tout, lout):
    """Prepare tokenized and tagged corpus file from those supplied by CHEMDNER."""
    click.echo('chemdataextractor.chemdner.prepare_tokens')
    # Collect the annotations into a dict
    anndict = defaultdict(list)
    for line in annotations:
        pmid, ta, start, end, text, category = line.strip().split('\t')
        anndict[(pmid, ta)].append((int(start), int(end), text))
    # Process the corpus
    for line in input:
        pmid, title, abstract = line.strip().split(u'\t')
        for t, section, anns in [(Title(title), 'T', anndict.get((pmid, 'T'), [])), (Paragraph(abstract), 'A', anndict.get((pmid, 'A'), []))]:
            # Write our tokens with POS and IOB tags
            tagged = _prep_tags(t, anns)
            for i, sentence in enumerate(tagged):
                tout.write(u' '.join(['/'.join([token, tag, label]) for token, tag, label in sentence]))
                lout.write(u' '.join(['/'.join([token, label]) for token, tag, label in sentence]))
                tout.write(u'\n')
                lout.write(u'\n')
            tout.write(u'\n')
            lout.write(u'\n')


def _prep_tags(t, annotations):
    """Apply IOB chemical entity tags and POS tags to text."""
    tags = [['O' for _ in sent.tokens] for sent in t.sentences]
    for start, end, text in annotations:
        done_first = False
        for i, sent in enumerate(t.sentences):
            for j, token in enumerate(sent.tokens):
                if start <= token.start < end or start < token.end <= end:
                    # Token start or end occurs within the annotation
                    tags[i][j] = 'I-CM' if done_first else 'B-CM'
                    done_first = True
    tagged = [[(token[0], token[1], tags[i][j]) for j, token in enumerate(sentence.pos_tagged_tokens)] for i, sentence in enumerate(t.sentences)]
    return tagged


@chemdner_cli.command()
@click.option('--corpus', '-c', type=click.File('r', encoding='utf8'), required=True)
@click.option('--output', '-o', type=click.File('w', encoding='utf8'), help='Output file.', default=sys.stdout)
@click.pass_obj
def tag(ctx, corpus, output):
    """Tag chemical entities and write CHEMDNER annotations predictions file."""
    click.echo('chemdataextractor.chemdner.tag')
    for line in corpus:
        pmid, title, abstract = line.strip().split(u'\t')
        # print(pmid)
        counter = 1
        d = Document(Title(title), Paragraph(abstract))
        for t, section in [(d.elements[0], 'T'), (d.elements[1], 'A')]:
            for cem in t.cems:
                code = u'%s:%s:%s' % (section, cem.start, cem.end)
                output.write(u'\t'.join([pmid, code, six.text_type(counter), '1']))
                output.write(u'\n')
                counter += 1

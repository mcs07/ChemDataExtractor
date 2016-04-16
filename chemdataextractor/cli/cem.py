# -*- coding: utf-8 -*-
"""
chemdataextractor.cli.cem
~~~~~~~~~~~~~~~~~~~~~~~~~

Chemical entity mention (CEM) commands.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import click

from ..nlp.cem import CrfCemTagger


@click.group()
@click.pass_context
def cem(ctx):
    """Chemical NER commands."""
    pass


@cem.command()
@click.argument('input', type=click.File('r', encoding='utf8'), required=True)
@click.option('--output', '-o', help='Output model file.', required=True)
@click.option('--clusters/--no-clusters', help='Whether to use cluster features', default=True)
@click.pass_obj
def train_crf(ctx, input, output, clusters):
    """Train CRF CEM recognizer."""
    click.echo('chemdataextractor.crf.train')
    sentences = []
    for line in input:
        sentence = []
        for t in line.split():
            token, tag, iob = t.rsplit('/', 2)
            sentence.append(((token, tag), iob))
        if sentence:
            sentences.append(sentence)

    tagger = CrfCemTagger(clusters=clusters)
    tagger.train(sentences, output)


# @cem.command()
# @click.option('--corpus', '-c', type=click.File('r', encoding='utf8'), required=True)
# @click.option('--gold', '-c', type=click.File('r', encoding='utf8'), required=True)
# @click.pass_obj
# def evaluate(ctx, corpus, gold):
#     """Evaluate performance on CHEMDNER corpus against gold annotations."""
#     click.echo('chemdataextractor.ner.evaluate')
#
#     # Collect the gold annotations into a dict
#     anndict = defaultdict(list)
#     for line in gold:
#         pmid, ta, start, end, text, category = line.strip().split('\t')
#         anndict[(pmid, ta)].append((int(start), int(end), text))
#
#     # Process the corpus
#     missed = defaultdict(int)
#     for line in corpus:
#         pmid, title, abstract = line.strip().split(u'\t')
#
#         # Create document that contains title and Paragraph, so abbreviation definitions can be shared.
#         d = Document(Title(title), Paragraph(abstract))
#         #print(pmid)
#         for t, section, golds in [(d.elements[0], 'T', anndict.get((pmid, 'T'), [])), (d.elements[1], 'A', anndict.get((pmid, 'A'), []))]:
#             out = [(ce.start, ce.end, ce.text) for ce in t.cems]
#             for gold in golds:
#                 for o in out:
#                     if not gold[0] == o[0] and gold[1] == o[1]:
#                         print('PARTIAL: %s : %s' % (str(gold), str(o)))
#                     elif gold[0] == o[0] and not gold[1] == o[1]:
#                         print('PARTIAL: %s : %s' % (str(gold), str(o)))
#
#                 # if not gold[0] in [o[0] for o in out] and not gold[1] in [o[1] for o in out]:
#                 #     missed[gold[2]] += 1
#                 #     print('FN: %s' % (str(gold)))
#                 if gold not in out:
#                     missed[gold[2]] += 1
#                     print('FN: %s' % str(gold))
#             # for o in out:
#             #     # print('OUT: %s' % str(o))
#             #     if o not in golds:
#             #         print('FP: %s' % str(o))
#             # if not out == golds:
#             #     print(t.text)
#             #     print(out)
#             #     print(golds)
#
#     sorted_missed = sorted(missed, key=missed.get, reverse=True)
#     for m in sorted_missed:
#         print('%s: %s' % (missed[m], m))
#
#     # golds = set()
#     #
#     # for line in open('/Users/matt/Developer/python/ChemDataExtractor/data/chemdner-1.0/training.annotations.txt'):
#     #     line = line.decode('utf8')
#     #     pmid, ta, start, end, text, category = line.strip().split('\t')
#     #     golds.add(text)
#     # for line in open('/Users/matt/Developer/python/ChemDataExtractor/data/chemdner-1.0/development.annotations.txt'):
#     #     line = line.decode('utf8')
#     #     pmid, ta, start, end, text, category = line.strip().split('\t')
#     #     golds.add(text)
#     #
#     # for line in corpus:
#     #     sentence = []
#     #     goldsentence = []
#     #     for t in line.split():
#     #         token, tag = t.rsplit('/', 1)
#     #         goldsentence.append((token, tag))
#     #         sentence.append(token)
#     #     if sentence:
#     #         has_mistake = False
#     #         tokentags = tagger.tag(sentence)
#     #         tokentags = [(token, tag if tag else 'O') for token, tag in tokentags]
#     #         # Print false positives
#     #         for i, tokentag in enumerate(tokentags):
#     #             if tokentag[1] == 'B-CM' and not goldsentence[i][1] in {'B-CM', 'I-CM'}:
#     #                 has_mistake = True
#     #                 entity_tokens = [tokentag[0]]
#     #                 for subsequent in tokentags[i+1:]:
#     #                     if subsequent[1] == 'I-CM':
#     #                         entity_tokens.append(subsequent[0])
#     #                     else:
#     #                         break
#     #                 # print(entity_tokens)
#     #                 entity = ' '.join(entity_tokens)
#     #                 if entity not in golds:
#     #                     print(entity)
#
#             # if has_mistake:
#             #     print(' '.join('/'.join([token, tag]) for token, tag in goldsentence))
#             #     print(' '.join('/'.join([token, tag]) for token, tag in tokentags))
#
#         #     output.write(' '.join('/'.join(tokentag) for tokentag in tagger.tag(sentence)))
#         #     output.write('\n')
#         # else:
#         #     output.write('\n')

# -*- coding: utf-8 -*-
"""
chemdataextractor.cli.pos
~~~~~~~~~~~~~~~~~~~~~~~~~

Part of speech tagging commands.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import logging
import sys

import click

from ..doc import Document, Text
from ..nlp.corpus import genia_training, wsj_training, wsj_evaluation, genia_evaluation
from ..nlp.pos import TAGS, ChemApPosTagger, ChemCrfPosTagger


log = logging.getLogger(__name__)


@click.group(name='pos')
@click.pass_context
def pos_cli(ctx):
    """POS tagger commands."""
    pass


@pos_cli.command()
@click.option('--output', '-o', help='Output model file.', required=True)
@click.pass_context
def train_all(ctx, output):
    """Train POS tagger on WSJ, GENIA, and both. With and without cluster features."""
    click.echo('chemdataextractor.pos.train_all')
    click.echo('Output: %s' % output)
    ctx.invoke(train, output='%s_wsj_nocluster.pickle' % output, corpus='wsj', clusters=False)
    ctx.invoke(train, output='%s_wsj.pickle' % output, corpus='wsj', clusters=True)
    ctx.invoke(train, output='%s_genia_nocluster.pickle' % output, corpus='genia', clusters=False)
    ctx.invoke(train, output='%s_genia.pickle' % output, corpus='genia', clusters=True)
    ctx.invoke(train, output='%s_wsj_genia_nocluster.pickle' % output, corpus='wsj+genia', clusters=False)
    ctx.invoke(train, output='%s_wsj_genia.pickle' % output, corpus='wsj+genia', clusters=True)


@pos_cli.command()
@click.argument('model', required=True)
@click.pass_context
def evaluate_all(ctx, model):
    """Evaluate POS taggers on WSJ and GENIA."""
    click.echo('chemdataextractor.pos.evaluate_all')
    click.echo('Model: %s' % model)
    ctx.invoke(evaluate, model='%s_wsj_nocluster.pickle' % model, corpus='wsj', clusters=False)
    ctx.invoke(evaluate, model='%s_wsj_nocluster.pickle' % model, corpus='genia', clusters=False)
    ctx.invoke(evaluate, model='%s_wsj.pickle' % model, corpus='wsj', clusters=True)
    ctx.invoke(evaluate, model='%s_wsj.pickle' % model, corpus='genia', clusters=True)
    ctx.invoke(evaluate, model='%s_genia_nocluster.pickle' % model, corpus='wsj', clusters=False)
    ctx.invoke(evaluate, model='%s_genia_nocluster.pickle' % model, corpus='genia', clusters=False)
    ctx.invoke(evaluate, model='%s_genia.pickle' % model, corpus='wsj', clusters=True)
    ctx.invoke(evaluate, model='%s_genia.pickle' % model, corpus='genia', clusters=True)
    ctx.invoke(evaluate, model='%s_wsj_genia_nocluster.pickle' % model, corpus='wsj', clusters=False)
    ctx.invoke(evaluate, model='%s_wsj_genia_nocluster.pickle' % model, corpus='genia', clusters=False)
    ctx.invoke(evaluate, model='%s_wsj_genia.pickle' % model, corpus='wsj', clusters=True)
    ctx.invoke(evaluate, model='%s_wsj_genia.pickle' % model, corpus='genia', clusters=True)


@pos_cli.command()
@click.option('--output', '-o', help='Output model file.', required=True)
@click.option('--corpus', type=click.Choice(['wsj', 'genia', 'wsj+genia']), help='Training corpus')
@click.option('--clusters/--no-clusters', help='Whether to use cluster features', default=True)
@click.pass_context
def train(ctx, output, corpus, clusters):
    """Train POS Tagger."""
    click.echo('chemdataextractor.pos.train')
    click.echo('Output: %s' % output)
    click.echo('Corpus: %s' % corpus)
    click.echo('Clusters: %s' % clusters)

    wsj_sents = []
    genia_sents = []

    if corpus == 'wsj' or corpus == 'wsj+genia':
        wsj_sents = list(wsj_training.tagged_sents())
        # For WSJ, remove all tokens with -NONE- tag
        for i, wsj_sent in enumerate(wsj_sents):
            wsj_sents[i] = [t for t in wsj_sent if not t[1] == '-NONE-']

    if corpus == 'genia' or corpus == 'wsj+genia':
        genia_sents = list(genia_training.tagged_sents())
        # Translate GENIA
        for i, genia_sent in enumerate(genia_sents):
            for j, (token, tag) in enumerate(genia_sent):
                if tag == '(':
                    genia_sents[i][j] = (token, '-LRB-')  # ( to -RLB- (also do for evaluation)
                elif tag == ')':
                    genia_sents[i][j] = (token, '-RRB-')  # ) to -RRB- (also do for evaluation)
                elif tag == 'CT':
                    genia_sents[i][j] = (token, 'DT')  # Typo?
                elif tag == 'XT':
                    genia_sents[i][j] = (token, 'DT')  # Typo?
                elif tag == '-':
                    genia_sents[i][j] = (token, ':')  # Single hyphen character for dash
                elif tag == 'N':
                    genia_sents[i][j] = (token, 'NN')  # Typo?
                elif tag == 'PP':
                    genia_sents[i][j] = (token, 'PRP')  # Typo?
                elif tag == '' and token == ')':
                    genia_sents[i][j] = (token, '-RRB-')  # Typo?
                elif tag == '' and token == 'IFN-gamma':
                    genia_sents[i][j] = (token, 'NN')  # Typo?
                elif '|' in tag:
                    genia_sents[i][j] = (token, tag.split('|')[0])  # If contains |, choose first part
            # Filter any tags not in the allowed tagset (Shouldn't be any left anyway)
            genia_sents[i] = [t for t in genia_sent if t[1] in TAGS]

    if corpus == 'wsj':
        training_corpus = wsj_sents
    elif corpus == 'genia':
        training_corpus = genia_sents
    elif corpus == 'wsj+genia':
        training_corpus = wsj_sents + genia_sents
    else:
        raise click.ClickException('Invalid corpus')

    tagger = ChemCrfPosTagger(clusters=clusters)
    tagger.train(training_corpus, output)


@pos_cli.command()
@click.argument('model', required=True)
@click.option('--corpus', type=click.Choice(['wsj', 'genia']), help='Evaluation corpus')
@click.option('--clusters/--no-clusters', help='Whether to use cluster features', default=True)
@click.pass_context
def evaluate(ctx, model, corpus, clusters):
    """Evaluate performance of POS Tagger."""
    click.echo('chemdataextractor.pos.evaluate')
    if corpus == 'wsj':
        evaluation = wsj_evaluation
        sents = list(evaluation.tagged_sents())
        for i, wsj_sent in enumerate(sents):
            sents[i] = [t for t in wsj_sent if not t[1] == '-NONE-']
    elif corpus == 'genia':
        evaluation = genia_evaluation
        sents = list(evaluation.tagged_sents())
        # Translate GENIA bracket tags
        for i, genia_sent in enumerate(sents):
            for j, (token, tag) in enumerate(genia_sent):
                if tag == '(':
                    sents[i][j] = (token, '-LRB-')
                elif tag == ')':
                    sents[i][j] = (token, '-RRB-')
    else:
        raise click.ClickException('Invalid corpus')
    tagger = ChemCrfPosTagger(model=model, clusters=clusters)
    accuracy = tagger.evaluate(sents)
    click.echo('%s on %s: %s' % (model, evaluation, accuracy))


@pos_cli.command()
@click.option('--output', '-o', type=click.File('wb'), help='Output model file.', required=True)
@click.option('--corpus', type=click.Choice(['wsj', 'genia', 'wsj+genia']), help='Training corpus')
@click.option('--clusters/--no-clusters', help='Whether to use cluster features', default=True)
@click.pass_obj
def train_perceptron(ctx, output, corpus, clusters):
    """Train Averaged Perceptron POS Tagger."""
    click.echo('chemdataextractor.pos.train')
    click.echo('Output: %s' % output)
    click.echo('Corpus: %s' % corpus)
    click.echo('Clusters: %s' % clusters)

    wsj_sents = []
    genia_sents = []

    if corpus == 'wsj' or corpus == 'wsj+genia':
        wsj_sents = list(wsj_training.tagged_sents())
        # For WSJ, remove all tokens with -NONE- tag
        for i, wsj_sent in enumerate(wsj_sents):
            wsj_sents[i] = [t for t in wsj_sent if not t[1] == '-NONE-']

    if corpus == 'genia' or corpus == 'wsj+genia':
        genia_sents = list(genia_training.tagged_sents())
        # Translate GENIA
        for i, genia_sent in enumerate(genia_sents):
            for j, (token, tag) in enumerate(genia_sent):
                if tag == '(':
                    genia_sents[i][j] = (token, '-LRB-')  # ( to -RLB- (also do for evaluation)
                elif tag == ')':
                    genia_sents[i][j] = (token, '-RRB-')  # ) to -RRB- (also do for evaluation)
                elif tag == 'CT':
                    genia_sents[i][j] = (token, 'DT')  # Typo?
                elif tag == 'XT':
                    genia_sents[i][j] = (token, 'DT')  # Typo?
                elif tag == '-':
                    genia_sents[i][j] = (token, ':')  # Single hyphen character for dash
                elif tag == 'N':
                    genia_sents[i][j] = (token, 'NN')  # Typo?
                elif tag == 'PP':
                    genia_sents[i][j] = (token, 'PRP')  # Typo?
                elif tag == '' and token == ')':
                    genia_sents[i][j] = (token, '-RRB-')  # Typo?
                elif tag == '' and token == 'IFN-gamma':
                    genia_sents[i][j] = (token, 'NN')  # Typo?
                elif '|' in tag:
                    genia_sents[i][j] = (token, tag.split('|')[0])  # If contains |, choose first part
            # Filter any tags not in the allowed tagset (Shouldn't be any left anyway)
            genia_sents[i] = [t for t in genia_sent if t[1] in TAGS]

    if corpus == 'wsj':
        training_corpus = wsj_sents
    elif corpus == 'genia':
        training_corpus = genia_sents
    elif corpus == 'wsj+genia':
        training_corpus = wsj_sents + genia_sents
    else:
        raise click.ClickException('Invalid corpus')

    tagger = ChemApPosTagger(clusters=clusters)
    tagger.train(training_corpus)
    tagger.save(output)


@pos_cli.command()
@click.argument('model', required=True)
@click.option('--corpus', type=click.Choice(['wsj', 'genia']), help='Evaluation corpus')
@click.pass_obj
def evaluate_perceptron(ctx, model, corpus):
    """Evaluate performance of Averaged Perceptron POS Tagger."""
    click.echo('chemdataextractor.pos.evaluate')
    if corpus == 'wsj':
        evaluation = wsj_evaluation
        sents = list(evaluation.tagged_sents())
        for i, wsj_sent in enumerate(sents):
            sents[i] = [t for t in wsj_sent if not t[1] == '-NONE-']
    elif corpus == 'genia':
        evaluation = genia_evaluation
        sents = list(evaluation.tagged_sents())
        # Translate GENIA bracket tags
        for i, genia_sent in enumerate(sents):
            for j, (token, tag) in enumerate(genia_sent):
                if tag == '(':
                    sents[i][j] = (token, '-LRB-')
                elif tag == ')':
                    sents[i][j] = (token, '-RRB-')
    else:
        raise click.ClickException('Invalid corpus')
    tagger = ChemApPosTagger(model=model)
    accuracy = tagger.evaluate(sents)
    click.echo('%s on %s: %s' % (model, evaluation, accuracy))


@pos_cli.command()
@click.option('--output', '-o', type=click.File('w', encoding='utf8'), help='Output file.', default=sys.stdout)
@click.argument('input', type=click.File('rb'), default=sys.stdin)
@click.pass_obj
def tag(ctx, input, output):
    """Output POS-tagged tokens."""
    log.info('chemdataextractor.pos.tag')
    log.info('Reading %s' % input.name)
    doc = Document.from_file(input)
    for element in doc.elements:
        if isinstance(element, Text):
            for sentence in element.sentences:
                output.write(' '.join('/'.join([token, tag]) for token, tag in sentence.pos_tagged_tokens))
                output.write('\n')

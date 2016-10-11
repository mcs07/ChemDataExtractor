# -*- coding: utf-8 -*-
"""
chemdataextractor.cli.tokenize
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tokenizer command line interface.

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


log = logging.getLogger(__name__)


@click.group(name='tokenize')
@click.pass_context
def tokenize_cli(ctx):
    """Tokenizer commands."""
    pass


@tokenize_cli.command()
@click.option('--output', '-o', type=click.File('wb'), help='Output model file.', required=True)
@click.option('--abbr', '-a', type=click.File('r', encoding='utf8'), help='Force abbreviations.', required=False)
@click.option('--colloc', '-c', type=click.File('r', encoding='utf8'), help='Force collocations.', required=False)
@click.argument('input', type=click.File('r', encoding='utf8'), required=True, nargs=-1)
@click.pass_obj
def train_punkt(ctx, input, output, abbr, colloc):
    """Train Punkt sentence splitter using sentences in input."""
    click.echo('chemdataextractor.tokenize.train_punkt')
    import pickle
    from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktTrainer
    punkt = PunktTrainer()
    # Set these to true to include collocations more leniently, then increase MIN_COLLOC_FREQ to restrict again
    # punkt.INCLUDE_ALL_COLLOCS = False
    # punkt.INCLUDE_ABBREV_COLLOCS = False
    # punkt.MIN_COLLOC_FREQ = 1
    # Don't train on titles. They may contain abbreviations, but basically never have actual sentence boundaries.
    for fin in input:
        click.echo('Training on %s' % fin.name)
        sentences = fin.read()  #.replace('.\n', '. \n\n')
        punkt.train(sentences, finalize=False, verbose=True)
    punkt.finalize_training(verbose=True)
    if abbr:
        abbreviations = abbr.read().strip().split('\n')
        click.echo('Manually adding abbreviations: %s' % abbreviations)
        punkt._params.abbrev_types.update(abbreviations)
    if colloc:
        collocations = [tuple(l.split('. ', 1)) for l in colloc.read().strip().split('\n')]
        click.echo('Manually adding collocs: %s' % collocations)
        punkt._params.collocations.update(collocations)
    model = PunktSentenceTokenizer(punkt.get_params())
    pickle.dump(model, output, protocol=pickle.HIGHEST_PROTOCOL)


@tokenize_cli.command()
@click.option('--output', '-o', type=click.File('w', encoding='utf8'), help='Output file.', default=sys.stdout)
@click.argument('input', type=click.File('rb'), default=sys.stdin)
@click.pass_obj
def sentences(ctx, input, output):
    """Read input document, and output sentences."""
    log.info('chemdataextractor.read.elements')
    log.info('Reading %s' % input.name)
    doc = Document.from_file(input)
    for element in doc.elements:
        if isinstance(element, Text):
            for raw_sentence in element.raw_sentences:
                output.write(raw_sentence.strip())
                output.write('\n')


@tokenize_cli.command()
@click.option('--output', '-o', type=click.File('w', encoding='utf8'), help='Output file.', default=sys.stdout)
@click.argument('input', type=click.File('rb'), default=sys.stdin)
@click.pass_obj
def words(ctx, input, output):
    """Read input document, and output words."""
    log.info('chemdataextractor.read.elements')
    log.info('Reading %s' % input.name)
    doc = Document.from_file(input)
    for element in doc.elements:
        if isinstance(element, Text):
            for sentence in element.sentences:
                output.write(' '.join(sentence.raw_tokens))
                output.write('\n')

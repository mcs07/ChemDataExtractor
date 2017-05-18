# -*- coding: utf-8 -*-
"""
chemdataextractor.cli.cem
~~~~~~~~~~~~~~~~~~~~~~~~~

Chemical entity mention (CEM) commands.

"""





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

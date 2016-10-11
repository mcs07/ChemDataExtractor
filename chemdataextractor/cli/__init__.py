# -*- coding: utf-8 -*-
"""
chemdataextractor.cli
~~~~~~~~~~~~~~~~~~~~~

ChemDataExtractor command line interface.

Once installed, ChemDataExtractor provides a command-line tool that can be used by typing 'cde' in a terminal.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import logging
import sys

import click
import six

from .. import __version__
from ..doc import Document


log = logging.getLogger(__name__)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Verbose debug logging.')
@click.version_option(__version__, '--version', '-V')
@click.help_option('--help', '-h')
@click.pass_context
def cli(ctx, verbose):
    """ChemDataExtractor command line interface."""
    log.debug('ChemDataExtractor v%s' % __version__)
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)
    logging.getLogger('requests').setLevel(logging.WARN)
    ctx.obj = {}


@cli.command()
@click.option('--output', '-o', type=click.File('w', encoding='utf8'), help='Output file.', default=sys.stdout)
@click.argument('input', type=click.File('rb'), default=sys.stdin)
@click.pass_obj
def extract(ctx, input, output):
    """Run ChemDataExtractor on a document."""
    log.info('chemdataextractor.extract')
    log.info('Reading %s' % input.name)
    doc = Document.from_file(input, fname=input.name)
    records = [record.serialize(primitive=True) for record in doc.records]
    jsonstring = json.dumps(records, indent=2, ensure_ascii=False)
    output.write(jsonstring)


@cli.command()
@click.option('--output', '-o', type=click.File('w', encoding='utf8'), help='Output file.', default=sys.stdout)
@click.argument('input', type=click.File('rb'), default=sys.stdin)
@click.pass_obj
def read(ctx, input, output):
    """Output processed document elements."""
    log.info('chemdataextractor.read')
    log.info('Reading %s' % input.name)
    doc = Document.from_file(input)
    for element in doc.elements:
        output.write('%s : %s\n=====\n' % (element.__class__.__name__, six.text_type(element)))


from . import cluster, config, data, tokenize, pos, chemdner, cem, dict, evaluate


cli.add_command(cluster.cluster_cli)
cli.add_command(config.config_cli)
cli.add_command(data.data_cli)
cli.add_command(tokenize.tokenize_cli)
cli.add_command(pos.pos_cli)
cli.add_command(chemdner.chemdner_cli)
cli.add_command(cem.cem)
cli.add_command(dict.dict_cli)
cli.add_command(evaluate.evaluate)

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
import logging

import click

from .. import __version__


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


# TODO: tokenize_cli
# @cli.command()
# @click.option('--output', '-o', type=click.File('w', encoding='utf8'), help='Output file.', default=sys.stdout)
# @click.argument('input', type=click.File('r', encoding='utf8'), required=True, nargs=-1)
# @click.pass_obj
# def tokenize(ctx, input, output):
#     """Read raw text from input, and write whitespace-separated tokens to output file."""
#     log.debug('chemdataextractor.tokenize')
#     for fin in input:
#         click.echo('Reading %s' % fin.name)
#         # Read each line
#         for line in fin.readlines():
#             #click.echo('Line: %s' % line)
#             text = Text(line)
#             for sentence in text.sentences:
#                 if sentence.tokens:
#                     #click.echo('Sentence: %s' % ' '.join([t.text for t in sentence.tokens]))
#                     #output.write(' '.join([t.text for t in sentence.tokens]))
#                     # output.write(' '.join([chem_normalize(t.text) for t in sentence.tokens]))
#                     # output.write('\n')
#                     output.write(' '.join([t.lex.normalized for t in sentence.tokens]))
#                     output.write('\n')



from . import cluster, config, data, punkt, pos, chemdner, cem, dict, evaluate


cli.add_command(cluster.cluster_cli)
cli.add_command(config.config_cli)
cli.add_command(data.data_cli)
cli.add_command(punkt.punkt_cli)
cli.add_command(pos.pos_cli)
cli.add_command(chemdner.chemdner_cli)
cli.add_command(cem.cem)
cli.add_command(dict.dict_cli)
cli.add_command(evaluate.evaluate)

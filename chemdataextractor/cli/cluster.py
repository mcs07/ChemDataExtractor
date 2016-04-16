# -*- coding: utf-8 -*-
"""
chemdataextractor.cli.cluster
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Word clusters command-line interface.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import logging

import click


log = logging.getLogger(__name__)


@click.group(name='cluster')
@click.pass_context
def cluster_cli(ctx):
    """Word clusters commands."""
    pass


@cluster_cli.command()
@click.option('--output', '-o', type=click.File('wb'), help='Output model file.', required=True)
@click.argument('input', type=click.File('r', encoding='utf8'), required=True)
@click.pass_obj
def load(ctx, input, output):
    """Read clusters from file and save to model file."""
    log.debug('chemdataextractor.cluster.load')
    import pickle
    click.echo('Reading %s' % input.name)
    clusters = {}
    for line in input.readlines():
        cluster, word, freq = line.split()
        clusters[word] = cluster
    pickle.dump(clusters, output, protocol=pickle.HIGHEST_PROTOCOL)


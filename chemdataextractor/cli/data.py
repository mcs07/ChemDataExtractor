# -*- coding: utf-8 -*-
"""
chemdataextractor.cli.data
~~~~~~~~~~~~~~~~~~~~~~~~~~

Data and model management interface.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import logging

import click

from ..data import PACKAGES, get_data_dir


log = logging.getLogger(__name__)


@click.group(name='data')
@click.pass_context
def data_cli(ctx):
    """Data and model management commands."""
    pass


@data_cli.command()
@click.pass_obj
def where(ctx):
    """Print path to data directory."""
    log.debug('chemdataextractor.data.where')
    click.echo(get_data_dir())


@data_cli.command()
@click.pass_obj
def list(ctx):
    """List active data packages."""
    log.debug('chemdataextractor.data.list')
    click.echo('Downloaded\tPackage')
    for package in PACKAGES:
        click.echo('%s\t%s' % (package.local_exists(), package.path))


@data_cli.command()
@click.pass_obj
def download(ctx):
    """Download data."""
    log.debug('chemdataextractor.data.download')
    count = 0
    for package in PACKAGES:
        success = package.download()
        if success:
            count += 1
    click.echo('Successfully downloaded %s new data packages (%s existing)' % (count, len(PACKAGES) - count))


@data_cli.command()
@click.pass_obj
def clean(ctx):
    """Prune data that is no longer required."""
    log.debug('chemdataextractor.data.clean')
    # TODO

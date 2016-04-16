# -*- coding: utf-8 -*-
"""
chemdataextractor.cli.config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Commands for managing ChemDataExtractor configuration.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import logging

import click

from ..config import config


log = logging.getLogger(__name__)


@click.group(name='config')
@click.help_option('--help', '-h')
@click.pass_context
def config_cli(ctx):
    """Manage configuration."""
    pass


@config_cli.command()
@click.pass_context
def list(ctx):
    """List all config values."""
    log.debug('chemdataextractor.config.list')
    for k in config:
        click.echo('%s : %s' % (k, config[k]))


@config_cli.command()
@click.argument('key', required=True)
@click.pass_context
def get(ctx, key):
    """Get the config value for a key."""
    log.debug('chemdataextractor.config.get')
    click.echo(config[key])


@config_cli.command()
@click.argument('key', required=True)
@click.argument('value', required=True)
@click.pass_context
def set(ctx, key, value):
    """Set the config value for a key."""
    log.debug('chemdataextractor.config.set')
    config[key] = value


@config_cli.command()
@click.argument('key', required=True)
@click.pass_context
def remove(ctx, key):
    """Remove the config value for a key."""
    log.debug('chemdataextractor.config.remove')
    del config[key]


@config_cli.command()
@click.pass_context
def clear(ctx):
    """Clear all config values."""
    log.debug('chemdataextractor.config.clear')
    config.clear()

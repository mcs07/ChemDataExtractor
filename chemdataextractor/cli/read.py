# -*- coding: utf-8 -*-
"""
chemdataextractor.cli.read
~~~~~~~~~~~~~~~~~~~~~~~~~~

Document reader command line interface.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import logging
import sys

import click
import six

from ..doc import Document


log = logging.getLogger(__name__)


@click.group(name='read')
@click.pass_context
def read_cli(ctx):
    """Reader commands."""
    pass


@read_cli.command()
@click.option('--output', '-o', type=click.File('w', encoding='utf8'), help='Output file.', default=sys.stdout)
@click.argument('input', type=click.File('r', encoding='utf8'), default=sys.stdin)
@click.pass_obj
def elements(ctx, input, output):
    """Read input document, and output document elements."""
    log.info('chemdataextractor.read.elements')
    log.info('Reading %s' % input.name)
    doc = Document.from_file(input)
    for element in doc.elements:
        output.write(element.__class__.__name__)
        output.write(' : ')
        output.write(six.text_type(element))
        output.write('\n=====\n')

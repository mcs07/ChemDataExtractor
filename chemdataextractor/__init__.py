# -*- coding: utf-8 -*-
"""
ChemDataExtractor
~~~~~~~~~~~~~~~~~

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging


__title__ = 'ChemDataExtractor'
__version__ = '1.3.0'
__author__ = 'Matt Swain'
__email__ = 'm.swain@me.com'
__license__ = 'MIT'
__copyright__ = 'Copyright 2017 Matt Swain and contributors'

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


from .doc.document import Document

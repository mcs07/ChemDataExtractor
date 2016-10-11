# -*- coding: utf-8 -*-
"""
ChemDataExtractor
~~~~~~~~~~~~~~~~~

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging


__title__ = 'ChemDataExtractor'
__version__ = '1.2.0'
__author__ = 'Matt Swain'
__email__ = 'm.swain@me.com'
__license__ = 'MIT'
__copyright__ = 'Copyright 2016 Matt Swain'

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


from .doc.document import Document

# -*- coding: utf-8 -*-
"""
chemdataextractor.text.unwrap
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tools for unwrapping hard-wrapped text. Most useful for text extracted from PDFs.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


# TODO: Need to revisit this. Would be better to have an algorithm that does unsupervised training.
# For unsupervised training, we could give it either wrapped or unwrapped text
# For supervised training, we could give both simultaneously


# class Unhyphenator:
#     """Unhyphenation algorithms for unwrapping hard-wrapped text."""
#
#     def __init__(self, joins=None):
#         """Initialise patterns and exceptions.
#
#         :param joins: A list words that are acceptable to form by joining two components.
#
#         """
#         self.joins = joins
#         if joins is None:
#             with open('../data/words/hyphen_joins.txt') as jf:
#                 self.joins = set(word.strip().lower() for word in jf)
#
#     def unhyphenate(self, part1, part2):
#         """Given two word components, return a string with them joined appropriately."""
#         part1 = part1.rstrip('-')
#         join1 = '%s-%s' % (part1, part2)
#         join2 = '%s%s' % (part1, part2)
#         p1s = part1.lower().lstrip(u'\'\"`’”“-([{/\\~')
#         p2s = part2.lower().rstrip(u'\'\"`’”“-,.:;!?)]}/\\0123456789')
#         p2s = re.sub('\'s$', '', p2s)
#         j1s = '%s-%s' % (p1s, p2s)
#         j2s = '%s%s' % (p1s, p2s)
#         # If either comp is not alpha or join with hyphen is in joins list, join with hyphen
#         if not re.match('^[a-z-]+$', p1s) or not re.match('^[a-z-]+$', p2s) or j1s in self.joins:
#             return join1
#         # If join without hyphen is in word list, join without hyphen
#         if j2s in self.joins:
#             return join2
#         return join1
#
#     def unwrap_text(self, text):
#         """Unwrap multiple lines of hard-wrapped text, unhyphenating words where applicable."""
#         unwrapped = ''
#         for line in text.split('\n'):
#             if not line.split():
#                 # Line is whitespace, just add as a new line
#                 unwrapped += '\n\n'
#             elif not unwrapped.split('\n', 1):
#                 # First line, just add it
#                 unwrapped += line
#             else:
#                 if not unwrapped.endswith('-'):
#                     # Regular line unwrap, add with a space
#                     if not unwrapped.endswith('\n'):
#                         unwrapped += ' '
#                     unwrapped += line
#                 else:
#                     # Hyphenated line unwrap, determine whether to remove hyphen
#                     pcomps = unwrapped.rsplit(None, 1)
#                     lcomps = line.split(' ', 2)
#                     if lcomps[0] in ['and', 'or'] and len(lcomps) > 1 and '-' in lcomps[1]:
#                         # Keep hyphen and add space
#                         unwrapped += ' ' + line
#                     else:
#                         join = self.unhyphenate(pcomps[-1], lcomps[0])
#                         unwrapped = pcomps[0] if len(pcomps) > 1 else ''
#                         unwrapped += ' ' + join
#                         unwrapped += ' ' + lcomps[1] if len(lcomps) > 1 else ''
#                         unwrapped += ' ' + lcomps[2] if len(lcomps) > 2 else ''
#         return unwrapped


# unhyphenator = Unhyphenator()
# unhyphenate = unhyphenator.unhyphenate
# unwrap_text = unhyphenator.unwrap_text

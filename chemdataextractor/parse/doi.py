from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .base import BaseParser
from .elements import W, R, Optional
from ..model import StringType, Compound
from .actions import merge


doi = ((R('[Dd][Oo][Ii]') + Optional(W(':'))).hide() +
       R('10[.][0-9]{4,}(?:[.][0-9]+)*') +
       W('/') +
       R('(?:(?!["&\'<>])\S)+')).add_action(merge)('doi')


class DoiParser(BaseParser):
    """"""
    root = doi

    def __init__(self):
        pass

    def interpret(self, result, start, end):
        c = Compound(
            doi=result.xpath('./text()')
        )

        yield c

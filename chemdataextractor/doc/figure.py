# -*- coding: utf-8 -*-
"""
chemdataextractor.doc.figure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Figure document elements.

"""





import logging

from .element import CaptionedElement


log = logging.getLogger(__name__)


class Figure(CaptionedElement):

    @property
    def records(self):
        caption_records = self.caption.records
        # Filter contextual records, because they normally only apply to the data within the figure.
        caption_records = [c for c in caption_records if not c.is_contextual and not c.is_unidentified]
        return caption_records

    def _repr_html_(self):
        html_lines = ['<figure>', self.caption._repr_html_(), '</figure>']
        # TODO: img element with figure URL
        return '\n'.join(html_lines)


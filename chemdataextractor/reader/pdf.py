# -*- coding: utf-8 -*-
"""
chemdataextractor.reader.pdf
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PDF document reader.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextLine, LTTextBox, LTFigure
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
import six

from ..doc.document import Document
from ..doc.text import Paragraph
from .base import BaseReader
from ..errors import ReaderError


class PdfReader(BaseReader):
    """"""

    def detect(self, fstring, fname=None):
        """"""
        if fname and not fname.endswith('.pdf'):
            return False
        return True

    def _process_layout(self, layout):
        """Process an LTPage layout and return a list of elements."""
        # Here we just group text into paragraphs
        elements = []
        for lt_obj in layout:
            if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                elements.append(Paragraph(lt_obj.get_text().strip()))
            elif isinstance(lt_obj, LTFigure):
                # Recursive...
                elements.extend(self._process_layout(lt_obj))
        return elements

    def parse(self, fstring):
        try:
            f = six.BytesIO(fstring)
            parser = PDFParser(f)
            document = PDFDocument(parser)
            if not document.is_extractable:
                raise ReaderError('PDF text extraction not allowed')
            rsrcmgr = PDFResourceManager()
            laparams = LAParams()
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            elements = []
            for page in PDFPage.create_pages(document):
                interpreter.process_page(page)
                layout = device.get_result()
                elements.extend(self._process_layout(layout))
            return Document(*elements)
        except Exception as e:
            raise ReaderError(e)


# Functions to determine captions from layout analysis
#
# def get_element_type(l, el_type):
#     """Return a flat list of all of one element type from a nested list of LT objects."""
#     elements = []
#     for el in l:
#         if isinstance(el, el_type):
#             elements.append(el)
#         elif isinstance(el, collections.Iterable) and not isinstance(el, LTItem):
#             elements.extend(get_element_type(el, el_type))
#     return elements
#
#
# def pair_up(images, captions):
#     """Pair up each caption with the image most likely to correspond to it."""
#     pairs = []
#     for cap in captions:
#         possibles = []
#         for im in images:
#             if cap.bbox[3] < im.bbox[1] and cap.bbox[0] < im.bbox[2] and cap.bbox[2] > im.bbox[0]:
#                 possibles.append(im)
#         if possibles:
#             closest = possibles[0]
#             for im in possibles:
#                 if get_distance(im, cap) < get_distance(closest, cap):
#                     closest = im
#             pairs.append({'ltimage':closest,'ltcap':cap})
#     return pairs
#
#
# def get_distance(fig, cap):
#     """Return the distance between the top-centre of cap and the bottom-centre of fig."""
#     figcen = [(fig.bbox[0]+fig.bbox[2])/2,fig.bbox[1]]
#     capcen = [(cap.bbox[0]+cap.bbox[2])/2,cap.bbox[3]]
#     distance = math.sqrt(pow(abs(figcen[0]-capcen[0]),2) + pow(abs(figcen[1]-capcen[1]),2))
#     return distance
#
#
# def add_image_numbers(fig_caps, all_images):
#     """Add the figure number and image number to each fig_cap."""
#     for fig_cap in fig_caps:
#         for i, im in enumerate(all_images):
#             if fig_cap['ltimage'].name == im.name:
#                 fig_cap['imnum'] = i
#                 fig_num = fig_cap['ltcap'].get_text().split(None,2)[1]
#                 if not fig_num.isdigit():
#                     fig_num = re.split('\D', fig_num)[0]
#                 fig_cap['fignum'] = fig_num
#     return fig_caps
#
#
# def remove_false_positives(fig_caps):
#     """If two captions have the same figure number remove the one farthest from its image."""
#     to_delete = []
#     for i in range(len(fig_caps)):
#         for j in range(i):
#             if fig_caps[i]['fignum'] == fig_caps[j]['fignum']:
#                 # Check if fig_caps[i]['ltcap'] or fig_caps[j]['ltcap'] has "shows" or "illustrates"
#                 try:
#                     captext1 = fig_caps[i]['ltcap'].get_text().split(None,2)[2]
#                     captext2 = fig_caps[j]['ltcap'].get_text().split(None,2)[2]
#                 except IndexError:
#                     captext1 = fig_caps[i]['ltcap'].get_text()
#                     captext2 = fig_caps[j]['ltcap'].get_text()
#                 # reports, presents
#                 if captext1.startswith('shows') or captext1.startswith('illustrates') or captext1.startswith('displays') or captext1.startswith('reports') or captext1.startswith('presents'):
#                     to_delete.append(i)
#                 elif captext2.startswith('shows') or captext2.startswith('illustrates') or captext2.startswith('displays') or captext2.startswith('reports') or captext2.startswith('presents'):
#                     to_delete.append(j)
#                 else:
#                     dis1 = get_distance(fig_caps[i]['ltimage'], fig_caps[i]['ltcap'])
#                     dis2 = get_distance(fig_caps[j]['ltimage'], fig_caps[j]['ltcap'])
#                     if dis1 > dis2:
#                         to_delete.append(i)
#                     else:
#                         to_delete.append(j)
#     fig_caps = [i for j, i in enumerate(fig_caps) if j not in to_delete]
#     return fig_caps

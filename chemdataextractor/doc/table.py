# -*- coding: utf-8 -*-
"""
chemdataextractor.doc.table
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Table processing.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
from collections import defaultdict

from ..model import Compound, ModelList
from ..parse.table import CompoundHeadingParser, CompoundCellParser, UvvisAbsHeadingParser, UvvisAbsCellParser, \
    QuantumYieldHeadingParser, QuantumYieldCellParser, UvvisEmiHeadingParser, UvvisEmiCellParser, ExtinctionCellParser, \
    ExtinctionHeadingParser, FluorescenceLifetimeHeadingParser, FluorescenceLifetimeCellParser, \
    ElectrochemicalPotentialHeadingParser, ElectrochemicalPotentialCellParser, IrHeadingParser, IrCellParser, \
    SolventCellParser, SolventHeadingParser, SolventInHeadingParser, UvvisAbsEmiQuantumYieldHeadingParser, \
    UvvisAbsEmiQuantumYieldCellParser, MeltingPointHeadingParser, MeltingPointCellParser, TempInHeadingParser, \
    UvvisAbsDisallowedHeadingParser, UvvisEmiQuantumYieldHeadingParser, UvvisEmiQuantumYieldCellParser
# TODO: Sort out the above import... import module instead
from ..nlp.tag import NoneTagger
from ..nlp.tokenize import FineWordTokenizer
from ..utils import memoized_property
from .element import CaptionedElement
from .text import Sentence


log = logging.getLogger(__name__)


class Table(CaptionedElement):

    #: Table cell parsers
    parsers = [
        (CompoundHeadingParser(), CompoundCellParser()),
        (UvvisAbsEmiQuantumYieldHeadingParser(), UvvisAbsEmiQuantumYieldCellParser()),
        (UvvisEmiQuantumYieldHeadingParser(), UvvisEmiQuantumYieldCellParser()),
        (UvvisEmiHeadingParser(), UvvisEmiCellParser()),
        (UvvisAbsHeadingParser(), UvvisAbsCellParser(), UvvisAbsDisallowedHeadingParser()),
        (IrHeadingParser(), IrCellParser()),
        (ExtinctionHeadingParser(), ExtinctionCellParser()),
        (QuantumYieldHeadingParser(), QuantumYieldCellParser()),
        (FluorescenceLifetimeHeadingParser(), FluorescenceLifetimeCellParser()),
        (ElectrochemicalPotentialHeadingParser(), ElectrochemicalPotentialCellParser()),
        (MeltingPointHeadingParser(), MeltingPointCellParser()),
        (SolventHeadingParser(), SolventCellParser()),
        (SolventInHeadingParser(),),
        (TempInHeadingParser(),)
    ]

    def __init__(self, caption, label=None, headings=None, rows=None, footnotes=None, **kwargs):
        super(Table, self).__init__(caption=caption, label=label, **kwargs)
        self.headings = headings if headings is not None else []  # list(list(Cell))
        self.rows = rows if rows is not None else []  # list(list(Cell))
        self.footnotes = footnotes if footnotes is not None else []

    @property
    def document(self):
        return self._document

    @document.setter
    def document(self, document):
        self._document = document
        self.caption.document = document
        for row in self.headings:
            for cell in row:
                cell.document = document
        for row in self.rows:
            for cell in row:
                cell.document = document

    def serialize(self):
        """Convert Table element to python dictionary."""
        data = {
            'type': self.__class__.__name__,
            'caption': self.caption.serialize(),
            'headings': [[cell.serialize() for cell in hrow] for hrow in self.headings],
            'rows': [[cell.serialize() for cell in row] for row in self.rows],
        }
        return data

    def _repr_html_(self):
        html_lines = ['<table class="table">']
        html_lines.append(self.caption._repr_html_  ())
        html_lines.append('<thead>')
        for hrow in self.headings:
            html_lines.append('<tr>')
            for cell in hrow:
                html_lines.append('<th>' + cell.text + '</th>')
        html_lines.append('</thead>')
        html_lines.append('<tbody>')
        for row in self.rows:
            html_lines.append('<tr>')
            for cell in row:
                html_lines.append('<td>' + cell.text + '</td>')
        html_lines.append('</tbody>')
        html_lines.append('</table>')
        return '\n'.join(html_lines)

    @property
    def records(self):
        """Chemical records that have been parsed from the table."""
        caption_records = self.caption.records
        # Parse headers to extract contextual data and determine value parser for the column
        value_parsers = {}
        header_compounds = defaultdict(list)
        table_records = ModelList()
        seen_compound_col = False
        log.debug('Parsing table headers')

        for i, col_headings in enumerate(zip(*self.headings)):
            # log.info('Considering column %s' % i)
            for parsers in self.parsers:
                log.debug(parsers)
                heading_parser = parsers[0]
                value_parser = parsers[1] if len(parsers) > 1 else None
                disallowed_parser = parsers[2] if len(parsers) > 2 else None
                allowed = False
                disallowed = False
                for cell in col_headings:
                    log.debug(cell.tagged_tokens)
                    results = list(heading_parser.parse(cell.tagged_tokens))
                    if results:
                        allowed = True
                        log.debug('Heading column %s: Match %s: %s' % (i, heading_parser.__class__.__name__, [c.serialize() for c in results]))
                    # Results from every parser are stored as header compounds
                    header_compounds[i].extend(results)
                    # Referenced footnote records are also stored
                    for footnote in self.footnotes:
                        # print('%s - %s - %s' % (footnote.id, cell.references, footnote.id in cell.references))
                        if footnote.id in cell.references:
                            log.debug('Adding footnote %s to column %s: %s' % (footnote.id, i, [c.serialize() for c in footnote.records]))
                            # print('Footnote records: %s' % [c.to_primitive() for c in footnote.records])
                            header_compounds[i].extend(footnote.records)
                    # Check if the disallowed parser matches this cell
                    if disallowed_parser and list(disallowed_parser.parse(cell.tagged_tokens)):
                        log.debug('Column %s: Disallowed %s' % (i, heading_parser.__class__.__name__))
                        disallowed = True
                # If heading parser matches and disallowed parser doesn't, store the value parser
                if allowed and not disallowed and value_parser and i not in value_parsers:
                    if isinstance(value_parser, CompoundCellParser):
                        # Only take the first compound col
                        if seen_compound_col:
                            continue
                        seen_compound_col = True
                    log.debug('Column %s: Value parser: %s' % (i, value_parser.__class__.__name__))
                    value_parsers[i] = value_parser
                    # Stop after value parser is assigned?

        # for hrow in self.headings:
        #     for i, cell in enumerate(hrow):
        #         log.debug(cell.tagged_tokens)
        #         for heading_parser, value_parser in self.parsers:
        #             results = list(heading_parser.parse(cell.tagged_tokens))
        #             if results:
        #                 log.debug('Heading column %s: Match %s: %s' % (i, heading_parser.__class__.__name__, [c.to_primitive() for c in results]))
        #             # Results from every parser are stored as header compounds
        #             header_compounds[i].extend(results)
        #             if results and value_parser and i not in value_parsers:
        #                 if isinstance(value_parser, CompoundCellParser):
        #                     # Only take the first compound col
        #                     if seen_compound_col:
        #                         continue
        #                     seen_compound_col = True
        #                 value_parsers[i] = value_parser
        #                 break  # Stop after first heading parser matches
        #         # Referenced footnote records are also stored
        #         for footnote in self.footnotes:
        #             # print('%s - %s - %s' % (footnote.id, cell.references, footnote.id in cell.references))
        #             if footnote.id in cell.references:
        #                 log.debug('Adding footnote %s to column %s: %s' % (footnote.id, i, [c.to_primitive() for c in footnote.records]))
        #                 # print('Footnote records: %s' % [c.to_primitive() for c in footnote.records])
        #                 header_compounds[i].extend(footnote.records)

        # If no parsers, skip processing table
        if value_parsers:

            # If no CompoundCellParser() in value_parsers and value_parsers[0] == [] then set CompoundCellParser()
            if not seen_compound_col and 0 not in value_parsers:
                log.debug('No compound column found in table, assuming first column')
                value_parsers[0] = CompoundCellParser()

            for row in self.rows:
                row_compound = Compound()
                # Keep cell records that are contextual to merge at the end
                contextual_cell_compounds = []
                for i, cell in enumerate(row):
                    log.debug(cell.tagged_tokens)
                    if i in value_parsers:
                        results = list(value_parsers[i].parse(cell.tagged_tokens))
                        if results:
                            log.debug('Cell column %s: Match %s: %s' % (i, value_parsers[i].__class__.__name__, [c.serialize() for c in results]))
                        # For each result, merge in values from elsewhere
                        for result in results:
                            # Merge each header_compounds[i]
                            for header_compound in header_compounds[i]:
                                if header_compound.is_contextual:
                                    result.merge_contextual(header_compound)
                            # Merge footnote compounds
                            for footnote in self.footnotes:
                                if footnote.id in cell.references:
                                    for footnote_compound in footnote.records:
                                        result.merge_contextual(footnote_compound)
                            if result.is_contextual:
                                # Don't merge cell as a value compound if there are no values
                                contextual_cell_compounds.append(result)
                            else:
                                row_compound.merge(result)
                # Merge contextual information from cells
                for contextual_cell_compound in contextual_cell_compounds:
                    row_compound.merge_contextual(contextual_cell_compound)
                # If no compound name/label, try take from previous row
                if not row_compound.names and not row_compound.labels and table_records:
                    prev = table_records[-1]
                    row_compound.names = prev.names
                    row_compound.labels = prev.labels
                # Merge contextual information from caption into the full row
                for caption_compound in caption_records:
                    if caption_compound.is_contextual:
                        row_compound.merge_contextual(caption_compound)
                # And also merge from any footnotes that are referenced from the caption
                for footnote in self.footnotes:
                    if footnote.id in self.caption.references:
                        # print('Footnote records: %s' % [c.to_primitive() for c in footnote.records])
                        for fn_compound in footnote.records:
                            row_compound.merge_contextual(fn_compound)

                log.debug(row_compound.serialize())
                if row_compound.serialize():
                    table_records.append(row_compound)

        # TODO: If no rows have name or label, see if one is in the caption

        # Include non-contextual caption records in the final output
        caption_records = [c for c in caption_records if not c.is_contextual]
        table_records += caption_records
        return table_records

    # TODO: extend abbreviations property to include footnotes
    # TODO: Resolve footnote records into headers


class Cell(Sentence):
    word_tokenizer = FineWordTokenizer()
    # pos_tagger = NoneTagger()
    ner_tagger = NoneTagger()

    @memoized_property
    def abbreviation_definitions(self):
        """Empty list. Abbreviation detection is disabled within table cells."""
        return []

    @property
    def records(self):
        """Empty list. Individual cells don't provide records, this is handled by the parent Table."""
        return []

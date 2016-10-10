# -*- coding: utf-8 -*-
"""
chemdataextractor.cli.evaluate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import copy
import json
import logging
import os

import click

from ..reader import RscHtmlReader, AcsHtmlReader, NlmXmlReader


log = logging.getLogger(__name__)


@click.group()
@click.pass_context
def evaluate(ctx):
    """Evaluation commands."""
    pass


@evaluate.command()
@click.argument('input', type=click.File('r'))
def run(input):
    """"""
    pub = os.path.basename(input.name).split('.', 1)[0]
    if pub == 'rsc':
        reader = RscHtmlReader()
    elif pub == 'acs':
        reader = AcsHtmlReader()
    elif pub == 'springer':
        reader = NlmXmlReader()
    else:
        raise click.ClickException('Invalid publisher')
    doc = reader.read(input)
    # Serialize all records apart from those that are just chemical names or just labels
    records = [record.serialize(primitive=True) for record in doc.records]
    records = [record for record in records if not record.keys() == ['names'] and not record.keys() == ['labels']]
    with open('%s-out.json' % os.path.splitext(input.name)[0], 'w') as outf:
        json.dump(records, outf, indent=2)


def eval_document(gold, out, transform=None):
    if transform:
        gold = transform(gold)
        out = transform(out)
    tp, fp, fn = 0, 0, 0
    tmp_out = copy.deepcopy(out)
    tmp_gold = copy.deepcopy(gold)
    for gc in gold:
        if gc not in tmp_out:
            fn += 1
        else:
            tmp_out.remove(gc)
    for oc in out:
        if oc not in tmp_gold:
            fp += 1
        else:
            tp += 1
            tmp_gold.remove(oc)
    return tp, fp, fn


def get_names(cs):
    """Return list of every name."""
    records = []
    for c in cs:
        records.extend(c.get('names', []))
    return records


def get_labels(cs):
    """Return list of every label."""
    records = []
    for c in cs:
        records.extend(c.get('labels', []))
    return records


def get_ids(cs):
    """Return chemical identifier records."""
    records = []
    for c in cs:
        records.append({k: c[k] for k in c if k in {'names', 'labels'}})
    return records


def get_spectra_type(cs):
    records = []
    for c in cs:
        for nmr in c.get('nmr_spectra', []):
            records.append('nmr')
        for uvvis in c.get('uvvis_spectra', []):
            records.append('uvvis')
        for ir in c.get('ir_spectra', []):
            records.append('ir')
    return records


def get_spectra_subject(cs):
    records = []
    for c in cs:
        for nmr in c.get('nmr_spectra', []):
            records.append({k: c[k] for k in c if k in {'names', 'labels'}})
        for uvvis in c.get('uvvis_spectra', []):
            records.append({k: c[k] for k in c if k in {'names', 'labels'}})
        for ir in c.get('ir_spectra', []):
            records.append({k: c[k] for k in c if k in {'names', 'labels'}})
    return records


def get_spectra_peaks(cs):
    records = []
    for c in cs:
        for nmr in c.get('nmr_spectra', []):
            if 'peaks' in nmr:
                records.append(nmr['peaks'])
        for uvvis in c.get('uvvis_spectra', []):
            if 'peaks' in uvvis:
                records.append(uvvis['peaks'])
        for ir in c.get('ir_spectra', []):
            if 'peaks' in ir:
                records.append(ir['peaks'])
    return records


def get_spectra_solvent(cs):
    records = []
    for c in cs:
        for nmr in c.get('nmr_spectra', []):
            if 'solvent' in nmr:
                records.append(nmr['solvent'])
        for uvvis in c.get('uvvis_spectra', []):
            if 'solvent' in uvvis:
                records.append(uvvis['solvent'])
        for ir in c.get('ir_spectra', []):
            if 'solvent' in ir:
                records.append(ir['solvent'])
    return records


def get_spectra_core(cs):
    records = []
    for c in cs:
        for nmr in c.get('nmr_spectra', []):
            nmr = {k: nmr[k] for k in nmr if k in {'peaks', 'solvent'}}
            records.append(nmr)
        for uvvis in c.get('uvvis_spectra', []):
            uvvis = {k: uvvis[k] for k in uvvis if k in {'peaks', 'solvent'}}
            records.append(uvvis)
        for ir in c.get('ir_spectra', []):
            ir = {k: ir[k] for k in ir if k in {'peaks', 'solvent'}}
            records.append(ir)
    return records


def get_spectra_temp(cs):
    records = []
    for c in cs:
        for nmr in c.get('nmr_spectra', []):
            if 'temperature' in nmr:
                records.append(nmr['temperature'])
        for uvvis in c.get('uvvis_spectra', []):
            if 'temperature' in uvvis:
                records.append(uvvis['temperature'])
        for ir in c.get('ir_spectra', []):
            if 'temperature' in ir:
                records.append(ir['temperature'])
    return records


def get_spectra_apparatus(cs):
    records = []
    for c in cs:
        for nmr in c.get('nmr_spectra', []):
            if 'apparatus' in nmr:
                records.append(nmr['apparatus'])
        for uvvis in c.get('uvvis_spectra', []):
            if 'apparatus' in uvvis:
                records.append(uvvis['apparatus'])
        for ir in c.get('ir_spectra', []):
            if 'apparatus' in ir:
                records.append(ir['apparatus'])
    return records


def get_spectra_full(cs):
    records = []
    for c in cs:
        for nmr in c.get('nmr_spectra', []):
            nmr['subject'] = {k: c[k] for k in c if k in {'names', 'labels'}}
            records.append(nmr)
        for uvvis in c.get('uvvis_spectra', []):
            uvvis['subject'] = {k: c[k] for k in c if k in {'names', 'labels'}}
            records.append(uvvis)
        for ir in c.get('ir_spectra', []):
            ir['subject'] = {k: c[k] for k in c if k in {'names', 'labels'}}
            records.append(ir)
    return records


def get_property_value(cs):
    records = []
    for c in cs:
        for qy in c.get('quantum_yields', []):
            if 'value' in qy:
                records.append(qy['value'])
        for mp in c.get('melting_points', []):
            if 'value' in mp:
                records.append(mp['value'])
        for fl in c.get('fluorescence_lifetimes', []):
            if 'value' in fl:
                records.append(fl['value'])
        for op in c.get('electrochemical_potentials', []):
            if 'value' in op:
                records.append(op['value'])
    return records


def get_property_units(cs):
    records = []
    for c in cs:
        for qy in c.get('quantum_yields', []):
            if 'units' in qy:
                records.append(qy['units'])
        for mp in c.get('melting_points', []):
            if 'units' in mp:
                records.append(mp['units'])
        for fl in c.get('fluorescence_lifetimes', []):
            if 'units' in fl:
                records.append(fl['units'])
        for op in c.get('electrochemical_potentials', []):
            if 'units' in op:
                records.append(op['units'])
    return records


def get_property_subject(cs):
    records = []
    for c in cs:
        for qy in c.get('quantum_yields', []):
            records.append({k: c[k] for k in c if k in {'names', 'labels'}})
        for mp in c.get('melting_points', []):
            records.append({k: c[k] for k in c if k in {'names', 'labels'}})
        for fl in c.get('fluorescence_lifetimes', []):
            records.append({k: c[k] for k in c if k in {'names', 'labels'}})
        for op in c.get('electrochemical_potentials', []):
            records.append({k: c[k] for k in c if k in {'names', 'labels'}})
    return records


def get_property_solvent(cs):
    records = []
    for c in cs:
        for qy in c.get('quantum_yields', []):
            if 'solvent' in qy:
                records.append(qy['solvent'])
        for mp in c.get('melting_points', []):
            if 'solvent' in mp:
                records.append(mp['solvent'])
        for fl in c.get('fluorescence_lifetimes', []):
            if 'solvent' in fl:
                records.append(fl['solvent'])
        for op in c.get('electrochemical_potentials', []):
            if 'solvent' in op:
                records.append(op['solvent'])
    return records


def get_property_temperature(cs):
    records = []
    for c in cs:
        for qy in c.get('quantum_yields', []):
            if 'temperature' in qy:
                records.append(qy['temperature'])
        for fl in c.get('fluorescence_lifetimes', []):
            if 'temperature' in fl:
                records.append(fl['temperature'])
        for op in c.get('electrochemical_potentials', []):
            if 'temperature' in op:
                records.append(op['temperature'])
    return records


def get_property_apparatus(cs):
    records = []
    for c in cs:
        for qy in c.get('quantum_yields', []):
            if 'apparatus' in qy:
                records.append(qy['apparatus'])
        for mp in c.get('melting_points', []):
            if 'solvent' in mp:
                records.append(mp['apparatus'])
        for fl in c.get('fluorescence_lifetimes', []):
            if 'apparatus' in fl:
                records.append(fl['apparatus'])
        for op in c.get('electrochemical_potentials', []):
            if 'apparatus' in op:
                records.append(op['apparatus'])
    return records


def get_property_core(cs):
    records = []
    for c in cs:
        for qy in c.get('quantum_yields', []):
            qy = {k: qy[k] for k in qy if k in {'value', 'units', 'solvent'}}
            records.append(qy)
        for qy in c.get('melting_points', []):
            qy = {k: qy[k] for k in qy if k in {'value', 'units', 'solvent'}}
            records.append(qy)
        for qy in c.get('fluorescence_lifetimes', []):
            qy = {k: qy[k] for k in qy if k in {'value', 'units', 'solvent'}}
            records.append(qy)
        for qy in c.get('electrochemical_potentials', []):
            qy = {k: qy[k] for k in qy if k in {'value', 'units', 'solvent'}}
            records.append(qy)
    return records


def get_property_full(cs):
    records = []
    for c in cs:
        for qy in c.get('quantum_yields', []):
            qy['subject'] = {k: c[k] for k in c if k in {'names', 'labels'}}
            records.append(qy)
        for qy in c.get('melting_points', []):
            qy['subject'] = {k: c[k] for k in c if k in {'names', 'labels'}}
            records.append(qy)
        for qy in c.get('fluorescence_lifetimes', []):
            qy['subject'] = {k: c[k] for k in c if k in {'names', 'labels'}}
            records.append(qy)
        for qy in c.get('electrochemical_potentials', []):
            qy['subject'] = {k: c[k] for k in c if k in {'names', 'labels'}}
            records.append(qy)
    return records


EVALS = [
    ('full', None),
    ('names', get_names),
    ('labels', get_labels),
    ('ids', get_ids),
    ('spectra type', get_spectra_type),
    ('spectra subject', get_spectra_subject),
    ('spectra peaks', get_spectra_peaks),
    ('spectra solvent', get_spectra_solvent),
    ('spectra temperature', get_spectra_temp),
    ('spectra apparatus', get_spectra_apparatus),
    ('spectra full', get_spectra_full),
    ('property value', get_property_value),
    ('property units', get_property_units),
    ('property subject', get_property_subject),
    ('property solvent', get_property_solvent),
    ('property temperature', get_property_temperature),
    ('property apparatus', get_property_apparatus),
    ('property full', get_property_full),
]


@evaluate.command()
def compare():
    """"""

    edir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data/cde-evaluation')
    for eval_name, transform in EVALS:
        print('Evaluation: %s' % eval_name)
        doc_count = 0
        tp, fp, fn = 0, 0, 0
        for filename in os.listdir(edir):
            filename = os.path.join(edir, filename)
            # print(filename)
            if filename.endswith('-out.json'):
                with open(filename) as outf:
                    out = json.load(outf)
                if not os.path.isfile('%s-gold.json' % filename[:-9]):
                    continue
                with open('%s-gold.json' % filename[:-9]) as goldf:
                    gold = json.load(goldf)
                doctp, docfp, docfn = eval_document(gold, out, transform)
                doc_count += 1
                tp += doctp
                fp += docfp
                fn += docfn
        print('TP: %s\tFP:%s\tFN:%s' % (tp, fp, fn))
        # if tp + fp > 0 and tp + fn > 0:
        p = 100 * float(tp) / (tp + fp) if tp > 0 or fp > 0 else 0
        r = 100 * float(tp) / (tp + fn) if tp > 0 or fn > 0 else 0
        f = 2 * p * r / (p + r) if p > 0 or r > 0 else 0
        print('P: %0.2f%%\tR: %0.2f%%\tF: %0.2f%%' % (p, r, f))
        print('%s documents' % doc_count)
        print('================================')

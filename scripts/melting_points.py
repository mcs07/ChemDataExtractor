# -*- coding: utf-8 -*-
"""
melting_points
~~~~~~~~~~~~~~

Patent melting points evaluation.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import copy
from collections import defaultdict
import gzip
import json
import logging
import math
import os
import re
import shutil
import pickle

import cirpy
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import rdMolDescriptors
import six

from chemdataextractor import Document
from chemdataextractor.doc import Paragraph, Table
from chemdataextractor.parse import ChemicalLabelParser, CompoundParser, MpParser
from chemdataextractor.text import HYPHENS, MINUSES
from chemdataextractor.text.normalize import excess_normalize

log = logging.getLogger(__name__)


def extract():
    """Extract melting points from patents."""
    Paragraph.parsers = [CompoundParser(), ChemicalLabelParser(), MpParser()]
    Table.parsers = []
    patents = []
    for root, dirs, files in os.walk('../examples/mp/grants'):
        for filename in files:
            if not filename.endswith('.xml'):
                continue
            path = os.path.abspath(os.path.join(root, filename))
            size = os.path.getsize(path)
            patents.append((path, filename, size))

    patents = sorted(patents, key=lambda p: p[2])

    for path, filename, size in patents:
        print(path)
        shutil.copyfile(path, '../examples/mp/used/%s' % filename)
        with open(path) as f:
            d = Document.from_file(f)
        if os.path.isfile('../examples/mp/results/%s.json' % filename):
            continue
        records = [r.serialize() for r in d.records if len(r.melting_points) == 1]
        with open('../examples/mp/results/%s.json' % filename, 'w') as fout:
            fout.write(json.dumps(records, ensure_ascii=False, indent=2).encode('utf8'))


def load_tetko():
    melting_points = defaultdict(list)
    mols = []
    mol = b''
    with open('../examples/melting_point.sdf') as sdf:
        for line in sdf:
            line = line
            if line == b'$$$$\n':
                mols.append(mol)
                mol = b''
            else:
                mol += line
    mol = b''
    with open('../examples/pyrolysis_point.sdf') as sdf:
        for line in sdf:
            line = line
            if line == b'$$$$\n':
                mols.append(mol)
                mol = b''
            else:
                mol += line
    for mol in mols:
        result = {}
        m = re.search('\n>  <Patent>\n(.+?)\n', mol)
        patent_id = m.group(1).strip()
        m = re.search('\n>  <OriginalText>\n(.+?)\n', mol)
        result[b'original_text'] = m.group(1).strip()
        m = re.search('\n>  <Value>\n(.+?)\n', mol)
        result[b'value'] = m.group(1).strip()
        m = re.search('\n>  <SMILES>\n(.+?)\n', mol)
        result[b'smiles'] = m.group(1).strip()
        m = re.search('\n>  <StdInChIKey>\n(.+?)\n', mol)
        result[b'inchikey'] = m.group(1).strip()
        # m = re.search('\n>  <SuspiciousValue>\n(.+?)\n', mol)
        # result[b'suspicious'] = m.group(1).strip()
        result[b'name'] = mol.split(b'\n', 1)[0].strip()
        result[b'float_value'] = float_value(result[b'value'])
        melting_points[patent_id].append(result)

    for filename in os.listdir('../examples/mp/results'):
        patent_id = filename[:-9]
        with open('../examples/mp/tetko/%s.json' % patent_id, 'w') as fout:
            json.dump(melting_points[patent_id], fout, ensure_ascii=False, indent=2)


def _get_standardized_result(result, tetko_results, n2s):
    names = sorted(result['names'], key=len, reverse=True)
    fv = float_value(standardize_value(result['melting_points'][0]['value']))
    if not fv:
        print('INVALID')
        print(names)
        print(result['melting_points'][0]['value'])
        return
    for name in names:
        for tetko_result in tetko_results:
            if excess_normalize(name) == excess_normalize(tetko_result['name']):
                return {
                    'name': name,
                    'smiles': tetko_result['smiles'],
                    'inchikey': tetko_result['inchikey'],
                    'value': result['melting_points'][0]['value'],
                    'float_value': fv
                }
    for name in names:
        if name not in n2s:
            print('MISSING: %s' % name)
            continue
            # results = cirpy.query(name.encode('utf8'), 'smiles', ['name_by_opsin', 'name_by_cir'])
            # print(name)
            # print([(r.value, r.resolver) for r in results])
            # n2s[name] = [(r.value, r.resolver) for r in results]
            # with open('n2s.pickle', 'w') as fout:
            #     pickle.dump(n2s, fout)
        smiles = n2s[name]
        if smiles:
            if '.' in smiles:
                continue
            mol = Chem.MolFromSmiles(smiles)
            if mol:
                inchikey = Chem.InchiToInchiKey(Chem.MolToInchi(mol))
                return {
                    'name': name,
                    'smiles': smiles,
                    'inchikey': inchikey,
                    'value': result['melting_points'][0]['value'],
                    'float_value': fv
                }


def standardize_results():
    # with open('n2s.pickle 7') as fin:
    #     n2s = pickle.load(fin)
    n2s = {}
    with open('opsin_input.txt') as op_in:
        with open('opsin_output.txt') as op_out:
            for name, smiles in six.moves.zip(op_in, op_out):
                n2s[name.strip().decode('utf8')] = smiles.strip().decode('utf8')

    result_dir = '../examples/mp/results'
    for filename in os.listdir(result_dir):
        if not filename.endswith('.json'):
            continue
        patent_id = filename[:-9]
        print(patent_id)
        tetko_file = '../examples/mp/tetko/%s.json' % patent_id
        if not os.path.isfile(tetko_file):
            continue
        with open('%s/%s' % (result_dir, filename)) as fin:
            results = json.loads(fin.read().decode('utf8'))
        with open(tetko_file) as tin:
            tetko_results = json.loads(tin.read().decode('utf8'))
        standardized_results = []
        for result in results:
            if 'names' not in result:
                continue
            standardized_result = _get_standardized_result(result, tetko_results, n2s)

            if standardized_result:
                standardized_results.append(standardized_result)
        with open('../examples/mp/standardized_results/%s.json' % patent_id, 'w') as fout:
            fout.write(json.dumps(standardized_results, ensure_ascii=False, indent=2).encode('utf8'))


def make_opsin_input():
    seen = set()
    with open('opsin_input.txt', 'w') as op_out:
        result_dir = '../examples/mp/results'
        for filename in os.listdir(result_dir):
            if not filename.endswith('.json'):
                continue
            patent_id = filename[:-9]
            print(patent_id)
            tetko_file = '../examples/mp/tetko/%s.json' % patent_id
            if not os.path.isfile(tetko_file):
                continue
            with open('%s/%s' % (result_dir, filename)) as fin:
                results = json.loads(fin.read().decode('utf8'))
            with open(tetko_file) as tin:
                tetko_results = json.loads(tin.read().decode('utf8'))
            for result in results:
                if 'names' not in result:
                    continue
                for name in result['names']:
                    in_tetko = False
                    for tetko_result in tetko_results:
                        if excess_normalize(name) == excess_normalize(tetko_result['name']):
                            in_tetko = True
                            break
                    if not in_tetko and name not in seen:
                        seen.add(name)
                        op_out.write(('%s\n' % name).encode('utf8'))


def standardize_value(value):
    for hyphen in HYPHENS | MINUSES:
        value = value.replace(hyphen, '-')

    range_m = re.match('^[~∼˜]?(-?[\d\.]+)[\-–−~∼˜]([\d\.]+)$', value)
    if range_m:
        start = range_m.group(1)
        end = range_m.group(2)
        # Fix e.g. 123-7 or 120-40
        if re.match('^\d+$', start) and re.match('^\d+$', end) and len(end) < len(start):
            end = start[:len(start) - len(end)] + end
        value = '%s to %s' % (start, end)
    return value


def float_value(value):
    if re.match('^\d\d\d\d\d\d$', value):
        # Missing hyphen?
        print('MISSING HYPHEN')
        print(value)
        value = value[:3] + ' to ' + value[3:]
        print(value)
    if re.match('^\d\d\d\d$', value):
        # Missing hyphen?
        print('MISSING HYPHEN')
        print(value)
        value = value[:2] + ' to ' + value[2:]
        print(value)

    if ' to ' in value:
        start, end = value.split(' to ')
        if start[0] == '>' or start[0] == '~' or start[0] == '<':
            start = start[1:]
        if end[0] == '>' or end[0] == '~' or end[0] == '<':
            end = end[1:]
        if re.match('^\d\d\d\d$', start) and re.match('^\d\d\d$', end):
            print('MISSING DECIMAL')
            print(start)
            start = start[:3] + '.' + start[3]
            print(start)
        if re.match('^\d\d\d\d$', end) and re.match('^\d\d\d$', start):
            print('MISSING DECIMAL')
            print(end)
            end = end[:3] + '.' + end[3]
            print(end)

        fstart = float(start)
        fend = float(end)
        if fend - fstart > 50 or fstart > fend:
            return
        value = (fstart + fend) / 2.0
    elif value[0] == '>' or value[0] == '~' or value[0] == '<':
        value = float(value[1:])  # TODO: Exclude?
    else:
        value = float(value)
    if value > 500:
        return
    return value


def compare():
    import matplotlib.pyplot as plt
    import numpy as np

    # Load values for entire tetko dataset
    tetko_all_values = []
    tetko_all_smiles = []
    tetko_all_by_inchi_key = defaultdict(list)
    mol = b''
    with open('../examples/melting_point.sdf') as sdf:
        for line in sdf:
            line = line
            if line == b'$$$$\n':
                m = re.search('\n>  <StdInChIKey>\n(.+?)\n', mol)
                inchikey = m.group(1).strip()
                m = re.search('\n>  <SMILES>\n(.+?)\n', mol)
                tetko_all_smiles.append(m.group(1).strip())
                m = re.search('\n>  <Value>\n(.+?)\n', mol)
                fv = float_value(m.group(1).strip())
                if fv is not None:
                    tetko_all_values.append(fv)
                    tetko_all_by_inchi_key[inchikey].append(fv)
                mol = b''
            else:
                mol += line
    mol = b''
    with open('../examples/pyrolysis_point.sdf') as sdf:
        for line in sdf:
            line = line
            if line == b'$$$$\n':
                m = re.search('\n>  <StdInChIKey>\n(.+?)\n', mol)
                inchikey = m.group(1).strip()
                m = re.search('\n>  <SMILES>\n(.+?)\n', mol)
                tetko_all_smiles.append(m.group(1).strip())
                m = re.search('\n>  <Value>\n(.+?)\n', mol)
                fv = float_value(m.group(1).strip())
                if fv is not None:
                    tetko_all_values.append(fv)
                    tetko_all_by_inchi_key[inchikey].append(fv)
                mol = b''
            else:
                mol += line

    # Load the samples
    my_results_by_inchikey = defaultdict(list)
    my_results_by_patent = defaultdict(list)
    tetko_results_by_inchikey = defaultdict(list)
    tetko_results_by_patent = defaultdict(list)

    result_dir = '../examples/mp/standardized_results'
    for filename in os.listdir(result_dir):
        if not filename.endswith('.json'):
            continue
        patent_id = filename[:-5]

        tetko_file = '../examples/mp/tetko/%s.json' % patent_id
        if not os.path.isfile(tetko_file):
            continue

        with open('%s/%s' % (result_dir, filename)) as fin:
            results = json.loads(fin.read().decode('utf8'))
            for m in results:
                m['patent_id'] = patent_id
                my_results_by_inchikey[m['inchikey']].append(m)
                my_results_by_patent[m['patent_id']].append(m)

        with open(tetko_file) as tin:
            tetko_results = json.loads(tin.read().decode('utf8'))
            for m in tetko_results:
                m['patent_id'] = patent_id
                tetko_results_by_inchikey[m['inchikey']].append(m)
                tetko_results_by_patent[m['patent_id']].append(m)

    tetko_lenient_results_by_inchikey = copy.deepcopy(tetko_results_by_inchikey)
    tetko_lenient_results_by_patent = copy.deepcopy(tetko_results_by_patent)

    my_melting_points = set()
    my_values = []
    my_smiles = []
    for inchikey, results in my_results_by_inchikey.items():
        if len(results) == 1:
            chosen = results[0]
        elif len(results) == 2:
            sorted_results = sorted(results, key=lambda x: x['float_value'])
            chosen = sorted_results[0]
        else:
            median = np.median([r['float_value'] for r in results])
            chosen = results[0]
            for result in results:
                if result['float_value'] - median < chosen['float_value'] < median:
                    chosen = result

        my_melting_points.add((inchikey, chosen['float_value']))
        my_values.append(chosen['float_value'])
        my_smiles.append(chosen['smiles'])

        # Lenient tetko
        if inchikey not in tetko_results_by_inchikey and inchikey in tetko_all_by_inchi_key:
            tetko_lenient_results_by_inchikey[inchikey].append(chosen)
            tetko_lenient_results_by_patent[chosen['patent_id']].append(chosen)

    tetko_melting_points = set()
    tetko_values = []
    tetko_smiles = []
    for inchikey, results in tetko_results_by_inchikey.items():
        tetko_melting_points.add((inchikey, results[0]['float_value']))
        tetko_values.append(results[0]['float_value'])
        tetko_smiles.append(results[0]['smiles'])

    tetko_lenient_melting_points = set()
    tetko_lenient_values = []
    tetko_lenient_smiles = []
    for inchikey, results in tetko_lenient_results_by_inchikey.items():
        tetko_lenient_melting_points.add((inchikey, results[0]['float_value']))
        tetko_lenient_values.append(results[0]['float_value'])
        tetko_lenient_smiles.append(results[0]['smiles'])

    print('My count: %s' % len(my_melting_points))
    print('Tetko count: %s' % len(tetko_melting_points))
    print('Tetko lenient count: %s' % len(tetko_lenient_melting_points))
    print('--------')

    exact_match_count = 0
    non_match_count = 0
    differences = []
    nonzero_differences = []
    for inchikey, value in my_melting_points:
        if inchikey in tetko_results_by_inchikey:
            if tetko_results_by_inchikey[inchikey][0]['float_value'] == value:
                exact_match_count += 1
            else:
                non_match_count += 1
                nonzero_differences.append(tetko_results_by_inchikey[inchikey][0]['float_value'] - value)
            differences.append(tetko_results_by_inchikey[inchikey][0]['float_value'] - value)

    # Root mean squared difference between values of the same compound
    rmsd = math.sqrt(sum(d * d for d in differences) / len(differences))
    nonzero_rmsd = math.sqrt(sum(d * d for d in nonzero_differences) / len(nonzero_differences))

    print('Exact matches: %s' % exact_match_count)
    print('Compound matches, values different: %s' % non_match_count)
    print('RMSD: %s' % rmsd)
    print('Nonzero diff RMSD: %s' % nonzero_rmsd)
    print('--------')

    common = len(my_melting_points & tetko_melting_points)
    my = len(my_melting_points - tetko_melting_points)
    tetko = len(tetko_melting_points - my_melting_points)
    total = len(my_melting_points | tetko_melting_points)

    print('Common: %s (%s%%)' % (common, (100.0 * common / total)))
    print('Just Mine: %s (%s%%)' % (my, (100.0 * my / total)))
    print('Just Tetko: %s (%s%%)' % (tetko, (100.0 * tetko / total)))
    print('Total count: %s' % total)
    print('--------')

    common_l = len(my_melting_points & tetko_lenient_melting_points)
    my_l = len(my_melting_points - tetko_lenient_melting_points)
    tetko_l = len(tetko_lenient_melting_points - my_melting_points)
    total_l = len(my_melting_points | tetko_lenient_melting_points)

    print('Common lenient: %s (%s%%)' % (common_l, (100.0 * common_l / total_l)))
    print('Just Mine lenient: %s (%s%%)' % (my_l, (100.0 * my_l / total_l)))
    print('Just Tetko lenient: %s (%s%%)' % (tetko_l, (100.0 * tetko_l / total_l)))
    print('Total count lenient: %s' % total_l)
    print('--------')

    print('tetko_all_values mean %s' % np.mean(tetko_all_values))
    print('tetko_values mean %s' % np.mean(tetko_values))
    print('my_values mean %s' % np.mean(my_values))

    # result_dir = '../examples/mp/standardized_results'
    # for filename in os.listdir(result_dir):
    #     if not filename.endswith('.json'):
    #         continue
    #     patent_id = filename[:-5]
    #     # print(my_results_by_patent[patent_id])
    #     # print(tetko_lenient_results_by_patent[patent_id])
    #     mine = {(r['inchikey'], r['float_value']): r for r in my_results_by_patent[patent_id]}
    #     tetko = {(r['inchikey'], r['float_value']): r for r in tetko_lenient_results_by_patent[patent_id]}
    #     print(patent_id)
    #     for k, v in mine.items():
    #         if k not in tetko:
    #             print('%s : %s' % (v['value'], v['name']))
    #
    #     print('------')
    #     for k, v in tetko.items():
    #         if k not in mine:
    #             print('%s : %s' % (v['original_text'], v['name']))
    #
    #     print('------')
    #     for k, v in tetko.items():
    #         if k in mine:
    #             print('%s : %s : %s : %s' % (v.get('original_text', v['value']), mine[k]['value'], v['name'], mine[k]['name']))
    #
    #     print('======')


    # my_mws = []
    # my_nas = []
    # for smiles in my_smiles:
    #     mol = Chem.MolFromSmiles(smiles)
    #     my_mws.append(rdMolDescriptors.CalcExactMolWt(mol))
    #     my_nas.append(mol.GetNumHeavyAtoms())
    #
    # tetko_mws = []
    # tetko_nas = []
    # for smiles in tetko_smiles:
    #     mol = Chem.MolFromSmiles(smiles)
    #     tetko_mws.append(rdMolDescriptors.CalcExactMolWt(mol))
    #     tetko_nas.append(mol.GetNumHeavyAtoms())
    # #
    # # tetko_all_mws = []
    # # tetko_all_nas = []
    # # for smiles in tetko_all_smiles:
    # #     mol = Chem.MolFromSmiles(smiles)
    # #     if not mol:
    # #         print(smiles)
    # #         continue
    # #     tetko_all_mws.append(rdMolDescriptors.CalcExactMolWt(mol))
    # #     tetko_all_nas.append(mol.GetNumHeavyAtoms())
    # #
    # print('my avg MW %s' % np.mean(my_mws))
    # print('tetko avg MW %s' % np.mean(tetko_mws))
    # # print('tetko all avg MW %s' % np.mean(tetko_all_mws))
    # print('my avg NA %s' % np.mean(my_nas))
    # print('tetko avg NA %s' % np.mean(tetko_nas))
    # # print('tetko all avg NA %s' % np.mean(tetko_all_nas))
    #
    #
    #
    binrange = range(0, 400, 10)
    mn, mbins, mpatches = plt.hist(my_values, binrange, normed=1)
    tn, tbins, tpatches = plt.hist(tetko_values, binrange, normed=1, facecolor='green')
    tan, tabins, tapatches = plt.hist(tetko_all_values, binrange, normed=1, facecolor='green')
    bincenters = 0.5 * (mbins[1:] + mbins[:-1])
    fig = plt.figure(num=None, figsize=(8, 5), dpi=200)
    plt.plot(bincenters, mn, '-', linewidth=3, label='ChemDataExtractor')
    plt.plot(bincenters, tn, '-', linewidth=3, label='Tetko')
    plt.plot(bincenters, tan, '-', linewidth=3, label='Tetko (All)')
    plt.grid(b=True, which='both', color='#cccccc', linestyle='-')
    fig.gca().set_axisbelow(True)
    plt.legend(loc='upper right', numpoints=1)
    plt.xlabel('Melting point (°C)')
    plt.ylabel('Data density')
    plt.savefig('mp-histogram.pdf', dpi=200)


def run_n2s():

    n2s = {}
    if os.path.isfile('n2s.pickle'):
        with open('n2s.pickle') as fin:
            n2s = pickle.load(fin)
    print('Starting with %s names' % len(n2s))
    result_dir = '../examples/mp/results'
    for filename in os.listdir(result_dir):
        if not filename.endswith('.json'):
            continue
        print(filename)
        with open('%s/%s' % (result_dir, filename)) as fin:
            results = json.loads(fin.read().decode('utf8'))
            for compound in results:
                if 'names' not in compound or 'melting_points' not in compound:
                    continue
                for name in compound['names']:
                    if name not in n2s:
                        results = cirpy.query(name.encode('utf8'), 'smiles', ['name_by_opsin', 'name_by_cir'])
                        print(name)
                        print([(r.value, r.resolver) for r in results])
                        n2s[name] = [(r.value, r.resolver) for r in results]
    with open('n2s.pickle', 'w') as fout:
        pickle.dump(n2s, fout)


def make_sdf():
    """Produce SDF of ChemDataExtractor and Tetko sample melting points."""
    # import numpy as np
    # my_results_by_inchikey = defaultdict(list)
    # result_dir = '../examples/mp/standardized_results'
    # fout = open('../examples/mp/sdf/chemdataextractor-melting-points.sdf', 'w')
    # writer = Chem.SDWriter(fout)
    # for filename in os.listdir(result_dir):
    #     if not filename.endswith('.json'):
    #         continue
    #     patent_id = filename[:-5]
    #     with open('%s/%s' % (result_dir, filename)) as fin:
    #         results = json.loads(fin.read().decode('utf8'))
    #         for m in results:
    #             m['patent_id'] = patent_id
    #             mol = Chem.MolFromSmiles(m['smiles'])
    #             mol.SetProp(b'_Name', m['name'].encode('utf-8'))
    #             mol.SetProp(b'OriginalText', m['value'].encode('utf-8'))
    #             mol.SetProp(b'Value', b'%s' % m['float_value'])
    #             mol.SetProp(b'Patent', m['patent_id'].encode('utf-8'))
    #             mol.SetProp(b'SMILES', Chem.MolToSmiles(mol, isomericSmiles=True))
    #             mol.SetProp(b'QuantityType', b'MeltingPoint')
    #             mol.SetProp(b'StdInChIKey', Chem.InchiToInchiKey(Chem.MolToInchi(mol)))
    #             if not mol:
    #                 print('WARNING: %s' % m)
    #                 return
    #             AllChem.Compute2DCoords(mol)
    #             writer.write(mol)
    #             my_results_by_inchikey[m['inchikey']].append(m)
    # writer.close()
    # fout.close()
    #
    # fout = open('../examples/mp/sdf/chemdataextractor-melting-points-filtered.sdf', 'w')
    # writer = Chem.SDWriter(fout)
    # for inchikey, results in my_results_by_inchikey.items():
    #     if len(results) == 1:
    #         m = results[0]
    #     elif len(results) == 2:
    #         sorted_results = sorted(results, key=lambda x: x['float_value'])
    #         m = sorted_results[0]
    #     else:
    #         median = np.median([r['float_value'] for r in results])
    #         chosen = results[0]
    #         for result in results:
    #             if result['float_value'] - median < chosen['float_value'] < median:
    #                 m = result
    #     mol = Chem.MolFromSmiles(m['smiles'])
    #     mol.SetProp(b'_Name', m['name'].encode('utf-8'))
    #     mol.SetProp(b'OriginalText', m['value'].encode('utf-8'))
    #     mol.SetProp(b'Value', b'%s' % m['float_value'])
    #     mol.SetProp(b'Patent', m['patent_id'].encode('utf-8'))
    #     mol.SetProp(b'SMILES', Chem.MolToSmiles(mol, isomericSmiles=True))
    #     mol.SetProp(b'QuantityType', b'MeltingPoint')
    #     mol.SetProp(b'StdInChIKey', Chem.InchiToInchiKey(Chem.MolToInchi(mol)))
    #     if not mol:
    #         print('WARNING: %s' % m)
    #         return
    #     AllChem.Compute2DCoords(mol)
    #     writer.write(mol)


    with open('../examples/mp/sdf/chemdataextractor-melting-points.sdf', 'rb') as f_in, gzip.open('../examples/mp/sdf/chemdataextractor-melting-points.sdf.gz', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

    with open('../examples/mp/sdf/chemdataextractor-melting-points-filtered.sdf', 'rb') as f_in, gzip.open('../examples/mp/sdf/chemdataextractor-melting-points-filtered.sdf.gz', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)


if __name__ == '__main__':
    # extract()
    # load_tetko()
    compare()
    # run_n2s()
    # standardize_results()
    # make_sdf()
    # make_opsin_input()
    # with open('n2s.pickle') as fin:
    #     n2s = pickle.load(fin)
    # for key, value in n2s.items():
    #     print(key)
    #     print(value)

    # mp = 0
    # py = 0
    # with open('../examples/melting_point.sdf') as sdf:
    #     for line in sdf:
    #         if line == b'$$$$\n':
    #             mp += 1
    # mol = b''
    # with open('../examples/pyrolysis_point.sdf') as sdf:
    #     for line in sdf:
    #         if line == b'$$$$\n':
    #             py += 1
    #
    # print(mp)
    # print(py)

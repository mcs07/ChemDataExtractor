#!/bin/sh

cde dict build data/cde-dict/jochem-cs.txt data/cde-dict/include.txt --output data/models/dict_chem_cs.pickle --cs
cde dict build data/cde-dict/jochem.txt --output data/models/dict_chem.pickle

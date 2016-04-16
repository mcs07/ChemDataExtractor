#!/bin/sh

cde chemdner prepare_tokens data/chemdner-1.0/evaluation.abstracts.txt --annotations data/chemdner-1.0/evaluation.annotations.txt --tout data/cde-ner/chemdner-evaluation-tag.txt --lout data/cde-ner/chemdner-evaluation-label.txt
cde chemdner prepare_tokens data/chemdner-1.0/training.abstracts.txt --annotations data/chemdner-1.0/training.annotations.txt --tout data/cde-ner/chemdner-training-tag.txt --lout data/cde-ner/chemdner-training-label.txt
cde chemdner prepare_tokens data/chemdner-1.0/development.abstracts.txt --annotations data/chemdner-1.0/development.annotations.txt --tout data/cde-ner/chemdner-development-tag.txt --lout data/cde-ner/chemdner-development-label.txt

#!/bin/sh

# Train Perceptron part-of-speech tagger on various corpus combinations
cde pos train --output data/models/perceptron_wsj_nocluster.pickle --corpus wsj --no-clusters
cde pos train --output data/models/perceptron_wsj.pickle --corpus wsj
cde pos train --output data/models/perceptron_genia_nocluster.pickle --corpus genia --no-clusters
cde pos train --output data/models/perceptron_genia.pickle --corpus genia
cde pos train --output data/models/perceptron_medpost_nocluster.pickle --corpus medpost --no-clusters
cde pos train --output data/models/perceptron_medpost.pickle --corpus medpost
cde pos train --output data/models/perceptron_wsj_genia_nocluster.pickle --corpus wsj+genia --no-clusters
cde pos train --output data/models/perceptron_wsj_genia.pickle --corpus wsj+genia
cde pos train --output data/models/perceptron_wsj_genia_medpost.pickle --corpus wsj+genia+medpost
cde pos train --output data/models/perceptron_wsj_genia_medpost_nocluster.pickle --corpus wsj+genia+medpost --no-clusters
cde pos train --output data/models/perceptron_wsj_medpost.pickle --corpus wsj+medpost
cde pos train --output data/models/perceptron_wsj_medpost_nocluster.pickle --corpus wsj+medpost --no-clusters
cde pos train --output data/models/perceptron_genia_medpost.pickle --corpus genia+medpost
cde pos train --output data/models/perceptron_genia_medpost_nocluster.pickle --corpus genia+medpost --no-clusters


cde pos evaluate data/models/perceptron_wsj_nocluster.pickle --corpus wsj
cde pos evaluate data/models/perceptron_wsj.pickle --corpus wsj
cde pos evaluate data/models/perceptron_genia_nocluster.pickle --corpus wsj
cde pos evaluate data/models/perceptron_genia.pickle --corpus wsj
cde pos evaluate data/models/perceptron_medpost_nocluster.pickle --corpus wsj
cde pos evaluate data/models/perceptron_medpost.pickle --corpus wsj
cde pos evaluate data/models/perceptron_wsj_genia_nocluster.pickle --corpus wsj
cde pos evaluate data/models/perceptron_wsj_genia.pickle --corpus wsj
cde pos evaluate data/models/perceptron_wsj_genia_medpost.pickle --corpus wsj
cde pos evaluate data/models/perceptron_wsj_genia_medpost_nocluster.pickle --corpus wsj
cde pos evaluate data/models/perceptron_wsj_medpost.pickle --corpus wsj
cde pos evaluate data/models/perceptron_wsj_medpost_nocluster.pickle --corpus wsj
cde pos evaluate data/models/perceptron_genia_medpost.pickle --corpus wsj
cde pos evaluate data/models/perceptron_genia_medpost_nocluster.pickle --corpus wsj

cde pos evaluate data/models/perceptron_wsj_nocluster.pickle --corpus genia
cde pos evaluate data/models/perceptron_wsj.pickle --corpus genia
cde pos evaluate data/models/perceptron_genia_nocluster.pickle --corpus genia
cde pos evaluate data/models/perceptron_genia.pickle --corpus genia
cde pos evaluate data/models/perceptron_medpost_nocluster.pickle --corpus genia
cde pos evaluate data/models/perceptron_medpost.pickle --corpus genia
cde pos evaluate data/models/perceptron_wsj_genia_nocluster.pickle --corpus genia
cde pos evaluate data/models/perceptron_wsj_genia.pickle --corpus genia
cde pos evaluate data/models/perceptron_wsj_genia_medpost.pickle --corpus genia
cde pos evaluate data/models/perceptron_wsj_genia_medpost_nocluster.pickle --corpus genia
cde pos evaluate data/models/perceptron_wsj_medpost.pickle --corpus genia
cde pos evaluate data/models/perceptron_wsj_medpost_nocluster.pickle --corpus genia
cde pos evaluate data/models/perceptron_genia_medpost.pickle --corpus genia
cde pos evaluate data/models/perceptron_genia_medpost_nocluster.pickle --corpus genia

cde pos evaluate data/models/perceptron_wsj_nocluster.pickle --corpus medpost
cde pos evaluate data/models/perceptron_wsj.pickle --corpus medpost
cde pos evaluate data/models/perceptron_genia_nocluster.pickle --corpus medpost
cde pos evaluate data/models/perceptron_genia.pickle --corpus medpost
cde pos evaluate data/models/perceptron_medpost_nocluster.pickle --corpus medpost
cde pos evaluate data/models/perceptron_medpost.pickle --corpus medpost
cde pos evaluate data/models/perceptron_wsj_genia_nocluster.pickle --corpus medpost
cde pos evaluate data/models/perceptron_wsj_genia.pickle --corpus medpost
cde pos evaluate data/models/perceptron_wsj_genia_medpost.pickle --corpus medpost
cde pos evaluate data/models/perceptron_wsj_genia_medpost_nocluster.pickle --corpus medpost
cde pos evaluate data/models/perceptron_wsj_medpost.pickle --corpus medpost
cde pos evaluate data/models/perceptron_wsj_medpost_nocluster.pickle --corpus medpost
cde pos evaluate data/models/perceptron_genia_medpost.pickle --corpus medpost
cde pos evaluate data/models/perceptron_genia_medpost_nocluster.pickle --corpus medpost

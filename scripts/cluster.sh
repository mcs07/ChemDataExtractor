#!/bin/sh

# Example script showing how to generate the word clusters

# Get dependencies
sudo apt-get -y update
sudo apt-get -y install git g++ make

# Install Percy Liang's brown-cluster tool
git clone https://github.com/percyliang/brown-cluster.git
cd brown-cluster
make

# Run wcluster. nohup runs it in background so we can do over ssh, allowing disconnections
nohup ./wcluster --c 1500 --threads 40 --text brown-cluster-input.txt &

# Generate the HTML pages of word clusters
./cluster-viewer/build-viewer.sh brown-cluster-input-c1500-p1.out/paths

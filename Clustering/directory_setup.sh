#!bin/bash
# A simple shell script to set up the directories necessary for the R scripts to run
mkdir data
mkdir data/hierarchical
mkdir data/hierarchical/low_slot
mkdir data/hierarchical/mid_slot
mkdir data/hierarchical/high_slot
mkdir data/kmedoids
mkdir data/kmedoids/low_slot
mkdir data/kmedoids/mid_slot
mkdir data/kmedoids/high_slot
mkdir data/series
mkdir data/t_test
mkdir visuals
mkdir visuals/gower_hierachical
mkdir visuals/hierarchical_dendrograms
mkdir visuals/hierarchical_quality
mkdir visuals/kmedoids_quality
mkdir visuals/trajectories
cp ../Trajectory_Mining/data/Series/players_frig_actv_ts-evt.csv data/series

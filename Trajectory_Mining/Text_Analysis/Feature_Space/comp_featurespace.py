# -*- coding: utf-8 -*-
"""Computes feature space of dissimilarity matrix using non-metric MDS.

NOTE: Also possible to use PCA algorithm as well!

We take all the killmails, in the entire dataset, and we estimate the 
distances between every killmail and every other killmail. We can then project 
this on to a 2-dimensional Euclidean space. Now we have a “feature space” that 
captures all the different ways in which ships have been configured. We can 
then trace trajectories throughout this space, and use characeristics of those 
trajectories to predict K/D…then each ship configuration would be relative to 
all other ship configurations, rather than just become related to the prior 
ship.

Written By: Adam Coscia
Updated On: 02/04/2020

"""
# Start timing
from sklearn.manifold import MDS
import pandas as pd
import numpy as np
import time
start = time.time()
total = 0


def lap(msg):
    """Records time elapsed."""
    global start, total
    elapsed = (time.time() - start) - total
    total = time.time() - start
    if elapsed > 3600:
        print(f'(+{elapsed/3600:.2f}h|t:{total/3600:.2f}h) {msg}')
    elif elapsed > 60:
        if total > 3600:
            print(f'(+{elapsed/60:.2f}m|t:{total/3600:.2f}h) {msg}')
        else:
            print(f'(+{elapsed/60:.2f}m|t:{total/60:.2f}m) {msg}')
    else:
        if total > 3600:
            print(f'(+{elapsed:.3f}s|t:{total/3600:.2f}h) {msg}')
        elif total > 60:
            print(f'(+{elapsed:.3f}s|t:{total/60:.2f}m) {msg}')
        else:
            print(f'(+{elapsed:.3f}s|t:{total:.3f}s) {msg}')


def run_MDS(df, dimensions=2, isMetric=True, seed=None):
    """Runs MDS on dissimilarity matrix, returns DataFrame of n-d space.

    https://scikit-learn.org/stable/modules/generated/sklearn.manifold.MDS.html
    https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html

    May optionally specify number of dimensions, whether the distances are
    metric, and if there is a seed you want to initial the random center to.
    """
    embedding = MDS(n_components=dimensions, metric=isMetric,
                    dissimilarity='precomputed', random_state=seed)
    df_transformed = embedding.fit_transform(df)
    del embedding
    return pd.DataFrame(df_transformed)


# Load CSVs from local file
lap("Loading CSV data from local files...")
df_lt = pd.read_csv(f'data/LT_s3_distmatrix.csv', encoding='utf-8')
df_st = pd.read_csv(f'data/ST_s3_distmatrix.csv', encoding='utf-8')
# preserve indices for new feature space
lt_idx = df_lt['killmail_id']
st_idx = df_st['killmail_id']
# set indices of dissimilarity matrices
df_lt = df_lt.set_index('killmail_id')
df_st = df_st.set_index('killmail_id')

# Computing MDS dimension reduction, returning feature space (FS)
lap("Running MDS transformation on distance matrices...")
# Since MDS is probabilistic, use a seed to reproduce results
seed = 1
dimensions = 2
dist_is_metric = False
# Run the MDS algorithm
fs_lt = run_MDS(df_lt, dimensions, dist_is_metric, seed)
fs_st = run_MDS(df_st, dimensions, dist_is_metric, seed)
# set index on new n-dimenstional feature space DataFrames
fs_lt = fs_lt.set_index(lt_idx)
fs_st = fs_st.set_index(st_idx)

# Write results to CSV
lap("Writing results to CSV...")
fs_lt.to_csv(f'data/LT_s3_featspace_s{seed}.csv')
fs_st.to_csv(f'data/ST_s3_featspace_s{seed}.csv')

lap("Exit")

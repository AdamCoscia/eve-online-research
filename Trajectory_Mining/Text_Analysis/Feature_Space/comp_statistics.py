# -*- coding: utf-8 -*-
"""Computes statistics per player.

We take all the killmails, in the entire dataset, and we estimate the 
distances between every killmail and every other killmail. We can then project 
this on to a 2-dimensional Euclidean space. Now we have a “feature space” that 
captures all the different ways in which ships have been configured. We can 
then trace trajectories throughout this space, and use characeristics of those 
trajectories to predict K/D...then each ship configuration would be relative to 
all other ship configurations, rather than just become related to the prior 
ship.

Written By: Adam Coscia
Updated On: 02/24/2020

"""
# Start timing
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


def stats_table(df1, df2):
    """Makes stats table from grouped series in df1, and combine with K/D
    observations from same group found in df2.
    """
    rows = []  # stats per player
    grouped = df2.groupby('character_id')  # get groups with K/D obs
    for cid, gp1 in df1.groupby('character_id'):
        gp2 = grouped.get_group(cid)  # get same group from df2
        kd_mean = gp2['kd_ratio'].mean()  # calc mean K/D
        kd_final = gp2['kd_ratio'].iloc[-1]  # get final K/D
        s = gp1["Euclidean_Distance"]  # euclidean distances
        rows.append([cid, s.var(), s.max()-s.min(), s.count(), s.mean(), 
                     s.std(), kd_mean, kd_final])
    return pd.DataFrame(data=rows, columns=['character_id', 'var', 'range', 
                        'count', 'mean', 'std_dev', 'avg_kd', 'final_kd'])


# Load CSVs from local file
lap("Loading CSV data from local files...")
df_lt = pd.read_csv(f'data/LT_victims_s3_featspace_s1_timeline.csv', 
                    encoding='utf-8')
df_st = pd.read_csv(f'data/ST_victims_s3_featspace_s1_timeline.csv', 
                    encoding='utf-8')
df_kd = pd.read_csv(f'../data/all_victims_kd.csv', encoding='utf-8')
# drop all infs and 0s from incomplete data
df_kd = df_kd.drop(df_kd[(df_kd.kd_ratio == np.inf) | (df_kd.kd_ratio == 0.0)].index)

# Create statistics table for each player
lap("Computing Player Statistics...")
lt_stats = stats_table(df_lt, df_kd)
st_stats = stats_table(df_st, df_kd)

# Write results to CSV
lap("Writing results to CSV...")
lt_stats.to_csv(f'data/LT_victims_s3_featspace_s1_stats.csv', index=False)
st_stats.to_csv(f'data/ST_victims_s3_featspace_s1_stats.csv', index=False)

lap("Exit")

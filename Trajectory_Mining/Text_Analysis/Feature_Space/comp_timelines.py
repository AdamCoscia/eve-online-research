# -*- coding: utf-8 -*-
"""Computes timeline of player trajectories in 2d feature space from prev
MDS output files.

We take all the killmails, in the entire dataset, and we estimate the 
distances between every killmail and every other killmail. We can then project 
this on to a 2-dimensional Euclidean space. Now we have a “feature space” that 
captures all the different ways in which ships have been configured. We can 
then trace trajectories throughout this space, and use characeristics of those 
trajectories to predict K/D…then each ship configuration would be relative to 
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


def construct_timelines(df):
    """Creates timelines of player absolute positions and distance between
    positions in 2d feature space created by MDS routine.

    Groups by character id to be able to separate players out of the
    MDS routine and returns list of groups with distances appended.
    """
    groupby = df.groupby('character_id')  # group dataframe by character_id
    num_groups = len(groupby)  # get number of groups
    count = 0  # current group number out of number of groups
    groups = []  # list to append modified group dataframes to
    for gp in groupby:
        # Get distances between coords and cat on to group
        x1 = gp["X"]
        x2 = gp["X"].shift()
        y1 = gp["Y"]
        y2 = gp["Y"].shift()
        euc_dist = ((x2 - x1)**2 + (y2 - y1)**2).apply(np.sqrt)
        euc_dist = euc_dist.rename('Euclidean_Distance')
        man_dist = np.abs(x2-x1) + np.abs(y2-y1)
        man_dist = man_dist.rename('Manhattan_Distance')
        groups.append(pd.concat([gp, euc_dist, man_dist], axis=1))
        # Record progress
        count += 1
        print(f"Progress {count/num_groups:2.1%}", end="\r")
    return groups


# Load CSVs from local file
lap("Loading CSV data from local files...")
df_lt = pd.read_csv(f'data/LT_s3_featspace_s1.csv', encoding='utf-8')
df_st = pd.read_csv(f'data/ST_s3_featspace_s1.csv', encoding='utf-8')
df = pd.read_csv(f'../data/all_victims_items_frigates_100+_s3.csv',
                 encoding='utf-8')

# set indices of feature spaces
df_lt = df_lt.set_index('killmail_id')
df_st = df_st.set_index('killmail_id')
# rename columns for ease of use
df_lt = df_lt.rename(columns={"0": "X", "1": "Y"})
df_st = df_st.rename(columns={"0": "X", "1": "Y"})

# Merge feat space df's with character id's
lap("Merging feature spaces with character id's...")
df_lt = df.merge(df_lt, on='killmail_id')
df_st = df.merge(df_st, on='killmail_id')

# Write intermediate results to CSV, don't save index
lap("Writing intermediate results to CSV...")
df_lt.to_csv(f'data/LT_victims_s3_featspace_s1.csv', index=False)
df_st.to_csv(f'data/ST_victims_s3_featspace_s1.csv', index=False)

# Set up dataframes for calculating euclidean distance b/w t and t-1
df_lt = df_lt.drop(columns=['ship_type_id', 'solar_system_id', 'items'])
df_st = df_st.drop(columns=['ship_type_id', 'solar_system_id', 'items'])

# Construct timelines by group
lap("Constructing timelines from intermediate results...")
groups_lt = construct_timelines(df_lt)
groups_st = construct_timelines(df_st)

# Create final dataframes
tm_lt = pd.concat(groups_lt)
tm_st = pd.concat(groups_st)

# Write results to CSV, don't save index
lap("Writing results to CSV...")
tm_lt.to_csv(f'data/LT_victims_s3_featspace_s1_timeline.csv', index=False)
tm_st.to_csv(f'data/ST_victims_s3_featspace_s1_timeline.csv', index=False)

lap("Exit")

# -*- coding: utf-8 -*-
"""Computes correlation between columns in data.

Written By: Adam Coscia
Updated On: 11/12/2019

"""
# Start timing
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


lap("Importing modules...")

import json
import os
import sys

import numpy as np
import pandas as pd

# Load CSV from local file
lap("Loading CSV data from local file...")
df = pd.read_csv(f'data/useable_victims_distancesAndKD.csv', encoding='utf-8')

# Group DataFrame by character_id and compute distance series for each group
lap("Computing correlation b/w cosine distances and kd by grouping character_id's...")
groupby = df.groupby('character_id')  # group dataframe by character_id
num_groups = len(groupby)  # get number of groups
count = 0  # current group number out of number of groups
results = {}  # dict to insert results to
for name, gp in groupby:
    # Order the observations and prepare the dataframe
    gp = (gp.sort_values(by=['killmail_id'])
                  .reset_index()
                  .drop('index', axis=1))
    # Generate correlations between columns:
    # kd_ratio  kd_ratio_diff  cos_dist_st  cos_dist_lt
    corr_kdd_cds = gp['kd_ratio_diff'].corr(gp['cos_dist_st'])
    corr_kdd_cdl = gp['kd_ratio_diff'].corr(gp['cos_dist_lt'])
    results[name] = {
            'corr_kdd_cds': corr_kdd_cds,
            'corr_kdd_cdl': corr_kdd_cdl
    }
    # Record progress
    count += 1
    print(f"Progress {count/num_groups:2.1%}", end="\r")

lap("Writing groups to file...")
with open('correlations.json', 'w') as f:
    f.write(json.dumps(results))

lap("Exit")

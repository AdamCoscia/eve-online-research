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
import statsmodels.api as sm

# Load CSV from local file
lap("Loading CSV data from local file...")
df = pd.read_csv(f'data/model_dataset.csv', encoding='utf-8')

# Group DataFrame by character_id and compute distance series for each group
lap("Getting average/sum cosine distance and kd by grouping character_id's...")
groupby = df.groupby('character_id')  # group dataframe by character_id
num_groups = len(groupby)  # get number of groups
count = 0  # current group number out of number of groups
sum_cos_dist_st = []  # list of sums of cos shot text distances per player
sum_cos_dist_lt = []  # list of sums of cos long text distances per player
final_kd = []  # list of last kd per player
avg_cos_dist_st = []  # list of averages of short text cos distances per player
avg_cos_dist_lt = []  # list of averages of long text cos distances per player
avg_kd = []  # list of average kd per player
for name, gp in groupby:
    # Order the observations and prepare the dataframe
    gp = (gp.sort_values(by=['killmail_id'])
                  .reset_index()
                  .drop('index', axis=1))
    # Generate averages and sums:
    sum_cos_dist_st.append(gp['cos_dist_st'].sum())  # sum of st cos dist
    sum_cos_dist_lt.append(gp['cos_dist_lt'].sum())  # sum of lt cos dist
    final_kd.append(gp['kd_ratio'].tail(1).iloc[0])  # final kd ratio
    avg_cos_dist_st.append(gp['cos_dist_st'].mean())  # avg st cos dist
    avg_cos_dist_lt.append(gp['cos_dist_lt'].mean())  # avg st cos dist
    avg_kd.append(gp['kd_ratio'].mean())  # avg kd ratio
    # Record progress
    count += 1
    print(f"Progress {count/num_groups:2.1%}", end="\r")

lap("Generating correlations...")
# Turn lists into Pandas series objects that are standard score scaled
scds = pd.Series(sum_cos_dist_st)
scds = (scds - scds.mean()) / scds.std()  # z-scaling

scdl = pd.Series(sum_cos_dist_lt)
scdl = (scdl - scdl.mean()) / scdl.std()  # z-scaling

sfkd = pd.Series(final_kd)
sfkd = (sfkd - sfkd.mean()) / sfkd.std()  # z-scaling

acds = pd.Series(avg_cos_dist_st)
acds = (acds - acds.mean()) / acds.std()  # z-scaling

acdl = pd.Series(avg_cos_dist_lt)
acdl = (acdl - acdl.mean()) / acdl.std()  # z-scaling

aakd = pd.Series(avg_kd)
aakd = (aakd - aakd.mean()) / aakd.std()  # z-scaling

lap("Writing results to file...")
with open('correlation_models.txt', 'w') as f:
    f.write("Final KD vs. Sum of Short Text Cosine Distances\n")
    mod = sm.OLS(sfkd, scds)  # predict final kd from sum cost dist st
    res = mod.fit()
    f.write(str(res.summary()))
    f.write("\n\n\n")

    f.write("Final KD vs. Sum of Long Text Cosine Distances\n")
    mod = sm.OLS(sfkd, scdl)  # predict final kd from sum cost dist lt
    res = mod.fit()
    f.write(str(res.summary()))
    f.write("\n\n\n")

    f.write("Avg KD vs. Avg Short Text Cosine Distances\n")
    mod = sm.OLS(aakd, acds)  # predict avg kd from avg cost dist lt
    res = mod.fit()
    f.write(str(res.summary()))
    f.write("\n\n\n")

    f.write("Avg KD vs. Avg Long Text Cosine Distances\n")
    mod = sm.OLS(aakd, acdl)  # predict avg kd from avg cost dist lt
    res = mod.fit()
    f.write(str(res.summary()))
    f.write("\n\n\n")

lap("Exit")

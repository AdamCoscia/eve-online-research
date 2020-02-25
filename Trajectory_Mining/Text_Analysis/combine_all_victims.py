# -*- coding: utf-8 -*-
"""Combines all victim slot investment files into single file. Then combines
slot data with item data.

Written By: Adam Coscia
Updated On: 11/10/2019

"""
# Start timing
import pandas as pd
import numpy as np
import sys
import os
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


# Sequentially load CSV's from file
lap("Loading CSV data from data/All/by_region...")
victims = []  # list of victim dataframes generated from CSV's
dirs = ["../Trajectory_Mining/data/All/by_region/10000002/Victims",
        "../Trajectory_Mining/data/All/by_region/10000016/Victims",
        "../Trajectory_Mining/data/All/by_region/10000033/Victims",
        "../Trajectory_Mining/data/All/by_region/10000069/Victims"]
ct = 0
for loc in dirs:
    files = [f for f in os.listdir(loc) if os.path.isfile(os.path.join(loc, f))]
    count = 0
    ct += 1
    num_files = len(files)  # number of CSV files
    for file in sorted(files):
        print(f"{ct}/4 | Progress {count/num_files:2.1%} ", end="\r")
        df = pd.read_csv(os.path.join(loc, file), encoding='utf-8')
        victims.append(df)
        count += 1

# Concat-ing dataframes and joining with other data set
lap("Concatenating victims and writing to CSV...")
df_victims_slots = pd.concat(victims)
df_victims_slots.to_csv('data/all_victims_slots.csv')

# Merging data sets and validating results
lap("Merging data sets...")
df_victims_items = pd.read_csv('data/all_victims_items.csv', header=0)
df_victims_all = pd.merge(df_victims_items, df_victims_slots, how='outer',
                          on=['killmail_id'], suffixes=('_items', '_slots'),
                          indicator=True)

# Save victim and attacker info to CSV
lap("Writing results to CSV...")
df_victims_all.to_csv('data/all_victims_complete.csv')

lap("Exit")

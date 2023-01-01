# -*- coding: utf-8 -*-
"""Filters all victims to include only useable killmails.

Filters:
- Ship Type (keep only combat-based Frigate-class ships)

Written By: Adam Coscia
Updated On: 01/23/2020

"""
# Start timing
import random
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


def drop_by_ship_type_id(df):
    """Drops rows that do not contain specific ship type IDs."""
    ship_type_idS = {583, 584, 585, 587, 589, 591, 593, 594, 597, 598, 602,
                     603, 608, 609, 2161, 2834, 3516, 3532, 3766, 11174, 11176,
                     11178, 11184, 11186, 11190, 11194, 11196, 11198, 11200,
                     11202, 11365, 11371, 11377, 11379, 11381, 11387, 11393,
                     11400, 12032, 12034, 12038, 12042, 12044, 17619, 17703,
                     17812, 17841, 17924, 17926, 17928, 17930, 17932, 32207,
                     32788, 33468, 33673, 33677, 33816, 34443, 35779, 37453,
                     37454, 37455, 37456, 47269}
    return df.drop(df[~df['ship_type_id'].isin(ship_type_idS)].index)


def drop_by_group_quality(df):
    """Drops groups that don't meet the quality requirements."""
    return (df.groupby('character_id')
              .filter(lambda x: len(x) > 99)
              .reset_index()
              .drop(columns=['index']))


def filter_random_groups(df, group_id, sample_size, replace, seed=None):
    """Randomly selects groups by group id, with or without replacement."""
    if replace:
        sample = (random.Random(seed)
                        .chioces(list(df[group_id].unique()), k=sample_size))
    else:
        sample = (random.Random(seed)
                        .sample(list(df[group_id].unique()), k=sample_size))
    groups = []
    for s in sample:
        groups.append(df.groupby(group_id).get_group(s))
    return (pd.concat(groups)
              .reset_index()
              .drop(columns=['index']))


# Sequentially load CSV's from file
lap("Loading CSV data...")
df = pd.read_csv('data/all_victims_items.csv', header=0)

# Filter out ship types
lap("Filtering ship types...")
df = drop_by_ship_type_id(df)

# Drop groups that don't meet group quality
lap("Dropping inadequate groups...")
df = drop_by_group_quality(df)

# Get random sampling of groups
lap("Sampling random groups...")
seed = 3
group_id = 'character_id'
sample_size = 20
replace = False
groups = filter_random_groups(df, group_id, sample_size, replace, seed)

# Save sampled groups to CSV
lap(f"Writing seed {seed} results to CSV...")
groups.to_csv(f'data/all_victims_items_frigates_100+_seedno{seed}.csv', 
              index=False)

lap("Exit")

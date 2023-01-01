# -*- coding: utf-8 -*-
"""Computes distance between killmails by text similarity.

Edit Distance Metrics
- Levenshtein Distance
- Damerau-Levenshtein Distance
- Jaro Distance
- Jaro-Winkler Distance
- Match Rating Approach Comparison
- Hamming Distance

Vector Distance Metrics
- Jaccard Similarity
- Cosine Distance

Written By: Adam Coscia
Updated On: 11/09/2019

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

from ast import literal_eval
from functools import reduce
import os
import sys

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


def get_long_text_cosine_distance(los1, los2):
    """Calculates cosine distance between two killmails' item lists.

    1. Converts collection of long text items to raw document representation.
    2. Converts the collection of raw documents to a matrix of TF-IDF features
       using TfidfVectorizer (combines vector counting and TF-IDF calculator).
    3. Computes cosine similarity between feature vectors. Uses linear kernel
       since TF-IDF matrix will be normalized already.

    Arguments:
        los1: First document, a list of raw strings.
        los2: Second document, a list of raw strings.
    Returns:
        cosine distance as a value between 0-1, with 1 being identical.
    """
    if type(los1) == float or type(los2) == float:
        return 0
    if len(los1) == 0 or len(los2) == 0:
        return 0
    doc1 = reduce(lambda x, y: f'{x} {y}', [x[0] for x in los1])  # Create bag of words
    doc2 = reduce(lambda x, y: f'{x} {y}', [x[0] for x in los2])  # Create bag of words
    tfidf = TfidfVectorizer().fit_transform([doc1, doc2])  # Vectorize the bag of words
    cos_dist = linear_kernel(tfidf[0:1], tfidf[1:2]).flatten()[0]  # Compute cosine distance
    return cos_dist


def get_short_text_cosine_distance(los1, los2):
    """Calculates cosine distance between two killmails' item lists.

    1. Converts collection of short text items to raw document representation.
    2. Converts the collection of raw documents to a matrix of TF-IDF features
       using TfidfVectorizer (combines vector counting and TF-IDF calculator).
    3. Computes cosine similarity between feature vectors. Uses linear kernel
       since TF-IDF matrix will be normalized already.

    Arguments:
        los1: First document, a list of raw strings.
        los2: Second document, a list of raw strings.
    Returns:
        cosine distance as a value between 0-1, with 1 being identical and 0
        being complete different.
    """
    if type(los1) == float or type(los2) == float:
        return 0
    if len(los1) == 0 or len(los2) == 0:
        return 0
    doc1 = reduce(lambda x, y: f'{x} {y}', [x[1] for x in los1])  # Create bag of words
    doc2 = reduce(lambda x, y: f'{x} {y}', [x[1] for x in los2])  # Create bag of words
    tfidf = TfidfVectorizer().fit_transform([doc1, doc2])  # Vectorize the bag of words
    cos_dist = linear_kernel(tfidf[0:1], tfidf[1:2]).flatten()[0]  # Compute cosine distance
    return cos_dist


# Load CSV from local file
lap("Loading CSV data from local file...")
df = pd.read_csv(f'data/all_victims_complete_partialKD.csv', encoding='utf-8')
df = df.drop(columns=['HighSlotISK', 'MidSlotISK', 'LowSlotISK', 'type', 'fill'])
df = df.dropna()

# Convert items column to correct data type
lap("Converting 'item' column value types...")
df['items'] = df['items'].apply(literal_eval)

# Group DataFrame by character_id and compute distance series for each group
lap("Computing cosine distances and change in kd by grouping character_id's...")
groupby = df.groupby('character_id')  # group dataframe by character_id
num_groups = len(groupby)  # get number of groups
count = 0  # current group number out of number of groups
groups = []  # list to append modified group dataframes to
for name, gp in groupby:
    # Order the observations and prepare the dataframe
    gp = (gp.sort_values(by=['killmail_id'])
                  .reset_index()
                  .drop('index', axis=1))
    # Generate change in kills over change in deaths and change in kd ratio
    kills1 = gp['k_count']
    kills2 = gp['k_count'].shift()
    deaths1 = gp['d_count']
    deaths2 = gp['d_count'].shift()
    idx = len(gp.columns)
    gp.insert(idx, 'del_kdratio', (kills2 - kills1) / (deaths2 - deaths1))
    gp.insert(idx+1, 'kd_ratio_diff', gp['kd_ratio']-gp['kd_ratio'].shift())
    # Generate pairs of observations sequentially to compare
    pairs = []
    items1 = gp['items']
    items2 = gp['items'].shift()
    for i in range(1, len(gp)):  # Start from 1 to avoid adding nan pair
        los1 = items1.iloc[i]
        los2 = items2.iloc[i]
        pairs.append((los2, los1))
    # Generate distance series using pairs list and different metrics
    # start distance series with nan due to starting range at 1
    cos_dist_lt = [np.nan]  # cosine distance b/w long text BoW
    cos_dist_st = [np.nan]  # cosine distance b/w short text BoW
    for pair in pairs:
        cos_dist_lt.append(get_long_text_cosine_distance(pair[0], pair[1]))
        cos_dist_st.append(get_short_text_cosine_distance(pair[0], pair[1]))
    idx = len(gp.columns)
    gp.insert(idx, 'cos_dist_lt', cos_dist_lt)
    gp.insert(idx, 'cos_dist_st', cos_dist_st)
    groups.append(gp)
    # Record progress
    count += 1
    print(f"Progress {count/num_groups:2.1%}", end="\r")

lap("Concatenating resulting groups and writing to file...")
df_res = pd.concat(groups)
df_res.to_csv(f'data/useable_victims_distancesAndKD.csv')

lap("Exit")

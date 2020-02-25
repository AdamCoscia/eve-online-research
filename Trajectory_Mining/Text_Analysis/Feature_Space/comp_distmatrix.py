# -*- coding: utf-8 -*-
"""Computes distance matrix using vector distance between all killmails.

We take all the killmails, in the entire dataset, and we estimate the 
distances between every killmail and every other killmail. We can then project 
this on to a 2-dimensional Euclidean space. Now we have a “feature space” that 
captures all the different ways in which ships have been configured. We can 
then trace trajectories throughout this space, and use characeristics of those 
trajectories to predict K/D…then each ship configuration would be relative to 
all other ship configurations, rather than just become related to the prior 
ship.

Edit Distance Metrics:
- Levenshtein Distance
- Damerau-Levenshtein Distance
- Jaro Distance
- Jaro-Winkler Distance
- Match Rating Approach Comparison
- Hamming Distance

Vector Distance Metrics:
- Jaccard Similarity
- Cosine Distance <- (currently using this one)

Written By: Adam Coscia
Updated On: 02/04/2020

"""
# Start timing
from sklearn.metrics.pairwise import linear_kernel
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import numpy as np
import sys
import os
from functools import reduce
from ast import literal_eval
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


def LTcosDist(los1, los2):
    """Calculates long-text cosine distance between two killmails' item lists.

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
    doc1 = reduce(lambda x, y: f'{x} {y}', [x[0] for x in los1])
    doc2 = reduce(lambda x, y: f'{x} {y}', [x[0] for x in los2])
    # Vectorize the bag of words
    tfidf = TfidfVectorizer().fit_transform([doc1, doc2])
    # Compute cosine distance
    cos_dist = linear_kernel(tfidf[0:1], tfidf[1:2]).flatten()[0]
    return cos_dist


def STcosDist(los1, los2):
    """Calculates cosine distance between two killmails' short-text item lists.

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
    doc1 = reduce(lambda x, y: f'{x} {y}', [x[1] for x in los1])
    doc2 = reduce(lambda x, y: f'{x} {y}', [x[1] for x in los2])
    # Vectorize the bag of words
    tfidf = TfidfVectorizer().fit_transform([doc1, doc2])
    # Compute cosine distance
    cos_dist = linear_kernel(tfidf[0:1], tfidf[1:2]).flatten()[0]
    return cos_dist


def compare_killmails_file_method(df):
    """Compares killmails by saving the comparisons in separate files denoted
    by killmail beinn compared to every other killmail.

    Example: 
    - compare main_row['killmail_id'] == 12345 to every other km using 
      long-text comparison
    - File will look like this:
      ```
      Killmail ID, Long-Text Cosine Distance
      12346, 0.23
      12347, 0.39
      ...
      ```

    After all files created, can later merge them together to create 2d
    feature space where (i,j) coords are killmail_ids being compared.
    """
    nrows = len(df)
    count = 0
    # for each killmail compare all other killmails to it and record results
    for i in range(nrows):
        # get main killmail row
        main_row = df.iloc[i]
        # open two files for each killmail, 1 for long text and 1 for short text
        f_lt = open(f'data/lt_{main_row["killmail_id"]}_cosDist.csv', 'w+')
        f_st = open(f'data/st_{main_row["killmail_id"]}_cosDist.csv', 'w+')
        # write headers at the top of the file
        f_lt.write('Killmail ID,Long-Text Cosine Distance\n')
        f_st.write('Killmail ID,Short-Text Cosine Distance\n')
        for j in range(nrows):
            # get comparison killmail row
            comp_row = df.iloc[j]
            # compute cosine distance b/w main row and comp row
            ltcosdist = LTcosDist(main_row['items'], comp_row['items'])
            stcosdist = STcosDist(main_row['items'], comp_row['items'])
            # write cosine distance to file
            f_lt.write(f'{comp_row["killmail_id"]},{ltcosdist}\n')
            f_st.write(f'{comp_row["killmail_id"]},{stcosdist}\n')
        f_lt.close()
        f_st.close()
        # Record progress
        count += 1
        print(f"Progress {count/nrows:2.2%}", end="\r", flush=True)


def compare_killmails_df_method(df):
    """Compares killmails by generating cosine distance and saving it to a
    DataFrame indexed by killmail ID's.

    Fills in the resultant DataFrames by mirroring the comparison over the
    diagonal, thus reducing n^2 comparisons to n*(n-1)/2 comparisons.
    """
    # Create two empty DataFrames indexed by killmails for ST and LT
    STres = pd.DataFrame(np.nan, index=df.killmail_id, columns=df.killmail_id)
    LTres = pd.DataFrame(np.nan, index=df.killmail_id, columns=df.killmail_id)
    nrows = len(df)
    count = 0
    # for each killmail compare all other killmails to it and record results
    for i in range(nrows):
        # get main killmail row and identifier
        main_row = df.iloc[i]
        id_i = main_row['killmail_id']
        for j in range(i, nrows):
            # get comparison killmail row and identifier
            comp_row = df.iloc[j]
            id_j = comp_row['killmail_id']
            # compute cosine distance b/w main row and comp row
            ltcosdist = LTcosDist(main_row['items'], comp_row['items'])
            stcosdist = STcosDist(main_row['items'], comp_row['items'])
            # Record cos dist in each res DataFrame
            STres.at[id_i, id_j] = stcosdist
            STres.at[id_j, id_i] = stcosdist
            LTres.at[id_i, id_j] = ltcosdist
            LTres.at[id_j, id_i] = ltcosdist
        # Record progress
        count += 1
        print(f"Progress {count/nrows:2.2%}", end="\r", flush=True)
    return STres, LTres


# Load CSV from local file
lap("Loading CSV data from local file...")
df = pd.read_csv(f'../data/all_victims_items_frigates_100+_seedno3.csv',
                 encoding='utf-8')

# Convert items column to correct data type
lap("Converting 'item' column value types...")
df['items'] = df['items'].apply(literal_eval)

# Compute distances between every killmail using method
lap("Computing cosine distances by killmail using DataFrame method...")
# compare_killmails_file_method(df)
STres, LTres = compare_killmails_df_method(df)

# Write results to CSV
lap("Writing results to CSV...")
STres.to_csv('data/ST_s3_distmatrix.csv')
LTres.to_csv('data/LT_s3_distmatrix.csv')

lap("Exit")

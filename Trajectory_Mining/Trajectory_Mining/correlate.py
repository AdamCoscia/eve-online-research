# -*- coding: utf-8 -*-
"""Generates correlation sets between data points/time series.

Utilizes the pandas library -
See https://pandas.pydata.org/pandas-docs/stable/api.html

Created by: Adam Coscia

Created on: 08/06/2018

Last Updated: 04/28/2019

"""
import math
import random
import sys

import pandas as pd
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean


def player_rstats(dft: pd.DataFrame, dstats=False):
    """Generates Pearson Correlation Coefficient (PCC) matrices and descriptive
    statistics for all player series.

    Since k/d ratio is the "base" series, we can flatten the result
    correlation matricies to only include the coefficients of k/d ratio vs
    slot and investment series.

    :param dft:
    :param dstats:
    :return:
    """
    # Group Data by Character ID and subset columns
    grouped = dft.groupby('character_id')[['kd_ratio', 'kd_prct',
                                           'od_ratio', 'od_prct']]

    # Generate Correlation Coefficients for each player!
    result = grouped.corr().reset_index().rename(columns={'level_1': 'stats'})

    if dstats:
        # Calculate player statistics on series and format like above
        stats = grouped.describe().stack()
        stats = stats.reset_index().rename(
            columns={'level_1': 'stats'}
        ).set_index(['character_id', 'stats'])

        # Join and sort the statistics and correlation arrays
        result = result.set_index(['character_id', 'stats'])
        result = pd.concat([result, stats])

    else:
        # Remove extraneous correlations
        ratio = result.drop(
            result[~result['stats'].isin(['od_ratio'])].index
        ).rename(columns={'kd_ratio': 'kd_od_ratio_corr'})
        ratio = ratio.drop(
            columns=['stats', 'kd_prct', 'od_prct', 'od_ratio']
        ).set_index('character_id')

        prct = result.drop(
            result[~result['stats'].isin(['od_prct'])].index
        ).rename(columns={'kd_prct': 'kd_od_prct_corr'})
        prct = prct.drop(
            columns=['stats', 'kd_ratio', 'od_ratio', 'od_prct']
        ).set_index('character_id')

        # Join correlations at the end
        result = ratio.join(prct)

    return result.sort_index()


def dtw_matrix(dfts: pd.DataFrame, k=None, seed=None, ids=None):
    """Creates DTW Correlation Matrices.

    :param dfts:  DataFrame containing time series data.
    :param k:  (Optional) Number of samples.
    :param seed:  (Optional) Seed for repeating specific tests.
    :param ids:  (Optional) Player IDS in seed test.
    :return:  The High Slot, Mid Slot, and Low Slot correlation matrices in
      2D python list.
    """
    print("DEBUG: DTW CORRELATIONS STARTED.")

    grouped = dfts.groupby('character_id')  # time series groups
    n = len(grouped)  # total number of series

    # Randomization for batch correlations
    #   Tests done:
    #     4/17/19 - seed = 1, k = 237 (10% of total time series)

    if seed is None:
        seed = random.random()  # create seed for reproducibility
    if k is None:
        k = n  # Set sample size to total number of series
    if ids is None:
        uids = dfts.character_id.unique()  # unique character ids
        ids = random.Random(seed).choices(uids, k=k)
    print(f"\tSEED: {seed}\n\tSAMPLE SIZE: {k}")

    # Slot Correlation Matrices
    hi_mat = [[None for x in range(k)] for x in range(k)]
    mid_mat = [[None for x in range(k)] for x in range(k)]
    lo_mat = [[None for x in range(k)] for x in range(k)]

    # List of lists
    hi_list = []
    mid_list = []
    lo_list = []

    # Get the time series for each of the random groups
    for cid in ids:
        group = grouped.get_group(cid)
        hi_list.append([x for x in group[['hi_slot']].values.tolist() for x
                        in x])
        mid_list.append([x for x in group[['mid_slot']].values.tolist() for x
                        in x])
        lo_list.append([x for x in group[['lo_slot']].values.tolist() for x
                        in x])

    print("DEBUG: HIGH MATRIX CALCULATIONS STARTED.")
    i = 0
    for hi1 in hi_list:
        j = i
        for hi2 in hi_list[i:]:
            hi_mat[i][j] = DTWDistance(hi1, hi2)
            # hi_mat[i][j], _ = fastdtw(hi1, hi2, dist=euclidean)
            j += 1
            # Prints a dot for each correlation performed
            sys.stdout.write('.')
            sys.stdout.flush()
            if j % (10+i) == 0 or j == k:
                sys.stdout.write('\n')
        print(f"DEBUG: {i+1}/{k} - HIGH SLOT - PLAYER {ids[i]} CORRELATED.")
        i += 1

    print("DEBUG: MID MATRIX CALCULATIONS STARTED.")
    i = 0
    for mid1 in mid_list:
        j = i
        for mid2 in mid_list[i:]:
            # mid_mat[i][j] = DTWDistance(mid1, mid2)
            mid_mat[i][j], _ = fastdtw(mid1, mid2, dist=euclidean)
            j += 1
            # Prints a dot for each correlation performed
            sys.stdout.write('.')
            sys.stdout.flush()
            if j % (10+i) == 0 or j == k:
                sys.stdout.write('\n')
        print(f"DEBUG: {i+1}/{k} - MID SLOT - PLAYER {ids[i]} CORRELATED.")
        i += 1

    print("DEBUG: LOW MATRIX CALCULATIONS STARTED.")
    i = 0
    for lo1 in lo_list:
        j = i
        for lo2 in lo_list[i:]:
            # lo_mat[i][j] = DTWDistance(lo1, lo2)
            lo_mat[i][j], _ = fastdtw(lo1, lo2, dist=euclidean)
            j += 1
            # Prints a dot for each correlation performed
            sys.stdout.write('.')
            sys.stdout.flush()
            if j % (10+i) == 0 or j == k:
                sys.stdout.write('\n')
        print(f"DEBUG: {i+1}/{k} - LOW SLOT - PLAYER {ids[i]} CORRELATED.")
        i += 1

    return hi_mat, mid_mat, lo_mat


def DTWDistance(s1, s2):
    DTW = {}

    for i in range(len(s1)):
        DTW[(i, -1)] = float('inf')
    for i in range(len(s2)):
        DTW[(-1, i)] = float('inf')
    DTW[(-1, -1)] = 0

    for i in range(len(s1)):
        for j in range(len(s2)):
            dist = (s1[i] - s2[j]) ** 2
            DTW[(i, j)] = dist + min(DTW[(i - 1, j)], DTW[(i, j - 1)],
                                     DTW[(i - 1, j - 1)])

    return math.sqrt(DTW[len(s1) - 1, len(s2) - 1])


# ============================================================================ #
# Use the Command Line or a Terminal to do basic pre-filtering!
dfts = pd.read_csv('../data/Series/players_frig_actv_ts-evt.csv', header=0)

# grouped = dfts.groupby('character_id')
# g1 = grouped.get_group(92358740)
# g2 = grouped.get_group(897120124)
# s1 = [x for x in g1[['hi_slot']].values.tolist() for x in x]
# s2 = [x for x in g2[['hi_slot']].values.tolist() for x in x]
# print(DTWDistance(s1, s2))

# Set seed, sample size, and player ids
seed = 1
uids = dfts.character_id.unique()  # unique character ids
n = len(uids)  # total number of samples
k = n//10  # 10% of total samples
ids = random.Random(seed).choices(uids, k=k)

# Calculate cost matrices
hmat, mmat, lmat = dtw_matrix(dfts, k=k, seed=seed, ids=ids)

# Convert them to DataFrames
idx = dfts.character_id.unique()
dfhm = pd.DataFrame(data=hmat, index=ids, columns=ids)
dfmm = pd.DataFrame(data=mmat, index=ids, columns=ids)
dflm = pd.DataFrame(data=lmat, index=ids, columns=ids)

# Save the new DataFrames!
dfhm.to_csv('../data/Series/dtw/evt_hmat_s1k237_20190417.csv')
dfmm.to_csv('../data/Series/dtw/evt_mmat_s1k237_20190417.csv')
dflm.to_csv('../data/Series/dtw/evt_lmat_s1k237_20190417.csv')

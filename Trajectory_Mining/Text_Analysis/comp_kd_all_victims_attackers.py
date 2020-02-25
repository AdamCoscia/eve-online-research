# -*- coding: utf-8 -*-
"""Computes k/d series for all players by combining victim and attacker
observations and representing each as a rolling tally of observations.

Written By: Adam Coscia
Updated On: 11/10/2019

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


def drop_attackers(dfv, dfa):
    """Drops attackers who don't appear in active victims."""
    return dfa.drop(dfa[~dfa.character_id.isin(dfv.character_id)].index)


def drop_by_ship_type_id(df):
    """Drops rows that do not contain specific ship type IDs."""
    ship_type_ids = {583, 584, 585, 587, 589, 591, 593, 594, 597, 598, 602,
                     603, 608, 609, 2161, 2834, 3516, 3532, 3766, 11174, 11176,
                     11178, 11184, 11186, 11190, 11194, 11196, 11198, 11200,
                     11202, 11365, 11371, 11377, 11379, 11381, 11387, 11393,
                     11400, 12032, 12034, 12038, 12042, 12044, 17619, 17703,
                     17812, 17841, 17924, 17926, 17928, 17930, 17932, 32207,
                     32788, 33468, 33673, 33677, 33816, 34443, 35779, 37453,
                     37454, 37455, 37456, 47269}
    return df.drop(df[~df['ship_type_id'].isin(ship_type_ids)].index)


def join_observations(dfv, dfa):
    """Join attackers and victims, dropping extra columns and adding column
    that displays type of observation, kill or death. 
    """
    # Make times into datetime
    dfv['killmail_time'] = pd.to_datetime(dfv['killmail_time'])
    dfa['killmail_time'] = pd.to_datetime(dfa['killmail_time'])

    # Add type of observation and remove extraneous columns
    dfv['type'] = ['death' for _ in range(len(dfv))]
    dfv = dfv.drop(columns=['solar_system_id', 'items'])
    dfa['type'] = ['kill' for _ in range(len(dfa))]
    dfa = dfa.drop(columns=['final_blow', 'damage_done'])

    # Combine the values into a single dataframe
    df = dfv.append(dfa, ignore_index=True, sort=False)

    # Clean up the resulting dataframe
    cols = ['character_id', 'killmail_time', 'killmail_id', 'ship_type_id', 
            'type']
    sort_cols = ['character_id', 'killmail_time', 'killmail_id']
    df = df[cols]  # reorder the columns
    df = (df.sort_values(by=sort_cols)  # sort values
            .reset_index()
            .drop(columns=['index'])
            .dropna())  # drop nans

    return df


def comp_kd_by_type(df):
    """Calculate k/d by incrementing kill and death column values while 
    chronologically parsing rows grouped by character id.

    Drops all observations from attackers starting with kills, as there
    is no victim data for the player until the first death. However,
    kills are still recorded until first death (at which point a ratio can be
    found).
    """
    grouped = df.groupby('character_id')  # group dataframe by character_id
    num_groups = len(grouped)  # get number of groups
    count = 0  # current group number out of number of groups
    groups = []  # list to append modified group dataframes to
    for cid, gp in grouped:
        # list of incrementally counted kills and deaths
        kills, deaths = [], []
        k_count, d_count = 0, 0
        # fill the lists with tallies of kills/deaths seen
        for row in gp.itertuples(index=False):
            if row.type == 'death':  # access attr of namedtuples with .
                d_count += 1
            elif row.type == 'kill':
                k_count += 1
            kills.append(k_count)
            deaths.append(d_count)
        # tack the lists onto the group as columns
        gp['kills'] = kills
        gp['deaths'] = deaths
        # put the group in a list of groups for concatting later
        groups.append(gp)
        # Record progress
        count += 1
        print(f"Progress {count/num_groups:2.1%}", end="\r")
    return groups


# Load CSVs from local file
lap("Loading CSV data from local files...")
df_vic = pd.read_csv(f'data/all_victims_items.csv', encoding='utf-8')
df_att = pd.read_csv(f'data/all_attackers.csv', encoding='utf-8')

# Prepare observations for k/d series generation
lap("Filtering and merging observations...")
# remove non-frigate kills and deaths
df_vic = drop_by_ship_type_id(df_vic)
df_att = drop_by_ship_type_id(df_att)
# only keep attackers that have victim observations as well
df_att = drop_attackers(df_vic, df_att)
# Combine observations into single dataframe
df_all = join_observations(df_vic, df_att)

# Creating K/D series
lap("Computing K/D series...")
groups = comp_kd_by_type(df_all)
# concat all of the groups together
df = pd.concat(groups)
# Create kd_ratio column, reset indices, drop type column
df['kd_ratio'] = df['kills'] / df['deaths']
df = df.reset_index().drop(columns=['index', 'type'])

# Write results to CSV
lap("Writing results to CSV...")
df.to_csv(f'data/all_victims_kd.csv', index=False)

lap("Exit")

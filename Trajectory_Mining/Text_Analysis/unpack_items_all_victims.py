# -*- coding: utf-8 -*-
"""Unpacks Raw API data from zkillboard into victim files that contain 

TEST - 10/02/2019
Params: 10000002201505.csv | 61MB | 28208 rows x 8 columns
Output:
```
(+0.000s|t:0.000s) Importing modules...
(+2.209s|t:2.209s) Loading CSV data from local file...
(+1.132s|t:3.341s) Converting DataFrame column value types...
(+18.746s|t:22.087s) Loading YAML files into memory...
(+3.88m|t:4.25m) Unpacking DataFrame values...
(+2.30m|t:6.55m) Writing results to CSV...
(+8.008s|t:6.68m) Exit
```

Written By: Adam Coscia
Updated On: 11/09/2019

"""
# Start timing
import yaml
import pandas as pd
import numpy as np
import sys
import os
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


def load_yaml(file_loc, encoding='utf-8'):
    """Loads yaml file at file_loc and returns Python object based on yaml
    structure.

    """
    data = None
    with open(file_loc, 'r', encoding=encoding) as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return data


def unpack(data: pd.DataFrame):
    """Operations to unpack nested data, yield row for row in old data.

    Iterate over each row of data using generator and unpack each row.
    """
    def parse_items(items):
        # Use sets for faster look-up time (no order needed to preserve)
        # lo_flags = {11, 12, 13, 14, 15, 16, 17, 18}
        # mi_flags = {19, 20, 21, 22, 23, 24, 25, 26}
        # hi_flags = {27, 28, 29, 30, 31, 32, 33, 34}
        itemList = []
        for item in items:
            itemName, groupName = 'Missing', 'Missing'
            try:
                item_type_id = item['item_type_id']
                try:
                    item_group_id = typeIDs[item_type_id]['groupID']
                    try:
                        itemName = typeIDs[item_type_id]['name']['en']
                        try:
                            groupName = groupIDs[item_group_id]['name']['en']
                        except:
                            pass
                    except:
                        pass
                except:
                    pass
            except:
                pass
            finally:
                itemList.append((itemName, groupName))
        return itemList

    def parse_attackers(attackers):
        attacker_keys = ('final_blow', 'damage_done', 'ship_type_id')
        for attacker in attackers:
            if 'character_id' in attacker:
                a = (attacker['character_id'], [])
                for a_key in attacker_keys:
                    if a_key in attacker:
                        a[1].append(attacker[a_key])
                    else:
                        a[1].append(np.nan)
                yield a

    for row in data.itertuples():
        # Some killmails are npcs, don't include their items and values
        if 'character_id' in row.victim:
            # These values are guaranteed in every killmail
            victim_row = [row.killmail_time,
                          row.solar_system_id,
                          row.victim['character_id']]
            # Try to add ship_type_id to victim values if exists
            if 'ship_type_id' in row.victim:
                victim_row.append(row.victim['ship_type_id'])
            else:
                victim_row.append(np.nan)
            # Try to add item info to victim values if exists
            if 'items' in row.victim and row.victim['items']:
                victim_row.append(parse_items(row.victim['items']))
            else:
                victim_row.append([])  # keep empty array
        else:
            victim_row = None
        if 'npc' in row.zkb:
            npc = row.zkb['npc']
        else:
            npc = False  # Assume there are attackers
        attacker_rows = []
        if not npc:
            attacker_rows.extend(
                [attacker for attacker in parse_attackers(row.attackers)]
            )
        yield victim_row, attacker_rows, row.killmail_id


# Specify S3 parameters and SQL query
bucket = 'dilabevetrajectorymining'
key = 'eve-trajectory-mining/Killmail_Fetching/killmail_scrapes/byregion/10000002/10000002201505.csv'
query = """
SELECT * 
  FROM s3Object s
 LIMIT 5
"""
# Let amazon do the api calls
# print('Querying s3 bucket...')
# df = select(bucket, key, query)

#
# Open YAML file of typeIDs to get names of items
# typeIDs.yaml -> dictionary of typeID keys which contain attributes
# ex. typeIDs[11317] -> {'description': {'en': 'blah', ...}, ...}
#     typeIDs[11317]['name']['en'] == '800mm Rolled Tungsten Compact Plates'
#     typeIDs[11317]['groupID'] == 329
#     groupIDs[329] -> {'name': {'en': 'blah', ...}, ...}
#     groupIDs[329]['name']['en'] == 'Armor Reinforcer'
#
lap("Loading YAML files into memory...")
root = "../Trajectory_Mining/docs/eve files"  # YAML file location
typeIDs = load_yaml(os.path.join(root, 'typeIDs.yaml'))
groupIDs = load_yaml(os.path.join(root, 'groupIDs.yaml'))
# invFlags = load_yaml(os.path.join(root, 'invFlags.yaml'))
# invMarketGroups = load_yaml(os.path.join(root, 'invMarketGroups.yaml'))
# categoryIDs = load_yaml(os.path.join(root, 'categoryIDs.yaml'))

# Sequentially load CSV's from file
lap("Loading CSV data from killmail_scrapes...")
victims = []  # list of victim dataframes generated from CSV's
attackers = []  # list of victim dataframes generated from CSV's
for root, dirs, files in os.walk("../Killmail_Fetching/killmail_scrapes/byregion", topdown=False):
    count = 0
    num_files = len(files)  # number of CSV files
    for file in sorted(files):
        print(f"Progress {count/num_files:2.1%} ", end="\r")
        df = pd.read_csv(os.path.join(root, file), encoding='utf-8')

        # Convert all timestamp strings to numpy.datetime64
        # print("> Converting DataFrame column value types ", end="")
        df['killmail_time'] = pd.to_datetime(df['killmail_time'],
                                             # Turn errors into NaT
                                             errors='coerce',
                                             # Use this format to parse str
                                             format='%Y-%m-%dT%H:%M:%SZ')

        # Convert all numeric values in 'solar_system_id' to smallest int type
        # Convert all non-numeric values in 'solar_system_id' to NaN
        df['solar_system_id'] = pd.to_numeric(df['solar_system_id'],
                                              # Turn errors into NaN
                                              errors='coerce',
                                              # Convert to smallest int type
                                              downcast='integer')

        # Convert values in columns to python objects
        df['victim'] = df['victim'].apply(literal_eval)
        df['attackers'] = df['attackers'].apply(literal_eval)
        df['zkb'] = df['zkb'].apply(literal_eval)

        # Unpack DataFrame subset containing lists and dicts
        # print("> Unpacking DataFrame values ", end="")
        victim_rows = []
        attacker_rows = []
        a_col = ['final_blow', 'damage_done', 'ship_type_id']
        v_col = ['killmail_time', 'solar_system_id', 'character_id',
                 'ship_type_id', 'items']
        for v_row, a_rows, k_id in unpack(df):
            if v_row is not None:  # If no character ID, don't append victim
                victim_rows.append(pd.DataFrame(
                    [v_row],
                    columns=v_col,
                    index=pd.Index([k_id], name='killmail_id')
                ))
            if a_rows:
                attacker_rows.extend([pd.DataFrame(
                    [a_row],
                    columns=a_col,
                    index=pd.MultiIndex.from_tuples(
                        [(k_id, a_id)],
                        names=('killmail_id',
                               'character_id')
                    )
                ) for a_id, a_row in a_rows])

        # Concat victim_rows together
        # print("> Concating victim rows ", end="\r")
        victims.append(pd.concat(victim_rows, sort=False))
        # attackers.append(pd.concat(attacker_rows, sort=False))
        count += 1

# Save victim and attacker info to CSV
lap("Writing results to CSV...")
df_victims = pd.concat(victims)
df_victims.to_csv('data/all_victims_items.csv')
# df_attackers = pd.concat(attackers)
# df_attackers.to_csv('data/all_attackers.csv')

lap("Exit")

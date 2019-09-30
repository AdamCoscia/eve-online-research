# -*- coding: utf-8 -*-
"""TODO

Utilizes the pandas library - https://pandas.pydata.org/pandas-docs/stable/api.html

Utilizes the boto3 library - 


Written By: Adam Coscia
Updated On: 09/30/2019

"""
from ast import literal_eval
import os
import sys

import pandas as pd

from s3Select import select


def unpack(data: pd.DataFrame):
    """Operations to unpack nested data, yield row for row in old data.

    Iterate over each row of data using generator and unpack each row.
    """
    def parse_items(items):
        # Use sets for faster look-up time (no order needed to preserve)
        lo_flags = {11, 12, 13, 14, 15, 16, 17, 18}
        mi_flags = {19, 20, 21, 22, 23, 24, 25, 26}
        hi_flags = {27, 28, 29, 30, 31, 32, 33, 34}
        # Initialize slot values to zero
        lo_slot, mi_slot, hi_slot = 0, 0, 0
        for item in items:
            try:
                if item['flag'] in lo_flags:
                    lo_slot += item['total_price']
                elif item['flag'] in mi_flags:
                    mi_slot += item['total_price']
                elif item['flag'] in hi_flags:
                    hi_slot += item['total_price']
            except (KeyError, TypeError, ValueError):
                pass
        yield lo_slot
        yield mi_slot
        yield hi_slot

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
                victim_row.extend(
                    [slot for slot in parse_items(row.victim['items'])]
                )
            else:
                victim_row.extend([0 for _ in range(3)])  # Fill with 0
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


# Specify parameters here
bucket='dilabevetrajectorymining'
key='eve-trajectory-mining/Killmail_Fetching/killmail_scrapes/byregion/10000002/10000002201505.csv'

# Write SQL query here
query="""
SELECT * 
  FROM s3Object s
 LIMIT 5;
"""

# Let amazon do the api calls
df = select(bucket, key, query)

# Convert all timestamp strings to numpy.datetime64
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
victim_rows = []
attacker_rows = []
a_col = ['final_blow', 'damage_done', 'ship_type_id']
v_col = ['killmail_time', 'solar_system_id', 'character_id', 'ship_type_id',
         'HighSlotISK', 'MidSlotISK', 'LowSlotISK']

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

# Save info to file
name = '10000002201505'

# Save victim info to CSV
df_victims = pd.concat(victim_rows, sort=False)
# v_out = os.path.join(*(out_folder, 'Victims', f'{name}_victims.csv'))
df_victims.to_csv(f'{name}_victims.csv')

# Save attacker info to CSV
df_attackers = pd.concat(attacker_rows, sort=False)
# a_out = os.path.join(*(out_folder, 'Attackers', f'{name}_attackers.csv'))
df_attackers.to_csv(f'{name}_attackers.csv', float_format='%g')

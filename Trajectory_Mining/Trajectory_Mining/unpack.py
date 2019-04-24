# -*- coding: utf-8 -*-
"""Killmail Raw Source Data Cleaning and Re-Formatting Script

Creates new CSV files from Raw CSV Data with only specific columns and cleans
unnecessary data from Web APIs scrapes.

Utilizes the pandas library -
See https://pandas.pydata.org/pandas-docs/stable/api.html

Handy Pandas commands guide -
See https://ikhlestov.github.io/pages/python-related/pandas-commands/

For quick tests in a Python Console, copy and paste...
>> import pandas as pd
>> import numpy as np
>> from ast import literal_eval
>> df = pd.read_csv(path_to_testfile)

Created by: Adam Coscia

Created on: 07/19/2018

Last Updated: 07/25/2018

"""
import logging
import os
import sys
from ast import literal_eval

import numpy as np
import pandas as pd


def file_gen(top_dir, out_root):
    """Creates list of file name, path to file, output

    os.walk -> top-down generator of root, directories, files in tree at top_dir

    """
    for in_root, _, files in os.walk(top_dir):
        for file_name in files:
            path_to_file = os.path.join(in_root, file_name)
            print(f'{path_to_file} set to be converted')
            yield (file_name.split('.')[0], path_to_file,
                   os.path.join(out_root, file_name.split('.')[0][:8]))


def check_type_cast(dataframe):
    """Check type casting of all important objects in original data"""
    print(list(dataframe.values)[0])
    print()
    print(list(dataframe['killmail_id'].values)[0])
    print(type(list(dataframe['killmail_id'].values)[0]))
    print()
    print(list(dataframe['killmail_time'].values)[0])
    print(type(list(dataframe['killmail_time'].values)[0]))
    print()
    print(list(dataframe['victim'].values)[0])
    print(type(list(dataframe['victim'].values)[0]))
    print()
    print(list(dataframe['victim'].values)[0]['items'])
    print(type(list(dataframe['victim'].values)[0]['items']))
    print()
    print(list(dataframe['victim'].values)[0]['items'][0])
    print(type(list(dataframe['victim'].values)[0]['items'][0]))
    print()
    print(list(dataframe['victim'].values)[0]['items'][0]['total_price'])
    print(type(list(dataframe['victim'].values)[0]['items'][0]['total_price']))
    print()
    print(list(dataframe['attackers'].values)[0])
    print(type(list(dataframe['attackers'].values)[0]))
    print()
    print(list(dataframe['attackers'].values)[0][0])
    print(type(list(dataframe['attackers'].values)[0][0]))
    print()
    print(list(dataframe['attackers'].values)[0][0]['final_blow'])
    print(type(list(dataframe['attackers'].values)[0][0]['final_blow']))
    print()
    print(list(dataframe['solar_system_id'].values)[0])
    print(type(list(dataframe['solar_system_id'].values)[0]))
    print()
    print(list(dataframe['zkb'].values)[0])
    print(type(list(dataframe['zkb'].values)[0]))
    print()
    print(list(dataframe['zkb'].values)[0]['npc'])
    print(type(list(dataframe['zkb'].values)[0]['npc']))


def unpack(data: pd.DataFrame):
    """Operations to unpack nested data, yield row for row in old data.

    Iterate over each row of ``data`` using generator and unpack each row.

    """
    def parse_items(items):
        lo_slot = mi_slot = hi_slot = 0
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
        for attacker in attackers:
            if 'character_id' in attacker:
                a = (attacker['character_id'], [])

                for a_key in attacker_keys:
                    if a_key in attacker:
                        a[1].append(attacker[a_key])
                    else:
                        a[1].append(np.nan)

                yield a

    attacker_keys = ('final_blow', 'damage_done', 'ship_type_id')
    # Use sets for faster look-up time (no order needed to preserve)
    lo_flags = {11, 12, 13, 14, 15, 16, 17, 18}
    mi_flags = {19, 20, 21, 22, 23, 24, 25, 26}
    hi_flags = {27, 28, 29, 30, 31, 32, 33, 34}

    for row in data.itertuples():
        if 'character_id' in row.victim:
            victim_row = [row.killmail_time,
                          row.solar_system_id,
                          row.victim['character_id']]

            if 'ship_type_id' in row.victim:
                victim_row.append(row.victim['ship_type_id'])
            else:
                victim_row.append(np.nan)

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

        yield victim_row, attacker_rows, row.Index


# ============================================================================ #
directory = '..\..\Killmail_Fetching\scrapes\AR'
output_root = '..\data\AR'
files = [file_set for file_set in file_gen(directory, output_root)]

start = input('Start Conversion? (y/n) >')
if start != 'y':
    sys.exit(0)  # Early exit

# Set logger
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                    datefmt='%Y/%m/%d %H:%M:%S',
                    level='DEBUG')

# Output file columns
a_col = ['final_blow', 'damage_done', 'ship_type_id']
v_col = ['killmail_time', 'solar_system_id', 'character_id', 'ship_type_id',
         'HighSlotISK', 'MidSlotISK', 'LowSlotISK']

# Clean and reformat every CSV at the file location
for name, in_path, out_folder in files:
    logging.info(f"Reading -> {in_path}")
    df = pd.read_csv(in_path,  # Path to CSV File
                     header=0,  # Use this row number as header
                     index_col=0,  # Use killmail_id as index
                     usecols=lambda x: x not in ('moon_id', 'war_id'),
                     # Apply str to 'killmail_time' for post-process
                     dtype={'killmail_time': str},
                     # Apply literal_eval to these columns
                     converters={
                         'victim': literal_eval,
                         'attackers': literal_eval,
                         'zkb': literal_eval
                     },
                     # Skip lines with extra columns, don't throw error!
                     error_bad_lines=False)

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

    # Check type casting by passing check=True
    # check_type_cast(df)

    # Unpack DataFrame subset containing lists and dicts
    logging.info(f"Unpacking -> {name}.csv")
    victim_rows = []
    attacker_rows = []
    for v_row, a_rows, k_id in unpack(df):
        if v_row is not None:  # If no character ID, don't append victim
            victim_rows.append(
                pd.DataFrame([v_row],
                             columns=v_col,
                             index=pd.Index([k_id], name='killmail_id'))
            )
        if a_rows:
            attacker_rows.extend(
                [pd.DataFrame([a_row],
                              columns=a_col,
                              index=pd.MultiIndex.from_tuples(
                                  [(k_id, a_id)],
                                  names=('killmail_id', 'character_id')
                              )) for a_id, a_row in a_rows]
            )

    logging.debug(f"Concatenating Victims in {name}.csv")
    df_victims = pd.concat(victim_rows, sort=False)

    logging.debug(f"Concatenating Attackers in {name}.csv")
    df_attackers = pd.concat(attacker_rows, sort=False)

    v_out = os.path.join(*(out_folder, 'Victims', f'{name}_victims.csv'))
    logging.info(f"Writing Victims to {name}_victims.csv")
    df_victims.to_csv(v_out)

    a_out = os.path.join(*(out_folder, 'Attackers', f'{name}_attackers.csv'))
    logging.info(f"Writing Attackers to {name}_attackers.csv")
    df_attackers.to_csv(a_out, float_format='%g')

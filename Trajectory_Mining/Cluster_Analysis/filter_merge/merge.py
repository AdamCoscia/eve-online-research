# -*- coding: utf-8 -*-
"""CSV File System Merging Script.

Merges CSV Files and applies FNC to the project.

Utilizes the pandas library -
See https://pandas.pydata.org/pandas-docs/stable/api.html

For quick tests in a Python Console, copy and paste...
>> import pandas as pd
>> import numpy as np
>> from ast import literal_eval
>> df = pd.read_csv(path_to_testfile)

Created by: Adam Coscia

Created on: 07/25/2018

Last Updated: 08/02/2018

"""
import os

import pandas as pd

victim_files = []
attacker_files = []
for root, _, files in os.walk('..\data\AR'):
    for name in files:
        if 'attackers' in name:
            attacker_files.append(os.path.join(root, name))
        elif 'victims' in name:
            victim_files.append(os.path.join(root, name))

victim_files = list(reversed(victim_files))  # Most recent first
attacker_files = list(reversed(attacker_files))  # Most recent first

victims: pd.DataFrame = pd.concat(
    [pd.read_csv(victim_file,
                 header=0,
                 index_col=0) for victim_file in victim_files]
)

attackers: pd.DataFrame = pd.concat(
    [pd.read_csv(attacker_file,
                 header=0,
                 index_col=[0, 1]) for attacker_file in attacker_files]
)

victims.to_csv('../data/AR/victims.csv')
attackers.to_csv('../data/AR/attackers.csv')

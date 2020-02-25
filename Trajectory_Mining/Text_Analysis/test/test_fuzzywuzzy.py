# -*- coding: utf-8 -*-
"""testing script"""
import os
import sys

import numpy as np
import pandas as pd
import nltk  # Natural Language Tool Kit
from fuzzywuzzy import fuzz, process  # Fuzzy String Matching
import jellyfish  # Distance metrics

#
# FuzzyWuzzy Package
#
# Simple Ratio
# >>> fuzz.ratio("this is a test", "this is a test!")
#     97
# Partial Ratio
# >>> fuzz.partial_ratio("this is a test", "this is a test!")
#     100
# Token Sort Ratio
# >>> fuzz.ratio("fuzzy wuzzy was a bear", "wuzzy fuzzy was a bear")
#     91
# >>> fuzz.token_sort_ratio("fuzzy wuzzy was a bear", "wuzzy fuzzy was a bear")
#     100
# Token Set Ratio
# >>> fuzz.token_sort_ratio("fuzzy was a bear", "fuzzy fuzzy was a bear")
#     84
# >>> fuzz.token_set_ratio("fuzzy was a bear", "fuzzy fuzzy was a bear")
#     100
# Process
# >>> choices = ["Atlanta Falcons", "New York Jets", "New York Giants", "Dallas Cowboys"]
# >>> process.extract("new york jets", choices, limit=2)
#     [('New York Jets', 100), ('New York Giants', 78)]
# >>> process.extractOne("cowboys", choices)
#     ("Dallas Cowboys", 90)
# You can also pass additional parameters to extractOne method to make it use a specific scorer. A typical use case is to match file paths:
# >>> process.extractOne("System of a down - Hypnotize - Heroin", songs)
#     ('/music/library/good/System of a Down/2005 - Hypnotize/01 - Attack.mp3', 86)
# >>> process.extractOne("System of a down - Hypnotize - Heroin", songs, scorer=fuzz.token_sort_ratio)
#     ("/music/library/good/System of a Down/2005 - Hypnotize/10 - She's Like Heroin.mp3", 61)
#
# NLTK (Natural Language Tool Kit)
# nltk.distance.edit_distance
#

l1 = [('800mm Rolled Tungsten Compact Plates', 'Armor Reinforcer'),
      ('Fleeting Compact Stasis Webifier', 'Stasis Web'),
      ('Scourge Heavy Missile', 'Heavy Missile'),
      ('Scourge Heavy Missile', 'Heavy Missile'),
      ("'Arbalest' Heavy Missile Launcher", 'Missile Launcher Heavy'),
      ('Nova Heavy Missile', 'Heavy Missile'),
      ('Mjolnir Heavy Missile', 'Heavy Missile'),
      ('Expanded Cargohold II', 'Expanded Cargohold'),
      ("'Arbalest' Heavy Missile Launcher", 'Missile Launcher Heavy'),
      ('Medium Inefficient Armor Repair Unit', 'Armor Repair Unit'),
      ('Expanded Cargohold II', 'Expanded Cargohold'),
      ("'Arbalest' Heavy Missile Launcher", 'Missile Launcher Heavy'),
      ('10MN Monopropellant Enduring Afterburner', 'Propulsion Module'),
      ('Mjolnir Heavy Missile', 'Heavy Missile'),
      ('Adaptive Invulnerability Field I', 'Shield Hardener'),
      ("'Arbalest' Heavy Missile Launcher", 'Missile Launcher Heavy'),
      ('Scourge Heavy Missile', 'Heavy Missile'),
      ('Medium C5-L Emergency Shield Overload I', 'Shield Booster'),
      ('Nova Heavy Missile', 'Heavy Missile'),
      ('Nova Heavy Missile', 'Heavy Missile'),
      ("Limited 'Anointed' EM Ward Field", 'Shield Hardener'),
      ('Scourge Heavy Missile', 'Heavy Missile'),
      ('Expanded Cargohold II', 'Expanded Cargohold'),
      ("'Arbalest' Heavy Missile Launcher", 'Missile Launcher Heavy')]

l2 = [('Republic Fleet Phased Plasma S', 'Projectile Ammo'),
      ('125mm Gatling AutoCannon I', 'Projectile Weapon'),
      ('Small Core Defense Field Extender I', 'Rig Shield'),
      ('Medium Shield Extender I', 'Shield Extender'),
      ('Small Core Defense Field Extender I', 'Rig Shield'),
      ('1MN Afterburner I', 'Propulsion Module'),
      ('Caldari Navy Nova Rocket', 'Rocket'),
      ('Republic Fleet Phased Plasma S', 'Projectile Ammo'),
      ('Republic Fleet Phased Plasma S', 'Projectile Ammo'),
      ('Caldari Navy Nova Rocket', 'Rocket'),
      ('Damage Control II', 'Damage Control'),
      ('Gyrostabilizer II', 'Gyrostabilizer'),
      ('Small Anti-EM Screen Reinforcer I', 'Rig Shield'),
      ('Republic Fleet Phased Plasma S', 'Projectile Ammo'),
      ('OE-5200 Rocket Launcher', 'Missile Launcher Rocket'),
      ('125mm Gatling AutoCannon I', 'Projectile Weapon'),
      ('125mm Gatling AutoCannon I', 'Projectile Weapon'),
      ('J5b Enduring Warp Scrambler', 'Warp Scrambler'),
      ('Overdrive Injector System II', 'Overdrive Injector System')]

# Long Text Lists
l1_lt = [x[0] for x in l1]
l2_lt = [x[0] for x in l2]
# Short Text Lists
l1_st = [x[1] for x in l1]
l2_st = [x[1] for x in l2]
# Long Text Distance Matrices
l1xl2_ld_ratio = [[0 for x in range(len(l2_lt))] for x in range(len(l1_lt))]
l1xl2_ld_partratio = [[0 for x in range(len(l2_lt))]
                      for x in range(len(l1_lt))]
l1xl2_ld_tokensortratio = [
    [0 for x in range(len(l2_lt))] for x in range(len(l1_lt))]
l1xl2_ld_tokensetratio = [
    [0 for x in range(len(l2_lt))] for x in range(len(l1_lt))]
# Short Text Distance Matrices
l1xl2_sd_ratio = [[0 for x in range(len(l2_st))] for x in range(len(l1_st))]
l1xl2_sd_partratio = [[0 for x in range(len(l2_st))]
                      for x in range(len(l1_st))]
l1xl2_sd_tokensortratio = [
    [0 for x in range(len(l2_st))] for x in range(len(l1_st))]
l1xl2_sd_tokensetratio = [
    [0 for x in range(len(l2_st))] for x in range(len(l1_st))]

# Long Text Comparison
for i in range(len(l1_lt)):
    for j in range(len(l2_lt)):
        # print(f'i:{i} j:{j}')
        word1 = l1_lt[i]
        word2 = l2_lt[j]
        # (word1, word2, fuzz.ratio(word1, word2))
        l1xl2_ld_ratio[i][j] = fuzz.ratio(word1, word2)
        # (word1, word2, fuzz.partial_ratio(word1, word2))
        l1xl2_ld_partratio[i][j] = fuzz.partial_ratio(word1, word2)
        # (word1, word2, fuzz.token_sort_ratio(word1, word2))
        l1xl2_ld_tokensortratio[i][j] = fuzz.token_sort_ratio(word1, word2)
        # (word1, word2, fuzz.token_set_ratio(word1, word2))
        l1xl2_ld_tokensetratio[i][j] = fuzz.token_set_ratio(word1, word2)

# Short Text Comparison
for i in range(len(l1_st)):
    for j in range(len(l2_st)):
        # print(f'i:{i} j:{j}')
        word1 = l1_st[i]
        word2 = l2_st[j]
        # (word1, word2, fuzz.ratio(word1, word2))
        l1xl2_sd_ratio[i][j] = fuzz.ratio(word1, word2)
        # (word1, word2, fuzz.partial_ratio(word1, word2))
        l1xl2_sd_partratio[i][j] = fuzz.partial_ratio(word1, word2)
        # (word1, word2, fuzz.token_sort_ratio(word1, word2))
        l1xl2_sd_tokensortratio[i][j] = fuzz.token_sort_ratio(word1, word2)
        # (word1, word2, fuzz.token_set_ratio(word1, word2))
        l1xl2_sd_tokensetratio[i][j] = fuzz.token_set_ratio(word1, word2)

pd.DataFrame(l1xl2_ld_ratio).to_csv('text/l1xl2_ld_ratio.csv', index=False)
pd.DataFrame(l1xl2_ld_partratio).to_csv(
    'text/l1xl2_ld_partratio.csv', index=False)
pd.DataFrame(l1xl2_ld_tokensortratio).to_csv(
    'text/l1xl2_ld_tokensortratio.csv', index=False)
pd.DataFrame(l1xl2_ld_tokensetratio).to_csv(
    'text/l1xl2_ld_tokensetratio.csv', index=False)
pd.DataFrame(l1xl2_sd_ratio).to_csv('text/l1xl2_sd_ratio.csv', index=False)
pd.DataFrame(l1xl2_sd_partratio).to_csv(
    'text/l1xl2_sd_partratio.csv', index=False)
pd.DataFrame(l1xl2_sd_tokensortratio).to_csv(
    'text/l1xl2_sd_tokensortratio.csv', index=False)
pd.DataFrame(l1xl2_sd_tokensetratio).to_csv(
    'text/l1xl2_sd_tokensetratio.csv', index=False)

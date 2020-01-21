# -*- coding: utf-8 -*-
"""testing script"""
import os
import sys
from functools import reduce

import numpy as np
import pandas as pd
import nltk  # Natural Language Tool Kit
from fuzzywuzzy import fuzz, process  # Fuzzy String Matching
import jellyfish  # Distance metrics
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


def get_cosine_distance(doc1, doc2):
    """

    """
    tfidf = TfidfVectorizer().fit_transform([doc1, doc2])  # Vectorize the bag of words
    cos_dist = linear_kernel(tfidf[0:1], tfidf[1:2]).flatten()[0]  # Compute cosine distance
    return cos_dist


# killmail_id,       killmail_time, solar_system_id, character_id, ship_type_id
#    46643819, 2015-05-15 19:02:00,        30000157,     90000814,          630
l1 = [('Large Shield Extender II', 'Shield Extender'),
      ('Rapid Light Missile Launcher II', 'Missile Launcher Rapid Light'),
      ('Caldari Navy Mjolnir Light Missile', 'Light Missile'),
      ('Damage Control II', 'Damage Control'),
      ('50MN Cold-Gas Enduring Microwarpdrive', 'Propulsion Module'),
      ('Large Shield Extender II', 'Shield Extender'),
      ('Caldari Navy Scourge Light Missile', 'Light Missile'),
      ('Caldari Navy Inferno Light Missile', 'Light Missile'),
      ('Rapid Light Missile Launcher II', 'Missile Launcher Rapid Light'),
      ('Phased Scoped Target Painter', 'Target Painter'),
      ('Caldari Navy Inferno Light Missile', 'Light Missile'),
      ('Medium Polycarbon Engine Housing I', 'Rig Navigation'),
      ('Nanofiber Internal Structure II', 'Nanofiber Internal Structure'),
      ('Ballistic Control System II', 'Ballistic Control system'),
      ('Ballistic Control System II', 'Ballistic Control system'),
      ('Rapid Light Missile Launcher II', 'Missile Launcher Rapid Light'),
      ('Caldari Navy Inferno Light Missile', 'Light Missile'),
      ('Caldari Navy Inferno Light Missile', 'Light Missile'),
      ('Caldari Navy Nova Light Missile', 'Light Missile'),
      ('Medium Core Defense Field Extender I', 'Rig Shield'),
      ('Caldari Navy Inferno Light Missile', 'Light Missile'),
      ('Warp Disruptor II', 'Warp Scrambler'),
      ('Rapid Light Missile Launcher II', 'Missile Launcher Rapid Light'),
      ('Medium Core Defense Field Extender I', 'Rig Shield')]

# killmail_id,       killmail_time, solar_system_id, character_id, ship_type_id
#    46643869, 2015-05-15 19:05:00,        30000157,     90000814,        32872
l2 = [('Caldari Navy Antimatter Charge S', 'Hybrid Charge'),
      ('Caldari Navy Antimatter Charge S', 'Hybrid Charge'),
      ('Drone Damage Amplifier II', 'Drone Damage Modules'),
      ('F85 Peripheral Damage System I', 'Damage Control'),
      ('Null S', 'Advanced Blaster Charge'),
      ('Caldari Navy Antimatter Charge S', 'Hybrid Charge'),
      ('Light Ion Blaster II', 'Hybrid Weapon'),
      ('J5b Enduring Warp Scrambler', 'Warp Scrambler'),
      ('Light Ion Blaster II', 'Hybrid Weapon'),
      ('Caldari Navy Antimatter Charge S', 'Hybrid Charge'),
      ('Drone Damage Amplifier II', 'Drone Damage Modules'),
      ('Small Transverse Bulkhead I', 'Rig Armor'),
      ('5MN Y-T8 Compact Microwarpdrive', 'Propulsion Module'),
      ('Light Ion Blaster II', 'Hybrid Weapon'),
      ('X5 Enduring Stasis Webifier', 'Stasis Web'),
      ('Small Transverse Bulkhead I', 'Rig Armor'),
      ('Warrior II', 'Combat Drone'),
      ('Small Transverse Bulkhead I', 'Rig Armor'),
      ('Light Ion Blaster II', 'Hybrid Weapon'),
      ('Light Ion Blaster II', 'Hybrid Weapon'),
      ('Caldari Navy Antimatter Charge S', 'Hybrid Charge'),
      ('Caldari Navy Antimatter Charge S', 'Hybrid Charge')]

# [TEST] Long Text Vectorizers
# The same document should have cosine distance of 1
doc1_lt = reduce(lambda x, y: f'{x} {y}', [x[0] for x in l1])  # Create bag of words
doc2_lt = reduce(lambda x, y: f'{x} {y}', [x[0] for x in l1])  # Create bag of words
cos_dist_lt = get_cosine_distance(doc1_lt, doc2_lt)
print(f"Document 1: {doc1_lt}")
print(f"Document 2: {doc2_lt}")
print(f"Cosine Distance:\n {cos_dist_lt}")

print("==========")

# Long Text Vectorizers
# Let's see how close the long texts are
doc1_lt = reduce(lambda x, y: f'{x} {y}', [x[0] for x in l1])
doc2_lt = reduce(lambda x, y: f'{x} {y}', [x[0] for x in l2])
cos_dist_lt = get_cosine_distance(doc1_lt, doc2_lt)
print(f"Document 1: {doc1_lt}")
print(f"Document 2: {doc2_lt}")
print(f"Cosine Distance:\n {cos_dist_lt}")

print("==========")

# [TEST] Short Text Vectorizers
# Again same texts should have cosine distance of 1
doc1_st = reduce(lambda x, y: f'{x} {y}', [x[1] for x in l2])
doc2_st = reduce(lambda x, y: f'{x} {y}', [x[1] for x in l2])
cos_dist_st = get_cosine_distance(doc1_st, doc2_st)
print(f"Document 1: {doc1_st}")
print(f"Document 2: {doc2_st}")
print(f"Cosine Distance:\n {cos_dist_st}")

print("==========")

# Short Text Vectorizers
# Let's see how close the short texts are
doc1_st = reduce(lambda x, y: f'{x} {y}', [x[1] for x in l1])
doc2_st = reduce(lambda x, y: f'{x} {y}', [x[1] for x in l2])
cos_dist_st = get_cosine_distance(doc1_st, doc2_st)
print(f"Document 1: {doc1_st}")
print(f"Document 2: {doc2_st}")
print(f"Cosine Distance:\n {cos_dist_st}")

print("==========")

# Short Text Vectorizers
# Cosine distance should be commutable
doc1_st = reduce(lambda x, y: f'{x} {y}', [x[1] for x in l2])
doc2_st = reduce(lambda x, y: f'{x} {y}', [x[1] for x in l1])
cos_dist_st = get_cosine_distance(doc1_st, doc2_st)
print(f"Document 1: {doc1_st}")
print(f"Document 2: {doc2_st}")
print(f"Cosine Distance:\n {cos_dist_st}")

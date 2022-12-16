#!~/usr/bin/py
# -*- coding: utf-8 -*-
"""TODO

Utilizes the pandas library - https://pandas.pydata.org/pandas-docs/stable/api.html

Utilizes the boto3 library - 


Written By: Adam Coscia
Created On: 08/06/2018
Updated On: 04/28/2019

"""

import boto3
import io
import pandas as pd
s3 = boto3.client('s3')

# Specify parameters here
bucket='dilabevetrajectorymining'
key='eve-trajectory-mining/Trajectory_Mining/data/Series/players_frig_actv_ts-evt.csv'
inputFormat='CSV'
outputFormat='CSV'
printStats=False

# Define parameters based on format
if outputFormat == 'CSV':
    inputParams = {"FileHeaderInfo": "None"}
elif outputFormat == 'JSON':
    inputParams = {"FileHeaderInfo": "Use"}
outputParams = {}

# Write SQL query here
query="""
SELECT * 
  FROM s3Object s
 LIMIT 5
"""

# Let amazon do the api calls
r = s3.select_object_content(
        Bucket=bucket,
        Key=key,
        ExpressionType='SQL',
        Expression=query,
        InputSerialization = {inputFormat: inputParams},
        OutputSerialization = {outputFormat: outputParams},
)

for event in r['Payload']:
    if 'Records' in event:
        records = event['Records']['Payload'].decode('utf-8')
        if outputFormat == 'CSV':
            df = pd.read_csv(io.StringIO(records))
        elif outputFormat == 'JSON':
            df = pd.read_json(io.StringIO(records), lines=True)
    elif 'Stats' in event and printStats:
        statsDetails = event['Stats']['Details']
        print("Stats details bytesScanned: ")
        print(statsDetails['BytesScanned'])
        print("Stats details bytesProcessed: ")
        print(statsDetails['BytesProcessed'])

# Now use the dataframe you got from your SQL query
pd.options.display.max_columns = len(df.columns)
print(df)

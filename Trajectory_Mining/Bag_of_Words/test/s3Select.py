# -*- coding: utf-8 -*-
"""Module providing pre-built s3 bucket api select request function.

Written By: Adam Coscia (acoscia125@gmail.com)
Updated On: 09/30/2019

"""
import io

import boto3
import pandas as pd


s3 = boto3.client('s3')


def select(bucket, key, query, inputFormat='CSV', outputFormat='CSV', 
           printStats=False):
    """Performs SQL-style select on CSV or JSON objects in S3 bucket.

    Globals
        s3: S3 client object used to make API requests
    Arguments
        bucket: S3 Bucket name
        key: Key of file in S3 bucket
        query: SQL query for selecting from file
        inputFormat: CSV or JSON
        outputFormat: CSV or JSON
        printStats: Prints stats on amount of data queried (useful for usage-tracking)
    Returns
        pandas DataFrame object representing the data from the query
    """
    # Define parameters based on I/O format
    df = None
    if outputFormat == 'CSV':
        inputParams = {"FileHeaderInfo": "None"}
    elif outputFormat == 'JSON':
        inputParams = {"FileHeaderInfo": "Use"}
    outputParams = {}

    # Request object from s3 bucket
    r = s3.select_object_content(
            Bucket=bucket,
            Key=key,
            ExpressionType='SQL',
            Expression=query,
            InputSerialization = {inputFormat: inputParams},
            OutputSerialization = {outputFormat: outputParams},
    )

    # Parse object contents
    for event in r['Payload']:
        if 'Records' in event:
            records = event['Records']['Payload'].decode('utf-8')
            if outputFormat == 'CSV':
                df = pd.read_csv(io.StringIO(records), engine='python',
                                 encoding='utf-8')
            elif outputFormat == 'JSON':
                df = pd.read_json(io.StringIO(records), engine='python', 
                                  lines=True)
        elif 'Stats' in event and printStats:
            statsDetails = event['Stats']['Details']
            print("Stats details bytesScanned: ")
            print(statsDetails['BytesScanned'])
            print("Stats details bytesProcessed: ")
            print(statsDetails['BytesProcessed'])
    return df


if __name__ == "__main__":
    # Specify parameters here
    bucket='dilabevetrajectorymining'
    key='eve-trajectory-mining/Killmail_Fetching/killmail_scrapes/byregion/10000002/10000002201505.csv'

    # Write SQL query here
    query="""
    SELECT * 
      FROM s3Object s
     LIMIT 5
    """

    # Let amazon do the api calls
    df = select(bucket, key, query)

    # Now use the dataframe you got from your SQL query
    print(df)

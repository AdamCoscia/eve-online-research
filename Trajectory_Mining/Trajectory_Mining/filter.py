# -*- coding: utf-8 -*-
"""Killmail Data Filtering Script.

Applies optimized filtration techniques for reducing data to core information.

Utilizes the pandas library -
See https://pandas.pydata.org/pandas-docs/stable/api.html


For quick tests in a Python Console, copy and paste...
>> import pandas as pd
>> import numpy as np
>> from ast import literal_eval
>> df = pd.read_csv(path_to_testfile)

Created by: Adam Coscia

Created on: 07/25/2018

Last Updated: 02/27/2019

"""
import numpy as np
import pandas as pd


def drop_by_activity(df: pd.DataFrame):
    """Drops non-active players from the dataframe. Active players are those
    players who have at least one killmail per month that resulted from their
    use of a combat-based Frigate-class ship type, for a minimum of 12 months
    or more.

    Examples
    --------
    Examples of players (character_id's) to keep and filter out:

    - FILTER: Player #87654321 has 20 killmails in each month from 01-2016
      to 11-2016 (11 months). Even though in total the player has 11*20 = 220
      killmails, those killmails do not span a 12+ month period.

    - KEEP: Player #14235867 has one killmail every other month from 01-2016
      to 12-2017 (24 months). Player has minimum 12 months worth of killmails,
      even though months are not consecutive.

    :param df:
    :return:
    """

    def keep_group(g: pd.DataFrame):
        """Filter function for determining if group should be kept. Group will
        be kept if there are 12+ unique monthly periods represented in the
        data.

        Example
        -------
        >> group = df.groupby('character_id').get_group(93952596)

        killmail_id        killmail_time  solar_system_id  character_id  ...

        63889534     2017-08-05 17:13:03         30000163      93952596  ...

        63642627     2017-07-23 05:38:18         30000163      93952596  ...

        63618325     2017-07-22 01:35:55         30000163      93952596  ...

        63617975     2017-07-22 01:00:03         30000163      93952596  ...

        62462163     2017-05-22 23:33:57         30000163      93952596  ...

        62287855     2017-05-15 02:46:06         30000163      93952596  ...

        >> pd.to_datetime(group.killmail_time).dt.to_period('M')

        killmail_id  killmail_time

        63889534     2017-08

        63642627     2017-07

        63618325     2017-07

        63617975     2017-07

        62462163     2017-05

        62287855     2017-05

        """
        return pd.to_datetime(g.killmail_time).dt.to_period('M').nunique() > 11

    return df.groupby('character_id').filter(
        lambda x: keep_group(x) if len(x) > 11 else False
    )


def drop_by_ship_type_id(df: pd.DataFrame):
    """Drops rows that do not contain specific ship type IDs.

    :param df:
    :return:
    """
    ship_type_ids = {583, 584, 585, 587, 589, 591, 593, 594, 597, 598, 602,
                     603, 608, 609, 2161, 2834, 3516, 3532, 3766, 11174, 11176,
                     11178, 11184, 11186, 11190, 11194, 11196, 11198, 11200,
                     11202, 11365, 11371, 11377, 11379, 11381, 11387, 11393,
                     11400, 12032, 12034, 12038, 12042, 12044, 17619, 17703,
                     17812, 17841, 17924, 17926, 17928, 17930, 17932, 32207,
                     32788, 33468, 33673, 33677, 33816, 34443, 35779, 37453,
                     37454, 37455, 37456, 47269}

    return df.drop(df[~df.ship_type_id.isin(ship_type_ids)].index)


def drop_attackers_by_character_id(dfv: pd.DataFrame, dfa: pd.DataFrame):
    """Drops attackers who don't appear in active victims.

    :param dfv:
    :param dfa:
    :return:
    """
    return dfa.drop(dfa[~dfa.character_id.isin(dfv.character_id)].index)


def join_investment_performance_series(dfi: pd.DataFrame, dfp: pd.DataFrame):
    """Join Investment and Performance Series, forward filling investment
    for later PCC analysis and clustering.

    Drops all observations in performance series starting with kills, as there
    is no investment data for the player until the first death. However,
    kills are still recorded until first death (at which point a ratio can be
    found).

    :param dfi:
    :param dfp:
    :return:
    """
    def keep_group(gp: pd.DataFrame):
        """See drop_by_activity() above for details."""
        return pd.to_datetime(gp['datetime']).dt.to_period('M').nunique() > 11

    # Create Datetime Indices
    dfp['datetime'] = pd.to_datetime(dfp['datetime'])
    dfi['datetime'] = pd.to_datetime(dfi['datetime'])

    # Add 'read' to all investment observations and drop overlapping columns
    dfi = dfi.assign(fill=pd.Series(['read' for _ in range(len(dfi))]))

    # Set the investment index and drop duplicate columns
    dfi = dfi.set_index(
        ['character_id', 'datetime']
    ).sort_index().drop(columns=['killmail_id', 'ship_type_id'])

    # Join the investments (right) and performance (left) series
    result = dfp.set_index(
        ['character_id', 'datetime']
    ).sort_index().join(dfi, sort=True).reset_index()

    # Backfill the NaN investment values
    cols = ['hi_slot', 'mid_slot', 'lo_slot', 'od_ratio', 'od_prct']
    result['fill'] = result['fill'].fillna(value='bfill')
    result[cols] = result.groupby(
        'character_id', sort=False
    )[cols].apply(lambda group: group.bfill())

    # Drop rows with inf or 0 in the k/d ratio and series ending in NaN
    result = result.drop(
        result[(result.kd_ratio == np.inf) | (result.kd_ratio == 0.0)].index
    )
    result = result.dropna(subset=cols)

    # After filtering, drop players with less than 12 unique observations
    result = result.groupby('character_id').filter(
        lambda group: keep_group(group) if len(group) > 11 else False
    )

    return result.set_index(['character_id', 'datetime']).sort_index()


def make_time_series_event_based(dfts: pd.DataFrame):
    """Make time series event based indexing, removing datetime column.

    :param dfts:
    :return:
    """
    return dfts.groupby('character_id').apply(lambda x: x.reset_index()).drop(
        ['index','datetime','character_id'],axis=1).reset_index().set_index(
        'character_id').rename(columns={'level_1': 'record'})


def make_time_series_period_based(dfts: pd.DataFrame):
    """Re-sample time series per day, dropping bad columns and filling in
    missing days.

    :param dfts:
    :return:
    """
    # Drop columns that won't work with the new model
    dfts = dfts.drop(
        ['killmail_id', 'ship_type_id', 'type', 'kd_diff', 'kd_ratio',
         'kd_prct', 'od_ratio', 'od_prct', 'fill'],
        axis=1
    )

    # Group frame by character_id to begin the resample process
    gp = dfts.groupby('character_id')
    # Drop the kills/deaths and resample each group by day, values become avg
    invt = gp.apply(lambda x: x.set_index(pd.to_datetime(x['datetime'])).drop(
        ['datetime', 'character_id', 'k_count', 'd_count'],
        axis=1).resample('D').mean())
    # Drop the slots and resample each group by day, values become max
    kd = gp.apply(lambda x: x.set_index(pd.to_datetime(x['datetime'])).drop(
        ['datetime', 'character_id', 'hi_slot', 'mid_slot', 'lo_slot'],
        axis=1).resample('D').max())

    # Join resampled dataframes
    dfpd = kd.join(invt).reset_index()
    # Create a 'fill'-type column to distinguish observations from backfills
    dfpd['fill'] = dfpd.isnull().any(axis=1).replace(
        {True: 'bfill', False: 'read'})
    # Finally backfill the NaNs!
    dfpd = dfpd.fillna(method='bfill')

    # Generate investment and performance metrics and reorder columns
    hi, mid, lo = dfpd.hi_slot, dfpd.mid_slot, dfpd.lo_slot
    k, d = dfpd.k_count, dfpd.d_count
    cols = ['character_id', 'datetime', 'k_count', 'd_count', 'kd_diff',
            'kd_ratio', 'kd_prct', 'hi_slot', 'mid_slot', 'lo_slot',
            'od_ratio', 'od_prct', 'fill']
    dfpd = dfpd.assign(
        kd_diff=(k - d),
        kd_ratio=(k / d),
        kd_prct=(2 * ((k / (k + d)) * 100 - 50)),
        od_ratio=(hi / (mid + lo)),
        od_prct=(2 * ((hi / (hi + mid + lo)) * 100 - 50))
    )[cols].set_index('character_id')

    return dfpd


# ============================================================================ #
# Use the Command Line or a Terminal to do basic pre-filtering!
dfts = pd.read_csv('../data/Series/players_frig_actv_ts.csv', header=0)

# dfe = make_time_series_event_based(dfts)
dfpd = make_time_series_period_based(dfts)

# dfev.to_csv('../data/Series/players_frig_actv_ts-evt.csv')
dfpd.to_csv('../data/Series/players_frig_actv_ts-prd.csv')

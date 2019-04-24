# -*- coding: utf-8 -*-
"""Script for creating investment and performance series from raw data.

Utilizes the pandas library -
See https://pandas.pydata.org/pandas-docs/stable/api.html

Created by: Adam Coscia

Created on: 08/06/2018

Last Updated: 02/27/2019

"""
import pandas as pd


def generate_investment_series(dfv: pd.DataFrame):
    """Generate and append percent of offensive spending for each row of the
    dataframe i.e. large positive values indicate high percent of offensive
    investment.

    Example
    -------
    >> Hi=1  (value in ISK)

    >> Mid=2

    >> Lo=2

    >> RatioOffenseDefense = Hi / (Mid + Lo) = 0.25

    >> PercentOffensiveSpending = ((Hi / Hi + Mid + Lo) * 100 - 50) * 2 = -60

    This means there was 60% more investment in defense than offense.

    """
    # Format the victims file
    result = dfv.rename(
        columns={'killmail_time': 'datetime', 'HighSlotISK': 'hi_slot',
                 'MidSlotISK': 'mid_slot', 'LowSlotISK': 'lo_slot'}
    ).drop(columns=['solar_system_id'])

    result = result.set_index(['character_id', 'datetime']).sort_index()
    hi, mid, lo = result.hi_slot, result.mid_slot, result.lo_slot

    return result.assign(
        od_ratio=(hi / (mid + lo)),
        od_prct=(2 * ((hi / (hi + mid + lo)) * 100 - 50))
    )


def generate_performance_series(dfa, dfv):
    """TODO"""
    # Assign Type column for cumulative sum later
    dfa = dfa.assign(type=pd.Series(['kill' for _ in range(len(dfa))]))
    dfv = dfv.assign(type=pd.Series(['death' for _ in range(len(dfv))]))

    # Glue kills and deaths together, sort by character and datetime
    result = pd.concat(
        [dfa, dfv], sort=False
    ).set_index(['character_id', 'killmail_time'])

    # Keep only categorical columns and reset index
    result = result.sort_index().filter(
        ['killmail_id', 'ship_type_id', 'type'], axis='columns'
    ).reset_index()

    # Produce cumulative counts for each observation in the 'type' column
    result = result.assign(
        k_count=result.groupby('character_id').apply(
            lambda x: (x['type'] == 'kill').cumsum()
        ).reset_index().type
    )
    result = result.assign(
        d_count=result.groupby('character_id').apply(
            lambda x: (x['type'] == 'death').cumsum()
        ).reset_index().type
    )

    # Calculate performance metrics! (Ratios, Percentages, and Difference)
    k, d = result.k_count, result.d_count
    result = result.assign(kd_diff=(k - d),
                           kd_ratio=(k / d),
                           kd_prct=(2 * ((k / (k + d)) * 100 - 50)))

    # Drop empty dates (why does this happen???) and rename column
    # This results in a loss of 5992 observations...
    result = result.dropna(subset=['killmail_time'])
    result = result.rename(columns={'killmail_time': 'datetime'})

    return result.set_index(['character_id', 'datetime']).sort_index()


# ============================================================================ #
# Use the Command Line or a Terminal to do basic pre-filtering!

dfa = pd.read_csv('../data/All/attackers_frig_actv.csv', header=0)
dfv = pd.read_csv('../data/All/victims_frig_actv.csv', header=0)

dfi = generate_investment_series(dfv)
dfp = generate_performance_series(dfa, dfv)

dfi.to_csv('../data/Series/invt_perf/players_frig_actv_invt.csv')
dfp.to_csv('../data/Series/invt_perf/players_frig_actv_perf.csv')
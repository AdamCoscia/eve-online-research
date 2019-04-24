# eve-trajectory-mining #

Last Modified: 04/24/2019

-----

## Dynamic Time Warping ##

*Idea:*

- Take any two player time series. Compute the optimal pairing of data points
  between the two series (multiple pairs allowed). Then figure out how
  dissimilar the two series are and give a number representing how well the 
  the two series fit together. This can be done for series of different
  lengths, with different end points.  

*Plan:*

- Compute pairwise distance matrix for all 2737 time series using DTW
  - Cost to match one point to another has to be determined!
  - Use all 3 variables (Hi, Mid, Low)??
- Cluster the pairwise distance matrix using:  
   - Heirarchal Clustering  
   - K-mediods  

## Structure

- Statistics\
  - \_models\
    - players_frig_actv_invt.csv
    - players_frig_actv_perf.csv
  - cluster\
    - [method]
      - ...
  - dtw\
    - [date]
      - [evt/prd] \_ [h/l/m]mat \_ s[#]k[#].csv
      - ...
    - ...
  - pearson\
    - players_frig_actv_corr.csv
    - players_frig_actv_dstats.csv
  - players_frig_actv_ts.csv
  - players_frig_actv_ts-evt.csv
  - players_frig_actv_ts-prd.csv
- README.md  

## Folders

- ***\_models*** (Player Models): Data representing how player strategy and
  success is modelled.

- ***cluster*** (Clustered Data): Data that has been clustered.

  - ***[method]***: Clustering Method used to 

- ***dtw***  (Dynamic Time Warping): Pairwise Correlation done using Dynamic
  Time Warping (DTW) as the distance metric between time series.

  - ***[date]***: Date correlation matrices were created.

- ***pearson*** (Pearson Correlation): Analysis done pairwise using Pearson
  Correlation statistics.

## Entities
  
## Filters

- **invt** (Investments): Filtered data that has generated an additional
column which represents how the player has invested their ISK across their 
ship's slots. This investment strategy represents how the player is managing
their career. This column is a time series of player progession, with each 
killmail and time being an observation in the series.

- **perf** (Performance): Filtered data that tracks all player's kills,
deaths, and kill/death ratio as a function of time. The observations are the 
killmails that the player was involved in, either earning a kill (the 
player was in the "attacker" section of the killmail), or earning a death 
(the player was the victim of the killmail).

- **ts** (Time Series): Investment and Performance datasets are joined on 
  the performance series and investment series holes are forward filled. This is
  done assuming the player has not deviated from ship design until their next 
  death.

  - **ts-evt** (Event-based Time Series): Dataset is indexed by event, rather
    than time. Series length is number of events. 
    - Assume equal-spacing (events happen on regular interval)
    - All information from **ts** is kept such as killmail id, ship type, 
      kill vs. death, etc.

  - **ts-prd** (Period-based Time Series): Dataset is averaged on each period of
    the total length of the series, e.g., Second, Minute, Hour, Day, Week, 
    Month, Year.
    - Series uses **Day** period basis.
    - All derived information (ratios and percents) and identifying infortmation
      (killmail id, ship type, kill vs. death) from **ts** is removed, and
      the derived information is recalculated:
      - Kills and Deaths become the last entries for each day
      - Slot Investments become the average of the slots for each day
      - Missing values for days between start and end dates are back-filled from
        next valid observation.

- **corr** (Correlation): Correlation between performance series (k/d ratio)
and each investment series (slots and offensive investment) for each player.

- **dstats** (Descriptive Statistics): Includes **corr** data. Descriptive 
statistics (mean, std, etc.) on each series are calculated per player.

- **TODO**

- **TODO**

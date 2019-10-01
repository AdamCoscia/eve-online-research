# eve-trajectory-mining #

Last Modified: 04/24/2019

-----

## Data Storage File Naming Conventions (FNC)

This is the reference for the FNC used in this section of the project. Files 
almost always follow this semantic:

- entitybeingtracked _ filter1 _ filter2 _ (...) _ daterange.csv

The order of the filters mirrors the order in which the filters were applied. 
Any files that don't follow this semantic are explicitly described below.

## Structure

- data\  
  - All\  
    - by_region\  
      - 10000002\  
        - Attackers\  
          - 10000002xxxxxx_attackers.csv (xxxxxx = yearmo)  
          - ...  
        - Victims\  
          - 10000002xxxxxx_victims.csv  
          - ...  
      - 10000016\  
        - Attackers\  
          - 10000016xxxxxx_attackers.csv  
          - ...  
        - Victims\  
          - 10000016xxxxxx_victims.csv  
          - ...  
      - 10000033\  
        - Attackers\  
          - 10000033xxxxxx_attackers.csv  
          - ...  
        - Victims\  
          - 10000033xxxxxx_victims.csv  
          - ...  
      - 10000069\  
        - Attackers\  
          - 10000069xxxxxx_attackers.csv  
          - ...  
        - Victims\  
          - 10000069xxxxxx_victims.csv  
          - ...
    - attackers.csv  
    - attackers_frig.csv  
    - attackers_frig_actv.csv  
    - victims.csv  
    - victims_frig.csv  
    - victims_frig_actv.csv  
  - Series\
    - *_*models\
      - ...
    - dtw\
      - ...
    - cluster\
      - ...
    - pearson\
      - ...
    - players_frig_actv_ts.csv
    - players_frig_actv_ts-evt.csv
    - players_frig_actv_ts-prd.csv
  - README.md  

## Folders

- **All**: Contains filtered and unfiltered data with no calculated values.
  These files are meant to be the base data sets, upon which analyses and
  statistical measures can be performed. All calculated values should be saved
  in "Statistics\".
  
- **Statistics**: Contains modified data sets derived from "All\" that contain
  calculations on series values. These files are meant to represent data that
  has been evaluated and analyzed to produce series that are meaningful to the
  project. All base data sets and non-derived data sets should be saved in 
  "All\".

## Entities

- **attackers**: All attacker information unpacked from each killmail's 
  "attacker" section. If a killmail has multiple attackers, the information is 
  spread across multiple rows, one for each attacker involved.

- **victims**: All victim information unpacked from each killmail. Includes
  total ISK value of all items in a player's High, Mid, and Low ship slots, 
  calculated from the items in the players inventory in each killmail.
  
- **players**: File is organized by character id, where each row is a record 
  of a single player's statistics, with the filters applied below.
  
## Filters

- **frig** (Frigate): Filtered data that only includes rows where the 
  'ship_type_id' value is one of the 65 combat-oriented, Frigate-class ships 
  available to players.

- **actv** (Active): Filtered data that only includes players that generated at
  least 12 killmails within the 37 month range of data collected. Additionally,
  among these 12 or more killmails, there must be at least 12 killmails that
  each represent a different month-period of the 37 month range.

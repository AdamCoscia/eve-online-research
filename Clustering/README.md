tory-mining #

Last Modified: 08/14/2019

-----

## Trajectory Mining Application

The scripts in this directory are designed to cluster time series data collected 
from Zkillboard in the Killmail Fetching directory, and perform basic statistical 
analysis and visualizations of the resulting clusters.

## Motivation:

Player strategy can be modelled using a 3-variable time series, in which each 
variable represents the percentage of the player's investment in either the 
low, mid, or high slot. By clustering players based on these time series, 
different types of player strategies can be isolated and analyzed to determine 
the different approaches players take to problem solving, and determine if any 
strategies are particularly successful.

Clustering will be done based on the distances between player's time series. 
After clusters have been computed, different statistics can be computed for 
each cluster. Some of these statistics will give insight into the characteristics 
of the strategy players in any given cluster use (eg. standard deviation of 
investment in a player's slot may indicate a more explorative strategy), while 
statistics based on ratio of kills to death (eg. overall mean and linear 
regression slope of kill to death ratio) can be used to measure the performance
of players in a given cluster.

The results of the clustering can be presented using different visualization
techniques. A simple linear regression can be used to see which slots players 
choose to invest in more over time, while a LOESS regression can give more 
detailed insight into the strategy utilized by players in a given cluster.

## Tech/Framework used:

**Built with**
- `R 3.5.2`
- `dplyr 0.8.3`
- 'stringr 1.4.0'
- 'dtw 1.20-1'
- `WeightedCluster 1.4`
- `cluster 2.1.0`

## Features:

- *TODO*

## Installation:

In order to use/modify the scripts here, `R 3.5.1` must be installed on your
system. Go to http://r-project.org/ to learn more.

## How to Get Started Using This Application?

***IMPORTANT:*** ALWAYS READ THE DOCUMENTATION AT THE TOP OF EACH FILE FIRST!

To get started on which file to modify, follow this handy guide!

- *TODO*

## Credits:

Designed and Developed exclusively by Nicholas Marina.

Created: 8/14/2019


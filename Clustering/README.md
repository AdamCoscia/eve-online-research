# eve-trajectory-mining #

Last Modified: 08/14/2019

-----

## Clustering Application

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
- `stringr 1.4.0`
- `dtw 1.20-1`
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

- Run the Bash script `directory_setup.sh` to create all necessary directories 
  (R doesn't create direcories by default) and copy the necessary data from the
  Trajectory_Mining directory.
- The `activity.R` script will separate players based on how many time series 
  points they have. The results of this script were not used in later scripts, 
  but it may be useful for modifications to this directory.
- The `dtw.R` script will compute a distance matrix using the best Dyanamic Time 
  Warping (DTW) fit. This script by default will use time series transformed to 
  percentage form using the `percent.R` script. If you wish to use it with its 
  default settings, run `percent.R` first. Otherwise, feel free to modify the 
  script on your own clone of the repo to use a different set of time series.
- The `hcluster.R` and `medoids.R` will cluster players based on the distance
  matrices computed by `dtw.R` using hierarchical and k-medoids clustering 
  algorithms, respectively. Both scripts create graphs of cluster quality, and
  `hcluster.R` creates dendrograms.
- The `gower.R` script will then perform hierarchical clustering based on clusters
  produced for low, mid, and high slot investments, using Gower's distance metric 
  for categorical data. By default, this script will use the ideal number of 
  clusters from the k-medoids clustering, but feel free to modify the script on your 
  own clone to use a different method or number of clusters.
- The `playerstats.R` script will compute statistics for each player based on his
  or her time series data. The `clusterstats.R` script will average these statistics
  for each cluster. The `playerstats.R` script by default includes the clusters
  produced by `gower.R` in the csv file produced, which will then be the clusters used 
  by '`clusterstats.R` for averaging. To compute average statistics for different 
  clusters, either modify `playerstats.R` or the resulting `player_stats.csv` file 
  on your own clone of the repo.
- The `t-test.R` will perform t-tests for each statistic computed by `playerstats.R` 
  for each cluster. It stores the t-test p-values in a "distance matrix" format (ie. 
  the element in the i<sup>th</sup> row and j<sup>th</sup> column is the p-value for 
  the t-test for cluster i and j.
- The `activity.R`, `trajectory_graphs.R`, and `slot_trajectory_graphs.R` scripts all 
  produce visuals for the clusters. These scripts are designed for the clusters produced 
  by running the scripts unedited, so this script may need to be adjusted to produce 
  legible visuals if other scripts are modified.
  

## Credits:

Designed and Developed exclusively by Nicholas Marina.

Created: 8/14/2019

Time Series data used were collected using scripts contained in the Trajectory_Mining and Killmail_Fetching directories. Both were Designed and Developed exclusively by Adam Coscia.

Packages Used:

  Hadley Wickham, Romain François, Lionel Henry and Kirill Müller
  (2019). dplyr: A Grammar of Data Manipulation. R package version
  0.8.3. https://CRAN.R-project.org/package=dplyr

  Hadley Wickham (2019). stringr: Simple, Consistent Wrappers for
  Common String Operations. R package version 1.4.0.
  https://CRAN.R-project.org/package=stringr

  Giorgino T (2009). “Computing and Visualizing Dynamic Time Warping
  Alignments in R: The dtw Package.” _Journal of Statistical Software_,
  *31*(7), 1-24. <URL: http://www.jstatsoft.org/v31/i07/>.

  Studer, Matthias (2013). WeightedCluster Library Manual: A practical
  guide to creating typologies of trajectories in the social sciences
  with R. LIVES Working Papers, 24. DOI:
  10.12682/lives.2296-1658.2013.24.

  Maechler, M., Rousseeuw, P., Struyf, A., Hubert, M., Hornik,
  K.(2019).  cluster: Cluster Analysis Basics and Extensions. R package
  version 2.1.0.

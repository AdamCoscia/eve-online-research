# The EVE Online Data Manager #

> Designed by Adam Coscia  
> Stevens Institute of Technology  
> Summer 2018  
> Advisor: Dr. Aron Lindberg  
> Last Modified: *03/21/2019*

-----

## Trajectory Mining Application

The scripts in this application are designed to unpack, merge, filter, analyze,
and present the time series data obtained from scraping Zkillboard in the 
Killmail Fetching Application.

## Motivation:

To track player performance, this application relies on analyzing player 
strategy and performance over time in the form of Irregular Time Series data. 
Observations are individual killmails, which include victim strategy data and 
attacker statistics, that form time series trajectories of individual player 
strategy evolving throughout their career. 

Player success, or kills earned and deaths recieved, and the ratio of kills 
to deaths, is tracked on the same series and may be predicted by player 
strategy. It is our hope that characteristic evolutions of strategy may 
correlate with better career performance i.e. a higher average k/d ratio as a 
function of player progression. 

To determine if such characteristic evolutions of strategy exist, clustering 
will be performed on the evolution of each player's time series i.e. the 
trajectory.  By analyzing these clusters, patterns may emerge that can be 
correlated with group success rate, and possibly categorizing clusters on 
group success.

## Tech/Framework used:

**Built with**
- `Python 3.6`
- `pandas 0.23.3`
- `numpy 1.14.5`
- `matplotlib 2.2.2`

## Features:

- **/data**

## Installation:

In order to use/modify the scripts here, `Python 3.6` must be installed on your
system. Go to http://python.org/ to learn more.

## How to Get Started Using This Application?

***IMPORTANT:*** ALWAYS READ THE DOCUMENTATION AT THE TOP OF EACH FILE FIRST!

To get started on which file to modify, follow this handy guide!

If you need to...
- 

Then 

If you need to...
- 

Then 

If you need to...
- 

Then 

## Credits:

Designed and Developed exclusively by Adam Coscia  
Created on 06/10/2018

Thanks to Dr. Aron Lindberg for allowing me to take on this project and develop
the tools needed to produce some quality data!

## License:

TODO

# Gathers time series data for players and averages the statistics gathered for each cluster.
# 
# Utilizes the []
# 
# Created By: Nicholas Marina
# Created On: 7/22/19
# Last Updated: 7/22/19

library(dplyr)
library(stringr)

# This variable is used to choose how many clusters to use. This should be where cluster quality is maximized.
k <- 4

# The data frame used to store the clusters is then imported. The number of clusters is then selected.
player_stats <- read.csv(file='data/gower.csv', check.names=FALSE)
col <- sprintf('%i_clusters', k)
clusters <- player_stats[,col]
player_stats <- select(player_stats, character_id)
player_stats$cluster <- clusters
ids <- player_stats$character_id

# The time series csv is then read in and trimmed
time_series <- read.csv(file='data/series/players_frig_actv_ts-evt-prct.csv') %>%
	filter(character_id %in% ids)

# The id column in the stats data frame is changed to match the order of the time_series ids
ids <- unique(time_series$character_id)
player_stats <- player_stats[match(ids, player_stats$character_id),]

# Lists are initialized to store the statistics for each player
kd <- list(avg=c(),std=c(), skew=c(), slope=c(), slope_std=c(), col='kd_ratio', prefix='kd_')
low <- list(avg=c(), std=c(), skew=c(), slope=c(), slope_std=c(), col='lo_prct', prefix='low_')
mid <- list(avg=c(), std=c(), skew=c(), slope=c(), slope_std=c(), col='mid_prct', prefix='mid_')
high <- list(avg=c(), std=c(), skew=c(), slope=c(), slope_std=c(), col='hi_prct', prefix='high_')
stats <- list(kd, low, mid, high)

# The stats are then calculated for each player
for(i in 1:1958){
	player <- ids[i]
	print(player)
	player_data <- filter(time_series, character_id == player)
	for(j in 1:4){
		colname <- stats[[j]]$col
		series <- player_data[,colname]
		series_mean <- mean(series)
		series_std <- sd(series)
		series_median <- median(series)
		stats[[j]]$avg[i] <- series_mean
		stats[[j]]$std[i] <- series_std
		# Pearson definition #2 of skewness
		stats[[j]]$skew[i] <- 3*(series_mean - series_median)/series_std
		series_t <- 1:length(series)
		series_lm <- lm(series~series_t)
		coeff <- unname(series_lm$coefficients)
		slope <- coeff[2]
		stats[[j]]$slope[i] <- slope
		lm_series <- slope*series_t
		series_adj <- series - lm_series
		stats[[j]]$slope_std[i] <- sd(series_adj)
	}
}

# The stats are then added to the data frame
for(i in 1:4){
	stat <- stats[[i]]
	prefix <- stat$prefix
	player_stats[,sprintf('%savg', prefix)] <- stat$avg
	player_stats[,sprintf('%sstd', prefix)] <- stat$std
	player_stats[,sprintf('%sskew', prefix)] <- stat$skew
	player_stats[,sprintf('%sslope', prefix)] <- stat$slope
	player_stats[,sprintf('%sslope_std', prefix)] <- stat$slope_std
}

# The stats are then written to a csv file
write.csv(player_stats, file='data/player_stats.csv')


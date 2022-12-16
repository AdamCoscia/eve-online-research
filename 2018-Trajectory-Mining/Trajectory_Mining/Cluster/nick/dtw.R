# Creates a distance matrix for all player time series using the DTW algorithm for each slot
#
# Utilizes the dplyr, stringr, and dtw packages
# Learn more at http://dtw.r-forge.r-project.org/
#
# Created By: Nicholas Marina
# Created On: 07/05/2019
# Last Updated: 08/16/2019

library(dplyr)
library(stringr)
library(dtw)

# The time series csv is read in
series <- read.csv(file='data/series/players_frig_actv_ts-evt-prct.csv')

# Lists are used to store each player's time series, as well as character ids
lo_series <- list()
mid_series <- list()
hi_series <- list()
character_ids <- list()

# Time series data for each player is then extracted and stored in the lists. If there are any NA values, the players are omitted.
ids <- unique(series$character_id)
k <- 1
print('Time series collection beginning')
for(i in ids){
	df <- filter(series, character_id == i)
	lo <- df$lo_prct
	mid <- df$mid_prct
	hi <- df$hi_prct
	if(!(NA %in% lo | NA %in% mid | NA %in% hi)){
		lo_series[[k]] <- lo
		mid_series[[k]] <- mid
		hi_series[[k]] <- hi
		character_ids[[k]] <- i
		k <- k + 1
	}	
}
print('Time series collected.')

# CSV files are created to store the distance matrices
sample_size <- length(character_ids)
write.table(matrix(character_ids, nrow=1, ncol=sample_size), file='data/dist/lo_dtw.csv', append=FALSE, sep=',', row.names=FALSE, col.names=FALSE)
write.table(matrix(character_ids, nrow=1, ncol=sample_size), file='data/dist/mid_dtw.csv', append=FALSE, sep=',', row.names=FALSE, col.names=FALSE)
write.table(matrix(character_ids, nrow=1, ncol=sample_size), file='data/dist/hi_dtw.csv', append=FALSE, sep=',', row.names=FALSE, col.names=FALSE)


# DTW values are then calculated iteratively for each slot - the dist object requires lower triangular form. Each row is appended to the csv
print('Beginning DTW Matrix Calculations...')
combinations <- (sample_size^2 - sample_size)/2
progress <- 0
for(i in 1:sample_size){
  print(sprintf('Iteration: %i', i))
  progress <- progress + i - 1
	print(sprintf('Progress: %f%s', 100*progress/combinations, '%'))
	lo_row <- replicate(sample_size, NA)
	mid_row <- replicate(sample_size, NA)
	hi_row <- replicate(sample_size, NA)
	for(j in 1:i){
		lo_row[j] <- dtw(lo_series[[i]], lo_series[[j]], distance.only=TRUE)$distance
		mid_row[j] <- dtw(mid_series[[i]], mid_series[[j]], distance.only=TRUE)$distance
		hi_row[j] <- dtw(hi_series[[i]], hi_series[[j]], distance.only=TRUE)$distance
	}
	write.table(matrix(lo_row, nrow=1, ncol=sample_size), file='data/dist/lo_dtw.csv', append=TRUE, sep=',', row.names=FALSE, col.names=FALSE)
	write.table(matrix(mid_row, nrow=1, ncol=sample_size), file='data/dist/mid_dtw.csv', append=TRUE, sep=',', row.names=FALSE, col.names=FALSE)
	write.table(matrix(hi_row, nrow=1, ncol=sample_size), file='data/dist/hi_dtw.csv', append=TRUE, sep=',', row.names=FALSE, col.names=FALSE)
}


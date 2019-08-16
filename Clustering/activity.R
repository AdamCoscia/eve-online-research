# Separates players into three groups based on activity
#
# Utilizes the dplyr and stringr packages
#
# Created By: Nicholas Marina
# Created On: 7/11/19
# Last Updated: 8/16/19

library(dplyr)
library(stringr)

# The csv containing time series data is read in
series <- read.csv('data/series/players_frig_actv_ts-evt-prct.csv')

# Character ids are stored in a vector
character_ids <- unique(series$character_id)

# Another vector is used to store time series length for each player
sample_size <- length(character_ids)
lengths <- c()
for(i in 1:sample_size){
	df <- filter(series, character_id == character_ids[i])
	lengths[i] <- length(df$killmail_id)
}

# The median activity is then calculated
med_length <- median(lengths)
print(med_length)

# Players are then separated into the bottom and top 50% of activity
bottom_half <- c()
bottom_lengths <- c()
top_half <- c()
top_lengths <- c()
for(i in 1:sample_size){
	if(lengths[i] > med_length){
		top_half <- append(top_half, character_ids[i])
		top_lengths <- append(top_lengths, lengths[i])
	} else{
		bottom_half <- append(bottom_half, character_ids[i])
		bottom_lengths <- append(bottom_lengths, lengths[i])
	}
}

# The 2 halves are halved again to get players separated in 25% increments
bot_med <- median(bottom_lengths)
top_med <- median(top_lengths)
actv_25 <- c()
actv_50 <- c()
actv_75 <- c()
actv_100 <- c()
bot_size <- length(bottom_half)
for(i in 1:bot_size){
	if(bottom_lengths[i] > bot_med){
		actv_50 <- append(actv_50, bottom_half[i])
	} else{
		actv_25 <- append(actv_25, bottom_half[i])
	}
}
top_size <- length(top_half)
for(i in 1:top_size){
	if(top_lengths[i] > top_med){
		actv_100 <- append(actv_100, top_half[i])
	} else{
		actv_75 <- append(actv_75, top_half[i])
	}
}

# The middle 50% is used as the medium activity group, and the bottom and top 25% are used as the low and high activity groups, respectively
med_activity <- append(actv_50, actv_75)
low_activity <- actv_25
high_activity <- actv_100
med_df <- filter(series, character_id %in% med_activity)
low_df <- filter(series, character_id %in% low_activity)
high_df <- filter(series, character_id %in% high_activity)

# The data frames are then written to csv files
write.csv(low_df, file='data/series/low_activity.csv')
write.csv(med_df, file='data/series/med_activity.csv')
write.csv(high_df, file='data/series/high_activity.csv')


# Converts time series from investment amounts to percentages for each slot
#
# Utilizes the dplyr package
#
# Created By: Nicholas Marina
# Created On: 07/05/19
# Last Updated: 08/16/19

library(dplyr)

# The time series csv is read in
series <- read.csv(file='data/series/players_frig_actv_ts-evt.csv')

# A total investment variable is added to the data frame, as well as the percentage of investment for each player
series <- series %>%
	mutate(total = hi_slot + mid_slot + lo_slot) %>%
		mutate(hi_prct = hi_slot/total, mid_prct = mid_slot/total, lo_prct = lo_slot/total) %>%
			select(-hi_slot, -mid_slot, -lo_slot, -total)

# The new data frame is written to a csv file
write.csv(series, file='data/series/players_frig_actv_ts-evt-prct.csv')


library(dplyr)
library(stringr)

# The player_stats csv is read in
player_stats <- read.csv('data/player_stats.csv')

# A vector is used to store cluster numbers
clust <- sort.int(unique(player_stats$cluster))
nclust <- length(clust)

# Statistic names are stored in a vector
colnames <- c()

# Iteration is used to build the vector
prefixes <- c('kd', 'low', 'mid', 'high')
stats <- c('avg', 'std', 'skew', 'slope', 'slope_std')

n <- 1
for(i in prefixes){
	for(j in stats){
		name <- paste(i, j, sep='_')
		colnames[n] <- name
		n <- n + 1
	}
}

# A data frame is then made for each statistic to store the t test results of each combination
for(stat in colnames){
	mat <- matrix(1, nrow=nclust, ncol=nclust)
	stat_vectors <- list()
	for(i in clust){
		stat_vectors[[i]] <- filter(player_stats, cluster == i)[,stat]
	}
	for(i in clust){
		for(j in clust){
			mat[i, j] <- t.test(stat_vectors[[i]], stat_vectors[[j]])$p.value
		}
	}
	df <- as.data.frame(mat)
	colnames(df) <- clust
	write.csv(df, file=sprintf('data/t_test/%s_t_test.csv', stat))
}

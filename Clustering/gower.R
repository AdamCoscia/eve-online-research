# Clusters nominal values based on kmedoids clustering of each slot trajectory using hierarchical clustering with Gower distance. 
# The number of clusters should be where quality of clustering is maximized.
#
# Utilizes the dplyr, stringr, and StatMatch packages
# Learn more at https://cran.r-project.org/web/packages/StatMatch/index.html
#
# Created By: Nicholas Marina
# Created On: 07/22/2019
# Last Updated: 08/16/2019

library(dplyr)
library(stringr)
library(StatMatch)

# Variables determine the number of clusters to use for low, mid, and high slots for easy adjustment
l_clusters <- 2
m_clusters <- 2
h_clusters <- 3

# The slot clusterings are read in and stored
low_clust <- read.csv(file=sprintf('data/kmedoids/low_slot/%d_clusters.csv', l_clusters))
mid_clust <- read.csv(file=sprintf('data/kmedoids/mid_slot/%d_clusters.csv', m_clusters))
high_clust <- read.csv(file=sprintf('data/kmedoids/high_slot/%d_clusters.csv', h_clusters))

# A new data frame is now created with data from all 3 clusterings
slot_clust <- low_clust %>%
	dplyr::select(character_id, cluster)
colnames(slot_clust) <- c('character_id','low_cluster')
slot_clust$mid_cluster <- mid_clust$cluster
slot_clust$high_cluster <- high_clust$cluster

# The numbers representing each cluster are converted to letters
lo_vals <- slot_clust$low_cluster
mid_vals <- slot_clust$mid_cluster
hi_vals <- slot_clust$high_cluster
lo_clusters <- unique(lo_vals)
mid_clusters <- unique(mid_vals)
hi_clusters <- unique(hi_vals)
sample_size <- length(lo_vals)
labels <- c('a', 'b', 'c')
for(i in 1:sample_size){
	lo_vals[i] <- labels[match(lo_vals[i], lo_clusters)]
	mid_vals[i] <- labels[match(mid_vals[i], mid_clusters)]
	hi_vals[i] <- labels[match(hi_vals[i], hi_clusters)]
}
slot_clust$low_cluster <- lo_vals
slot_clust$mid_cluster <- mid_vals
slot_clust$high_cluster <- hi_vals
head(slot_clust)

# This data frame is saved to a csv file for reference
write.csv(slot_clust, file='data/kmedoids/all_slots_kmedoids.csv')

# The data frame has its first column dropped, and then a distance matrix is calculated using Gower distance.
character_ids <- slot_clust$character_id
slot_clust <- slot_clust %>%
	select(-character_id)
dist <- gower.dist(slot_clust)

# The distance matrix must then be converted to a data frame to be stored as a csv file
for(i in 1:sample_size){
	for(j in i:sample_size){
		if(i != j){
			dist[i, j] <- NA
		}
	}
}
dist <- as.data.frame(dist)
colnames(dist) <- character_ids
write.csv(dist, file='data/dist/gower_matrix.csv', row.names=FALSE)

# Te=he dataframe is converted back to a distance matrix, and the players are then clustered
dist <- as.dist(dist)
clust <- hclust(dist)
clust$labels <- character_ids
pdf(file='visuals/gower_hierarchical/gower_hierarchical.pdf', height = 10, width=40)
plot(clust, main='Gower Distance Hierarchical Clustering', xlab='Character ID')
dev.off()

# The variable m determines up to how many clusters to determine cluster quality for
m <- 15

# A new data frame is made to store the clustering indices
cluster_frame <- select(low_clust, character_id)

# Cluster quality for hierarchical clusterings from 2 to m clusters is then calculated. Visuals with rectangles around clusters are also created for these clusterings.
HG = 0
PBC = 0
ASW = 0
for(i in 2:m){
	pdf(file=sprintf('visuals/gower_hierarchical/%d_clusters.pdf', i), height = 25, width = 40)
	plot(clust, main=sprintf('Gower Distance Hierarchical Clustering'), xlab='Character ID')
	rect.hclust(clust, k=i)
	dev.off()
	k_clust <- cutree(clust, k=i)
	cluster_frame[sprintf('%d_clusters', i)] <- k_clust
	quality <- unname(wcClusterQuality(dist, k_clust)$stats)
	HG[i - 1] <- quality[2]
	PBC[i - 1] <- quality[1]
	ASW[i - 1] <- quality[4]
}

# Cluster quality metrics are then graphed
pdf(file='visuals/gower_hierarchical/gower_hierarchical_quality.pdf')
plot(2:m, HG, type='l', col='green', main='Gower Hierarchical Cluster Quality',ylim=c(0,1.25) ,xlab='Number of Clusters', ylab='Cluster Quality', xaxt='n', yaxt='n')
lines(2:m, ASW, col='cyan')
lines(2:m, PBC, col='red')
legend(0.85*m, 1.25, legend=c('HG','ASW','PBC'), col=c('green','cyan','red'), lty=1)
axis(1, 2:m)
axis(2, c(0, 0.2, 0.4, 0.6, 0.8, 1.0))
dev.off()

# The cluster data frame is then stored in a csv file
write.csv(cluster_frame, file='data/gower.csv', row.names=FALSE)

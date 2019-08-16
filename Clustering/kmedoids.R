# Clusters from distance matrix computed by dtw.R in a data structure easily usable in R, using k medoids clustering.
#
# Utilizes the dplyr, stringr, and WeightedCluster packages
# Learn more at https://cran.r-project.org/web/packages/WeightedCluster/index.html
#
# Created By: Nicholas Marina
# Created On: 06/04/19
# Last Updated: 08/16/19

library(dplyr)
library(stringr)
library(WeightedCluster)

# Here the distance matrices are read in
ldist <- as.dist(read.csv(file='data/dist/lo_dtw.csv', check.names=FALSE))
mdist <- as.dist(read.csv(file='data/dist/mid_dtw.csv', check.names=FALSE))
hdist <- as.dist(read.csv(file='data/dist/hi_dtw.csv', check.names=FALSE))
character_id <- colnames(read.csv(file='data/dist/lo_dtw.csv', check.names=FALSE))
print(character_id)
length(character_id)

kclust <- function(dist, k, title, dname){
# Computes k medoids clustering for a distance matrix up to a certain number of clusters, and stores each clustering as well as a plot showing the quality as a function of number of clusters.
#
# :param dist: The cleaned distance matrix
# :param k: The upper limit on the number of clusters to compute (ie. if k=5, clusterings from 2 to 5 medoids will be computed)
# :param title: The title of the graph rendered by the function
# :param dname: The name used for the directory to save files to
# :return: This is a void function

	PBC = 0
	HG = 0
	ASW = 0
	for(i in 2:k){
		cluster <- wcKMedoids(dist, i, cluster.only=TRUE)
		quality <- unname(wcKMedoids(dist, i)$stats)
		cluster_data <- data.frame(character_id, cluster)
		write.csv(cluster_data, file = sprintf('data/kmedoids/%s/%d_clusters.csv', dname, i))
		PBC[i-1] <- quality[1]
		HG[i-1] <- quality[2]
		ASW[i-1] <- quality[4]
	}
	pdf(file = paste(paste('visuals/kmedoids_quality', dname, sep='/'), 'pdf', sep='.'), height = 10, width = 10)
	plot(2:k, HG, type = 'l', col = 'green', ylim = c(0, 1.15), main = title, xlab = 'Number of Clusters', ylab = 'Quality')
	lines(2:k, ASW, col = 'cyan')
	lines(2:k, PBC, col = 'red')
	axis(1, 2:k)
	legend(.9*k, 1.15, legend=c('HG', 'ASW', 'PBC'), col=c('green','cyan','red'), lty=1)
	dev.off()
	return()
}

kclust(ldist, 20, 'Low Slot K-Medoids Clustering Quality', 'low_slot')
kclust(mdist, 20, 'Mid Slot K-Medoids Clustering Quality', 'mid_slot')
kclust(hdist, 20, 'High Slot K-Medoids Clustering Quality', 'high_slot')


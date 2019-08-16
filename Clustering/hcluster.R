# Takes distance matrices computed by dtw.R and computes hierarchal clusterings, and graphs cluster quality as a function of number of clusters
#
# Utilizes the dplyr, stringr, and WeightedCluster packages
# Learn more at https://cran.r-project.org/web/packages/WeightedCluster/index.html
#
# Created By: Nicholas Marina
# Created On: 07/20/2019
# Last Updated: 07/20/2019

library(dplyr)
library(stringr)
library(WeightedCluster)

# Here the distance matrices are read in
ldist <- as.dist(read.csv('data/dist/lo_dtw.csv', check.names=FALSE))
mdist <- as.dist(read.csv('data/dist/mid_dtw.csv', check.names=FALSE))
hdist <- as.dist(read.csv('data/dist/hi_dtw.csv', check.names=FALSE))

# The hclust function is used to create a cluster object for each slot, each of which is stored in a variable. Ward linkage is used in this clustering.
lo_hclust <- hclust(ldist, method='ward.D2')
mid_hclust <- hclust(mdist, method='ward.D2')
hi_hclust <- hclust(hdist, method='ward.D2')

# The hclust object is difficult to store in lists, so rendering PDFs is done individually for each clustering, rather than iteratively
pdf(file ='visuals/hierarchical_dendrograms/low_slot.pdf', height = 20, width = 60)
plot(lo_hclust, main = 'Low Slot Hierarchical Clustering', hang=-1, xlab = 'Character ID', ylab = 'Distance')
dev.off()

pdf(file ='visuals/hierarchical_dendrograms/mid_slot.pdf', height = 20, width = 60)
plot(mid_hclust, main = 'Mid Slot Hierarchical Clustering', hang=-1, xlab = 'Character ID', ylab = 'Distance')
dev.off()

pdf(file ='visuals/hierarchical_dendrograms/high_slot.pdf', height = 20, width = 60)
plot(hi_hclust, main = 'High Slot Hierarchical Clustering', hang=-1, xlab = 'Character ID', ylab = 'Distance')
dev.off()

# Now clusterings in a certain range of number of clusters will be computed, and their qualities will be stored
nclusterings = function(clust, n, slot) {
# Computes clusterings with 2 to n clusters, stores the clusterings in a csv file, and creates a graph of different quality metrics as a function of number of clusters
#
# :param clust: hclust object for the given slot
# :param n: Upper limit of number of clusters for which to produce clusterings
# :param slot: A string input for the slot, to be used in file naming\
# :return: This function is a void function

	PBC = 0
	HG = 0
	ASW = 0
	if(slot == 'low'){
		diff = ldist
		title = 'Low Slot Hierarchal Clustering Quality'
	}
	else if(slot == 'mid'){
		diff = mdist
                title = 'Mid Slot Hierarchal Clustering Quality'
	}
	else{
		diff = hdist
                title = 'High Slot Hierarchal Clustering Quality'
	}
	# This for loop generates clusterings with clusters from 2 to n, stores the clusterings in csv files, and stores cluster quality measurements in the four lists
	for(i in 2:n){
		cluster_values = cutree(clust, k = i)
		write.csv(cluster_values, file = sprintf('data/hierarchical/%s_slot/%d_clusters', slot, i))
		quality <- unname(wcClusterQuality(diff, cluster_values)$stats)
		PBC[i-1] <- quality[1]
		ASW[i-1] <- quality[4]
		HG[i-1] <- quality[2]
	}
	# The quality measurements are graphed on the y axis, with the number of clusters on the x axis
	pdf(file = paste(paste('visuals/hierarchical_quality', slot, sep='/'), 'pdf', sep ='.'), height = 10, width = 10)
	plot(2:n, HG, type = 'l', col = 'green', ylim = c(0, 1.15), main = title, xlab = 'Number of Clusters', ylab = 'Quality')
	lines(2:n, ASW, col = 'cyan')
	lines(2:n, PBC, col = 'red')
	axis(1, 2:n)
	legend(.9*n, 1.15, legend=c('HG', 'ASW', 'PBC'), col=c('green','cyan','red'), lty=1)
	dev.off()
	return()
}

nclusterings(lo_hclust, 20, 'low')
nclusterings(mid_hclust, 20, 'mid')
nclusterings(hi_hclust, 20, 'high')

for(i in 2:20){	
	pdf(file = sprintf('visuals/hierarchical_dendrograms/low_slot-%i.pdf', i), height = 20, width = 60)
	plot(lo_hclust, main = 'Low Slot Hierarchical Clustering', hang=-1, xlab = 'Character ID', ylab = 'Distance')
	rect.hclust(lo_hclust, k=i)
	dev.off()

	pdf(file = sprintf('visuals/hierarchical_dendrograms/mid_slot-%i.pdf', i), height = 20, width = 60)
	plot(mid_hclust, main = 'Mid Slot Hierarchical Clustering', hang=-1, xlab = 'Character ID', ylab = 'Distance')
	rect.hclust(mid_hclust, k=i)
	dev.off()

	pdf(file = sprintf('visuals/hierarchical_dendrograms/high_slot-%i.pdf', i), height = 20, width = 60)
	plot(hi_hclust, main = 'High Slot Hierarchical Clustering', hang=-1, xlab = 'Character ID', ylab = 'Distance')
	rect.hclust(hi_hclust, k=i)
	dev.off()
}


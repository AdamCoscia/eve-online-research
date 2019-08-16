# Creates scatter plots of each slot cluster to illustrate their meaning
#
# Utilizes the stringr package
#
# Created By: Nicholas Marina
# Created On: 07/31/19
# Last Updated: 08/16/19

library(stringr)

# Cluster and time series data are read in
ts_data <- read.csv(file='data/series/players_frig_actv_ts-evt-prct.csv')
cluster_df <- read.csv(file='data/kmedoids/all_slots_kmedoids.csv')

# Vectors are used to store all unique clusters, and a variable stores the number of clusters
lo_clusters <- unique(cluster_df$low_cluster)
n_lo <- length(lo_clusters)
mid_clusters <- unique(cluster_df$mid_cluster)
n_mid <- length(mid_clusters)
hi_clusters <- unique(cluster_df$high_cluster)
n_hi <- length(hi_clusters)

print(n_lo)
print(n_mid)
print(n_hi)

# A list of lists stores the points and ids for each cluster
lo_investment <- rep(list(c()), n_lo)
lo_time <- rep(list(c()), n_lo)
lo_ids <- rep(list(c()), n_lo)
mid_investment <- rep(list(c()), n_mid)
mid_time <- rep(list(c()), n_mid)
mid_ids <- rep(list(c()), n_mid)
hi_investment <- rep(list(c()), n_hi)
hi_time <- rep(list(c()), n_hi)
hi_ids <- rep(list(c()), n_hi)

# Loops are used to fill the lists
for(i in 1:n_lo){
	clust <- subset(cluster_df, low_cluster == lo_clusters[i])
	lo_ids[[i]] <- append(lo_ids[[i]], clust$character_id)
}
for(i in 1:n_mid){
	clust <- subset(cluster_df, mid_cluster == mid_clusters[i])
	mid_ids[[i]] <- append(mid_ids[[i]], clust$character_id)
}
for(i in 1:n_hi){
	clust <- subset(cluster_df, high_cluster == hi_clusters[i])
	hi_ids[[i]] <- append(hi_ids[[i]], clust$character_id)
}

print(lo_ids)
print(mid_ids)
print(hi_ids)

for(i in 1:n_lo){
	for(id in lo_ids[[i]]){
		df <- subset(ts_data, character_id == id)
		ts <- df$lo_prct
		ts_length <- length(ts)
		t <- (0:(ts_length - 1))/(ts_length - 1)
		lo_time[[i]] <- append(lo_time[[i]], t)
		lo_investment[[i]] <- append(lo_investment[[i]], ts)
	}
}
for(i in 1:n_mid){
	for(id in mid_ids[[i]]){
		df <- subset(ts_data, character_id == id)
		ts <- df$mid_prct
		ts_length <- length(ts)
		t <- (0:(ts_length - 1))/(ts_length - 1)
		mid_time[[i]] <- append(mid_time[[i]], t)
		mid_investment[[i]] <- append(mid_investment[[i]], ts)
	}
}
for(i in 1:n_hi){
	for(id in hi_ids[[i]]){
		df <- subset(ts_data, character_id == id)
		ts <- df$hi_prct
		ts_length <- length(ts)
		t <- (0:(ts_length - 1))/(ts_length - 1)
		hi_time[[i]] <- append(hi_time[[i]], t)
		hi_investment[[i]] <- append(hi_investment[[i]], ts)
	}
}

print(lo_time)
print(lo_investment)
print(mid_time)
print(mid_investment)
print(hi_time)
print(hi_investment)

# A color coded graph is made for each cluster
colors <- c('red', 'green', 'blue')
jpeg(file='visuals/trajectories/low_initial_color_coded.jpg', height=1000, width=1000)
plot.new()
par(mar=c(5.1, 4.1, 4.1, 8.1), xpd=TRUE)
title(main='Player Low Slot Trajectories', xlab = 'Time Series Progression', ylab='Percent Investment')
axis(1)
axis(2, at=seq(0, 1, by=0.2), labels=paste(100*seq(0, 1, by=0.2), '%'))
legend('top', inset=c(0, -0.0175), fill=colors[1:n_lo], cex=0.85, legend=1:n_lo, horiz=TRUE, title='Cluster')
for(i in 1:n_lo){
	points(lo_time[[i]], lo_investment[[i]], col=colors[i], cex=0.1)
}
dev.off()
jpeg(file='visuals/trajectories/mid_initial_color_coded.jpg', height=1000, width=1000)
plot.new()
par(mar=c(5.1, 4.1, 4.1, 8.1), xpd=TRUE)
title(main='Player Mid Slot Trajectories', xlab = 'Time Series Progression', ylab='Percent Investment')
axis(1)
axis(2, at=seq(0, 1, by=0.2), labels=paste(100*seq(0, 1, by=0.2), '%'))
legend('top', inset=c(0, -0.0175), fill=colors[1:n_mid], cex=0.85, legend=1:n_mid, horiz=TRUE, title='Cluster')
for(i in 1:n_mid){
	points(mid_time[[i]], mid_investment[[i]], col=colors[i], cex=0.1)
}
dev.off()
jpeg(file='visuals/trajectories/high_initial_color_coded.jpg', height=1000, width=1000)
plot.new()
par(mar=c(5.1, 4.1, 4.1, 8.1), xpd=TRUE)
title(main='Player High Slot Trajectories', xlab = 'Time Series Progression', ylab='Percent Investment')
axis(1)
axis(2, at=seq(0, 1, by=0.2), labels=paste(100*seq(0, 1, by=0.2), '%'))
legend('top', inset=c(0, -0.0175), fill=colors[1:n_hi], cex=0.85, legend=1:n_hi, horiz=TRUE, title='Cluster')
for(i in 1:n_hi){
	points(hi_time[[i]], hi_investment[[i]], col=colors[i], cex=0.1)
}
dev.off()

# An array of graphs is then made for each cluster
w = 1200*n_lo
jpeg(file='visuals/trajectories/low_initial_array.jpg', height=1200, width=w)
plot.new()
par(mfrow=c(1, n_lo))
for(i in 1:n_lo){
	axis(1)
	axis(2, at=seq(0, 1, by=0.2), labels=paste(100*seq(0, 1, by=0.2), '%'))
	plot(lo_time[[i]], lo_investment[[i]], main=sprintf('Cluster %i Low Slot Time Series', i), xlab='Time Series Progression', ylab='Percent Investment')
}
dev.off()
w = 1200*n_mid
jpeg(file='visuals/trajectories/mid_initial_array.jpg', height=1200, width=w)
plot.new()
par(mfrow=c(1, n_mid))
for(i in 1:n_mid){
	axis(1)
	axis(2, at=seq(0, 1, by=0.2), labels=paste(100*seq(0, 1, by=0.2), '%'))
	plot(mid_time[[i]], mid_investment[[i]], main=sprintf('Cluster %i Mid Slot Time Series', i), xlab='Time Series Progression', ylab='Percent Investment')
}
dev.off()
w = 1200*n_hi
jpeg(file='visuals/trajectories/high_initial_array.jpg', height=1200, width=w)
plot.new()
par(mfrow=c(1, n_hi))
for(i in 1:n_hi){
	axis(1)
	axis(2, at=seq(0, 1, by=0.2), labels=paste(100*seq(0, 1, by=0.2), '%'))
	plot(hi_time[[i]], hi_investment[[i]], main=sprintf('Cluster %i High Slot Time Series', i), xlab='Time Series Progression', ylab='Percent Investment')
}
dev.off()

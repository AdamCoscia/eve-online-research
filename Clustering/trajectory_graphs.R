# Visualizes trajectories to demonstrate differences between the clusters.
#
# Utilizes the []
#
# Created By: Nicholas Marina
# Created On: 07/23/19
# Last Updated: 07/23/19

library(stringr)
library(stats)

# A boolean is used to skip the long LOESS and Linear Computations
skip_loess <- TRUE

# Time series and clustering data are read in
time_series <- read.csv(file='data/series/players_frig_actv_ts-evt-prct.csv')
cluster_df <- read.csv(file='data/gower.csv', check.names=FALSE)

# The variable n represents the number of clusters to use. This should be where cluster quality is maximized.
n <- 4

# Character ids and clusters are stored in vectors
character_ids <- cluster_df$character_id
col <- sprintf('%d_clusters', n)
clusters <- cluster_df[,col]

# A list of lists is used to store which players are in which cluster
cluster_ids <- rep(list(c()), n)
sample_size <- length(character_ids)
for(i in 1:sample_size){
	cluster_ids[[clusters[i]]] <- append(cluster_ids[[clusters[i]]], character_ids[i])
}

# A list is made to keep track of colors to represent each cluster. Colors should be added to match the number of clusters.
colors <- c('red', 'blue', 'green', 'cyan')

# Lists of lists are used to store time series points for each cluster
lo_slot <- rep(list(c()), n)
mid_slot <- rep(list(c()), n)
hi_slot <- rep(list(c()), n)
time <- rep(list(c()), n)

# A nested loop is used to graph all trajectories
pdf(file='visuals/trajectories/low_color_coded.pdf', height=10, width=10)
plot.new()
par(mar=c(5.1, 4.1, 4.1, 8.1), xpd=TRUE)
title(main='Player Low Slot Trajectories', xlab = 'Time Series Progression', ylab='Percent Investment')
axis(1)
axis(2, at=seq(0, 1, by=0.2), labels=paste(100*seq(0, 1, by=0.2), '%'))
legend('top', inset=c(0, -0.025), fill=colors, cex=0.75, legend=c(1, 2, 3, 4), horiz=TRUE, title='Cluster')
for(i in 1:n){
	for(j in cluster_ids[[i]]){
		df <- subset(time_series, character_id == j)
		lo <- df$lo_prct
		ts_length <- length(lo)
		lo_slot[[i]] <- append(lo_slot[[i]], lo)
		t <- (0:(ts_length-1))/(ts_length-1)
		time[[i]] <- append(time[[i]], t)
		lines(t, lo, col=colors[i])
	}
}
dev.off()
pdf(file='visuals/trajectories/mid_color_coded.pdf', height=10, width=10)
plot.new()
par(mar=c(5.1, 4.1, 4.1, 8.1), xpd=TRUE)
title(main='Player Mid Slot Trajectories', xlab = 'Time Series Progression', ylab='Percent Investment')
axis(1)
axis(2, at=seq(0, 1, by=0.2), labels=paste(100*seq(0, 1, by=0.2), '%'))
legend('top', inset=c(0, -0.025), fill=colors, cex=0.75, legend=c(1, 2, 3, 4), horiz=TRUE, title='Cluster')
for(i in 1:n){
	for(j in cluster_ids[[i]]){
		df <- subset(time_series, character_id == j)
		mid <- df$mid_prct
		ts_length <- length(mid)
		mid_slot[[i]] <- append(mid_slot[[i]], mid)
		t <- (0:(ts_length-1))/(ts_length-1)
		lines(t, mid, col=colors[i])
	}
}
dev.off()
pdf(file='visuals/trajectories/high_color_coded.pdf', height=10, width=10)
plot.new()
par(mar=c(5.1, 4.1, 4.1, 8.1), xpd=TRUE)
title(main='Player High Slot Trajectories', xlab = 'Time Series Progression', ylab='Percent Investment')
axis(1)
axis(2, at=seq(0, 1, by=0.2), labels=paste(100*seq(0, 1, by=0.2), '%'))
legend('top', inset=c(0, -0.025), fill=colors, cex=0.75, legend=c(1, 2, 3, 4), horiz=TRUE, title='Cluster')
for(i in 1:n){
	for(j in cluster_ids[[i]]){
		df <- subset(time_series, character_id == j)
		hi <- df$hi_prct
		hi_slot[[i]] <- append(hi_slot[[i]], hi)
		ts_length <- length(hi)
		t <- (0:(ts_length - 1))/(ts_length-1)
		lines(t, hi, col=colors[i])
	}
}
dev.off()

# A 3xn array of graphs is then made for each slot
w <- 1200*n
max_length <- 0
# The max length of the time series is used for setting the scale of the points in each scatter plot
for(i in 1:n){
	if(length(time[[i]]) > max_length){
		max_length <- length(time[[i]])
	}
}
jpeg(file='visuals/trajectories/array.jpg', height=3600, width=w)
par(mfrow=c(3, n))
for(i in 1:n){
	scale <- 0.1*max_length/length(time[[i]])
	plot.new()
	title(main=sprintf('Cluster %i Low Slot Time Series', i), xlab='Time Series Progression', ylab='Percent Investment')
	axis(1)
	axis(2, at=seq(0, 1, by=0.2), labels=paste(100*seq(0, 1, by=0.2), '%'))
	for(id in cluster_ids[[i]]){
		df <- subset(time_series, character_id == id)
		ts <- df$lo_prct
		ts_length <- length(ts)
		t <- (0:(ts_length - 1))/(ts_length - 1)
		lines(t, ts, cex=0.005)
	}
	points(time[[i]], lo_slot[[i]], cex=0.015, col='blue')
}
for(i in 1:n){
	scale <- 0.1*max_length/length(time[[i]])
	plot.new()
	title(main=sprintf('Cluster %i Mid Slot Time Series', i), xlab='Time Series Progression', ylab='Percent Investment')
	axis(1)
	axis(2, at=seq(0, 1, by=0.2), labels=paste(100*seq(0, 1, by=0.2), '%'))
	for(id in cluster_ids[[i]]){
		df <- subset(time_series, character_id == id)
		ts <- df$mid_prct
		ts_length <- length(ts)
		t <- (0:(ts_length - 1))/(ts_length - 1)
		lines(t, ts, cex=0.005)
	}
	points(time[[i]], mid_slot[[i]], cex=0.015, col='blue')
}
for(i in 1:n){
	scale <- 0.1*max_length/length(time[[i]])
	plot.new()
	title(main=sprintf('Cluster %i High Slot Time Series', i), xlab='Time Series Progression', ylab='Percent Investment')
	axis(1)
	axis(2, at=seq(0, 1, by=0.2), labels=paste(100*seq(0, 1, by=0.2), '%'))
	for(id in cluster_ids[[i]]){
		df <- subset(time_series, character_id == id)
		ts <- df$hi_prct
		ts_length <- length(ts)
		t <- (0:(ts_length - 1))/(ts_length - 1)
		lines(t, ts, cex=0.005)
	}
	points(time[[i]], hi_slot[[i]], cex=0.015, col='blue')
}
dev.off()

if(skip_loess){
	stop('Array Graphs Completed')
	quit()
}
quit()

# A loop is then used to plot the linear and loess regressions of each cluster's trajectories
for(i in 1:n){
	lo <- lo_slot[[i]]
	mid <- mid_slot[[i]]
	lo_bound <- lo
	hi_bound <- colSums(rbind(mid, lo))
	t <- time[[i]]
	lo_df <- data.frame(t, lo_bound)
	hi_df <- data.frame(t, hi_bound)
	print(sprintf('Beginning Low linear computations for cluster %d.', i))
	lo_line <- lm(lo_bound~t, lo_df)
	print(sprintf('Beginning Low linear regression computations for cluster %d.', i))
	hi_line <- lm(hi_bound~t, hi_df)
	print(sprintf('Beginning Low LOESS computations for cluster %d.', i))
	lo_loess <- loess(lo_bound~t, lo_df)
	print(sprintf('Beginning High LOESS computations for cluster %d.', i))
	hi_loess <- loess(hi_bound~t, hi_df)
	print(sprintf('Rendering linear regression graph for cluster %d...', i))
	pdf(file=sprintf('visuals/trajectories/cluster_%d_linear.pdf', i), height=10, width=10)
	plot.new()
	par(mar=c(5.1, 4.1, 4.1, 8.1), xpd=TRUE)
	title(main=sprintf('Cluster %d Linear Trajectory Model', i), xlab='Time Series Progression', ylab='Percent Investment')
	axis(1)
	axis(2, at=seq(0, 1, by=0.2), labels=paste(100*seq(0, 1, by=0.2), '%'))
	lo_coeff <- unname(lo_line$coefficients)
	hi_coeff <- unname(hi_line$coefficients)
	x_val <- 0:1
	lo_y <- colSums(rbind(0:1*lo_coeff[2], c(lo_coeff[1], lo_coeff[1])))
	hi_y <- colSums(rbind(0:1*hi_coeff[2], c(hi_coeff[1], hi_coeff[1])))
	lines(0:1, lo_y)
	lines(0:1, hi_y)
	polygon(c(x_val, rev(x_val)), c(hi_y, rev(lo_y)), col='green')
	polygon(c(x_val, rev(x_val)), c(lo_y, c(0, 0)), col='red')
	polygon(c(x_val, rev(x_val)), c(c(1, 1), rev(hi_y)), col='blue')
	legend('top', inset=c(0, -0.025), fill=c('red', 'green', 'blue'), cex=0.75, legend=c('Low', 'Mid', 'High'), horiz=TRUE, title='Slot')
	dev.off()
	print(sprintf('Rendering LOESS graph for cluster %d...', i))
	pdf(file=sprintf('visuals/trajectories/cluster_%d_loess.pdf', i), height=10, width=10)
	plot.new()
	par(mar=c(5.1, 4.1, 4.1, 8.1), xpd=TRUE)
	title(main=sprintf('Cluster %d LOESS Trajectory Model', i), xlab='Time Series Progression', ylab='Percent Investment')
	axis(1)
	axis(2, at=seq(0, 1, by=0.2), labels=paste(100*seq(0, 1, by=0.2), '%'))
	x_val <- seq(0, 1, by=0.05)
	lo_loess <- loess(lo_bound~t, lo_df)
	hi_loess <- loess(hi_bound~t, hi_df)
	lo_y <- predict(lo_loess, x_val)
	hi_y <- predict(hi_loess, x_val)
	lines(x_val, lo_y)
	lines(x_val, hi_y)
	polygon(c(x_val, rev(x_val)), c(hi_y, rev(lo_y)), col='green')
	polygon(c(x_val, c(1, 0)), c(lo_y, c(0, 0)), col='red')
	polygon(c(c(0, 1), rev(x_val)), c(c(1, 1), rev(hi_y)), col='blue')
	legend('top', inset=c(0, -0.025), fill=c('red', 'green', 'blue'), cex=0.75, legend=c('Low', 'Mid', 'High'), horiz=TRUE, title='Slot')
	dev.off()
}

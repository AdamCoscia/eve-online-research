# Creates filled area plots for overall average investment percentages
#
# Utilizes the stringr library
#
# Created By: Nicholas Marina
# Created On: 8/1/19
# Last Updated: 8/16/19

library(stringr)

cluster_stats <- read.csv(file='data/cluster_stats.csv')

lo <- cluster_stats$low_avg
mid <- cluster_stats$mid_avg
hi <- cluster_stats$high_avg
kd <- cluster_stats$kd_avg
n_clusters <- length(lo)




jpeg(file='visuals/trajectories/average_investments.jpg', height=4800, width=4800)
par(mfrow=c(2, 2))
for(i in 1:n_clusters){
	plot.new()
	axis(2, at=seq(0, 1, by=0.2), labels=paste(100*seq(0, 1, by=0.2), '%'), cex.axis=4)
	title(main=sprintf('Cluster %i (Average K/D = %f)', i, kd[i]), cex.main=6)
	lo_bound <- lo[i]
	hi_bound <- lo[i] + mid[i]
	polygon(c(0, 1, 1, 0), c(lo_bound, lo_bound, 0, 0), col='red')
	text(0.192, lo_bound-0.03, sprintf('Low Slot Investment = %f %s', 100*lo[i], '%'), cex=5) 
	polygon(c(0, 1, 1, 0), c(hi_bound, hi_bound, lo_bound, lo_bound), col='green')
	text(0.19, hi_bound-0.03, sprintf('Mid Slot Investment = %f %s', 100*mid[i], '%'), cex=5) 
	polygon(c(0, 1, 1, 0), c(1, 1, hi_bound, hi_bound), col='cyan')
	text(0.193, 0.97, sprintf('High Slot Investment = %f %s', 100*hi[i], '%'), cex=5) 
}
text(-0.75, 1.25, 'Cluster Average Investments',cex=30, font=2)
dev.off()

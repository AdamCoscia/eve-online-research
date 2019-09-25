library(stats)

x <- c(0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 4, 5)
y <- c(1.1, 0.7, 1.4, 1.9, 3.5, 4.1, 8.3, 7.4, 13.5, 14.7, 13.9, 21.5)
model <- loess(y ~ x)
df <- data.frame(x=seq(0, 5, by=0.2))
df$y <- predict(model, seq(0, 5, by=0.2))
df

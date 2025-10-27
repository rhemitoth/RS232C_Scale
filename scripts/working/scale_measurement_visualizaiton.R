## ---------------------------
##
## Script name: Visualize scale weights
##
## Author: Rhemi Toth
##
## Date Created: 2025-09-08
##
## Email: rhemitoth@g.harvard.edu
##
## ---------------------------
##
## Notes:
##   
##
## ---------------------------

rm(list = ls())


# Load Packages -----------------------------------------------------------

library(tidyverse)

# Load data ---------------------------------------------------------------

weights <- read_csv("/Users/rhemitoth/Documents/PhD/Cembra/RS232C_Scale/data/scale_weights.csv")


# Compute delta -----------------------------------------------------------

weights <- weights %>%
  mutate(change_since_t0 = Gross - weights$Gross[1],
         weight_diff = Gross - lag(Gross))%>%
  filter(Gross <= 60)

# Change Since T0 Plot ----------------------------------------------------

ggplot(weights, aes(x = Timestamp, y = change_since_t0))+
  geom_line(color = "cornflowerblue")+
  geom_point(color = "cornflowerblue", size = 2)+
  labs(x = "Time",
       y = "kg",
       title = "Change in mass since T0")+
  theme_bw()

ggplot(weights, aes(x = Timestamp, y = change_since_t0))+
  geom_line(color = "cornflowerblue")+
  geom_point(color = "cornflowerblue", size = 2)+
  labs(x = "Time",
       y = "kg",
       title = "Change in mass since T0")+
  theme_bw()+
  facet_wrap(~date(Timestamp), scales = "free_x")


# Raw weight --------------------------------------------------------------

ggplot(weights, aes(x = Timestamp, y = Gross))+
  geom_line(color = "cornflowerblue")+
  geom_point(color = "cornflowerblue", size = 2)+
  labs(x = "Time",
       y = "kg",
       title = "Body Mass Over Time")+
  theme_bw()

ggplot(weights, aes(x = Timestamp, y = Gross))+
  geom_line(color = "cornflowerblue")+
  geom_point(color = "cornflowerblue", size = 2)+
  labs(x = "Time",
       y = "kg",
       title = "Change in mass over time")+
  theme_bw()+
  facet_wrap(~date(Timestamp), scales = "free_x")


library(tidyverse)
library(ggplot2)


#####################################################
###################### Q1 ###########################
#####################################################

library(tidyverse)
library(dplyr)
library(lubridate)

reversal <- x <- data.frame(cbind(c("Costco", "Trader Joe's", "Publix", "Starbucks", "Kohl's", "Home Depot", "Target", "CVS", "Chipotle Mexican Grill", "Meijer", "Walmart", "Best Buy", "Macy's", "Dollar General", "Aldi", "BJ's Wholesale Club", "Walgreens", "Lowe's", "Whole Foods", "Wegmans", "Giant Company", "Kroger", "McDonald's", "Gap", "Amazon", "Giant Eagle"), c("2021-05-14", "2021-05-14", "2021-05-15", "2021-05-17", "2021-05-17", "2021-05-17", "2021-05-17", "2021-05-17", "2021-05-17", "2021-05-17", "2021-05-18", "2021-05-18", "2021-05-18", "2021-05-18", "2021-05-18", "2021-05-18", "2021-05-19", "2021-05-19", "2021-05-19", "2021-05-19", "2021-05-19", "2021-05-20", "2021-05-21", "2021-05-21", "2021-05-24", "2021-05-24")))

reversal <- reversal %>%
  rename("company_name" = X1) %>%
  rename("date_of_reversal" = X2)

class(reversal$date_of_reversal)
reversal <- reversal %>%
  mutate(date_of_reversal = ymd(date_of_reversal))
class(reversal$date_of_reversal)

write_csv(reversal, "mask_requirement_reversal.csv")



#####################################################
###################### Q2 ###########################
#####################################################

walmart <- read_csv("retail_data_export_w_fips.csv")
walmart_avfoot <- walmart %>%
  group_by(dayofmonth, month) %>%
  summarise(avfoot = mean(daily_visitors,na.rm = TRUE))
walmart_avfoot <- walmart_avfoot[-c(1:3),]

g1 <- ggplot(data = walmart_avfoot, aes(x = dayofmonth, y = avfoot)) +
  theme_classic() +
  geom_line(color = "dodgerblue3",
            size = 0.8) +
  geom_point(color = "dodgerblue4",
             size = 1.6) +
  geom_vline(aes(xintercept=median(dayofmonth)+0.5),
             linetype="dashed",
             color = "firebrick3",
             size = 1.0) +
  scale_x_continuous(breaks = seq(4, 31, 1)) +
  labs(
    title="Average Daily Foot Traffic in Walmarts (May 4-May31, 2021)",
    y="Average Daily Foot Traffic (All US Stores)",
    x="Day of Month (May 2021)"
  ) +
  theme(axis.title.x = element_text(size = 11),
        axis.title.y = element_text(size = 11),
        plot.title = element_text(size = 13, hjust = 0.5)) +
  annotate("text", x = 17.7, y = 178, label = "Mask Requirements Reversed, May 18",
           family = "serif", fontface = "italic", colour = "darkred", size = 4)

ggsave("g1.png",width = 16,height = 10,units = "cm",dpi = 1000)



#####################################################
###################### Q3 ###########################
#####################################################

walmart_footstat <- walmart %>%
  group_by(STATEFP, dayofmonth, month) %>%
  summarise(avfoot = mean(daily_visitors, na.rm = TRUE))

walmart_footstat <- walmart_footstat[walmart_footstat$dayofmonth > 3,]

############# By State #################

walmart_footstat <- walmart_footstat %>%
  mutate (state_name = case_when(
    STATEFP == 1 ~ "Alabama", STATEFP == 2 ~ "Alaska", STATEFP == 4 ~ "Arizona", STATEFP == 5 ~ "Arkansas", STATEFP == 6 ~ "California", STATEFP == 8 ~ "Colorado", STATEFP == 9 ~ "Connecticut", STATEFP == 10 ~ "Delaware", STATEFP == 11 ~ "District of Columbia", STATEFP == 12 ~ "Florida", STATEFP == 13 ~ "Georgia", STATEFP == 15 ~ "Hawaii", STATEFP == 16 ~ "Idaho", STATEFP == 17 ~ "Illinois", STATEFP == 18 ~ "Indiana", STATEFP == 19 ~ "Iowa", STATEFP == 20 ~ "Kansas", STATEFP == 21 ~ "Kentucky", STATEFP == 22 ~ "Louisiana", STATEFP == 23 ~ "Maine", STATEFP == 24 ~ "Maryland", STATEFP == 25 ~ "Massachusetts", STATEFP == 26 ~ "Michigan", STATEFP == 27 ~ "Minnesota", STATEFP == 28 ~ "Mississippi", STATEFP == 29 ~ "Missouri", STATEFP == 30 ~ "Montana", STATEFP == 31 ~ "Nebraska", STATEFP == 32 ~ "Nevada", STATEFP == 33 ~ "New Hampshire", STATEFP == 34 ~ "New Jersey", STATEFP == 35 ~ "New Mexico", STATEFP == 36 ~ "New York", STATEFP == 37 ~ "North Carolina", STATEFP == 38 ~ "North Dakota", STATEFP == 39 ~ "Ohio", STATEFP == 40 ~ "Oklahoma", STATEFP == 41 ~ "Oregon", STATEFP == 42 ~ "Pennsylvania", STATEFP == 44 ~ "Rhode Island", STATEFP == 45 ~ "South Carolina", STATEFP == 46 ~ "South Dakota", STATEFP == 47 ~ "Tennessee", STATEFP == 48 ~ "Texas", STATEFP == 49 ~ "Utah", STATEFP == 50 ~ "Vermont", STATEFP == 51 ~ "Virginia", STATEFP == 53 ~ "Washington", STATEFP == 54 ~ "West Virginia", STATEFP == 55 ~ "Wisconsin", STATEFP == 56 ~ "Wyoming", STATEFP == 60 ~ "American Samoa", STATEFP == 66 ~ "Guam", STATEFP == 69 ~ "Northern Mariana Islands", STATEFP == 72 ~ "Puerto Rico", STATEFP == 78 ~ "Virgin Islands"))

g3 <- ggplot() +
  geom_line(data = walmart_footstat,
            aes(x = dayofmonth, y = avfoot, color = statename),
            alpha = 0.5, size = 0.5) +
  geom_vline(data = walmart_footstat,
             aes(xintercept=median(dayofmonth)+0.5),
             linetype="dashed",
             color = "firebrick3",
             size = 1.0) +
  scale_x_continuous(breaks = seq(4, 31, 1)) +
  labs(
    title="Average Daily Foot Traffic in Walmarts by States (May 4-May 31, 2021)",
    y="Average Daily Foot Traffic",
    x="Day of Month (May 2021)",
    color = "State Name"
  ) +
  theme_classic() +
  theme(axis.title.x = element_text(size = 18),
        axis.title.y = element_text(size = 18),
        plot.title = element_text(size = 20, hjust = 0.02),
        legend.title = element_text(size = 9)) +
  annotate("text", x = 17.7, y = 310, label = "Mask Requirements Reversed, May 18",
           family = "serif", fontface = "italic", colour = "darkred", size = 4)

ggsave("g3.png",width = 26,height = 14,units = "cm",dpi = 1000)

########## Illinois (Required) ###########

walmart_il <- walmart_footstat[walmart_footstat$STATEFP == 17,]

g2 <- ggplot() +
  geom_line(data = walmart_footstat,
            aes(x = dayofmonth, y = avfoot, group= STATEFP),
            alpha = 0.5, color = "cornflowerblue", size = 0.3) +
  geom_line(data = walmart_il,
            aes(x = dayofmonth, y = avfoot),
            color = "orangered1",
            size = 0.5) +
  geom_vline(data = walmart_footstat,
             aes(xintercept=median(dayofmonth)+0.5),
             linetype="dashed",
             color = "firebrick3",
             size = 1.0) +
  scale_x_continuous(breaks = seq(4, 31, 1)) +
  labs(
    title="Average Daily Foot Traffic in Walmarts by States (May 4-May 31, 2021)",
    y="Average Daily Foot Traffic",
    x="Day of Month (May 2021)"
  ) +
  theme_classic() +
  theme(axis.title.x = element_text(size = 11),
        axis.title.y = element_text(size = 11),
        plot.title = element_text(size = 11, hjust = 0.5)) +
  annotate("text", x = 17.7, y = 310, label = "Mask Requirements Reversed, May 18",
           family = "serif", fontface = "italic", colour = "darkred", size = 4)

ggsave("g2.png",width = 14,height = 10,units = "cm",dpi = 1000)

########## DC (lifted) ###########

walmart_dc <- walmart_footstat[walmart_footstat$STATEFP == 11,]

g4 <- ggplot() +
  geom_line(data = walmart_footstat,
            aes(x = dayofmonth, y = avfoot, group= STATEFP),
            alpha = 0.5, color = "cornflowerblue", size = 0.3) +
  geom_line(data = walmart_dc,
            aes(x = dayofmonth, y = avfoot),
            color = "darkorchid2",
            size = 0.5) +
  geom_vline(data = walmart_footstat,
             aes(xintercept=median(dayofmonth)+0.5),
             linetype="dashed",
             color = "firebrick3",
             size = 1.0) +
  scale_x_continuous(breaks = seq(4, 31, 1)) +
  labs(
    title="Average Daily Foot Traffic in Walmarts by States (May 4-May 31, 2021)",
    y="Average Daily Foot Traffic",
    x="Day of Month (May 2021)"
  ) +
  theme_classic() +
  theme(axis.title.x = element_text(size = 11),
        axis.title.y = element_text(size = 11),
        plot.title = element_text(size = 11, hjust = 0.5)) +
  annotate("text", x = 17.7, y = 310, label = "Mask Requirements Reversed, May 18",
           family = "serif", fontface = "italic", colour = "darkred", size = 4)

ggsave("g4.png",width = 14,height = 10,units = "cm",dpi = 1000)

########## Maine (lifted) ###########

walmart_ma <- walmart_footstat[walmart_footstat$STATEFP == 23,]

g5 <- ggplot() +
  geom_line(data = walmart_footstat,
            aes(x = dayofmonth, y = avfoot, group= STATEFP),
            alpha = 0.5, color = "cornflowerblue", size = 0.3) +
  geom_line(data = walmart_ma,
            aes(x = dayofmonth, y = avfoot),
            color = "chartreuse3",
            size = 0.5) +
  geom_vline(data = walmart_footstat,
             aes(xintercept=median(dayofmonth)+0.5),
             linetype="dashed",
             color = "firebrick3",
             size = 1.0) +
  scale_x_continuous(breaks = seq(4, 31, 1)) +
  labs(
    title="Average Daily Foot Traffic in Walmarts by States (May 4-May 31, 2021)",
    y="Average Daily Foot Traffic",
    x="Day of Month (May 2021)"
  ) +
  theme_classic() +
  theme(axis.title.x = element_text(size = 11),
        axis.title.y = element_text(size = 11),
        plot.title = element_text(size = 13, hjust = 0.5)) +
  annotate("text", x = 17.7, y = 310, label = "Mask Requirements Reversed, May 18",
           family = "serif", fontface = "italic", colour = "darkred", size = 4)

ggsave("g5.png",width = 16,height = 9.5,units = "cm",dpi = 1000)



###################### Q4 ###########################
#####################################################

walmart_county <- walmart[walmart$dayofmonth > 3,]
walmart_county <- walmart[complete.cases(walmart[,3]),]
walmart_county <- walmart_county %>%
  mutate(post = case_when(
    dayofmonth < 18 ~ 0,
    dayofmonth > 17 ~ 1
  ))
reg1 <- lm(daily_visitors ~ post, data = walmart_county)
summary(reg1)
coef(reg1)



###################### Q5 ###########################
#####################################################
vote2020 <- read_csv("vote2020.csv")
vaccine <- read_csv("county_week26_data_fixed.csv")
vaccine <- vaccine %>%
  mutate(fips = `FIPS Code`)
vote2020 <-vote2020 %>%
  mutate(fips = county_fips)
walmart_county <- walmart[walmart$dayofmonth > 3,]
walmart_county <- walmart[complete.cases(walmart[,3]),]
walmart_joined <- left_join(walmart_county, vote2020, by = "fips")
walmart_joined <- left_join(walmart_joined, vaccine, by = "fips")

walmart_joined <- walmart_joined %>%
  mutate(trump_vs = per_gop *100)
walmart_joined <- walmart_joined %>%
  mutate(vaccine_hes = `Estimated hesitant` *100)
walmart_joined <- walmart_joined %>%
  mutate(post = case_when(
    dayofmonth < 18 ~ 0,
    dayofmonth > 17 ~ 1
  ))

library(foreign)
write.dta(walmart_joined, file = "walmart_vote_vaccine.dta")

################ Regression ##################

reg2a <- walmart_joined %>%
  lm(daily_visitors ~ post + trump_vs + post*trump_vs, data = .)
summary(reg2a)
coef(reg2a)

reg2b <- walmart_joined %>%
  lm(daily_visitors ~ post + vaccine_hes + post*vaccine_hes, data = .)
summary(reg2b)
coef(reg2b)

reg2c <- walmart_joined %>%
  lm(daily_visitors ~ post + trump_vs + vaccine_hes + post*trump_vs + post*vaccine_hes + post*trump_vs*vaccine_hes, data = .)
summary(reg2c)
coef(reg2c)

################# Also did regression using STATA to check the accuracy #################
## Here is my Stata code
## gen post_trump = post * trump_vs
## gen post_vaccine = post * vaccine_hes
## gen post_trump_vaccine = post * trump_vs * vaccine_hes
## gen dem_vs = per_dem * 100
## gen post_dem = post * dem_vs
## gen post_dem_vaccine = post * dem_vs * vaccine_hes

## reg daily_visitors post
## est store r1
## outreg2 [r1] using out.tex, replace

## reg daily_visitors post trump_vs post_trump
## est store r2a
## outreg2 [r2a] using out.tex, append

## reg daily_visitors post vaccine_hes post_vaccine
## est store r2b
## outreg2 [r2b] using out.tex, append

## reg daily_visitors post trump_vs vaccine_hes post_trump post_vaccine post_trump_vaccine
## est store r2c
## outreg2 [r2c] using out.tex, append

## reg daily_visitors post dem_vs post_dem
## est store r3a
## outreg2 [r3a] using out.tex, append

## reg daily_visitors post dem_vs vaccine_hes post_dem post_vaccine post_dem_vaccine
## est store r3b
## outreg2 [r3b] using out.tex, append

################# Some additional data visualizations ################
################# spatial map ####################

library(sf)
library(tidycensus)
library("ggplot2")


county_gdf <- st_read("tl_2016_us_county.shp")
county_gdf <- st_transform(county_gdf, 4326)
us_map <- fortify(county_gdf, region = "fips")


retail <- read_csv("retail_data_export_w_fips.csv")
retail <- st_as_sf(
  retail,
  coords = c("INTPTLON", "INTPTLAT"),
  crs = 4326)

retail_merged <- st_join(
  retail, 
  county_gdf,  
  join = st_within)
retail_merged <- retail_merged %>%
  mutate(county_fips = fips.y)

vote2020 <- read_csv("vote2020.csv")
walmart_retail <- retail_merged[retail_merged$dayofmonth > 3,]
walmart_retail<- left_join(walmart_retail, vote2020, by = "county_fips")
walmart_retail <- walmart_retail %>%
  mutate(trump_vs = per_gop *100)

walmart_retail <- walmart_retail %>%
  mutate(gop_rate = case_when(
    trump_vs<20 ~ "0~25%",
    trump_vs<50 &trump_vs >= 25 ~ "25-50%",
    trump_vs<75 &trump_vs >= 50 ~ "50~75%",
    trump_vs<100 &trump_vs >= 75 ~ "75-100%"
  ))

################# gop_rate ##################

map1 <- ggplot() +
  geom_sf(data = walmart_retail,aes(color = gop_rate)) +
  scale_color_brewer(palette = "Reds") +
  guides(color=guide_legend(reverse=TRUE,title="gop_rate")) + 
  theme(panel.grid = element_blank(),
        panel.background = element_blank(),
        axis.text = element_blank(),
        axis.ticks = element_blank(),
        axis.title = element_blank(),
        legend.position = c(0.18,0.75),
        legend.text.align=1) +
  theme_bw()  
ggsave("map1.png",width = 14,height = 10,units = "cm",dpi = 1000)

################# vaccine_hes ##################

retail <- read_csv("retail_data_export_w_fips.csv")
retail <- st_as_sf(
  retail,
  coords = c("INTPTLON", "INTPTLAT"),
  crs = 4326)

retail_merged <- st_join(
  retail, 
  county_gdf,  
  join = st_within)
retail_merged <- retail_merged %>%
  mutate(fips = fips.y)

vaccine <- read_csv("county_week26_data_fixed.csv")
vaccine <- vaccine %>%
  mutate(fips = `FIPS Code`)
walmart_retail <- retail_merged[retail_merged$dayofmonth > 3,]
walmart_joined <- left_join(walmart_retail, vaccine, by = "fips")
walmart_joined <- walmart_joined %>%
  mutate(vaccine_hes = `Estimated hesitant` *100)

map2 <- ggplot() +
  geom_sf(data = walmart_joined,aes(color = vaccine_hes)) +
  scale_color_distiller(palette = "Blues") +
  guides(color=guide_legend(reverse=TRUE,title="vaccine_hes")) + 
  theme(panel.grid = element_blank(),
        panel.background = element_blank(),
        axis.text = element_blank(),
        axis.ticks = element_blank(),
        axis.title = element_blank(),
        legend.position = c(0.18,0.75),
        legend.text.align=1) +
  theme_bw()  
ggsave("map2.png",width = 14,height = 10,units = "cm",dpi = 1000)



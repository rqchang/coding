# -*- coding: utf-8 -*-
"""
Spyder Editor

Author: Ruiquan
Subject: census data prediction

"""
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats as stats
import statsmodels.api as sm

# Display all columns in pandas
pd.set_option('display.max_columns', None)

# Load the data
df = pd.read_csv('usa_00001.csv')
df.head()

# Change the categorical measurement of education (educd) to a continuous variable (educdc)
## Check unique values in EDUCD
df['EDUCD'].unique()
## Using the crosswork.csv
crosswalk = pd.read_csv('PPHA_30545_MP01-Crosswalk.csv')
## Transform data to convert to dictionary
crosswalk = crosswalk.set_index('educd').T
crosswalk
## convert crosswoalk to dictionary
crosswalk.to_dict('list')
## Duplicate the EDUCD column to create EDUCDC column
df['EDUCDC'] = df['EDUCD']
## Map values from the dictionary we created
df= df.replace({'EDUCDC': crosswalk})
## Verify
df[['EDUCD', 'EDUCDC']].head(10)
## Merge 'educdc' to the dataset
crosswalk = pd.read_csv('PPHA_30545_MP01-Crosswalk.csv') 
df = df.merge(crosswalk, left_on='EDUCD', right_on='educd')
df.head()

# Dummy variables
## Check the unqique values
df['educd'].unique()
## hsdip == 1 when educd == 71, 63, 81, 85, 64
df['hsdip'] = np.where((df['educd'] == 71) | (df['educd'] == 63) | (df['educd'] == 81)
                       | (df['educd'] == 85) | (df['educd'] == 64), 1, 0)
df.loc[df['hsdip']== 1]
## coldip == 1 when educd == 114, 101, 116, 115
df['coldip'] = np.where((df['educd'] == 114) | (df['educd'] == 101) | (df['educd'] == 116)
                       | (df['educd'] == 115), 1, 0)
df.loc[df['coldip']== 1]
## white == 1 when RACE == 1
df['RACE'].unique()
df['white'] = np.where((df['RACE'] == 1), 1, 0)
## black == 1 when RACE == 2
df['black'] = np.where((df['RACE'] == 2), 1, 0)
## hispanic == 1 when HISPAN == 1, 2, 3, 4
df['HISPAN'].unique()
df['hispanic'] = np.where((df['HISPAN'] == 1) | (df['HISPAN'] == 2) 
                          | (df['HISPAN'] == 3) | (df['HISPAN'] == 4), 1, 0)
df.loc[df['hispanic']== 1]
## married == 1 when MARST == 1, 2
df['MARST'].unique()
df['married'] = np.where((df['MARST'] == 1) | (df['MARST'] == 2), 1, 0)
## female ==1 when SEX == 2
df['female'] = np.where((df['SEX'] == 2), 1, 0)
## vet == 1 when VETSTAT == 2
df['VETSTAT'].unique()
df['vet'] = np.where((df['VETSTAT'] == 2), 1, 0)

# Variables and interaction terms
## hsdip_educdc = hsdip * educdc
df['hsdip_educdc'] = df['hsdip'] * df['educdc']
## coldip_educdc = coldip * educdc
df['coldip_educdc'] = df['coldip'] * df['educdc']
## age squared
df['age_sq'] = np.power(df['AGE'], 2)
## lnincome
df = df[df.INCWAGE > 0]
df['ln_incwage'] = np.log(df['INCWAGE'])

# Data analysis
df[['YEAR','INCWAGE','ln_incwage','educdc','female','AGE','age_sq',
    'white','black','hispanic','married','NCHILD','vet','hsdip','coldip',
    'hsdip_educdc','coldip_educdc']].describe().round(3)
## scatter plot ln(incwage) and education
plt.figure(figsize=(12,8))
sns.regplot(y="ln_incwage", x="educdc", data=df, line_kws={"color": "green"})
plt.xlabel("educdc", fontsize=15)
plt.ylabel("ln(incwage)", fontsize=15)
plt.title("Scatter plot of ln(incwage) and educdc", fontsize=20)
## estimate the model:
## 𝑙𝑛(𝑖𝑛𝑐𝑤𝑎𝑔𝑒)=𝛽0+𝛽1𝑒𝑑𝑢𝑐𝑑𝑐+𝛽2𝑓𝑒𝑚𝑎𝑙𝑒+𝛽3𝑎𝑔𝑒+𝛽4𝑎𝑔𝑒𝑠𝑞+𝛽5𝑤ℎ𝑖𝑡𝑒+𝛽6𝑏𝑙𝑎𝑐𝑘+𝛽7ℎ𝑖𝑠𝑝𝑎𝑛𝑖𝑐+𝛽8𝑚𝑎𝑟𝑟𝑖𝑒𝑑+𝛽9𝑛𝑐ℎ𝑖𝑙𝑑+𝛽10𝑣𝑒𝑡+𝜖
import statsmodels.formula.api as smf
model = smf.ols('ln_incwage ~ educdc + female + AGE + age_sq + white + black + hispanic + married + NCHILD + vet', 
                data = df).fit()
model.summary()
## hypothesis test
R_sq = 0.305
n = 7953
q = 10
F = (R_sq/q)/((1-R_sq)/(n-q-1))
aov_table = sm.stats.anova_lm(model, typ=2)
def anova_table(aov):
    aov['mean_sq'] = aov[:]['sum_sq']/aov[:]['df']
    cols = ['sum_sq', 'df', 'mean_sq', 'F', 'PR(>F)']
    aov = aov[cols]
    return aov
anova_table(aov_table).round(4)
## race has no effect on wages
### run unrestricted model with all variables
unres_model = smf.ols('ln_incwage ~ educdc + female + AGE + age_sq + white + black + hispanic + married + NCHILD + vet', 
                      data = df).fit()
ssr_ur = np.sum((unres_model.fittedvalues - df.ln_incwage)**2)
ssr_ur
#### run restricted model
res_model = smf.ols('ln_incwage ~ educdc + female + AGE + age_sq + married + NCHILD + vet', 
                    data = df).fit()
ssr_r = np.sum((res_model.fittedvalues - df.ln_incwage)**2)
ssr_r
### q = 3, n = 7953, k = 10
q = 3
n = 7953
k = 10
F = ((ssr_r - ssr_ur)/q)/(ssr_ur/(n-k-1))
F
### Critical value
cv = stats.f.ppf(q=1-.05, dfn=q, dfd=(n-k-1))
cv
### Verify the calculation
formula = 'ln_incwage ~ educdc + female + AGE + age_sq + white + black + hispanic + married + NCHILD + vet'
f_model = smf.ols(formula, df).fit()
hypotheses = '(white = black = hispanic=0)'
f_test = f_model.f_test(hypotheses)
print(f_test)

# Graph ln(incwage) and education
df1 = df[(df['hsdip'] == 0) & (df['coldip'] == 0)]
df2 = df[(df['hsdip'] == 1)]
df3 = df[(df['coldip'] == 1)]
## Three distinct linear fit lines indicating different degree levels
plt.figure(figsize=(12,8))
sns.regplot(y="ln_incwage", x="educdc", data=df1, 
            line_kws={"color": "blue"}, marker='+')
sns.regplot(y="ln_incwage", x="educdc", data=df2, 
            line_kws={"color": "orange"}, marker='+')
sns.regplot(y="ln_incwage", x="educdc", data=df3, 
            line_kws={"color": "green"}, marker='+')
plt.title('Relationship between Education and ln(Income)', fontsize=20)
plt.legend(labels=['No High School Diploma', 'High School Diploma', 'College Degree'], fontsize=10)
plt.xlabel('educdc', fontsize=15)
plt.ylabel('ln(incwage)', fontsize=15)

# Model that allows the returns to education to vary by degree acquired
## 𝑙𝑛(𝑖𝑛𝑐𝑤𝑎𝑔𝑒)=𝛽0+𝛽1𝑒𝑑𝑢𝑐𝑑𝑐+𝛽2𝟙[ℎ𝑠𝑑𝑖𝑝]+𝛽3𝟙[𝑐𝑜𝑙𝑑𝑖𝑝]+𝛽4𝑓𝑒𝑚𝑎𝑙𝑒+𝛽5𝑎𝑔𝑒+𝛽6𝑎𝑔𝑒𝑠𝑞+𝛽7𝑤ℎ𝑖𝑡𝑒+ 
## 𝛽8𝑏𝑙𝑎𝑐𝑘+𝛽9ℎ𝑖𝑠𝑝𝑎𝑛𝑖𝑐+𝛽10𝑚𝑎𝑟𝑟𝑖𝑒𝑑+𝛽11𝑛𝑐ℎ𝑖𝑙𝑑+𝛽12𝑣𝑒𝑡+𝛽13ℎ𝑠𝑑𝑖𝑝∗𝑒𝑑𝑢𝑐𝑑𝑐+𝛽14𝑐𝑜𝑙𝑑𝑖𝑝∗𝑒𝑑𝑢𝑐𝑑𝑐+𝜖
pred_model = smf.ols('ln_incwage ~ educdc + hsdip + coldip + female + AGE + age_sq + white + black + hispanic + married + NCHILD + vet + hsdip_educdc + coldip_educdc', data = df).fit()
pred_model.summary()
ia1 = {'educdc': [12], 'AGE': [22], 'female': [1], 'hsdip': [1], 
       'coldip': [0], 'age_sq': [484], 'white': [0], 'black': [0],
       'hispanic': [0], 'married': [0], 'NCHILD': [0], 'vet': [0],
       'hsdip_educdc': [12], 'coldip_educdc': [0]}
##　predicted ln(incwage) for individual with a highe school diploma　
pa1 = pd.DataFrame(data=ia1)
pa1
prediction_a1 = pred_model.get_prediction(pa1)
prediction_a1.summary_frame(alpha=0.05)
## college diploma
ia2 = {'educdc': [16], 'AGE': [22], 'female': [1], 'hsdip': [0],
       'coldip': [1], 'age_sq': [484], 'white': [0], 'black': [0],
       'hispanic': [0], 'married': [0], 'NCHILD': [0], 'vet': [0],
       'hsdip_educdc': [0], 'coldip_educdc': [16]}
pa2 = pd.DataFrame(data=ia2)
pa2
prediction_a2 = pred_model.get_prediction(pa2)
prediction_a2.summary_frame(alpha=0.05)


# -*- coding: utf-8 -*-
"""
@author: Ruiquan
@subject: covid vaccine prediction
"""

import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression,LinearRegression, Lasso
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import Ridge
from sklearn.linear_model import Lasso

import matplotlib.pyplot as plt
import seaborn as sns

# Data cleaning
data = pd.read_csv("Covid002.csv", engine='python', encoding='latin1')
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
variables_df = pd.read_excel('Variable Description.xlsx')

## Filter Opportunity Insights
grouped = variables_df.groupby('Source')['Variable']
group1 = grouped.get_group('Opportunity Insights')
group1 = group1.values.tolist()

## Filter PM COVID
group2 = grouped.get_group('PM_COVID')
group2 = group2.values.tolist()

## Subset the dataset
general = ['county', 'state', 'deathspc'] 
var = general + group1 + group2
covid = data[var]
covid.head(5)

## Drop all nan observations
covid = covid.dropna(axis=0, how='any')
dummies = pd.get_dummies(covid['state'])
dummies.shape
## Join the encoded dummies
covid = covid.drop('state',axis = 1)
covid = covid.join(dummies)
covid.head()

## Split the sample
X = covid.drop(['county', 'deathspc'], axis = 1)
y = covid['deathspc']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=25)


# OLS estimator
ols_model = LinearRegression().fit(X_train, y_train)

## Get the MSE in training sets
y_pred_train = ols_model.predict(X_train)
mse_train = mean_squared_error(y_train, y_pred_train)

## Get the MSE in validation sets
y_pred_valid = ols_model.predict(X_test)
mse_valid = mean_squared_error(y_test, y_pred_valid)
### overfitting: ols_model.score(X_train, y_train) > ols_model.score(X_test, y_test)


# RR & Lasso
## Define range of values of lambda
## a: [-2,2]
## lambda = b = 10^a: [0.01,100]
a = np.linspace(start=-2, stop=2, num=100)
b = 10**a
alpha_param = b
## Create a parameters grid
param_grid = [{'alpha': alpha_param }]

## Ridge
ridge = Ridge(normalize = True)
## cv = 10
grid_search_ridge = GridSearchCV(ridge, param_grid, cv = 10, scoring = 'neg_mean_squared_error')
grid_search_ridge.fit(X_train, y_train)
## Calculate a vector of mean and standard deviation values for each lambda
def vector_values(grid_search, trials):
    mean_vec = np.zeros(trials)
    std_vec = np.zeros(trials)
    i = 0
    final = grid_search.cv_results_    
    for mean_score, std_score in zip(final["mean_test_score"], final["std_test_score"]):
        mean_vec[i] = - mean_score
        std_vec[i] = std_score
        i = i+1 
    return mean_vec, std_vec
## Test error for each Ridge model
mean_vec, std_vec = vector_values(grid_search_ridge, 100)

## Lasso
lasso = Lasso(normalize = True)
## cv = 10
grid_search_lasso = GridSearchCV(lasso, param_grid, cv = 10, scoring = 'neg_mean_squared_error')
grid_search_lasso.fit(X_train, y_train)
## Test error for each Lasso model
mean_vec_l, std_vec_l = vector_values(grid_search_lasso, 100)

## Plot 10FCV estimates of test errors
## MSE vs. log(lambda) = a: [-2,2]
plt.figure(figsize=(12,10))
plt.title('Ridge Regression', fontsize=16)
plt.plot(np.log(alpha_param), mean_vec)
plt.errorbar(np.log(alpha_param), mean_vec, yerr = std_vec)
plt.ylabel("MSE", fontsize=16)
plt.xlabel("log(lambda)", fontsize=16)
plt.show()

plt.figure(figsize=(12,10))
plt.title('Lasso Regression', fontsize=16)
plt.plot(np.log(alpha_param), mean_vec_l)
plt.errorbar(np.log(alpha_param), mean_vec_l, yerr = std_vec)
plt.ylabel("MSE", fontsize=16)
plt.xlabel("log(lambda)", fontsize=16)
plt.show()

## Find the lowest MSE score
min(mean_vec)
min(mean_vec_l)
## Optimal lambda: one that minimizes MSE
lambda_r = alpha_param[np.where(mean_vec == min(mean_vec))][0]
lambda_l = alpha_param[np.where(mean_vec_l == min(mean_vec_l))][0]

## Re-estimate
## Re-esitimate the Ridge model using lambda_r
ridge_model = Ridge(alpha=lambda_r, fit_intercept=True, 
                    normalize=True, max_iter=1000000).fit(X_train, y_train)
df1 = pd.DataFrame({'feature': X.columns, 'coefficient': ridge_model.coef_})
df1.insert(loc=0, column='index1', value=np.arange(len(df1)))

plt.figure(figsize=(16,12))
ax = sns.barplot(x='index1', y='coefficient', color="#4169E1", data=df1)
ax.set_title('Coefficient of Ridge model with lambda_r', fontsize=16)
plt.show()

## Re-esitimate the Lasso model using lambda_l
lasso_model = Lasso(alpha=lambda_l, fit_intercept=True, 
                    normalize=True, max_iter=1000000).fit(X_train, y_train)
df2 = pd.DataFrame({'feature': X.columns, 'coefficient': lasso_model.coef_})
## Drop the predictors that coefficient = 0
df2 = df2[df2['coefficient'] != 0]
df2.insert(loc=0, column='index1', value=np.arange(len(df2)))

plt.figure(figsize=(16,12))
ax = sns.barplot(x='index1', y='coefficient', color="#008B8B", data=df2)
ax.set_title('Coefficient of Lasso model with lambda_l', fontsize=16)
plt.show()

## MSE
ridge_model = Ridge(alpha=lambda_r, fit_intercept=True, 
                    normalize=True, max_iter=1000000).fit(X_train, y_train)
ridge_tpre = ridge_model.predict(X_train)
tmse_r = mean_squared_error(y_train, ridge_tpre)
ridge_pre = ridge_model.predict(X_test)
vmse_r = mean_squared_error(y_test, ridge_pre)

lasso_model = Lasso(alpha=lambda_l, fit_intercept=True, 
                    normalize=True, max_iter=1000000).fit(X_train, y_train)
lasso_tpre = lasso_model.predict(X_train)
tmse_l = mean_squared_error(y_train, lasso_tpre)
lasso_pre = lasso_model.predict(X_test)
vmse_l = mean_squared_error(y_test, lasso_pre)

ols_tpre = ols_model.predict(X_train)
tmse_o = mean_squared_error(y_train, ols_tpre)
ols_pre = ols_model.predict(X_test)
vmse_o = mean_squared_error(y_test, ols_pre)
                            

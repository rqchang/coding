# -*- coding: utf-8 -*-
"""
@author: Ruiquan

@subject: tax evasion and audits

"""
import numpy as np
import pandas as pd

from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import pyplot


audit = pd.read_csv('audit.csv')
audit.replace([np.inf, -np.inf], np.nan, inplace=True)
audit.dropna(inplace=True)
audit.describe()


# LPM
x = audit.drop(['Risk'], axis = 1)
y = audit['Risk']
x_train = x.head(388)
y_train = y.head(388)
x_test = x.tail(387)
y_test = y.tail(387)

## LPM regression (>0.5)
lpm = LinearRegression()
lpm.pred = lpm.fit(x_train, y_train).predict(x_test) > 0.5
print(pd.DataFrame(confusion_matrix(y_test, lpm.pred), index=['y=0', 'y=1'], columns=['y_pred=0', 'y_pred=1']))
print('LPM Accuracy:', accuracy_score(y_test, lpm.pred))
print('error rate:', 1-accuracy_score(y_test, lpm.pred))
print('PPV (positive predictive value)(>0.5):', 28/(28+5))

## LPM regression (>0.8)
lpm = LinearRegression()
lpm.pred = lpm.fit(x_train, y_train).predict(x_test) > 0.8
print(pd.DataFrame(confusion_matrix(y_test, lpm.pred), index=['y=0', 'y=1'], columns=['y_pred=0', 'y_pred=1']))
print('LPM Accuracy:', accuracy_score(y_test, lpm.pred))
print('error rate:', 1-accuracy_score(y_test, lpm.pred))
print('PPV (positive predictive value)(>0.8):', 11/(11+0))


# KNN
## k = 1
x_norm = pd.DataFrame(preprocessing.scale(x))
x_norm_train = x_norm.head(388)
x_norm_test = x_norm.tail(387)
x_train = x.head(388)
x_test = x.tail(387)
y_train = y.head(388)
y_test = y.tail(387)

## confusion matrix (normalized)
knn_1_norm = KNeighborsClassifier(n_neighbors = 1)
knn_1_norm.fit(x_norm_train, y_train)
knn_1_norm.pred = knn_1_norm.predict(x_norm_test)
print(pd.DataFrame(confusion_matrix(y_test, knn_1_norm.pred), index=['y=0', 'y=1'], columns=['y_pred=0', 'y_pred=1']))
print('k-NN (normazlied) Accuracy:', accuracy_score(y_test, knn_1_norm.pred))
print('error rate: ', 1-accuracy_score(y_test, knn_1_norm.pred))
print('PPV (positive predictive value):', 81/(81+25))
print('TPR (true positive rate):', 81/(81+1))
## confusion matrix (not normalized)
knn_1 = KNeighborsClassifier(n_neighbors = 1)
knn_1.fit(x_train, y_train)
knn_1.pred = knn_1.predict(x_test)
print(pd.DataFrame(confusion_matrix(y_test, knn_1.pred), index=['y=0', 'y=1'], columns=['y_pred=0', 'y_pred=1']))
print('k-NN (not normalized) Accuracy:', accuracy_score(y_test, knn_1.pred))
print('error rate:', 1-accuracy_score(y_test, knn_1.pred))
print('PPV (positive predictive value):', 70/(70+1))
print('TPR (true positive rate):', 70/(70+12))

## heat plots
grid, axes = plt.subplots(nrows = 1, ncols = 2, figsize = (16, 5))
## normalized
cm_knn_1_norm = confusion_matrix(y_test, knn_1_norm.pred, normalize = 'true')
sns.heatmap(cm_knn_1_norm, annot=True, fmt='.2%', cmap='Blues', ax = axes[0])
axes[0].set(title = "Confusion Matrix with labels (k = 1, normalized)",
           xlabel = 'Predicted Values',
           ylabel = 'Actual Values')

axes[0].xaxis.set_ticklabels(['False','True'])
axes[0].yaxis.set_ticklabels(['False','True'])
## not normalized
cm_knn_1 = confusion_matrix(y_test, knn_1.pred, normalize = 'true')
sns.heatmap(cm_knn_1, annot=True, fmt='.2%', cmap='Blues', ax = axes[1])
axes[1].set(title = "Confusion Matrix with labels (k = 1, not normalized)",
           xlabel = 'Predicted Values',
           ylabel = 'Actual Values')

axes[1].xaxis.set_ticklabels(['False','True'])
axes[1].yaxis.set_ticklabels(['False','True'])

## k = 5
## confusion matrix (normalized)
knn_5_norm = KNeighborsClassifier(n_neighbors = 5)
knn_5_norm.fit(x_norm_train, y_train)
knn_5_norm.pred = knn_5_norm.predict(x_norm_test)
print(pd.DataFrame(confusion_matrix(y_test, knn_5_norm.pred), index=['y=0', 'y=1'], columns=['y_pred=0', 'y_pred=1']))
print('k-NN (normazlied) Accuracy:', accuracy_score(y_test, knn_5_norm.pred))
print('error rate: ', 1-accuracy_score(y_test, knn_5_norm.pred))
print('PPV (positive predictive value):', 79/(79+39))
print('TPR (true positive rate):', 79/(79+3))
## confusion matrix (not normalized)
knn_5 = KNeighborsClassifier(n_neighbors = 5)
knn_5.fit(x_train, y_train)
knn_5.pred = knn_5.predict(x_test)
print(pd.DataFrame(confusion_matrix(y_test, knn_5.pred), index=['y=0', 'y=1'], columns=['y_pred=0', 'y_pred=1']))
print('k-NN (not normalized) Accuracy:', accuracy_score(y_test, knn_5.pred))
print('error rate:', 1-accuracy_score(y_test, knn_5.pred))
print('PPV (positive predictive value):', 58/(58+0))
print('TPR (true positive rate):', 58/(58+24))

## heat plots
## normalized
cm_knn_5_norm = confusion_matrix(y_test, knn_5_norm.pred, normalize = 'true')
sns.heatmap(cm_knn_5_norm, annot=True, fmt='.2%', cmap='Greens', ax = axes[0])
axes[0].set(title = "Confusion Matrix with labels (k = 5, normalized)",
           xlabel = 'Predicted Values',
           ylabel = 'Actual Values')

axes[0].xaxis.set_ticklabels(['False','True'])
axes[0].yaxis.set_ticklabels(['False','True'])
## not normalized
cm_knn_5 = confusion_matrix(y_test, knn_5.pred, normalize = 'true')
sns.heatmap(cm_knn_5, annot=True, fmt='.2%', cmap='Greens', ax = axes[1])
axes[1].set(title = "Confusion Matrix with labels (k = 1, not normalized)",
           xlabel = 'Predicted Values',
           ylabel = 'Actual Values')
axes[1].xaxis.set_ticklabels(['False','True'])

## optimal k by 5FCV
## By 5-fold cross-validation, find the k with the lowest classification error rate
## normalized
from sklearn.model_selection import GridSearchCV, KFold

def odd(n):
    return list(range(1, 2*n, 2))
ks = odd(194)
knni = KNeighborsClassifier()
para = {'n_neighbors':ks}
knn_cv = GridSearchCV(knni, para, cv = KFold(5, random_state=13, shuffle=True))
knn_cv.fit(x_norm, y)
print(knn_cv.best_params_)
print(knn_cv.best_score_)

knni = KNeighborsClassifier()
para = {'n_neighbors':ks}
knn_cv = GridSearchCV(knni, para, cv = KFold(5, random_state=13, shuffle=True))
knn_cv.fit(x, y)
print(knn_cv.best_params_)
print(knn_cv.best_score_)


# False negative vs. fals positive rate
## Assigning the same cost to false positives and false positives and determine the optimal value of k
## one way: get optimal k from accuracy rate
ac_rate = []
for i in ks:
     knn = KNeighborsClassifier(n_neighbors=i)
     knn.fit(x_norm_train, y_train)
     pred_i = knn.predict(x_norm_test)
     ac_rate.append(np.mean(pred_i == y_test))
max_value = max(ac_rate)
opt_k = ac_rate.index(max_value)

## another way: assigning a ratio of costs of false positives and false negatives = 1 : 1
fn = []
for i in ks:
     knn = KNeighborsClassifier(n_neighbors=i)
     knn.fit(x_norm_train, y_train)
     pred_i = knn.predict(x_norm_test)
     fn.append(sum(y_test - pred_i > 0))
    
fp = []
for i in ks:
     knn = KNeighborsClassifier(n_neighbors=i)
     knn.fit(x_norm_train, y_train)
     pred_i = knn.predict(x_norm_test)
     fp.append(sum(y_test - pred_i < 0))

cost = []
for i in range(194):
    cost.append((1/2)*fp[i] + (1/2)*fn[i])
cost = np.ndarray.tolist(np.array(cost))

min_value = min(cost)
opt_k = cost.index(min_value)

## assume the ratio of costs of false positives and false negatives = 1 : 2
## FP: y_test = 0, pred_i = 1
## FN: y_test = 1, pred_i = 0
cost_1 = []
for i in range(194):
    cost_1.append((1/3)*fp[i] + (2/3)*fn[i])
cost_1 = np.ndarray.tolist(np.array(cost_1))
min_value1 = min(cost_1)
opt_k1 = cost_1.index(min_value1)

cost_3 = []
for i in range(194):
    cost_3.append((1/6)*fp[i] + (5/6)*fn[i])
cost_3 = np.ndarray.tolist(np.array(cost_3))
min_value3 = min(cost_3)
opt_k3 = cost_3.index(min_value3)

# assume the ratio of costs of false positives and false negatives = 2 : 1
## FP: y_test = 0, pred_i = 1
## FN: y_test = 1, pred_i = 0
cost_2 = []
for i in range(194):
    cost_2.append((2/3)*fp[i] + (1/3)*fn[i])
cost_2 = np.ndarray.tolist(np.array(cost_2))
min_value2 = min(cost_2)
opt_k2 = cost_2.index(min_value2)


# Comparison
## vs. LPM
## First, find how many firms are predicted by the optimal k-NN to have committed tax fraud
## k = 1, normalized
knn_1_norm = KNeighborsClassifier(n_neighbors = 1)
knn_1_norm.fit(x_norm_train, y_train)
knn_1_norm.pred = knn_1_norm.predict(x_norm_test)
print(pd.DataFrame(confusion_matrix(y_test, knn_1_norm.pred), index=['y=0', 'y=1'], columns=['y_pred=0', 'y_pred=1']))
print("number of firms are predicted to have committed tax fraud:", 25+81)

## Second, find the threshold q where you would “predict” the same number of firms 
## as having committed tax fraud using the LPM
lpm = LinearRegression()
for n in np.arange(0,0.5,0.01).round(2):
    lpm.pred = lpm.fit(x_train, y_train).predict(x_test) > n
    pred_1 = (confusion_matrix(y_test, lpm.pred)).sum(axis=0)
    if pred_1[1] == 25 + 81:
        print("the shreshold q using LPM:", n)
        
## confusion_matrix of LPM with threshold
lpm = LinearRegression()
lpm.pred = lpm.fit(x_train, y_train).predict(x_test) > 0.12
print(pd.DataFrame(confusion_matrix(y_test, lpm.pred), index=['y=0', 'y=1'], columns=['y_pred=0', 'y_pred=1']))

## Then identify which has a lower proportion of firms that did not commit tax evasion
print("false discovery rate of k-NN:", 25/(81+25))
print("false discovery rate of LPM:", 48/(58+48))
print("false negative rate of k-NN:", 1/(81+1))
print("false negative rate of LPM:", 24/(24+58))

## vs. LDA
## Use LDA to classify the firms in the testing data
lda = LinearDiscriminantAnalysis()
lda.pred = lda.fit(x_train, y_train).predict(x_test)
print(pd.DataFrame(confusion_matrix(y_test, lda.pred), index=['y=0', 'y=1'], columns=['y_pred=0', 'y_pred=1']))
print("positive predictive rate of LDA:", 28/(28+5))
print("true positive rate of LDA:", 28/(28+54))

## k-NN: apples-to-apples comparison
## k = 1, unnormalized (higher positive predictive rate than normalized)
knn_1 = KNeighborsClassifier(n_neighbors = 1)
knn_1.fit(x_train, y_train)
knn_1.pred = knn_1.predict(x_test)
print(pd.DataFrame(confusion_matrix(y_test, knn_1.pred), index=['y=0', 'y=1'], columns=['y_pred=0', 'y_pred=1']))
print("positive predictive rate of k-NN:", 70/(70+1))
print("true postive rate of k-NN:", 70/(70+12))



#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  6 21:25:38 2022

@author: changruiquan
"""

import spacy
from spacytextblob.spacytextblob import SpacyTextBlob
import os
import glob
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

path = r'/Users/changruiquan/Documents/GitHub'
nlp = spacy.load('en_core_web_sm')
nlp.add_pipe('spacytextblob')

# read txt files
def read_txt(path):
    txts= glob.glob(os.path.join(path, "*.txt"))
    txt_files = sorted(txts, key=lambda t: -os.stat(t).st_mtime)
    for i in range(len(txt_files)):
        text = []
        for f in txt_files:
            file = open(f, 'r').read()
            file = file.replace('\n\n', ' ').replace('\n', ' ')
            text.append(file)
    return text

text = read_txt(path)

# sentiment analysis
def get_polarity(text):
    polarity = []
    for i in range(len(text)):
        doc = nlp(text[i])
        pol = doc._.blob.polarity
        polarity.append(pol)
    return polarity

def get_subjectivity(text):
    subjectivity = []
    for i in range(len(text)):
        doc = nlp(text[i])
        sub = doc._.blob.subjectivity
        subjectivity.append(sub)
    return subjectivity

# show countries discussed in the article
def show_countries(text, key):
    country_keys = labels
    country_values = []
    for i in range(len(text)):
        doc = nlp(text[i])
        countries = set([(ent.text) for ent in doc.ents if ent.label_=='GPE'])
        country_values.append(countries)
    countries_dic = {country_keys[i]: country_values[i] for i in range(len(country_keys))}
    return countries_dic[key]

# other summary statistics: I am curious about the numbers mentioned
## e.g., UNHCR this week urged donors to provide US$1.85 billion to support up 
## to 8.3 million refugees who could flee Ukraine by the end of the year.
def show_stats(text, key):
    stats_keys = labels
    stats_values = []
    for i in range(len(text)):
        doc = nlp(text[i])
        stats = [(ent.label_, ent.text) for ent in doc.ents if (ent.label_=='CARDINAL') 
                 or (ent.label_=='QUANTITY') or (ent.label_=='MONEY')]
        stats_values.append(stats)
    stats_dic = {stats_keys[i]: stats_values[i] for i in range(len(stats_keys))}
    return stats_dic[key]

# draw sentiment plot
labels = ['04-08', '04-29', '05-06', '05-13', '05-20',
          '05-27', '06-03', '06-10', '06-17', '06-24']    
pol = get_polarity(text)
pos_pol = [v if v > 0 else np.NaN for v in pol]
neg_pol = [v if v < 0 else np.NaN for v in pol]
sub = get_subjectivity(text)
ticks = list(range(0,10))

fig, axs = plt.subplots(2, figsize=(14, 14))
sns.scatterplot(range(len(pol)), pos_pol, data=text, marker='o', s=80, color='dodgerblue', ax=axs[0])
sns.scatterplot(range(len(pol)), neg_pol, data=text, marker='o', s=80, color='darkred', ax=axs[0])
axs[0].set_title('Polarity of the Refugee Briefs Over Time: April 8th 2022 - June 24th 2022', fontsize=14)
axs[0].set_xlabel('Date of the Refugee Brief Issued', fontsize=12)
axs[0].set_ylabel('Polarity (negative - positive)', fontsize=12)
axs[0].set_xticks(ticks, labels)
for x,y in zip(range(len(pol)), pol):
    label = "{:.3f}".format(y)
    axs[0].annotate(label, (x,y), textcoords="offset points",
                     xytext=(0,6), ha='center', fontsize=12)

sns.scatterplot(range(len(pol)), sub, data=text, marker='o', s=80, ax=axs[1])
axs[1].set_title('Subjectivity of the Refugee Briefs Over Time: April 8th 2022 - June 24th 2022', fontsize=14)
axs[1].set_xlabel('Date of the Refugee Brief Issued', fontsize=12)
axs[1].set_ylabel('Subjectivity (objective - subjective)', fontsize=12)
axs[1].set_xticks(ticks, labels)
for x,y in zip(range(len(sub)), sub):
    label = "{:.3f}".format(y)
    axs[1].annotate(label, (x,y), textcoords="offset points",
                     xytext=(0,6), ha='center', fontsize=12)

os.chdir(r'/Users/changruiquan/Documents/GitHub/homework-3-rqchang-1')
fig.savefig('question1_plot.png', dpi=300)

## test:
## show countries in the refugee brief on April 8th
show_countries(text, '04-08')
## show statistics in the refugee brief on April 29th
show_stats(text, '04-29')





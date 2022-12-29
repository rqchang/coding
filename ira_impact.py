import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import scipy.stats as stats
import seaborn as sns
import regex as re
from matplotlib.patches import StepPatch

os.chdir(r'/Users/changruiquan/Desktop/RA/generic')
ptb = pd.read_csv('ptBclass.csv')
ptd = pd.read_csv('ptDclass.csv')
non_nego = pd.read_csv('non_negotiation.csv')

#################### drugs selected for negotiation #########################
non_nego['drug_name'] = non_nego['drug'].str.lower()
non_list = list(non_nego['drug_name'].unique())

# nego_status: 0 = non_negotiable, 1 = negotiable
ptd['nego_status']=np.where(ptd["match_name"].isin(non_list),0,1)
ptb['nego_status']=np.where(ptb["match_name"].isin(non_list),0,1)
ptd['medicare'] = 'd'
ptb['medicare'] = 'b'

ptb = ptb.drop(['Unnamed: 0.1', 'Unnamed: 0'], axis=1)
ptd = ptd.drop(['Unnamed: 0.1', 'Unnamed: 0'], axis=1)
frames = [ptd, ptb]
df = pd.concat(frames).reset_index()

# IRA: 10 Part D drugs in 2026, 15 Part D drugs in 2027, 
# 15 Part B and Part D drugs in 2028, 20 Part B and Part D drugs in 2029 
list_2026 = list(df[(df['medicare']=='d') & (df['nego_status']==1)]
                 .sort_values(by=['Spending'], ascending=False).head(10).match_name)

list_2027 = list(df[(df['medicare']=='d') & (df['nego_status']==1) & (~df['match_name'].isin(list_2026))]
                 .sort_values(by=['Spending'], ascending=False).head(15).match_name)

list_2028 = list(df[(df['nego_status']==1) & (~df['match_name'].isin(list_2026)) & 
                    (~df['match_name'].isin(list_2027))].sort_values(by=['Spending'], ascending=False)
                 .head(15).match_name)

list_2029 = list(df[(df['nego_status']==1) & (~df['match_name'].isin(list_2026)) & 
                    (~df['match_name'].isin(list_2027)) & (~df['match_name'].isin(list_2028))]
                 .sort_values(by=['Spending'], ascending=False).head(20).match_name)

col = 'match_name'
conditions = [df[col].isin(list_2026), df[col].isin(list_2027), 
              df[col].isin(list_2028), df[col].isin(list_2029)]
choices = [2026, 2027, 2028, 2029]
df['time'] = np.select(conditions, choices, default=np.nan)


############################## plot numbers #################################
# negotiated drugs:
df['same_class'] = df['same_class'].str.replace(r'{', '').str.replace(r'}', '').str.replace("'", '')
df['class'] = df['class'].str.replace(r'[', '').str.replace(r']', '')
df['class'] = df['class'].str.replace("'", '')
df_nego = df.dropna()
nego_list = list(df_nego['match_name'].unique())

# drugs in selected classes
def selected_drugs(year):
    df_selected = df[df['time']<=year]
    match = list(df_selected['match_name'].unique())
    temp = df_selected['same_class'].str.split(',').tolist()
    temp1 = [j for i in temp for j in i]
    temp2 = [i.lstrip().rstrip() for i in temp1]
    temp3 = [] 
    for i in temp2:
        if i not in temp3:
            temp3.append(i)
    same_class = []
    for i in temp3:
        if i not in match:
            same_class.append(i)
    selected = match + same_class
    return selected

# all drugs
match = list(df['match_name'].unique())
temp = df['same_class'].str.split(',').tolist()
temp1 = [j for i in temp for j in i]
temp2 = [i.lstrip().rstrip() for i in temp1]
temp3 = [] 
for i in temp2:
    if i not in temp3:
        temp3.append(i)
same_class = []
for i in temp3:
    if i not in match:
        same_class.append(i)
all_drugs = match + same_class
len(all_drugs)

selected_26 = selected_drugs(2026)
selected_27 = selected_drugs(2027)
selected_28 = selected_drugs(2028)
selected_29 = selected_drugs(2029)
perc_26 = len(selected_26)/len(all_drugs)
perc_27 = len(selected_27)/len(all_drugs)
perc_28 = len(selected_28)/len(all_drugs)
perc_29 = len(selected_29)/len(all_drugs)

selected = [len(selected_26), len(selected_27), len(selected_28), len(selected_29)]
others = [len(all_drugs)-len(selected_26), len(all_drugs)-len(selected_27),
          len(all_drugs)-len(selected_28), len(all_drugs)-len(selected_29)]
base_line = [0, 0, 0, 0]
year = np.linspace(2026, 2030, 5)
y = [base_line, selected, others]
color = ['darkred', 'darkblue']
l = ['Drug Classes Selected for Negotiation', 'Other Unaffected Drug Classes']

fig, ax = plt.subplots(1, figsize=(16,9))
plt.title('Total Numbers of Drugs in The Drug Classes Selected for Negotiation: 2026-2029', fontsize=18)
plt.xlabel('Year', fontsize=16)
plt.ylabel('Number of Drugs', fontsize=16)
plt.xticks(np.arange(2026.5, 2030.5, 1), fontsize=14)
ax.set_xticklabels(['2026','2027','2028','2029'])
plt.yticks(fontsize=14)
for i in range(len(y)-1):
    plt.stairs(y[i+1], year, baseline=None, fill=False, color=color[i], label=l[i], alpha=1, linewidth=3)
    plt.legend(loc='upper right',fontsize=14)
for i,j in zip(year,selected):
    ax.annotate('%.0f'%(j),xy=(i+0.38,j+0.01), fontsize=16)
for i,j in zip(year,others):
    ax.annotate('%.0f'%(j),xy=(i+0.38,j+0.01), fontsize=16)
fig.savefig('numbers.png', dpi=300)


############################### plot sales ###################################
def match(n,lst):
    match=None
    shorten = [l for l in lst if str(l).startswith(n[:3])]
    if len(shorten)==1:
        match = shorten[0]
    else:
        sim=1
        for l in shorten:
            new_sim = sim_score(n,l)
            if new_sim < sim:
                sim = new_sim
                match=l
    return match

def sim_score(s1,s2):
    if len(s1)>len(s2):
        long=s1
        s1=s2
        s2=long
    score=9999
    #print(s1)
    #print(s2)

    for i in range(1,len(s1)):
        sub=s1[:-i]
        #print(i)
        #print(sub)
        #print(sub)
        if sub in s2:
            score = i/len(s1)
            break
    return score

ndc=pd.read_csv("ndc_product.csv")
subndc=ndc.loc[:,["PROPRIETARYNAME","PHARM_CLASSES"]]
subndc["PROPRIETARYNAME"]=[str(i).lower() for i in list(subndc["PROPRIETARYNAME"])]
subndc

d=pd.read_csv("partD.csv")
l=[c for c in d.columns if "20" in c]
l.append("Brand Name")
d=d.loc[:,l]
names = [re.sub("20","",n) for n in l]
names = [re.sub("\n","",n) for n in names]
d=d.set_axis(names,axis=1,inplace=False)
def str2num(n):
    n=re.sub("\$","",n)
    n=re.sub(",","",n)
    n=float(n)
    return (n)

d["Total Spending"]=d["Total Spending"].apply(lambda x: str2num(x))
d["Brand Name"]=d["Brand Name"].apply(lambda x: x.lower())
d["match_name"]=d["Brand Name"].apply(lambda x:match(x.lower(),list(subndc["PROPRIETARYNAME"])))
d=d.sort_values(by="Total Spending", ascending=False)

b=pd.read_csv("partB.csv")
b=b.set_axis(b.loc[0,],axis=1,inplace=False)
b=b.loc[1:,]
l=[c for c in list(b.columns) if type(c)==str and "20" in c]
l.append("Brand-Name")
b=b.loc[:,l]
names = [re.sub("20","",n) for n in l]
names = [re.sub("\n","",n) for n in names]
names=names = [re.sub("-"," ",n) for n in names]
b=b.set_axis(names,axis=1,inplace=False)
b["Total Spending"]=b["Total Spending"].apply(lambda x: str2num(x))
b["match_name"]=b["Brand Name"].apply(lambda x:match(x.lower(),list(subndc["PROPRIETARYNAME"])))

bd=pd.concat([d.loc[:,["Total Spending","Brand Name","match_name"]],b.loc[:,["Total Spending","Brand Name","match_name"]]])
df_bd = bd.drop_duplicates(keep='last')

def get_spending(n):
    row=df_bd.loc[d["match_name"]==n,]
    set_bn= set().union(row["Brand Name"])
    #print(set_bn)
    if len(row)==1:
        spending=float(row["Total Spending"])
    else:
        spending = sum(list(row["Total Spending"]))
    return spending

all_spending = sum([get_spending(i) for i in all_drugs])/1000000000
spending_26 = sum([get_spending(i) for i in selected_26])/1000000000
spending_27 = sum([get_spending(i) for i in selected_27])/1000000000
spending_28 = sum([get_spending(i) for i in selected_28])/1000000000
spending_29 = sum([get_spending(i) for i in selected_29])/1000000000

psale_26 = spending_26 / all_spending
psale_27 = spending_27 / all_spending
psale_28 = spending_28 / all_spending
psale_29 = spending_29 / all_spending

selected = [spending_26, spending_27, spending_28, spending_29]
others = [all_spending-spending_26, all_spending-spending_27, 
          all_spending-spending_28, all_spending-spending_29]
base_line = [0, 0, 0, 0]
year = np.linspace(2026, 2030, 5)
y = [base_line, selected, others]
color = ['darkred', 'darkblue']
l = ['Drug Classes Selected for Negotiation', 'Other Unaffected Drug Classes']

fig, ax = plt.subplots(1, figsize=(16,9))
plt.title('Total Sales of Drugs in The Drug Classes Selected for Negotiation: 2026-2029', fontsize=18)
plt.xlabel('Year', fontsize=16)
plt.ylabel('Total Sales ($Billion)', fontsize=16)
plt.xticks(np.arange(2026.5, 2030.5, 1), fontsize=14)
ax.set_xticklabels(['2026','2027','2028','2029'])
plt.yticks(fontsize=14)
for i in range(len(y)-1):
    plt.stairs(y[i+1], year, baseline=None, fill=False, color=color[i], label=l[i], alpha=1, linewidth=3)
    plt.legend(loc='lower right',fontsize=14)
for i,j in zip(year,selected):
    ax.annotate(f'{j:.2%}',xy=(i+0.38,j+0.1), fontsize=16)
for i,j in zip(year,others):
    ax.annotate(f'{j:.2%}',xy=(i+0.38,j+0.1), fontsize=16)
fig.savefig('sales.png', dpi=300)


############################# plot drug classes ##############################
df_ira = df[(df['time']==2026)|(df['time']==2027)|(df['time']==2028)|(df['time']==2029)]

df_bd_combined = df_bd.groupby(['match_name'])['Total Spending'].sum().reset_index()
df_bd_combined = df_bd_combined.sort_values(by='Total Spending', ascending=False)

ndc = pd.read_csv('ndc_product.csv')
temp = df_ira['class'].str.split(',').tolist()
temp1 = [j for i in temp for j in i]
temp2 = [i.lstrip().rstrip() for i in temp1]
classes = [] 
for i in temp2:
    if i not in classes:
        classes.append(i)
sorted(classes)

dct = {}
for ele in classes:
    num = classes.index(ele)
    df_name = 'df_' + '%s'%(num)
    globals()[df_name] = ndc[ndc['PHARM_CLASSES'].str.contains(ele, na=False)]
    drug_name = 'drug' + '%s'%(num)
    dct['lst_%s'%num] = list(globals()[df_name].PROPRIETARYNAME.str.lower().unique())
    df2_name = 'spending_' + '%s'%(num)
    globals()[df2_name] = df_bd_combined[df_bd_combined['match_name'].isin(list(dct.values())[num])].head(10)
    globals()[df2_name]['class'] = ele
    
frames = [spending_0, spending_1, spending_2, spending_3, spending_4, spending_5, spending_6,
         spending_7, spending_8, spending_9, spending_10, spending_11, spending_12, spending_13,
         spending_14, spending_15, spending_16, spending_17, spending_18, spending_19, spending_20,
         spending_21, spending_22, spending_23, spending_24, spending_25, spending_26, spending_27,
         spending_28, spending_29, spending_30, spending_31, spending_32, spending_33, spending_34,
         spending_35, spending_36, spending_37, spending_38, spending_39]

spending = pd.concat(frames)
spending = spending.rename(columns={'Total Spending': 'medicare_spending'})
spending.to_csv('spending.csv', mode="a", index=True, 
                header=True, encoding='utf-8_sig')

class_spending = pd.read_csv('medicare.csv')
class_spending = class_spending[['class', 'medicare_spending', 'us_spending']]
class_spending = class_spending.dropna()

df_spending = class_spending.groupby(['class'])['medicare_spending', 'us_spending'].sum().reset_index()
df_spending = df_spending.sort_values(by='class', ascending=False)
df_spending['pct_medicare'] = df_spending['medicare_spending']/df_spending['us_spending']
df_spending = df_spending.sort_values(by='pct_medicare')

fig, ax = plt.subplots(1, figsize=(16,19))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

b1 = plt.barh(df_spending['class'], df_spending['pct_medicare'], color='#718dbf')
plt.title('Share of Sales Occurred in Medicare among Drug Classes Selected for Negotiation', 
          loc='left', fontsize=22)
plt.xlabel('Proportion', fontsize=16)
plt.ylabel('Drug Classes', fontsize=16)
plt.xticks(fontsize=14)
plt.yticks(fontsize=12)
colors = list('wk')
for bars, color in zip(ax.containers, colors):
    labels = [f'{x:.2%}' for x in bars.datavalues]
    ax.bar_label(bars, labels=labels, color=color, label_type='center', fontsize=14)
fig.savefig("medicare%.svg", bbox_inches='tight')







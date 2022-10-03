#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 01:17:07 2022

@author: rqchang/Ruiquan Chang
"""


import urllib.request
from bs4 import BeautifulSoup
import pandas as pd
import re


# retrieve the general issue page, get volume, link, issue_date
def readAER(baseurl):
    url = baseurl
    try:
        volume_page = urllib.request.urlopen(url=url).read()
    except urllib.request.HTTPError as e:
       print(e.code)
    except urllib.request.URLErrror as e:
        print(str(e))

    # create table title
    save_csv('volume', 'issue_date', 'article_title', 'authors', 'page_numbers', 'article_link',
             'jel_code', 'jel_description')
    bs = BeautifulSoup(volume_page, "html.parser")
    bs1 = bs.section.contents[5]
    bs2 = bs1.find_all("article")

    # collect volume information: volume, link, issue_date
    for i in range(0, len(bs2)):
        bs3 = bs2[i].find_all("a")
        for j in range(0, len(bs3)):
            volume_str = bs2[i].span.string     # volume
            issue_date_str = bs3[j].string    # issue_date
            link_str = "https://www.aeaweb.org" + bs3[j].get("href")    # link
            readchildlink(volume_str,issue_date_str,link_str)


# retrieve specific issue page, get article_link, page_numbers, article_title
def readchildlink(volume_str, issue_date_str, childurl):
    url = childurl
    try:
        issue_page = urllib.request.urlopen(url=url).read()
    except urllib.request.HTTPError as e:
        print(e.code)
    except urllib.request.URLErrror as e:
        print(str(e))

    child_soup = BeautifulSoup(issue_page, "html.parser")
    child_soup_page = child_soup.find_all("article")

    for i in range(0, len(child_soup_page)):
        child_soup_page1 = child_soup_page[i].find_all("a")
        child_soup_page2 = child_soup_page[i].find_all(class_="page-range")
        for j in range(0, len(child_soup_page1)):    # process the articles in each issue page
            article_link_str = "https://www.aeaweb.org" + child_soup_page1[j].get("href")   # article_link
            page_numbers_str = child_soup_page2[j].string    # page_numbers
            article_title_str = child_soup_page1[j].text    # article_title
            if article_title_str == "Front Matter":    # no need to get Front Matter
                continue
            else:
                print('%s-%s: The article “%s”is processing' %(volume_str,issue_date_str,article_title_str))
                readGrandsonlink(volume_str, issue_date_str, article_title_str, page_numbers_str, article_link_str)


# retrieve article pages below specific issue page (article_link)，get authors, jel_code, jel_description
def readGrandsonlink(volume_str, issue_date_str, article_title_str, page_numbers_str, article_link_str):
    url = article_link_str
    try:
      article_page = urllib.request.urlopen(url=url).read()
    except urllib.request.HTTPError as e:
        print(e.code)
    except urllib.request.URLErrror as e:
        print(str(e))

    gs_soup = BeautifulSoup(article_page, "html.parser")
    authors_str = ""

    # authors
    gs_soup_authors = gs_soup.find_all(class_="author")
    for j in range(0, len(gs_soup_authors)):
        if j == 0:
            authors_str = authors_str + gs_soup_authors[j].text.strip()
        else:
            authors_str = authors_str + "; " + gs_soup_authors[j].text.strip()

    gs_soup1 = gs_soup.find(class_="jel-codes")

    # if the article doesn't have jel_code
    try:
        gs_soup2 = gs_soup1.select("li")
    except AttributeError as e:
        save_csv(volume_str, issue_date_str, article_title_str, authors_str, page_numbers_str, article_link_str,
                 "NONE", "NONE")
        return

    # jel_code, jel_description
    for i in range(0, len(gs_soup2)):
        jel_code_str = gs_soup2[i].strong.string
        restr = r'(?<=\t\t\t\t\t\t\t\t).*?(?=\n\t\t\t\t\t\t\t\t)'
        gs_soup3 = gs_soup2[i].text
        result = re.findall(re.compile(restr),gs_soup3)     
        jel_description_str = result[0]
        save_csv(volume_str, issue_date_str, article_title_str, authors_str, page_numbers_str, article_link_str, jel_code_str, jel_description_str)


# store web scraping results
def save_csv(volume_str, issue_date_str, article_title_str, authors_str, page_numbers_str, article_link_str, jel_code_str, jel_description_str):
    data = {'volume': volume_str, 'issue_date': issue_date_str, 'article_title': article_title_str,
            'authors': authors_str, 'page_numbers': page_numbers_str, 'article_link': article_link_str,
            'jel_code': jel_code_str, 'jel_description': jel_description_str}
    df = pd.DataFrame(data,index=[0])
    df.to_csv("task1b_ruiquan_chang.csv", mode="a", index=False, header=False, encoding='utf-8_sig')


if __name__ == '__main__':
    baseurl = "https://www.aeaweb.org/journals/aer/issues"
    readAER(baseurl)
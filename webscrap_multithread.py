#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 01:17:07 2022

@author: changruiquan
"""


import urllib.request
from bs4 import BeautifulSoup
import pandas as pd
import re
import threading
import os


def readAER(baseurl,t1,t2):
    url = baseurl
    try:
        volume_page = urllib.request.urlopen(url=url).read()
    except urllib.request.HTTPError as e:
       print(e.code)
    except urllib.request.URLErrror as e:
        print(str(e))

    # create table title
    save_csv('volume', 'issue_date', 'article_title', 'authors', 'page_numbers', 'article_link',
             'jel_code', 'jel_description',1000)
    bs = BeautifulSoup(volume_page, "html.parser")
    bs1 = bs.section.contents[5]
    bs2 = bs1.find_all("article")

    # collect basic volume information: volume, link, issue_date
    if t2 == 100:
        t2 = len(bs2)
    for i in range(t1, t2):
        bs3 = bs2[i].find_all("a")
        for j in range(0, len(bs3)):
            volume_str = bs2[i].span.string     # volume
            issue_date_str = bs3[j].string  # issue_date
            link_str = "https://www.aeaweb.org" + bs3[j].get("href")
            readchildlink(volume_str, issue_date_str, link_str,t1)

    # merge results of all threads into destination csv
    if t1 == 0:
        merge_file("test-thread0.csv", "task1b_ruiquan_chang_threads.csv")
        os.remove("test-thread0.csv")
    elif t1 == 3:
        merge_file("test-thread3.csv", "task1b_ruiquan_chang_threads.csv")
        os.remove("test-thread3.csv")
    elif t1 == 6:
        merge_file("test-thread6.csv", "task1b_ruiquan_chang_threads.csv")
        os.remove("test-thread6.csv")
    elif t1 == 9:
        merge_file("test-thread9.csv", "task1b_ruiquan_chang_threads.csv")
        os.remove("test-thread9.csv")
    elif t1 == 12:
        merge_file("test-thread12.csv", "task1b_ruiquan_chang_threads.csv")
        os.remove("test-thread12.csv")
    elif t1 == 15:
        merge_file("test-thread15.csv", "task1b_ruiquan_chang_threads.csv")
        os.remove("test-thread15.csv")
    elif t1 == 18:
        merge_file("test-thread18.csv", "task1b_ruiquan_chang_threads.csv")
        os.remove("test-thread18.csv")
    else:
        merge_file("test-thread21.csv", "task1b_ruiquan_chang_threads.csv")
        os.remove("test-thread21.csv")


# retrieve issue page，get article_title, authors, page_numbers, article_link
def readchildlink(volume_str, issue_date_str, childurl,t1):
    url = childurl
    try:
        issue_page = urllib.request.urlopen(url=url).read()
    except urllib.request.HTTPError as e:
        print(e.code)
    except urllib.request.URLErrror as e:
        print(str(e))

    child_soup = BeautifulSoup(issue_page, "html.parser")
    child_soup_page = child_soup.find_all("article")

    # retrieve every articles below specific issue page, get article_link, page_numbers, article_title
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
                print('%s-%s: The article “%s”is processing' %(volume_str, issue_date_str, article_title_str))
                readGrandsonlink(volume_str, issue_date_str, article_title_str, page_numbers_str, article_link_str, t1)


# retrieve article page (article_link)，get authors, jel_code, jel_description
def readGrandsonlink(volume_str, issue_date_str, article_title_str, page_numbers_str, article_link_str, t1):
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
                 "NONE", "NONE",t1)
        return

    # jel_code, jel_description
    for i in range(0, len(gs_soup2)):
        jel_code_str = gs_soup2[i].strong.string
        restr = r'(?<=\t\t\t\t\t\t\t\t).*?(?=\n\t\t\t\t\t\t\t\t)'  #查找jel_description的正则表达式
        gs_soup3 = gs_soup2[i].text
        result = re.findall(re.compile(restr),gs_soup3)     #返回list结果
        jel_description_str = result[0]
        save_csv(volume_str, issue_date_str, article_title_str, authors_str, page_numbers_str, article_link_str, jel_code_str, jel_description_str, t1)


# store web scraping results
def save_csv(volume_str, issue_date_str, article_title_str, authors_str, page_numbers_str, article_link_str, jel_code_str, jel_description_str, t1):
    data = {'volume': volume_str, 'issue_date': issue_date_str, 'article_title': article_title_str,
            'authors': authors_str, 'page_numbers': page_numbers_str, 'article': article_link_str,
            'jel_code': jel_code_str, 'jel_description': jel_description_str}
    df = pd.DataFrame(data, index=[0])
    if t1 == 1000:
        df.to_csv("test-thread.csv", mode="a", index=False, header=False, encoding='utf-8_sig')     #写表头到结果文件中
    elif t1 == 0:
        df.to_csv("test-thread0.csv", mode="a", index=False, header=False, encoding='utf-8_sig')   #用encoding='utf-8'可能出现authors乱码
    elif t1 == 3:
        df.to_csv("test-thread3.csv", mode="a", index=False, header=False, encoding='utf-8_sig')
    elif t1 == 6:
        df.to_csv("test-thread6.csv", mode="a", index=False, header=False, encoding='utf-8_sig')
    elif t1 == 9:
        df.to_csv("test-thread9.csv", mode="a", index=False, header=False, encoding='utf-8_sig')
    elif t1 == 12:
        df.to_csv("test-thread12.csv", mode="a", index=False, header=False, encoding='utf-8_sig')
    elif t1 == 15:
        df.to_csv("test-thread15.csv", mode="a", index=False, header=False, encoding='utf-8_sig')
    elif t1 == 18:
        df.to_csv("test-thread18.csv", mode="a", index=False, header=False, encoding='utf-8_sig')
    else:
        df.to_csv("test-thread21.csv", mode="a", index=False, header=False, encoding='utf-8_sig')


# merge files of multithreading
def merge_file(sfile, dfile):
    df = pd.read_csv(sfile)
    df.to_csv(dfile, encoding="utf_8_sig", index=False, header=False, mode='a+')


if __name__ == '__main__':
    baseurl = "https://www.aeaweb.org/journals/aer/issues"

    # start 8 threads to perform parsing simultaneously
    thread1 = threading.Thread(name='t1', target=readAER, args=(baseurl,  0,  3))
    thread2 = threading.Thread(name='t2', target=readAER, args=(baseurl,  3,  6))
    thread3 = threading.Thread(name='t3', target=readAER, args=(baseurl,  6,  9))
    thread4 = threading.Thread(name='t4', target=readAER, args=(baseurl,  9, 12))
    thread5 = threading.Thread(name='t5', target=readAER, args=(baseurl, 12, 15))
    thread6 = threading.Thread(name='t6', target=readAER, args=(baseurl, 15, 18))
    thread7 = threading.Thread(name='t7', target=readAER, args=(baseurl, 18, 21))
    thread8 = threading.Thread(name='t8', target=readAER, args=(baseurl, 21, 100))
    thread1.start() 
    thread2.start()  
    thread3.start()
    thread4.start()
    thread5.start()
    thread6.start()
    thread7.start()
    thread8.start()

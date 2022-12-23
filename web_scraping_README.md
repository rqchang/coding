# Web Scraping - American Economic Review

## Project Description

This project conducts web scraping utilizing Python to get detailed information for each article in every issue available on the American Economic Review website (https://www.aeaweb.org/journals/aer/issues), including:

- 📖 Volume and issue number
- 📅 Issue-date information
- 📄 The article's title
- 👤 The article's author(s)
- 🔢 The article's page-numbers
- 🔗 The permanent link to the article
- 🏷 The article's JEL code(s)
- 🗂 The article's JEL coed description(s)

Packages used: urllib.request, BeautifulSoup, Pandas, RE. 

Another multithreading version which processes more efficiently is attached (). The deliverable spreadsheet is named as 'results.csv'.

## Project Deliverable

### Logic

**1) readAER(baseurl):** 

Base url page (https://www.aeaweb.org/journals/aer/issues). Parse all volumes in the general issue page, and get their 'volume' (volume_str), 'issue_date' (issue_date_str), 'issue_link' (link_str). According to the issue link retrieved (link_str), call readchildlink() and pass donw volume_str, issue_date_str to the next function.

![image](https://user-images.githubusercontent.com/102669789/193464752-0fb59ee1-97ec-4523-8bf6-86b978335100.png)

**2) readchildlink():** 

Parse specific issue page (e.g., https://www.aeaweb.org/issues/696), and get the corresponding 'article_title' (article_title_str), 'page_numbers' (page_numbers_str), 'article_link' (article_link_str). According to the article link retrieved (article_link_str), call readGrandsonlink() and pass down volumn_str, issue_date_str, article_title_str, page_numbers_str, to the next function.

![image](https://user-images.githubusercontent.com/102669789/193464806-7695470f-7125-4499-82c4-cc03fc14f5c2.png)

**3) readGrandsonlink():**

Parse specific article page (e.g., https://www.aeaweb.org/articles?id=10.1257/aer.20190668), and get corresponding 'authors' (authors_str), 'jel_code' (jel_code_str), 'jel_description' (jel_description_str). Call save_csv() and store all the web scraping results.

![image](https://user-images.githubusercontent.com/102669789/193464851-f086f841-43b1-4f04-8cad-1f7322779091.png)
![image](https://user-images.githubusercontent.com/102669789/193464910-e234db7e-fb63-4cca-b9ba-3605627de32c.png)

**4) save_csv():**

Save all web scrapint results to .cvs file, including 'volume', 'issue_date', 'article_title', 'authors', 'page_numbers', 'article_link', 'jel_code', 'jel_description'.

Through web scrapping the provided urls, issue-level data is stored in a .csv file. The deliverable spreadsheet ('task1b_ruiquan_chang.csv') is structured as follows:

<img width="800" alt="image" src="https://user-images.githubusercontent.com/102669789/193464634-3e7efbd8-d630-4423-9fcb-cb79648f8bb3.png">

## Multithreading Version

Besides the original code, I also provide a multithreading version, which could greatly save the processing time (from approximately an hour to only 5 minutes). The code is names as 'ruiquan_chang_multithread.py'.

## Author Information

Should you have any questions, please feel free to contact the author: Ruiquan Chang <rqchang@uchicago.edu>.

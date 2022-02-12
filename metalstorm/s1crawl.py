"""
    Crawl metalstorm albums page and add them to the db.
"""

import bs4
import os
import parse
import sqlite3
import time
import unidecode

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# config

sqlitefile = 'sqlite\\metalstorm.db'

# clean up

if os.path.exists(sqlitefile):
    os.remove(sqlitefile)

# database

con = sqlite3.connect(sqlitefile)
con.execute('pragma journal_mode=wal')
cur = con.cursor()

# create table 

cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS albums
    (
        artist      text not null,
        album       text not null,
        year        int not null,
        format      text not null,
        style       text,
        rating      real,
        votes       int,
        attempted   int not null default 0,
        finished    int not null default 0,
        timestamp   real not null,
        url         text primary key
    );
    '''
)
con.commit()

# open gecko driver

browser = Firefox()
browser.implicitly_wait(3)
browser.get('https://metalstorm.net/bands/albums.php?a_where=&a_what=')

input('set search filters and click enter ')

# start the scrape

while True:
    try:
        WebDriverWait(browser, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@class="cbox"]')))
    except: break
    time.sleep(3)

    soup = bs4.BeautifulSoup(browser.page_source, 'lxml')
    cbox = soup.find_all('div', {'class': 'cbox'})
    if len(cbox) < 2: continue
    cbox = cbox[-1]

    # get rows, each row is an album
    
    rows = cbox.find_all('tr')
    if len(rows) < 2: continue
    rows = rows[1:]
    for row in rows:
        cols = row.find_all('td')
        cols = cols[2:8]
        
        artist = cols[0].find_all('a', href=True)[0].text.strip()
        album = cols[0].find_all('a', href=True)[1].text.strip()
        url = cols[0].find_all('a', href=True)[1]['href'].strip()

        temp = parse.parse('{0} ({1})', artist)
        if temp is not None:
            artist = temp[0].strip()

        artist = unidecode.unidecode(artist)
        album = unidecode.unidecode(album)
        
        year = int(cols[1].text.strip())

        format = cols[2].text.strip()

        style = cols[3].text.strip()
        style = None if len(style) == 0 else style

        rating = cols[4].text.strip().split('(', 1)[0].strip()
        rating = None if len(rating) == 0 else float(rating)

        votes = cols[5].text.strip()
        votes = None if len(votes) == 0 else int(votes)

        timestamp = time.time()

        cur.execute(
            '''
            insert or ignore into albums
            values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            ''',
            (artist, album, year, format, style, rating, votes, 0, 0, timestamp, url)
        )
        print(artist, album, year, format, style, rating, votes, 0, 0, timestamp, url)

    con.commit()

    pagination = soup.find_all('ul', {'class': 'pagination'})
    if len(pagination) == 0: break
    pagination = pagination[-1]
    lis = pagination.find_all('li')
    for i, li in enumerate(lis):
        if li.has_attr('class'):
            i += 1
            break

    if i < len(lis):
        page = lis[i].find('a', href=True)['href'].strip()
        nextpage = 'https://metalstorm.net/bands/' + page
        browser.get(nextpage)
    else: break

browser.close()
con.close()

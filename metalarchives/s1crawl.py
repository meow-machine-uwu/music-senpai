"""
    Crawl metalarchives albums page and add them to the db.
"""

import bs4
import os
import sqlite3
import time
import unidecode

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# config

sqlitefile = 'sqlite\\metalarchives.db'

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
        format      text not null,
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
browser.get('https://www.metal-archives.com/search/advanced/?searchString=&type=')

input('set search filters and click enter ')

# start the scrape

while True:
    try:
        WebDriverWait(browser, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, '//tr[@class="odd"]')))
    except: break
    time.sleep(3)

    soup = bs4.BeautifulSoup(browser.page_source, 'lxml')
    odd  = soup.findAll('tr', {'class': 'odd'})
    even = soup.findAll('tr', {'class': 'even'})
    rows = odd + even

    for i, row in enumerate(rows):
        try: artist, album, format_, released = row
        except: continue

        result      = album.findAll('a', href=True)[0]['href']
        artist      = unidecode.unidecode(artist.get_text()).strip()
        album       = unidecode.unidecode(album.get_text()).strip()
        format_     = unidecode.unidecode(format_.get_text()).strip()
        timestamp   = time.time()

        print(artist, album)

        cur.execute(
            '''
            INSERT OR IGNORE INTO albums
            VALUES (?, ?, ?, ?, ?, ?, ?);
            ''',
            (artist, album, format_, 0, 0, timestamp, result)
        )
    
    con.commit()

    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//a[@class="next paginate_button"]'))).click()
    except: break

    time.sleep(3)


browser.close()
con.close()

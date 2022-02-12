"""
    Scrape spotify for artist album tracks.
    FYI: I login here so I can't crawl without a time limit.
"""

import keyring
import re
import spotipy
import sqlite3
import sys
import time
import unidecode

from spotipy.oauth2 import SpotifyOAuth


# config

sqlitefile = 'sqlite\\metalarchives.db'

cid = keyring.get_password('spotify', 'cid')
csc = keyring.get_password('spotify', 'csc')

# these are the scopes i use
scopes = [
    'user-follow-modify',
    'user-follow-read',
    'user-library-modify',
    'user-library-read',
    'playlist-modify-private',
    'playlist-read-collaborative',
    'playlist-read-private',
    'playlist-modify-public',
]
scopes = " ".join(scopes)

# connect to the step_01 database
# this will find all the matches in the search url text file (last one)
con = sqlite3.connect(sqlitefile)
cur = con.cursor()

cur.execute(
    '''
    create table if not exists spotify
    (
        artist      text not null,
        album       text not null,
        count       int not null default 0,
        track       text,
        url         text,
        primary key(track, url)
    );  
    '''
)
con.commit()

cur.execute(
    '''
    select artist, album, url from albums
    where attempted = 0
    and finished = 0;
    '''
)
entries = cur.fetchall()

# login
print('logging on')
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=cid, 
                                               client_secret=csc,
                                               redirect_uri="http://localhost:8888/callback",
                                               scope=scopes))
current_user = sp.current_user()

# get entries
print('getting targets')
for artist, album, url in entries:

    cur.execute(
        '''
        update albums
        set attempted=1
        where url=?;
        ''',
        (url,)
    )

    print('searching', artist, album)
    while True:
        try:
            search = sp.search("{0} {1}".format(artist, album), type = "album")
            time.sleep(3.0)
            break
        except:
            time.sleep(3.0)

    ralbum  = unidecode.unidecode(album)
    rartist = unidecode.unidecode(artist)

    ralbum  = ralbum.lower()
    rartist = rartist.lower()

    ralbum  = re.sub('[^a-z0-9]', '', ralbum)
    rartist = re.sub('[^a-z0-9]', '', rartist)

    for x in search["albums"]["items"]:
        salbum  = x['name']
        sartist = x['artists'][0]['name']
        talbum  = salbum
        tartist = sartist
        print('search result', sartist, salbum)

        salbum  = unidecode.unidecode(salbum)
        sartist = unidecode.unidecode(sartist)

        salbum  = salbum.lower()
        sartist = sartist.lower()

        salbum  = re.sub('[^a-z0-9]', '', salbum)
        sartist = re.sub('[^a-z0-9]', '', sartist)

        if salbum.startswith(ralbum) or ralbum.startswith(salbum):
            if sartist.startswith(rartist) or rartist.startswith(sartist):
                print('found', artist, album)
                try:
                    tracks = sp.album_tracks(x['id'])
                    tracks = [x["id"] for x in tracks["items"]]
                    for track in tracks:
                        cur.execute(
                            '''
                            insert or ignore into spotify
                            values (?, ?, ?, ?, ?)
                            ''',
                            (tartist, talbum, len(tracks), track, url)

                        )
                    con.commit()
                except Exception as error: 
                    print(error)
                    pass
                time.sleep(3.0)
con.close()

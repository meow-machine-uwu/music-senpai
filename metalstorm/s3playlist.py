import sqlite3
import time

import keyring
import spotipy
from spotipy.oauth2 import SpotifyOAuth


# config

SONGSPERPLAYLIST = input('please enter # of songs per playlist you want ')
PLAYLISTPREFIX = input('please enter the playlist prefix you want ')
APPEND = True

sqlitefile = 'sqlite\\metalstorm.db'

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

# login
print('logging on')
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=cid, 
                                               client_secret=csc,
                                               redirect_uri="http://localhost:8888/callback",
                                               scope=scopes))
current_user = sp.current_user()

# get playlists so we can figure out if we already made them
print('gathering playlists')
playlists = {}
offset = 0
if APPEND:
    while True:
        items = sp.current_user_playlists(offset=offset)
        offset += 50
        for item in items['items']:
            playlists[item['name']] = item
        time.sleep(3)
        if items['next'] is None: break

# connect to the step_01 database
# this will find all the matches in the search url text file (last one)
con = sqlite3.connect(sqlitefile)
cur = con.cursor()

cur.execute(
    '''
    select count(*) from spotify;
    '''
)
count = cur.fetchone()[0]
limit = int(SONGSPERPLAYLIST)
offset = 0
num = 1

while True:
    cur.execute(
        '''
        select track from spotify
        order by url
        limit ?
        offset ?;
        ''',
        (limit, offset)
    )

    offset += limit
    
    playlistname = '{1}{0:03d}'.format(num, PLAYLISTPREFIX)
    print(playlistname)
    num += 1

    tracks = list(map(lambda x: x[0], cur.fetchall()))
    print('len tracks', len(tracks))
    if len(tracks) == 0: break

    # create playlists if dne
    print('creating playlists')
    if playlistname not in playlists:
        while True:
            try:
                playlists[playlistname] = sp.user_playlist_create(
                    current_user["id"], 
                    playlistname, 
                    public=True,
                )
                print('created', playlistname)
                time.sleep(3)
                break
            except Exception as e:
                print(e)
                time.sleep(20)

    # add to playlist
    for i in range(0, len(tracks), 50):
        print('adding', i)

        while True:
            try:
                sp.user_playlist_add_tracks(
                    current_user["id"], 
                    playlists[playlistname]["id"], 
                    tracks[i:i+50]
                )
                time.sleep(5)
                break
            except Exception as e:
                print(e)
                time.sleep(20)
        print('done')
    
con.close()

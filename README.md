# music-senpai
Scrape various metal sites.

Do you have spotify? Do you want to scrape your favorite metal sites for releases and add them to a playlist? Then these scripts are for you.

I do this so smaller bands have an even chance of discovery without the spotify pay2win scheme.

IF YOU NEED HELP, PM ON DISCORD AND I CAN WALK YOU THROUGH EVERYTHING.

## Dependencies
You need three things.

Python+Pip

Firefox (for the geckodriver).

Spotify Developer ID and Secret (sign up here: https://developer.spotify.com/dashboard/login) (it takes like 10 seconds, super easy)

Once you have your spotify developer account, create a project. This project will tell you your client id and client secret which will be used later. You also want to edit the settings of your project to use the callback: http://localhost:8888/callback.

## Install dependencies
pip install spotipy
pip install selenium
pip install bs4 lxml
pip install parse
pip install unidecode

## Walkthrough
1. In the top folder, there is a file called save_secret.py. RUN THIS FIRST.
You can run it as many times as you want (in case you fudged up).
I do not and will not have any access to the keyring or any private data. 
This is why I ask you to make a spotify developer account instead of using mine.

2. Once that is set, go into the metalstorm folder. Run the scripts in order from s1crawl (for step 1: crawl), s2search (for step 2: search), and s3playlist (for step 3: playlist).

2A. crawl
    0. run: python.exe s1crawl.py
    1. s1crawl will open the firefox driver to the metalstorm site.
    2. it will wait until you set your filter criteria.
    3. once you are done setting your filters, press any button in the terminal.
    4. the driver will proceed to go to each page and save the artist/album info to the sqlite db.

2B. search
    0. run: python.exe s2search.py
    1. this is where step 1 will be important. we are using the spotify api to search albums and save the track ids from those albums for step 2C.
    2. you get terminal updates as to what the script is doing. this will not use the browser.
    3. THIS MAY TAKE A WHILE

2C. playlist
    0. run: python.exe s3playlist.py
    1. you will be asked two things:
        a. how many songs per playlist (please enter a number)
        b. what do you want the playlist prefix to be
    2. we then take tracks ids found in 2B and generate playlists.

You don't have to do step 1 each time. Just the 1st time.

## Disclaimer
I don't have the ability to automatically check and filter out racist/facist bands (although I want to). I have to do it manually at the moment. In the future, I will add this but it will make step 2A take MUCH longer.
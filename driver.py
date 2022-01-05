# App Idea: New Music App
#
# Description: This application will list all music released in the last week
# by a list of artists specified by the user. This list will be read from a file
# for now, but an extension to this project includes a front-end implementation
# that stores the list of artists.

import spotipy
import sys
import calendar
import time
import datetime as DT
import datetime
import json
from tqdm import tqdm
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth


# Returns a list of artists from the given file
def get_artists(file_name):
    artists = []
    file = open(file_name, "r")
    for line in file:  
        artists.append(line.strip())
    return artists

# Given a list of dictionaries, remove the duplicates with the same name
def remove_dups(albums):
    result = []
    result.append(albums[0])
    curr = albums[0]['name']
    i = 1
    while i < len(albums):
        if curr != albums[i]['name']:
            result.append(albums[i])
            curr = albums[i]['name']
        i += 1
    return result

# Given a beginning epoch time and the albums and singles lists, 
# return a list of sorted singles and albums released from the beginning
# time to the current epoch time
def find_music(albums, singles, begin):
    result = []
    curr_time = int(time.time())
    a_index = 0
    s_index = 0
    while a_index < len(albums) and s_index < len(singles):
        if date_to_epoch(albums[a_index]['release_date']) < begin and date_to_epoch(singles[s_index]['release_date']) < begin:
            break
        # If latest album is more recent than latest single
        if date_to_epoch(albums[a_index]['release_date']) > date_to_epoch(singles[s_index]['release_date']):
            if date_to_epoch(albums[a_index]['release_date']) >= begin:
                result.append(albums[a_index])
                a_index += 1
            else:
                break
        else:
            if date_to_epoch(singles[s_index]['release_date']) >= begin:
                result.append(singles[s_index])
                s_index += 1
            elif date_to_epoch(singles[s_index]['release_date']) < begin:
                break
    return result

# Converts a given date (YYYY-MM-DD) to epoch time
def date_to_epoch(date):
    split = date.split('-')
    return int(datetime.datetime(int(split[0]), int(split[1]), int(split[2]), 0, 0).timestamp())

# Take all music from selected artists and place all recent music into a list
def list_curr_music(name, begin, spotify):
    if name.strip() == '':
        return []
    results = spotify.search(q='artist:' + name, type='artist')
    items = results['artists']['items']
    if len(items) == 0:
        print("Code 101A: Please enter a valid artist name")
        exit()
    artist = items[0]
    if artist['name'].lower() != name.lower():
        print("Code 101B: " + name + " is not a valid artist.")
        exit()
    artist_url = artist['uri']

    # List all albums from a given artist
    results = spotify.artist_albums(artist_url, album_type='album')
    results_singles = spotify.artist_albums(artist_url, album_type='single')
    albums = results['items']
    singles = results_singles['items']

    while results['next']:
        results = spotify.next(results)
        albums.extend(results['items'])
    while results_singles['next']:
        results_singles = spotify.next(results_singles)
        singles.extend(results_singles['items'])

    albums = remove_dups(albums)
    singles = remove_dups(singles)
    # print("Albums by " + name + ":")
    # for a in albums:
    #     print(a['name'])
    # print("\nSingles by " + name + ":")
    # for s in singles:
    #     print(s['name'])

    # Find all music from a specified beginning date to the current day
    begin = int(begin.timestamp())
    res = find_music(albums, singles, begin)
    return res

################################################################################################

# Setup

spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
artists = get_artists("artists.txt")

date = DT.date.today() - DT.timedelta(days=7)
date = datetime.datetime(date.year, date.month, date.day, 0, 0)
if len(sys.argv) > 1:
    input = sys.argv[1].split("-")
    date = datetime.datetime(int(input[0]), int(input[1]), int(input[2]), 0, 0)

################################################################################################

# Create a playlist with all new music

scope = 'playlist-modify-public'
username = 'a70i492rfiv8o6375hmq6epes'

token = SpotifyOAuth(scope=scope, username=username)
spotifyObject = spotipy.Spotify(auth_manager=token)

playlist_name = 'New Music'
playlist_desc = 'All new music from your selected artists'

curr_playlist_now = spotifyObject.user_playlists(user=username)['items'][0]['name']
if curr_playlist_now != 'New Music':
    spotifyObject.user_playlist_create(user=username, name=playlist_name, public=True, description=playlist_desc)

curr_playlist = spotifyObject.user_playlists(user=username)['items'][0]['id']

song_uri_list = []

#for artist in artists:
for i in tqdm (range (len(artists)), 
               desc="Loading…", 
               ascii=False, ncols=75):
    songs = list_curr_music(artists[i], date, spotify)
    for s in songs:
        result_tracks = spotifyObject.album_tracks(album_id=s['uri'])
        # print(json.dumps(result_tracks, sort_keys=4, indent=4))
        tracklist = result_tracks['items']
        for track in tracklist:
            song_uri_list.append(track['uri'])
    # Progress bar
    

if len(song_uri_list) > 0:
    print(len(song_uri_list))
    spotifyObject.user_playlist_replace_tracks(user=username, playlist_id=curr_playlist, tracks=song_uri_list)
        

################################################################################################

# Pause and skip music on device

# scope2 = 'user-modify-playback-state'
# token2 = SpotifyOAuth(scope=scope2, username=username)
# spotifyObject2 = spotipy.Spotify(auth_manager=token2)



    



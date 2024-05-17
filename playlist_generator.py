import os
import json
import base64
import spotipy
import requests
import urllib.parse
from time import sleep
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime, timedelta
from flask import Flask, redirect, request, jsonify, session

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

#scopes = "ugc-image-upload user-read-playback-state user-modify-playback-state user-read-currently-playing app-remote-control streaming playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public user-follow-modify user-follow-read user-read-playback-position user-top-read user-read-recently-played user-library-modify user-library-read user-read-email user-read-private user-soa-link user-soa-unlink soa-manage-entitlements soa-manage-partner soa-create-partner"

scope = "user-read-currently-playing"

scope = 'user-read-currently-playing user-read-private user-read-email playlist-read-private playlist-modify-public playlist-modify-private'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=scope))

# Gets artist from text 
def get_artists_from_txt_file():

    my_file = open("artists.txt", "r") 

    data = my_file.read()  
    artist_list = data.split("\n") 

    my_file.close()

    return artist_list

def create_playlist():
    # Create playlist
    value = sp.user_playlist_create(1226802397, "Summer Smash - Spotify API")

    # print(json.dumps(value, indent=4))

    # print(value['id'])

    return value['id']

def filter_json():
    timestamp = "timestamp"
    context = "context"



    # Create a new dictionary with only the desired keys
    filtered_data = {
        timestamp: value[timestamp],
        context: value[context]
    }

    # Convert the filtered data dictionary back to a JSON string
    print(json.dumps(filtered_data, indent=4))




if __name__ == '__main__':
    artist_list = get_artists_from_txt_file()
    print(artist_list, '\n')

    # value = sp.current_user()
    # value = sp.current_user_playing_track()
    # value = sp.playlist_add_items()
    #print(json.dumps(value, indent=4))



    # Initialize an empty dictionary
    artist_dict = {}

    # Loop through artists
    for artist in artist_list:

        value = sp.search(q=artist, type="artist", market="US")

        artist_name = str(json.dumps(value["artists"]["items"][0]["name"], indent=4))[1:-1]
        artist_id = str(json.dumps(value["artists"]["items"][0]["id"], indent=4))[1:-1]

        artist_dict[artist_name] = artist_id

    print(artist_dict)

    # value = sp.search(q="Chief Keef", type="artist", market="US")
    # print(json.dumps(value["artists"]["items"][0]["id"], indent=4))
    # print(json.dumps(value["artists"]["items"][0]["name"], indent=4))

    # artist_name = str(json.dumps(value["artists"]["items"][0]["name"], indent=4))[1:-1]
    # artist_id = str(json.dumps(value["artists"]["items"][0]["id"], indent=4))[1:-1]
    # print(artist_id)
    # print(artist_name)

    # artist_dict[artist_name] = artist_id

    print(artist_dict)
 




#value = sp.artist_top_tracks()


# link = "https://open.spotify.com/playlist/5wjtNCVGUxBcS6MIX2sZQu?si=783fe4c7c53f4cfa&pt=f028bb50b95f357ed71fa9a9aadab1cb"




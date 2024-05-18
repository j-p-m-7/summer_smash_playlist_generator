import os
import json
import spotipy
import requests
from time import sleep
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

# Loads environment variables
load_dotenv()

# Gets Spotify credentials from .env
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

# Gets Setlist credentials from .env
API_KEY = os.getenv('API_KEY')

# Sets Setlist URL
BASE_URL = "https://api.setlist.fm/rest/"

# Sets user scopes
#scopes = "ugc-image-upload user-read-playback-state user-modify-playback-state user-read-currently-playing app-remote-control streaming playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public user-follow-modify user-follow-read user-read-playback-position user-top-read user-read-recently-played user-library-modify user-library-read user-read-email user-read-private user-soa-link user-soa-unlink soa-manage-entitlements soa-manage-partner soa-create-partner"
scope = "user-read-currently-playing"
scope = 'user-read-currently-playing user-read-private user-read-email playlist-read-private playlist-modify-public playlist-modify-private'

# Initializes an instance of the Spotify class as an object
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=scope))



############## Testing ##############

def filter_json():
    timestamp = "timestamp"
    context = "context"
    pass

    # Create a new dictionary with only the desired keys
    filtered_data = {
        timestamp: value[timestamp],
        context: value[context]
    }

    # Convert the filtered data dictionary back to a JSON string
    print(json.dumps(filtered_data, indent=4))

############## Testing ##############





### Spotify API ###

# Gets artist from text 
def get_artists_from_txt_file():

    # Open file
    my_file = open("artists.txt", "r") 
    
    # Puts artists in Python list
    data = my_file.read()  
    artist_list = data.split("\n") 

    my_file.close()

    return artist_list

# Creates dictionary with artist and artist id as key value pairs
def create_artist_dict(artist_list):
    # Initialize an empty dictionary
    artist_dict = {}

    # Loop through artists
    for artist in artist_list:

        # Search for artist name via Spotify Search
        value = sp.search(q=artist, type="artist", market="US")

        # Get artist name and id
        artist_name = str(json.dumps(value["artists"]["items"][0]["name"], indent=4))[1:-1]
        artist_id = str(json.dumps(value["artists"]["items"][0]["id"], indent=4))[1:-1]

        # Assign artist name and id as key value pairs in dictionary
        artist_dict[artist_name] = artist_id

    return artist_dict

# Creates dictionary with artist and artist top 10 tracks as key value pairs
def create_artist_tracks_dict(artist_dict):

    # Initialize an empty dictionary
    artist_tracks_dict = {}

    # Iterate through artist name and artist id in dictionary
    for key, value in artist_dict.items():

        # Get artist top tracks
        data = sp.artist_top_tracks(value)

        # Assign tracks variable
        tracks = data["tracks"]

        # Initalize list
        tracks_list = []

        # For track in tracks, get uri and append to list
        for track in tracks:
            uri = track["uri"]
            # value = sp.track(uri)["name"]
            # print(value)
            tracks_list.append(uri)

        # Assign artist name and list of top 10 artist tracks as key value pairs in dictionary
        artist_tracks_dict[key] = tracks_list

    print(artist_tracks_dict)

    return artist_tracks_dict

# Converts all tracks to iterable python list
def tracks_dict_to_list(tracks):
    total_tracks = []

    total_tracks = [y for x in tracks.values() for y in x]

    return total_tracks

# Creates playlist with user specified name
def create_playlist(name):

    # Create playlist
    value = sp.user_playlist_create(1226802397, name)
    print(json.dumps(value, indent=4))
    sleep(100)

    # Returns playlist id
    return value['id']

# Adds tracks to playlist
def add_tracks_to_playlist(playlist_id, list_tracks):    
    n = 0
    batch_size = 100

    while n < len(list_tracks):
        sp.playlist_add_items(playlist_id, list_tracks[n:n+batch_size])
        n += batch_size

# Runs all relevant Spotify API functions
def create_spotify_api_playlist():
    artist_list = get_artists_from_txt_file()
    print(artist_list, '\n')

    artist_dict = create_artist_dict(artist_list)
    print("\ngenerated artist_dict...\n")

    tracks_dict = create_artist_tracks_dict(artist_dict)
    print("generated tracks_dict...\n")

    tracks_list = tracks_dict_to_list(tracks_dict)
    print("generated tracks_list...\n")

    playlist_id = create_playlist("Summer Smash - Spotify API")
    print("created playlist...\n")
    
    add_tracks_to_playlist(playlist_id, tracks_list)   
    print("added tracks to playlist!\n")







### Setlist API ###

# Gets artist
def get_artist(artist_name):
    url = BASE_URL + '1.0/search/artists'

    params = {
        #'artistName': artist_name,
        'artistMbid': 'e4a51f17-a57b-47b1-b37b-f552d0f8e9e6',
        'p': '1',
        'sort': 'sortName'
    }

    headers = {
        'Accept': 'application/json',
        'x-api-key': API_KEY
    }

    response = requests.get(url, headers=headers, params=params)

    return response.json()



# Runs all relevant Setlist API functions
def create_setlist_api_playlist():

    # Creates playlist with user specified name
    playlist_id = create_playlist("Summer Smash - Setlist API")
    print("created playlist...\n")

# Main
if __name__ == '__main__':

    # create_spotify_api_playlist()
    # create_setlist_api_playlist()

    artist_list = get_artists_from_txt_file()

    print(artist_list, '\n')

    artist = get_artist(artist_list[0])

    print(json.dumps(artist, indent=4))

    
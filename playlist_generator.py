import os
import re
import json
import spotipy
import requests
from time import sleep
from dotenv import load_dotenv
from collections import Counter
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



# Testing
def filter_json(value):
    ############################ Testing ############################
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
    ############################ Testing ############################
# Testing




# Reads the .env file and returns a dictionary of the environment variables
def read_env_file():
    env_vars = {}
    if os.path.exists('.env'):
        with open('.env', 'r') as env_file:
            lines = env_file.readlines()
            for line in lines:
                key, value = line.strip().split('=', 1)
                env_vars[key] = value
    return env_vars

# Sets up the API keys for Spotify and Setlist
def setup_api_keys():
    print("Setting up API keys for Spotify and Setlist.")

    env_vars = read_env_file()

    spotify_client_id = input(f"Enter your Spotify Client ID [{env_vars.get('SPOTIFY_CLIENT_ID', '')}]: ") or env_vars.get('SPOTIFY_CLIENT_ID', '')
    spotify_client_secret = input(f"Enter your Spotify Client Secret [{env_vars.get('SPOTIFY_CLIENT_SECRET', '')}]: ") or env_vars.get('SPOTIFY_CLIENT_SECRET', '')
    setlist_api_key = input(f"Enter your Setlist API Key [{env_vars.get('SETLIST_API_KEY', '')}]: ") or env_vars.get('SETLIST_API_KEY', '')

    env_content = f"""
    SPOTIFY_CLIENT_ID={spotify_client_id}
    SPOTIFY_CLIENT_SECRET={spotify_client_secret}
    SETLIST_API_KEY={setlist_api_key}
        """

    with open('.env', 'w') as env_file:
        env_file.write(env_content.strip())

    print(".env file created successfully with your API keys!")

# Creates the Spotipy object instance
def load_and_initialize_spotify():
    load_dotenv()

    # Gets Spotify credentials from .env
    CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
    REDIRECT_URI = os.getenv('REDIRECT_URI')

    # Sets user scopes
    scope = 'user-read-currently-playing user-read-private user-read-email playlist-read-private playlist-modify-public playlist-modify-private'

    # Initializes an instance of the Spotify class as an object
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                                   client_secret=CLIENT_SECRET,
                                                   redirect_uri=REDIRECT_URI,
                                                   scope=scope))
    return sp







################################## Spotify API ##################################

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
            tracks_list.append(uri)

        # Assign artist name and list of top 10 artist tracks as key value pairs in dictionary
        artist_tracks_dict[key] = tracks_list

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
def created_playlist_with_spotify_api():
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

#################################################################################





################################## Setlist API ##################################

# Function to check if an artist exists on Spotify
def check_artist_exists(artist_name):
    results = sp.search(q=f'artist:{artist_name}', type='artist')
    return len(results['artists']['items']) > 0

# If artist does exist, add them to the list in this function
def add_artists_to_list(artists):
    # Lists to hold results
    exists_on_spotify = []
    does_not_exist_on_spotify = []

    # Check each artist
    for artist in artists:

        if check_artist_exists(artist):
            exists_on_spotify.append(artist)
    
    # else:
    #     does_not_exist_on_spotify.append(artist)

    return exists_on_spotify

# Gets artist ID
def get_artist_mbid(artist_name):

    url = 'https://musicbrainz.org/ws/2/artist/'

    params = {
        'query': artist_name,
        'fmt': 'json'
    }

    headers = {
        'User-Agent': 'YourAppName/1.0 (your-email@example.com)'
    }

    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()

        if 'artists' in data and data['artists']:
            # Assuming the first result is the most relevant one
            artist = data['artists'][0]
            return artist['id']
        
        else:
            return None
        
    else:
        print(f"Error: {response.status_code}")
        return None

# Gets artist last 20 setlists
def get_artist_setlists(artist_mbid):

    url = BASE_URL + '1.0/artist/' + artist_mbid + '/setlists'
    
    params = {
        #'artistName': artist_name,
        'artistMbid': artist_mbid,
        'p': '1',
    }

    headers = {
        'Accept': 'application/json',
        'x-api-key': API_KEY
    }

    response = requests.get(url, headers=headers, params=params)

    return response.json()

# Creates artist dictionary with artist name and artist mbid as key value pairs
def create_artist_dict_sl(artist_list):

    artist_dict = {}

    for index, artist_name in enumerate(artist_list):

        if (index + 1) % 15 == 0:
            sleep(3)
            print("processed 15 artists...\n")   

        mbid = get_artist_mbid(artist_name)
        artist_dict[artist_name] = mbid
        sleep(.1)

    print("done!\n")

    print(artist_dict)

    return artist_dict

# Removes NoneType values
def clean_artist_dict(artist_dict):

    for artist_name in list(artist_dict.keys()):
        if artist_dict[artist_name] == None:
            del artist_dict[artist_name]

    
    return artist_dict

# Creates dictionary of artists and their top 20 tracks from last 20 sets
def create_artist_tracks_dict_sl(artist_dict):
    artist_tracks_dict = {}
    
    for index, (artist_name, artist_mbid) in enumerate(artist_dict.items()):

        sleep(.9)

        if (index + 1) == 2:
            sleep(3)

        if (index + 1) % 10 == 0:
            sleep(3)
            print("Processed 10 artists and acquired the top 20 tracks for each...\n")

        #print(index, artist_name, artist_mbid)

        # Gets artist
        artist_setlists = get_artist_setlists(artist_mbid)

        if "code" not in artist_setlists:

            # Find setslists
            value = artist_setlists
            songs = []


            # Loop through artists sets (default is 20)
            for i in range(len(value["setlist"])):

                # Ensure sets are not empty
                if value["setlist"][i]["sets"]["set"] != []:

                    # Filter to sets where the song number is between 5 and 30
                    if 5 < len(value["setlist"][i]["sets"]["set"][0]["song"]) < 30:

                        # Loop through songs
                        for song in value["setlist"][i]["sets"]["set"][0]["song"]:
                            
                            # Add song to songs list
                            songs.append(song["name"])

            # Prints list and len

            songs = [x for x in songs if x]

            #print("Number of songs", len(songs),'\n')

            # Count occurrences of each song
            song_counts = Counter(songs)

            # Sort the dictionary based on count of occurrences
            sorted_song_counts = dict(sorted(song_counts.items(), key=lambda x: x[1], reverse=True))

            # Extract top 10 most common songs
            top_songs = list(sorted_song_counts.keys())[:10]

            artist_tracks_dict[artist_name] = top_songs

    print("Acquired all top 20 tracks for each of the", len(artist_tracks_dict.keys()), "artists")

    return artist_tracks_dict

# Remove punctuation and convert to uppercase
def normalize(s):
    return re.sub(r'[^\w\s]', '', s).upper().strip()

# Creates a URIs list of all tracks by all artists
def get_uris_for_artist_tracks(artist_tracks_dict):
    # Loop through artists
    tracks_list = []
    uris_list = []
    conflicts = []
    index = 1

     # Handles edge cases
     # These tracks are on Spotify but are not by the artist listed in the JSON from the Setlist API
     # TODO -- rework this to be more dynamic
    known_tracks = {
    "BEEN BALLIN": "spotify:track:2EK77Jcm0Pvzd5nonAYOHX",
    "OFF THE GRID": "spotify:track:6LNoArVBBVZzUTUiAX2aKO",
    "MISS THE RAGE": "spotify:track:5n4FTCMefvyKUjeWumdaWv",
    # Add more known tracks here
    }

    # Tracks that do not exist on Spotify
    # TODO -- rework this to be more dynamic
    nonexistent_tracks = ['FOOL YA']

    # List to hold tracks that were not found
    not_found_tracks = []

    # Loop through artist name and tracks in dictionary
    for artist_name, tracks in artist_tracks_dict.items():

        # List to hold tracks that were not found for the artist
        artist_not_found_tracks = []

        # If artist has tracks
        if artist_tracks_dict[artist_name] != []:

            # Set to hold featured artists
            featured_artists = set()

            # Loop through tracks
            for queried_song in tracks:

                # Normalize queried song to be uppercase and without punctuation
                normalized_song = normalize(queried_song)

                # Queries
                query_1 = f'track:{queried_song}, artist:{artist_name}'
                query_2 = f'{queried_song} {artist_name}'
                song = f"track:{queried_song}"

                # If song is in known tracks, add it to the list
                # This skips the API call and saves time
                # Use this for songs that are in the API but don't have the correct artist listed
                if normalized_song in known_tracks:
                    uri = known_tracks[normalized_song]
                    uris_list.append(uri)
                    tracks_list.append(queried_song)
                    continue

                # If song is in nonexistent tracks, add it to the list
                # This skips the API call and saves time
                # Use this for songs that are not found in the API
                elif normalized_song in nonexistent_tracks:
                        # No results were returned for the track
                        artist_not_found_tracks.append(queried_song)
                        continue  # Skip to the next track

                # Else if song is not in known tracks or nonexistent tracks, query the Spotify API
                else:
                    value = sp.search(q=query_2,offset=0, type="track")            

                # Loop through tracks
                for i in range(len(value["tracks"])):
                    
                    # List for all artists on one tracks
                    track_artists=[]

                    # Get name of track
                    returned_song = value["tracks"]["items"][i]["name"]

                    if normalize(queried_song) in normalize(returned_song):
                        
                        # Lists to hold track artists
                        track_artist_info = value["tracks"]["items"][i]["artists"]
                        list_of_artists = [artist["name"].upper() for artist in track_artist_info]
                        track_artists = [artist for artist in list_of_artists]

                        # If artist name in tracks artist, add it to the list of songs to be added
                        if artist_name.upper() in track_artists:

                            # Assign uris and track names
                            uri = value["tracks"]["items"][i]["uri"]
                            track = value["tracks"]["items"][i]["name"]

                            # Append to lists
                            # Uris list will be used to add tracks to playlist
                            uris_list.append(uri)
                            tracks_list.append(track)

                            # Adds featured artists to a set
                            # This is done such that if an artist played another artists track at a concert (via Setlist API) the track will be added  
                            featured_artists.update([artist for artist in list_of_artists if artist.upper() != artist_name.upper()])
                             
                        # Include tracks played at concert that are by artists other than current artist
                        elif any(item in track_artists for item in list(featured_artists)):
                            uri = value["tracks"]["items"][i]["uri"]
                            track = value["tracks"]["items"][i]["name"]

                            uris_list.append(uri)
                            tracks_list.append(track)   

                        # Account for weird track that includes Chief Keef but not listed in JSON
                        elif query_2.lower() == "been ballin' chief keef":
                            #print("Featured", featured_artists)
                            
                            uri = value["tracks"]["items"][i]["uri"]
                            track = value["tracks"]["items"][i]["name"]

                            uris_list.append(uri)
                            tracks_list.append(track)  
                            
                        # Else if song not found
                        else:
                            track = queried_song.upper()
                            track_artists = str([artist_name.upper()]) + " was not"
                            artist_not_found_tracks.append(track)
                        
                        # Break once correct values found
                        break

                    # Else if song not found
                    else:
                        track = queried_song.upper()
                        track_artists = str([artist_name.upper()]) + " was not"
                        artist_not_found_tracks.append(track)

                        # Break once correct values found
                        break
               
            # Turn set into list
            unique_featured_artists = list(featured_artists)

            # Prints
            print("Unique featured artists for",artist_name,":\n", unique_featured_artists,'\n')    
            print("Songs not found for", artist_name + ":\n", artist_not_found_tracks)            
        
        # Append to list of tracks not found
        not_found_tracks.append(artist_not_found_tracks)

    return uris_list

# Runs all relevant Setlist API functions
def created_playlist_with_setlist_api():

    # Gets Setlist credentials from .env
    API_KEY = os.getenv('SETLIST_API_KEY')
    # Sets Setlist URL
    BASE_URL = "https://api.setlist.fm/rest/"


    artists = get_artists_from_txt_file()
    print("Loaded", len(artists),"from text file.",'\n')

    artist_list = add_artists_to_list(artists)
    print("Filtered artists from text file to only artists that exist on Spotify")
    print("The subsequent list contains", len(artist_list), "artists." '\n')

    artist_dict = create_artist_dict_sl(artist_list=artist_list)
    print("Created dictionary containing artists and their unique MBID\n")

    artist_dict = clean_artist_dict(artist_dict)
    print("Cleaned dictionary to remove NoneType values (artists with no MBID)\n")

    artist_tracks_dict = create_artist_tracks_dict_sl(artist_dict)
    print('Created dictionary containing artists and their top 20 tracks from last 20 sets\n')

    uris_list = get_uris_for_artist_tracks(artist_tracks_dict)
    print("Created list of URIs for all tracks by all artists\n")

    # Creates a playlist with the name "Summer Smash - Setlist API" and returns the id
    playlist_id = create_playlist("Summer Smash - Setlist API")
    print("Created playlist...\n")

    add_tracks_to_playlist(playlist_id, uris_list)
    print("Added tracks to playlist successfully!\n")

    # Creates playlist with user specified name
    playlist_id = create_playlist("Summer Smash - Setlist API")
    print("created playlist...\n")

#################################################################################




# Main Function
# Filter this function to only run the functions you want to test
# IE if you only want to run the Setlist API functions, comment out the Spotify API functions using the '#' symbol
if __name__ == '__main__':

    # Sets up API keys
    # TODO - update this function to be more dynamic
    # setup_api_keys()
    # Initializes Spotify object
    sp = load_and_initialize_spotify()

    # Creates playlist with Spotify API
    created_playlist_with_spotify_api()
    # Creates playlist with Setlist API
    created_playlist_with_setlist_api()

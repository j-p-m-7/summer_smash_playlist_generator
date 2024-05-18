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



# Gets artist
def get_artist_setlists(artist_mbid):
    url = BASE_URL + '1.0/artist/' + artist_mbid + '/setlists'
    print(url)
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

    return artist_dict

# Runs all relevant Setlist API functions
def create_setlist_api_playlist():

    # Creates playlist with user specified name
    playlist_id = create_playlist("Summer Smash - Setlist API")
    print("created playlist...\n")

# Main
if __name__ == '__main__':
    pass
    # create_spotify_api_playlist()
    # create_setlist_api_playlist()

    artist_list = get_artists_from_txt_file()
    print(artist_list, '\n')

    artist_dict = create_artist_dict_sl(artist_list)
    #artist_dict = {'Travis Scott': 'e4a51f17-a57b-47b1-b37b-f552d0f8e9e6', 'Big Sean': '942a9807-9c1a-4a0e-a285-1fde2c5be9d1', 'Destroy Lonely': '987d3d86-0d7a-4292-ae96-a8d59e456436', 'Flo Milli': '21dab5d7-3bda-4f72-a054-6379729dcb62', 'That Mexican OT': '115dc8c9-cb04-4dd6-859e-39739eb57215', 'BKTHERULA': '4b62f375-7bff-49c2-ae7e-24b8de579ba8', 'Black Kray': '030cf5e5-b5d8-4a66-a291-0a7fe4b4b075', 'BLP Kosher': '11be1aca-4f6e-4880-9960-8064587f3531', 'Famous Dex': 'c34cfbd6-1df2-4865-96d9-e3bb4fe0577d', 'Clip': '0d051286-f737-464b-86a8-1e5ed6ceb2a2', 'Lazer Dim 700': '95b0d5b3-2815-4ffc-9bfe-2ace8300b463', 'Osamason': '35214d53-009b-45d9-8a00-6664325b9e2a', 'Vonoff1700': 'f528202c-3c0a-4094-a3c8-9cbf24574351', 'BossFTR': None, 'Elijah Wallace': '211c0cac-1410-4c68-98f4-0a8c6370b07a', 'Kami': 'a4ab2092-0ff9-4914-bc95-27e13058a5e2', 'Don Toliver': 'a0723a3c-4135-438e-85c5-012712144ede', 'Sheck Wes': '07ab04d4-bdbc-4c93-bfb2-457693a4ff94', 'Sofaygo': '654d48fb-4fe4-472d-81e6-039e54f2f27b', 'Chase B': 'fd9ae276-af7a-4ca1-ba33-02696ece031d', 'Playboi Carti': '2baf3276-ed6a-4349-8d2e-f4601e7b2167', 'Kodak Black': '5ec1ecc6-4535-4911-a27a-e26343f4a189', 'Lil Tecca': 'e6fdf3f9-8077-4126-b0cf-94da9a8b627e', 'Lucki': '9ccaca30-60aa-4890-ae6c-ab55225ee274', 'Ski Mask the Slump God': 'faf916e0-ffc5-4345-a10b-b79ed8c9b8f6', 'Bia': '2c3ddff8-0de5-412a-8f0c-8925f84d5a9a', 'Lil Skies': '8328b279-1863-487b-976a-58a62b85220a', 'Mick Jenkins': '64c4dfcc-ba2b-4036-ac01-1636ae15ebb8', 'Paris Texas': '22685c6b-2900-4fc0-a030-d56c00cc0601', 'Rich Amiri': '8ae4189a-67e8-4466-91cb-8902f2b72ab2', 'Baby KIA': 'd7af667a-1ce4-4e0c-9ca5-de921ee70a40', 'Cash Cobain': '4f57372b-2054-4722-a534-a99ab2598120', 'Nettspend': '4585749c-5489-4699-9daf-1ffa9717179f', 'TiaCorine': 'ad45f650-0ee6-431f-bb2d-4b340befd73e', 'XavierSoBased': '155cfd40-dcde-471e-acc0-32179916165c', '2Rare': 'a46875f6-dd94-464a-b3da-761e5fddbe92', 'Freddy Got Magic': 'da4f76e8-9b35-45b0-962f-99815fb1f777', 'Uneek': 'eee7b205-c228-4f3d-b0b6-68165b66736a', '$AM': 'ae215dbf-5cba-4c33-8882-5b3c65a98c29', 'Chief Keef': '9118f524-be76-4eaf-875c-ccf15e2a2ad6', 'Denzel Curry': '5f95440d-7737-4a36-9bcf-c05337f7129b', 'JID': 'd616b606-cf6a-4b6e-ab0f-e253b8db6610', 'Ken Carson': '860d7dc2-618d-437e-a3bb-7b91c2d40095', 'Lil Yachty': 'a668565b-41b8-44a8-9d5c-8e609dbf69fc', 'Waka Flocka Flame': '59eda569-b380-4958-b98c-051d1667b3e1', 'YG Marley': '3ac35781-a75c-42d7-a053-ae47e7e64314', 'Anycia': '8e504b01-438a-49d5-ac71-032d2a4e86cb', 'BabyTron': 'dc1e73d5-4ff6-4c40-bbd6-493f4dd0d047', 'Bashfortheworld': '3803bbb5-38c3-400d-aec8-3985cdd84cbe', 'Homixide Gang': '6e61b52a-9001-4638-9f10-f684c180a749', 'Lil B': '1550f952-c91b-40d7-9b4d-d26a259ee932', 'Hardrock': 'ed8bfe40-0d3a-452b-bc97-9cbf9c077fda', 'ICYTWAT': '0f1f484f-63a6-4c32-bf33-c65054915aa9', 'Joeyy': 'c80fa3a7-51b3-45e5-9711-6ae15fe5c522', 'Laundry Day': 'f3141f03-a60c-4831-8486-1d0f883001db', 'Lil Gnar': 'ac6a425c-35c3-4fd3-bcb6-39075bf2845a', 'Robb Bank$': 'decaf88d-365d-4441-bfef-f3fc8a7eac21', 'Fukuyurpain': None, 'Shed Theory': 'b9503776-04f8-467b-9ce9-62564adb780d', 'Zack Bia': 'c66efab7-0615-4387-b6d3-7bfe549d5017', 'Kerwin Frost': '77a641d5-7f82-4fe0-9b2d-59ed00d9061b', 'F1LTHY': '394d497b-e36d-4203-8c7c-1015cf9891dd', 'DJ Scheme': '5e1ef0b7-c6fe-4238-b99d-08833269a763', 'GloupJake': None}
    print(artist_dict)


    ## Iterate through all last 20 setlists, grab only ones where the total songs > 20
    # value = get_artist_setlists(mbid)
    # print(len(value["setlist"][0]["sets"]["set"][0]["song"]))











    # # Specify the filename
    # filename = "artist_info.json"

    # # Write JSON data to file
    # with open(filename, 'w') as file:
    #     json.dump(value, file, indent=4)

    # print(f"JSON data has been written to {filename}")



    # artist_list = get_artists_from_txt_file()

    # print(artist_list, '\n')

    # artist = get_artist(artist_list[0])

    # print(json.dumps(artist, indent=4))

    
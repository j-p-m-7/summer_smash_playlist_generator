import os
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

    #print(response.status_code)



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

            # Extract top 15-20 most common songs
            top_songs = list(sorted_song_counts.keys())[:20]

            #print("Here are the top", len(top_songs), "songs:\n", top_songs,'\n\n\n')

            artist_tracks_dict[artist_name] = top_songs


        #print('\n',artist_tracks_dict)

    #print(json.dumps(artist_tracks_dict, indent=4))

    # # Specify the filename
    # filename = "artist_tracks_dict.json"

    # # Write JSON data to file
    # with open(filename, 'w') as file:
    #     json.dump(artist_tracks_dict, file, indent=4)

    #print(f"JSON data has been written to {filename}")
    print("Acquired all top 20 tracks for each of the", len(artist_tracks_dict.keys()), "artists")

    return artist_tracks_dict

# Creates a URIs list of all tracks by all artists
def placeholder_function():
    pass



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





    # artists = get_artists_from_txt_file()
    # print("Loaded", len(artists),"from text file.",'\n')

    # artist_list = add_artists_to_list(artists)
    # print("Filtered artists from text file to only artists that exist on Spotify")
    # print("The subsequent list contains", len(artist_list), "artists." '\n')

    #artist_dict = create_artist_dict_sl(artist_list=artist_list)
    # print("Created dictionary containing artists and their unique MBID\n")

    # artist_dict = {'Travis Scott': 'e4a51f17-a57b-47b1-b37b-f552d0f8e9e6', 'Playboi Carti': '2baf3276-ed6a-4349-8d2e-f4601e7b2167', 'Chief Keef': '9118f524-be76-4eaf-875c-ccf15e2a2ad6', 'Don Toliver': 'a0723a3c-4135-438e-85c5-012712144ede', 'Sheck Wes': '07ab04d4-bdbc-4c93-bfb2-457693a4ff94', 'Sofaygo': '654d48fb-4fe4-472d-81e6-039e54f2f27b', 'Chase B': 'fd9ae276-af7a-4ca1-ba33-02696ece031d', 'Big Sean': '942a9807-9c1a-4a0e-a285-1fde2c5be9d1', 'Destroy Lonely': '987d3d86-0d7a-4292-ae96-a8d59e456436', 'Flo Milli': '21dab5d7-3bda-4f72-a054-6379729dcb62', 'That Mexican OT': '115dc8c9-cb04-4dd6-859e-39739eb57215', 'Kodak Black': '5ec1ecc6-4535-4911-a27a-e26343f4a189', 'Lil Tecca': 'e6fdf3f9-8077-4126-b0cf-94da9a8b627e', 'Lucki': '9ccaca30-60aa-4890-ae6c-ab55225ee274', 'Ski Mask The Slump God': 'faf916e0-ffc5-4345-a10b-b79ed8c9b8f6', 'Denzel Curry': '5f95440d-7737-4a36-9bcf-c05337f7129b', 'JID': 'd616b606-cf6a-4b6e-ab0f-e253b8db6610', 'Ken Carson': '860d7dc2-618d-437e-a3bb-7b91c2d40095', 'Lil Yachty': 'a668565b-41b8-44a8-9d5c-8e609dbf69fc', 'Waka Flocka Flame': '59eda569-b380-4958-b98c-051d1667b3e1', 'YG Marley': '3ac35781-a75c-42d7-a053-ae47e7e64314', 'Bktherula': '4b62f375-7bff-49c2-ae7e-24b8de579ba8', 'Black Kray': '030cf5e5-b5d8-4a66-a291-0a7fe4b4b075', 'BLP Kosher': '11be1aca-4f6e-4880-9960-8064587f3531', 'Famous Dex': 'c34cfbd6-1df2-4865-96d9-e3bb4fe0577d', 'BIA': '2c3ddff8-0de5-412a-8f0c-8925f84d5a9a', 'Lil Skies': '8328b279-1863-487b-976a-58a62b85220a', 'Paris Texas': '22685c6b-2900-4fc0-a030-d56c00cc0601', 'Rich Amiri': '8ae4189a-67e8-4466-91cb-8902f2b72ab2', 'Anycia': '8e504b01-438a-49d5-ac71-032d2a4e86cb', 'Babytron': 'dc1e73d5-4ff6-4c40-bbd6-493f4dd0d047', 'Bashfortheworld': '3803bbb5-38c3-400d-aec8-3985cdd84cbe', 'Homixide Gang': '6e61b52a-9001-4638-9f10-f684c180a749', 'Lil B': '1550f952-c91b-40d7-9b4d-d26a259ee932', 'Clip': '0d051286-f737-464b-86a8-1e5ed6ceb2a2', 'Lazer Dim 700': '95b0d5b3-2815-4ffc-9bfe-2ace8300b463', 'Osamason': '35214d53-009b-45d9-8a00-6664325b9e2a', 'Vonoff1700': 'f528202c-3c0a-4094-a3c8-9cbf24574351', 'Baby KIA': 'd7af667a-1ce4-4e0c-9ca5-de921ee70a40', 'Cash Cobain': '4f57372b-2054-4722-a534-a99ab2598120', 'Nettspend': '4585749c-5489-4699-9daf-1ffa9717179f', 'Tiacorine': 'ad45f650-0ee6-431f-bb2d-4b340befd73e', 'Xaviersobased': '155cfd40-dcde-471e-acc0-32179916165c', 'Hardrock': 'ed8bfe40-0d3a-452b-bc97-9cbf9c077fda', 'ICYTWAT': '0f1f484f-63a6-4c32-bf33-c65054915aa9', 'Joeyy': 'c80fa3a7-51b3-45e5-9711-6ae15fe5c522', 'Laundry Day': 'f3141f03-a60c-4831-8486-1d0f883001db', 'Lil Gnar': 'ac6a425c-35c3-4fd3-bcb6-39075bf2845a', 'Robb Bank$': 'decaf88d-365d-4441-bfef-f3fc8a7eac21', 'Bossftr': None, 'Elijah Wallace': '211c0cac-1410-4c68-98f4-0a8c6370b07a', 'Kami': 'a4ab2092-0ff9-4914-bc95-27e13058a5e2', '2Rare': 'a46875f6-dd94-464a-b3da-761e5fddbe92', 'Freddy Got Magic': 'da4f76e8-9b35-45b0-962f-99815fb1f777', 'Uneek': 'eee7b205-c228-4f3d-b0b6-68165b66736a', '$AM': 'ae215dbf-5cba-4c33-8882-5b3c65a98c29', 'Shed Theory': 'b9503776-04f8-467b-9ce9-62564adb780d', 'Zack Bia': 'c66efab7-0615-4387-b6d3-7bfe549d5017', 'Filthy': '4ec6a35c-624c-49f2-8f2b-e6a9e8ddfda4', 'DJ Scheme': '5e1ef0b7-c6fe-4238-b99d-08833269a763'}

    # artist_dict = clean_artist_dict(artist_dict)
    #print("Cleaned dictionary to remove NoneType values (artists with no MBID)\n")




    #################################################### testing ####################################################


    #artist_tracks_dict = {'Travis Scott': ['FE!N', 'NO BYSTANDERS', 'SICKO MODE', 'I KNOW ?', 'goosebumps', 'BUTTERFLY EFFECT', 'Antidote', 'TOPIA TWINS', 'HYAENA', 'MODERN JAM', 'MY EYES', 'TELEKINESIS', 'Mo Bamba', 'Type Shit', 'Cinderella', 'lose', 'MELTDOWN', 'Trance', 'Bandit', 'Turn Yo Clic Up'], 'Playboi Carti': ['Sky', 'Stop Breathing', 'Rockstar Made', 'Off the Grid', 'On That Time', 'JumpOutTheHouse', 'Flex Up', 'No Sl33p', 'R.I.P.', 'Miss The Rage', 'Teen X', 'New N3on', 'F33l Lik3 Dyin', 'Control', 'Shoota', 'R.I.P Fredo', 'Location', 'Die4Guy', 'Wokeuplikethis*', 'FlatBed Freestyle'], 'Chief Keef': ['Faneto', 'Love Sosa', 'War', 'Earned It', "Been Ballin'", "I Don't Like", 'Let Me See', 'Save That Shit', 'Hadouken', 'Kobe', 'Love No Thotties', 'Status', '3Hunna', 'Fool Ya', 'Close That Door', 'Hallelujah', "Hate Bein' Sober", 'Understand Me', 'Action Figures', 'Tec'], 'Don Toliver': ['Bandit', 'After Party', 'Too Many Nights', 'Private Landing', "CAN'T SAY", 'Lemonade', "I Can't Save You (interlude)", 'Cardigan', 'HAD ENOUGH', 'No Pole', 'WHAT TO DO?', 'Smoke', 'GANG GANG', 'No Idea', 'Attitude', 'Bus Stop', 'Around Me', 'What You Need', 'Embarrassed', 'FIELD TRIP'], 'Sheck Wes': ['GANG GANG', 'Stick', 'NO BYSTANDERS', 'Mo Bamba', 'Live Sheck Wes', 'Gmail', 'LFG!', 'Fuck Everybody', 'Enzo', 'Do That', 'Veteran', 'FE!N', 'Beast', 'Sheck Jesus', 'Hard in da Paint', 'Amped', 'Sicko Mode', 'Chippi Chippi', 'PAIN!'], 'Sofaygo': ['Hell Yeah', 'ON THE MOON', 'WE GOOD', 'BACKSEAT', 'YE', 'Off the Map', '4SUM+', 'Stay Awake', 'Smoke', 'MP5', 'Everyday', 'Knock Knock', 'AFTER DARK', 'Shut Up!', 'WHAT YOU WANT', 'F A POST', 'BEAUTIFUL ROCKSTAR', 'PURE', 'RC', 'Cards (Shut Up!)'], 'Chase B': ['Lemonade', 'Ring Ring', 'Know Yourself', 'Superhero (Heroes & Villains)', 'Sky', 'Just Wanna Rock', 'Rich Flex', 'FRANCHISE', 'Mo Bamba', 'FRANCHISE (REMIX)', 'm.A.A.d city', "Can't Tell Me Nothing", 'MAYDAY!', 'Mamacita', 'Work (Remix)', 'Look at Me!', 'Grove St. Party'], 'Big Sean': ['All Me', 'Blessings', 'Mercy', 'My Last', 'Bounce Back', "I Don't Fuck With You", 'Paradise', 'Clique', 'BIG BANK', 'Beware', 'I Know', "I Don't Like", 'Play No Games', 'Sanctified', 'Dance (A$$)', 'Wolves', 'Precision', 'One Man Can Change the World', 'Why Would I Stop?', 'Moves'], 'Destroy Lonely': ['how u feel?', 'came in wit', 'BLITZ', 'NEVEREVER', 'FAKENGGAS', 'raver', 'by the pound', 'NOSTYLIST', 'if looks could kill', 'biggest problem', 'all the time', 'fly sht', 'DANGEROUS', 'TURNINUP', 'VTMNTSCOAT', 'new new', 'passenger', 'which one', 'chris paul', 'catch a kill'], 'Flo Milli': ['Conceited', 'We Not Humping', 'Bed Time', 'Rodeo', 'Like That Bitch', 'Beef FloMix', 'I Am', 'In the Party', 'May I', 'Flo Milli Freestyle', 'Roaring 20s', 'Fruit Loop', 'Big Steppa', 'One Margarita (Margarita Song)', 'Mean', 'Pockets Bigger', 'Weak', 'Bundles 2', 'Bundles', 'You Never Wanna Lose Me'], 'That Mexican OT': ['Johnny Dang', 'V-Man', 'September 8th', '02.02.99', 'Cowboy Killer', 'Point Em Out', 'La cobra', 'Breannan', 'Barrio', 'Twisting Fingers', 'Skelz', 'Hit List', 'Bow down', 'Opp or 2'], 'Kodak Black': ['No Flockin', 'Super Gremlin', 'ZEZE', 'Roll in Peace', 'Skrilla', 'Tunnel Vision', 'Wake Up in the Sky', 'There He Go', "Can't Stop Won't Stop", '300 Blackout', "Transportin'", 'Walk', 'Versatile', 'First Show', 'Jayda Wayda', 'Rocketman', 'm.A.A.d city', 'Faneto', 'Lucid Dreams', 'Poland'], 'Lil Tecca': ['500lbs', 'Yves', 'HVN ON EARTH', 'Gist', 'Never Left', 'Did It Again', 'Diva', 'Love Me', 'Ransom', 'Fell in Love', 'TEC', 'Real Discussions', 'CHOPPA SHOOT THE LOUDEST', 'Out of Love', 'DUI', 'REPEAT IT', 'LOT OF ME', 'Down With Me', 'Bossanova', 'Shots'], 'Lucki': ['COINCIDENCE', 'GEEKED N BLESSED', 'RIP Act', 'More Than Ever', 'U.G.K', 'TUNE & SCOTTY', '13', 'Sunset', 'New Drank', 'Faith', 'Y NOT?', 'NEPTUNE V.S INDUSTRY', 'Out My Way', 'Peach Dream', 'DNA', 'NOTICED YA', 'Greed', 'MADE MY DAY', 'Unlimited', '4 the Betta'], 'Ski Mask The Slump God': ['Legends', 'Nuketown', 'Take a Step Back', 'SAD!', 'Look at Me!', 'Jocelyn Flores', 'Faucet Failure', 'Catch Me Outside', 'RIP Roach', 'LA LA', 'BabyWipe', 'H2O', 'So High', 'Florida Water', 'How You Feel? (Freestyle)', 'Achoo!', 'Shibuya (Japan)', 'Japan', 'Cat Piss', 'Off the Wall!'], 'Denzel Curry': ['Walkin', "Ain't No Way", 'BLACK BALLOONS | 13LACK 13ALLOONZ', 'RICKY', 'Ultimate', 'CLOUT COBAIN | CLOUT CO13A1N', 'WISH', 'SUMO | ZUMO', 'Dog Food', 'DIET_', 'GOATED.', 'BLOOD ON MY NIKEZ', 'Hate Government', 'ULT', 'SWITCH IT UP | ZW1TCH 1T UP', 'Threatz', "G's Up", 'Hit the Floor', 'SKED', 'Lonely Man'], 'JID': ['NEVER', 'Raydar', 'Dance Now', 'Workin Out', 'Down Bad', 'Off Deez', '151 Rum', 'Surround Sound', 'Stick', 'Crack Sandwich', 'Bruddanem', 'Costa Rica', 'Off da Zoinkys', 'Kody Blu 31', 'Galaxy', 'Just in Time', 'Sistanem', 'Stars', 'EdEddnEddy', 'Wells Fargo'], 'Ken Carson': ['Freestyle 2', 'Rock N Roll', 'i need u', 'Yale', 'Go', 'Hella', 'Freestyle 3', 'Shoot', 'Teen Bean', 'Run + Ran', "It's Over", 'PDBMH', 'Clutch', 'Paranoid', 'money & sex', 'Nobody', 'X', 'Hardcore', 'Lose It', 'Me N My Kup'], 'Lil Yachty': ['drive ME crazy!', 'pRETTy', 'In the Air Tonight', 'the ride-', 'sAy sOMETHINg', 'sHouLd i B?', 'The Alchemist.', 'the BLACK seminole.', 'Coffin', 'Broccoli', 'Flex Up', 'Get Dripped', 'Yacht Club', 'NBAYOUNGBOAT', 'Minnesota', 'Poland', 'Strike (Holster)', 'Gimme da Lite', 'One Night', 'WE SAW THE SUN!'], 'Waka Flocka Flame': ['No Hands', 'Hard in da Paint', 'Wild Boy', 'Grove St. Party', 'Turn Down for What', 'Look at Me!', 'Round of Applause', 'Karma', 'Rooster in My Rari', 'Clap', 'Mo Bamba', 'YuNg BrAtZ', "Bustin' at 'em", 'Wasted', 'Bring It Back', 'Make It Rain', 'Ayy Ladies', "O Let's Do It", 'Just Wanna Rock', 'dashstar*'], 'YG Marley': ['Opening Jam', 'Marching to Freedom', 'Running to a Solution', 'Ex-Factor', 'Lost Ones', 'Exodus', 'Killing Me Softly With His Song', 'Fu-Gee-La', 'Put Your Hands Where My Eyes Could See', 'Look at Me Now', 'One Love / People Get Ready', 'Ready or Not', 'Is This Love', 'Praise Jah in the Moonlight', 'Slow Down', 'Buffalo Soldier', 'Pass the Kouchie', 'Could You Be Loved', "I'll Be Over You"], 'Bktherula': ['SANTANNY', 'ARE WE DONE?', "Tweakin' Together", 'TAN', '?????', 'LEFT RIGHT', 'CODE', 'CRAYON', 'MOSHPIT', 'BACK', 'RACKS UP', 'Pssyonft', 'MIND FUCK', 'THROUGH 2 U', 'HE SAY SHE SAY', 'Vaderz', 'FOREVER, PT. 2 (JEZEBEL)', 'SHAKIN IT', 'WISHUWASDACREW', 'ILOVEUBACK<3'], 'Black Kray': ['Iced out Castle', 'Princess Cuts Mah Wrist', 'Hydrocodone', 'Shorty 13 Onah Block', 'Stevie J and Joseline', 'Shynin on Western Ave', 'Yng16', 'Codeine Tears in Her Fanta', 'Edward Scissorhandz', 'Ending Prayer Goth Luv', '$$$ RAIN TOUCHED ME', '$$$ FLEXICAN GUDDAH LUV $$', '30 Round Clip Kreayshawn', 'ICED OUT UZI[GVCCIKRAY] $$ CAME THRU THIS BITCH ONAH WALRU$$ WAVED UP', 'Plug Walk', 'Gvcci Speedboats', 'NOBODY EVER LOVED ME'], 'BLP Kosher': ['The Nac', 'The Nac 2', 'Jew on the Canoe', 'Mazel Tron', 'Special K', 'Inferno 2', '2000’s Baby', 'Fools Gold', 'The Nac 3', 'Inferno', 'Cheese Touch', 'Castle', 'Skidoo', 'Dreidel Bop', 'Cheap Gas', 'Violent Lullaby', 'Gravity', 'Locusts', 'Beatbox Freestyle', 'Iguanas'], 'Famous Dex': ['New Wave', 'PICK IT UP', 'Drip from My Walk', 'JAPAN', 'Hoes Mad', "Where's Dexter", 'Ok Dexter', 'Mmhmm', 'On My Waist', 'Bag It', 'Get Out My Face', 'Jump in the Crowd', 'Goyard Pt. 2'], 'BIA': ['LONDON', 'BEST ON EARTH', 'BIA BIA', 'COVER GIRL', "CAN'T TOUCH THIS", 'WHOLE LOTTA MONEY', 'CLASSY', 'BIG BUSINESS', "I'M THAT BITCH", 'DON’T TELL', 'RAISE THE STAKES', 'Sturdy', 'FALLBACK', 'PLATE', 'Super Freaky Girl Remix', "I'm Geekin", 'GEEKALEEK', 'SAME HANDS', 'MOTIONLESS', 'FOUR SEASONS'], 'Lil Skies': ['Welcome to the Rodeo', 'Creeping', 'Havin My Way', 'Lust', 'Nowadays', 'Red Roses', 'I', 'I Know You', 'Riot', 'RAGE!', 'Magic', 'BASE', 'Fidget', 'Make A Toast', 'I Like Girls', 'Ice Water', 'Breathe', 'Signs of Jealousy', 'Dead Broke', 'Real Ties'], 'Paris Texas': [], 'Rich Amiri': ['MADONNA & RIHANNA', 'FORZA FREESTYLE', 'ILLUMINATI', 'OUTTA THERE', 'QUARTERMILLI', 'AINT NOTHING', 'ONE CALL', 'I WANT EVERYTHING', 'WHAT IT COST', 'HANDOUTS', 'ruthless', 'Havoc', 'CODEINE CRAZY', 'H00DBYAIR'], 'Anycia': ['DROP TOP', 'UP, LIT.', 'BIG BODY', 'REFUND', 'SPLASH BROTHERS', 'BRB', 'BACK OUTSIDE', 'HOMEWRECKER', 'WHAT DID I DO?', 'BAD WEATHER', 'TYPE BEAT', 'White Girl'], 'Babytron': ['Out on Bond', 'Manute Bol', 'A2Z', 'Jesus Shuttlesworth', 'Zap Zone', 'Long Nights', '#CERTIFIED', 'Down, Up!', 'Crash Yo Whip Music', 'Ex', 'Case Dismissed', 'Stutter Flow', 'Emperor of the Universe', '241', 'Mazel Tron', '8th Wonder of the World', 'Paul Bearer', 'Boondocks', 'Blah blah blah', 'Sith Lord'], 'Bashfortheworld': ['Crib in the Sky', 'Rich Gang', 'King of the Hill', 'Plato O Plomo ?', 'Tuck That Hate In', 'Third World', 'Diabla', 'Mundo', 'Face Card', 'Trap Star'], 'Homixide Gang': ['Lifestyle', 'Uzi Work', '5!RE', 'Holler!', 'Drakon !', '5unna', "Can't Go", 'TF!', 'ADHD', 'V-Friends', 'Homixide Language', 'Notice It', 'Lif3', 'Block Work', 'Dive In', 'Tripping', '55 Lifestyle', 'Tatted', 'B5', 'ROAD RAGE!'], 'Lil B': ['Like a Martian', 'Ski Ski Basedgod', 'Bitch Mob Anthem', 'Pretty Bitch', 'Suck My Dick Hoe', 'Vans', 'Wonton Soup', 'I Own Swag', 'Grove St. Party', 'Look Like Jesus', 'In Love With the BasedGod', 'I Love You', 'Connected in Jail', 'Witness', 'IShowSpeed', 'Flex 36', 'Swag Like Ohio', 'Bill Bellamy', 'Ellen Degeneres', 'Base for Your Face'], 'Lazer Dim 700': ['Asian Rock', 'Faneto', 'Tony Dim', 'mini sto', 'injoyable', 'sheft', 'awsum', 'Treacherous', 'captivity', 'evil curse', 'wigan out', 'Super Jump', 'Shoot Freely'], 'Osamason': ['cts-v', 'X & Sex', 'troops', 'Trenches', 'Lil O', 'Kutta', 'Me When', 'Cartel', 'Rehhab', 'Alot', 'Freestyle', 'All Star', 'Nothing', 'Need It', 'Flxr', 'Uno', 'For Da Flex', 'Werkin', 'Baghdad', '3x'], 'Cash Cobain': [], 'Nettspend': ['we not like you', 'shine n peace', '2024 Freestyle', 'drankdrankdrank', 'Take you out', 'What they say', 'Yooo', 'Funuyuh', 'Packs', 'Deftones', 'drank2', 'wake up', 'where the racks at', 'dude', 'benihana', 'Gen 5', 'no waiting', 'GoOd Night', 'Section', 'i <3 va'], 'Tiacorine': ['Lotto', 'Rocket', 'YUNG JOC', 'Pancakes', 'Give No Fuck', 'Get the Strap', 'Gas Station', 'Boogie', 'Chaka Khan', 'FreakyT', 'Shamone', 'Blick', 'Olive', 'Paris Hilton', 'Bonnet', 'Dipset', '30', 'FYK', 'Luigi'], 'Xaviersobased': ['ion een kno uu', 'turn up!!', 'Shawty Thro It Backk', '47 w me', "shouldn't", 'yh i kno', 'top 1', 'royalty', 'haha', 'police', '-tion', 'spend it when i wanna/everyone is someone in la', 'get them racks then i go', 'bag it', 'hemi 2', 'patchmade', 'lettering', 'yung feeshmeeks', '115 racks', 'how i feel'], 'Hardrock': [], 'ICYTWAT': [], 'Joeyy': ['Gout', 'Eminem', 'Bubble Bass', 'Glitz', 'Shirt', 'Petco', 'NoAuto.Shed', 'Sublingual', 'Garbanzo', 'Coat I Would Buy', 'Pfizer', 'Barnacle', 'Tempt', 'GROG', 'Vlone', 'Crayon', 'PCX', 'MCM', 'zyzz', 'In This Club'], 'Laundry Day': ['Dysmorphia', 'Why is Everyone a DJ?', 'Jane', 'Little Bird', 'FRIENDS', 'Harvard', 'Crazy Stupid Love', 'BULLDOG', 'Party in the U.S.A.', 'Did You Sleep Last Night?', 'Lavender', 'Moved On', 'Y.K.Y.N.U.N.Y.', 'My Life', 'CHA', 'We All Gotta Find a Reason', 'The Bus', 'Girl From Lingeria', 'Green Vision', 'Interview'], 'Lil Gnar': ['No Regular', 'Missiles', 'Diamond Choker', 'NEW BUGATTI', 'Faneto', 'Death Note', 'Not the Same', 'Man Down', 'Almighty Gnar', 'Moshpit', 'Dip Roll', 'My Bruddas', 'PB&J', 'Sticky Rice', "Don't Like", 'Look At Me!'], 'Robb Bank$': ['225', 'Bett', 'Griffith Did Nothing Wrong', 'Innadat', 'URUS (ECSTACY)', 'Threatz', 'My Bleed', 'LIFTED', 'Respect The Shooter', 'Top Man GOTTI (Gun Talk)', 'Broward Coward', 'ItWasntMe', 'Bedrock', '430 Kuban Doll (Interlewd)', 'Pressure', 'Phone Sex', "It Wasn't Me", 'Dream Mode', 'Project 8', '2Phoneshawty'], 'Elijah Wallace': [], 'Kami': ['Reboot', 'Behind the Scenes', '2 Td', 'Just Like the Movies', 'Payload', 'Superstar Moves', 'Beware', 'Brand New', 'A Bit', 'No choices', 'Home Movies', 'FDT'], '2Rare': [], 'Shed Theory': [], 'Zack Bia': ['Alright', 'HUMBLE.', 'Kill Bill', 'Just Wanna Rock', 'Tití me preguntó', 'Break From Toronto', 'Come and See Me', 'In Ha Mood', 'No Role Modelz', 'Strike (Holster)', 'Work', 'Mo Bamba', 'Antidote', 'FE!N', 'Pound Town', 'SkeeYee', 'Crew Love', "Buy U a Drank (Shawty Snappin')", 'Party in the U.S.A.', 'Never Lose Me'], 'Filthy': [], 'DJ Scheme': ['Robbery', 'Bandit', 'Armed & Dangerous', 'Take a Step Back', 'Look at Me!', 'SAD!', 'Fuck Love', 'YuNg BrAtZ', 'NO BYSTANDERS', 'H00DBYAIR', 'Stop Breathing', 'Fighting My Demons', 'FE!N', 'Miss The Rage', 'Faneto', 'Revenge', 'Lucid Dreams', 'Lean Wit Me', '#ImSippinTeaInYoHood', 'Shoota']}
    
    #artist_tracks_dict = {'Travis Scott': ['FE!N', 'NO BYSTANDERS', 'SICKO MODE', 'I KNOW ?', 'goosebumps', 'BUTTERFLY EFFECT', 'Antidote', 'TOPIA TWINS', 'HYAENA', 'MODERN JAM', 'MY EYES', 'TELEKINESIS', 'Mo Bamba', 'Type Shit', 'Cinderella', 'lose', 'MELTDOWN', 'Trance', 'Bandit', 'Turn Yo Clic Up'], 'Playboi Carti': ['Sky', 'Stop Breathing', 'Rockstar Made', 'Off the Grid', 'On That Time', 'JumpOutTheHouse', 'Flex Up', 'No Sl33p', 'R.I.P.', 'Miss The Rage', 'Teen X', 'New N3on', 'F33l Lik3 Dyin', 'Control', 'Shoota', 'R.I.P Fredo', 'Location', 'Die4Guy', 'Wokeuplikethis*', 'FlatBed Freestyle'], 'Chief Keef': ['Faneto', 'Love Sosa', 'War', 'Earned It', "Been Ballin'", "I Don't Like", 'Let Me See', 'Save That Shit', 'Hadouken', 'Kobe', 'Love No Thotties', 'Status', '3Hunna', 'Fool Ya', 'Close That Door', 'Hallelujah', "Hate Bein' Sober", 'Understand Me', 'Action Figures', 'Tec']}

    #artist_tracks_dict = {'Travis Scott': ['FE!N', 'NO BYSTANDERS', 'SICKO MODE', 'I KNOW ?', 'goosebumps', 'BUTTERFLY EFFECT', 'Antidote', 'TOPIA TWINS', 'HYAENA', 'MODERN JAM', 'MY EYES', 'TELEKINESIS', 'Mo Bamba', 'Type Shit', 'Cinderella', 'lose', 'MELTDOWN', 'Trance', 'Bandit', 'Turn Yo Clic Up']}

    #artist_tracks_dict = {'Playboi Carti': ['Sky', 'Stop Breathing', 'Rockstar Made', 'Off the Grid', 'On That Time', 'JumpOutTheHouse', 'Flex Up', 'No Sl33p', 'R.I.P.', 'Miss The Rage', 'Teen X', 'New N3on', 'F33l Lik3 Dyin', 'Control', 'Shoota', 'R.I.P Fredo', 'Location', 'Die4Guy', 'Wokeuplikethis*', 'FlatBed Freestyle']}

    artist_tracks_dict = {'Chief Keef': ['Faneto', 'Love Sosa', 'War', 'Earned It', "Been Ballin'", "I Don't Like", 'Let Me See', 'Save That Shit', 'Hadouken', 'Kobe', 'Love No Thotties', 'Status', '3Hunna', 'Fool Ya', 'Close That Door', 'Hallelujah', "Hate Bein' Sober", 'Understand Me', 'Action Figures', 'Tec']}
    #artist_tracks_dict = {'Chief Keef': ['Fool ya', 'Faneto'],'Travis Scott': ['FE!N']}

    #artist_tracks_dict = create_artist_tracks_dict_sl(artist_dict)

    print('\n\n')
    # Loop through artists
    tracks_list = []
    uris_list = []
    conflicts = []
    index = 1

    for artist_name, tracks in artist_tracks_dict.items():

        not_found_tracks = []

        if artist_tracks_dict[artist_name] != []:

            featured_artists = set()

            for queried_song in tracks:
                print("\nQuerying", queried_song, "by", artist_name, "...")

                query_1 = f'track:{queried_song}, artist:{artist_name}'
                query_2 = f'{queried_song} {artist_name}'
                song = f"track:{queried_song}"

                #value = sp.search(q=f"track:{queried_song}, artist:{artist_name}", limit=1,offset=0)
                #value = sp.search(q=query, limit=1,offset=0, type="track")

                
                # I disavow this if statement logic:
                if query_2.lower() == "been ballin' chief keef":
                    value = sp.search(q='Been Ballin Ballout',offset=0, type="track")
                            
                else:
                    ######################## Which is better??? ########################

                    #value = sp.search(q=song,offset=0, type="track")               #20 vs 17
                    value = sp.search(q=query_2,offset=0, type="track")             #20 vs 18
                    #value = sp.search(q=query, limit=1,offset=0, type="track")

                    ####################################################################
                
                #print(query_2)
                #print(value)
                for i in range(len(value["tracks"])):
                    
                    track_artists=[]

                    returned_song = value["tracks"]["items"][i]["name"]
                    #print(returned_song)

                    if queried_song.upper() in returned_song.upper():

                        #print("Queried Song: ", queried_song, "\nReturned Song: ", returned_song,'\n')
                        track_artist_info = value["tracks"]["items"][i]["artists"]
                        list_of_artists = [artist["name"].upper() for artist in track_artist_info]
                        track_artists = [artist for artist in list_of_artists]
                        
                        # If artist name in tracks artist, add it to the list of songs to be added
                        if artist_name.upper() in track_artists:
                            uri = value["tracks"]["items"][i]["uri"]
                            track = value["tracks"]["items"][i]["name"]


                            uris_list.append(uri)
                            tracks_list.append(track)

                            # Adds featured artists to a set
                            # This is done such that if an artist played another artists track at a concert
                            # the track will be added  
                            featured_artists.update([artist for artist in list_of_artists if artist.upper() != artist_name.upper()])

                            #print(track)
                             
                        # Include tracks played at concert that are by artists other than current artist
                        elif any(item in track_artists for item in list(featured_artists)):
                            print("Featured", featured_artists)
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
                            

                        else:
                            track = queried_song.upper()
                            track_artists = str([artist_name.upper()]) + " was not"
                            not_found_tracks.append(track)
                        
                        print(queried_song.upper(), "by", [artist_name.upper()], "queried")
                        print(track.upper(), "by", track_artists, "found")
                        break

                    else:
                        track = queried_song.upper()
                        track_artists = str([artist_name.upper()]) + " was not"
                        not_found_tracks.append(track)


                  
                    break
               
            unique_featured_artists = list(featured_artists)
            print("Unique featured artists for",artist_name,":\n", unique_featured_artists,'\n')    
            print("Songs not found for", artist_name + ":\n", not_found_tracks)            

                # # Tries to find the track based off of querying the name only with limit of 1
                # try:
                #     returned_song = value["tracks"]["items"][0]["name"]
                #     returned_artists = value["tracks"]["items"][0]["artists"][0]["name"]

                #     uri = value["tracks"]["items"][0]["uri"]
                #     id = value["tracks"]["items"][0]["id"]
                #     name = value["tracks"]["items"][0]["name"]

                
                #     if artist_name.lower() not in returned_artists.lower():

                #         # Looks for top 10 tracks based on query of song and artist name
                #         value = sp.search(q=f"track:{queried_song} {artist_name}", type="track")
                # except:
                #     print("oi")
    
                
    #uris_list = get_uris_for_artist_tracks(artist_tracks_dict)
    print('\n\n\n')
    print('=' * 120)
    queried_songs = [value for sublist in artist_tracks_dict.values() for value in sublist]
    print()
    print('-' * 120)
    print("Tracks queried:\n", queried_songs)
    print('-' * 120)
    print("Tracks returned:\n", tracks_list)
    print('-' * 120)
    print("Difference (Queried vs Returned):\n",len(queried_songs), "vs", len(tracks_list))
    print('-' * 120)
    print("Tracks not found:", not_found_tracks)
    print('\n\n')
    print('=' * 120)
    exit()

    with open('json_tests/uris_list.txt', 'w') as f:
        f.write(f"{uris_list}\n")
        
    playlist_id = create_playlist("Summer Smash - Setlist API")
    print()

    add_tracks_to_playlist(playlist_id, uris_list)





    




    #################################################### testing ####################################################



    
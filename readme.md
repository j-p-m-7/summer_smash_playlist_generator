# Summer Smash Music Festival Playlist Generator

## Overview

The Summer Smash Music Festival Playlist Generator is a project designed to create two playlists for the Summer Smash Music Festival. The first playlist will consist of the top 10 tracks for each artist at the festival, sourced from the Spotify API. The second playlist will include the top 10 most common songs performed at each artist's 20 most recent concerts, obtained from the Setlist API. I would like to compare each playlist and see which one is more accurate regarding the songs each artist performs.

## Features

- **Spotify Integration:** Utilizes the Spotify API to retrieve top tracks for festival artists.
- **Setlist Integration:** Integrates with the Setlist API to fetch songs from each artist's recent concerts.
- **Playlist Creation:** Automatically generates playlists on Spotify based on the retrieved data.
- **Customization:** Allows customization of playlist names and other parameters.

## Requirements

- Python 3.x (I used Python 3.11 but this should work with most versions)
- `spotipy` Python library for Spotify API access
- `requests` Python library for HTTP requests

You can install the required Python libraries using the `requirements.txt` file, as shown in the steps below.

## Usage

1. Clone the repository to your local machine:

```bash
git clone https://github.com/j-p-m-7/summer-smash-playlists.git
```

2. Install the required Python libraries:

```bash
pip install -r requirements.txt
```

3. Set up API keys for Spotify and Setlist:

- Obtain API keys for Spotify and Setlist by registering your application on their respective developer portals.
- Create a `.env` file in the project directory and add your API keys:

```plaintext
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SETLIST_API_KEY=your_setlist_api_key
```

4. Run the script to generate playlists:

```bash
python playlist_generator.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Spotify API](https://developer.spotify.com/documentation/web-api/)
- [Setlist API](https://api.setlist.fm/docs/1.0/index.html)

## Contributors

- j-p-m-7

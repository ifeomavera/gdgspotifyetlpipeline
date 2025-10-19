import os # module to interact with the operating system, in the project, it is for checking if a file exists.
import pandas as pd #module to create dataframes and transform the data into a json file
import spotipy #module to connect with spotify using https requests
from spotipy.oauth2 import SpotifyOAuth #module for authentication, spotify uses OAuth for authentication

# Set your credentials all gotten from the spotify developers dashboard.
client_id = 'e1579079c582472d998f11f720ae99e2'
client_secret = '5eecc48f72ca4d8fa9baecafb0e3b662'
redirect_uri = 'http://127.0.0.1:8888/callback'

# Set up Spotify OAuth, for the scope we're only using 'user-read-recently-played', becasue we want to get the songs recently played.
scope = 'user-read-recently-played'
#sp_oauth object to manage the OAuth2 flow, we could put the arguments directly in the Spotify client, but this way is cleaner and "secure"
sp_oauth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope, cache_path='.cache')

# Create a Spotipy client, this can simply be done by passing the sp_oauth object to the Spotify client.
sp = spotipy.Spotify(auth_manager=sp_oauth)

# Creating the recent tracks log, this helps to collect more than 50 tracks, which is the amount of repsonses at a time spotify gives you,over time.
historical_tracks_file = 'all_recent_tracks.json'

# Checks if the file exists, if it does, read it into a dataframe and convert to a list of dictionaries.
if os.path.exists(historical_tracks_file):
    historical_tracks_df = pd.read_json(historical_tracks_file)
    tracks_ls = historical_tracks_df.to_dict('records')
else:
    tracks_ls = []

# Get current user's recently played tracks, limit to 50 (maximum allowed by Spotify API)
recent_tracks = sp.current_user_recently_played(limit=50)

# Creating the recent tracks list, extracting song data from the API response, and appending to the recent_tracks_ls list.
recent_tracks_ls = []
for item in recent_tracks['items']:
    track_name = item['track']['name']
    artist_name = item['track']['artists'][0]['name']
    played_at = item['played_at']
    
    recent_tracks_ls.append({
        'track_name': track_name,
        'artist_name': artist_name,
        'played_at': played_at
    })

tracks_ls.extend(recent_tracks_ls)
unique_tracks = {track['played_at']: track for track in tracks_ls}.values()

df = pd.DataFrame(recent_tracks_ls)
track_df = pd.DataFrame(unique_tracks)
track_df['played_at'] = pd.to_datetime(track_df['played_at'], utc=True)
track_df.sort_values(by ='played_at', inplace=True)

df.to_json("recent_tracks.json", orient="records", indent=4)
track_df.to_json("all_recent_tracks.json", orient="records", indent=4)

print("Played Pipeline executed!")
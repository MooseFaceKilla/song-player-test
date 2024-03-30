from flask import Flask, request, render_template
from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from waitress import serve

# Load environment variables from .env file
load_dotenv()

# Accessing environment variables
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

app = Flask(__name__)

# Spotify API authentication
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Define route for home page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        artist_name = request.form['artist_name']
        correct_artist_name, top_tracks = get_top_tracks(artist_name)
        if top_tracks:
            return render_template('top_tracks.html', artist=correct_artist_name, tracks=top_tracks)
        else:
            error_message = f"No artist found with the name '{artist_name}'."
            return render_template('index.html', error=error_message)
    else:
        return render_template('index.html')

# Function to get artist's top tracks
def get_top_tracks(artist_name):
    results = sp.search(q=artist_name, type='artist', limit=1)
    if len(results['artists']['items']) > 0:
        correct_artist_name = results['artists']['items'][0]['name']
        artist_id = results['artists']['items'][0]['id']
        top_tracks = sp.artist_top_tracks(artist_id=artist_id, country='US')['tracks']
        return correct_artist_name, top_tracks
    else:
        return None, None

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=42069)

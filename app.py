import requests
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


# Function to get artist's top tracks
def get_top_tracks(artist_name):
    results = sp.search(q=artist_name, type='artist', limit=1)
    if len(results['artists']['items']) > 0:
        correct_artist_name = results['artists']['items'][0]['name']
        artist_id = results['artists']['items'][0]['id']
        top_tracks = sp.artist_top_tracks(artist_id=artist_id, country='US')['tracks']
        return correct_artist_name, top_tracks
    else:
        error_message = f"No artist found with the name '{artist_name}'. Please try a different artist."
        return None, None, error_message


# Define route for home page
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/search', methods=['POST'])
def search():
    artist_name = request.form['artist_name']
    correct_artist_name, top_tracks = get_top_tracks(artist_name)
    if correct_artist_name:
        return render_template('top_tracks.html', artist=correct_artist_name, tracks=top_tracks)
    else:
        error_message = f"No artist found with the name '{artist_name}'."
        return render_template('searchByArtistName.html', error=error_message)


@app.route('/hyperlinks')
def hyperlinks():
    return render_template('hyperlinks.html')


@app.route('/searchByArtistName')
def search_by_artist_name():
    return render_template('searchByArtistName.html')


if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=42069)

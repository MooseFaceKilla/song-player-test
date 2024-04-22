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


@app.route('/search', methods=['POST'])
def search():
    artist_name = request.form['artist_name']
    correct_artist_name, top_tracks = get_top_tracks(artist_name)
    if correct_artist_name:
        return render_template('top_tracks.html', artist=correct_artist_name, tracks=top_tracks)
    else:
        error_message = f"No artist found with the name '{artist_name}'."
        return render_template('searchByArtistName.html', error=error_message)


# Function to get top tracks by artist name
def get_top_tracks(artist_name):
    results = sp.search(q=artist_name, type='artist', limit=1)
    if len(results['artists']['items']) > 0:
        correct_artist_name = results['artists']['items'][0]['name']
        artist_id = results['artists']['items'][0]['id']
        top_tracks = sp.artist_top_tracks(artist_id=artist_id, country='US')['tracks']
        return correct_artist_name, top_tracks
    else:
        error_message = f"No artist found with the name '{artist_name}'. Please try a different artist."
        return None, None


# Define route for search by song name page
@app.route('/search-by-song', methods=['POST'])
def search_by_song():
    song_name = request.form['song_name']
    tracks = search_by_song_name(song_name)
    return render_template('top_tracks.html', artist=song_name, tracks=tracks)


# Function to search by song name
def search_by_song_name(song_name):
    results = sp.search(q=song_name, type='track', limit=10)
    tracks = []
    for track in results['tracks']['items']:
        track_info = {
            'name': track['name'],
            'artists': ', '.join([artist['name'] for artist in track['artists']]),
            'preview_url': track['preview_url']
        }
        tracks.append(track_info)
    return tracks


@app.route('/search-by-album', methods=['POST'])
def search_by_album():
    album_name = request.form['album_name']
    albums = search_by_album_name(album_name)
    return render_template('album_results.html', albums=albums)


def search_by_album_name(album_name):
    results = sp.search(q=album_name, type='album', limit=10)
    albums = []
    for album in results['albums']['items']:
        album_info = {
            'id': album['id'],  # Include the album ID in the album info
            'name': album['name'],
            'artists': ', '.join([artist['name'] for artist in album['artists']]),
            'release_date': album['release_date'],
            'image_url': album['images'][0]['url'] if album['images'] else None
        }
        albums.append(album_info)
    return albums


@app.route('/album-details/<album_id>')
def album_details(album_id):
    album_details = get_album_details(album_id)
    if album_details:
        return render_template('album_details.html', album_details=album_details)
    else:
        return render_template('error.html', error_message="Album details not found.")


def get_album_details(album_id):
    album = sp.album(album_id)
    if album:
        album_details = {
            'name': album['name'],
            'artists': ', '.join([artist['name'] for artist in album['artists']]),
            'release_date': album['release_date'],
            'image_url': album['images'][0]['url'] if album['images'] else None
        }
        return album_details
    else:
        return None


# Define route for home page
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/hyperlinks')
def hyperlinks():
    return render_template('hyperlinks.html')


@app.route('/searchbyartistname')
def searchbyartistname():
    return render_template('searchbyartistname.html')


@app.route('/searchbysongname')
def searchbysongname():
    return render_template('searchbysongname.html')


@app.route('/searchbyalbumname')
def searchbyalbumname():
    return render_template('searchByAlbumName.html')


if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=42069)

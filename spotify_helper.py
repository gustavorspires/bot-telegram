import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import re
from dotenv import load_dotenv

"""
Módulo de apoio para as funções do comando /spotify
"""

# Carregamento de variáveis de ambiente
load_dotenv()
SCOPE = "playlist-modify-public playlist-modify-private playlist-read-private"
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
USERNAME = os.getenv("SPOTIFY_USERNAME")

# Autenticação com o Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    username=USERNAME
))


def create_playlist(name):
    """
    Cria uma nova playlist no Spotify com o nome fornecido.
    """
    playlist = sp.user_playlist_create(USERNAME, name, public=True, collaborative=True)
    return playlist['id'], playlist['external_urls']['spotify']

def add_track(playlist_id, track_query):
    """
    Adiciona uma faixa à playlist especificada.
    """
    track_id = None
    match = re.search(r"(track/|spotify:track:)([a-zA-Z0-9]+)", track_query)
    if match:
        track_id = match.group(2)
        track_info = sp.track(track_id)
    else:
        results = sp.search(q=track_query, type='track', limit=1)
        if results['tracks']['items']:
            track_info = results['tracks']['items'][0]
            track_id = track_info['id']
        else:
            return False, None

    sp.playlist_add_items(playlist_id, [track_id])
    return True, track_info['name']

def remove_track(playlist_id, track_query):
    """
    Remove uma faixa da playlist especificada.
    """
    track_id = None
    match = re.search(r"(track/|spotify:track:)([a-zA-Z0-9]+)", track_query)
    if match:
        track_id = match.group(2)
        track_info = sp.track(track_id)
    else:
        results = sp.search(q=track_query, type='track', limit=1)
        if results['tracks']['items']:
            track_info = results['tracks']['items'][0]
            track_id = track_info['id']
        else:
            return False, None

    sp.playlist_remove_all_occurrences_of_items(playlist_id, [track_id])
    return True, track_info['name']


import spotipy
import tqdm as tqdm
from spotipy import SpotifyClientCredentials


def get_or_create_playlist(playlist_name, token, username):
    sp = spotipy.Spotify(auth=token)
    sp.trace = False

    current_playlists = sp.current_user_playlists(limit=50)
    current_playlists_names = [playlist['name'] for playlist in current_playlists['items']]
    current_playlists_ids = [playlist['id'] for playlist in current_playlists['items']]

    if playlist_name in current_playlists_names:
        playlist_id = current_playlists_ids[current_playlists_names == playlist_name]
    else:
        playlist = sp.user_playlist_create(username, playlist_name)
        playlist_id = playlist['id']

    return playlist_id


def find_track_ids(tracks):
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

    for track in tqdm.tqdm(tracks):
        name = track.name
        artist = track.artist
        album = track.album

        track_id = search_track_id(album, artist, name, sp)
        if len(track_id) == 0:
            track_id = search_track_id(album, '', name, sp)

        track.track_id = track_id

    found_tracks = [track for track in tracks if len(track.track_id) > 0]
    missing_tracks = [track for track in tracks if len(track.track_id) == 0]

    return found_tracks, missing_tracks


def search_track_id(album, artist, name, sp):

    selected_track_id = ''
    name_split = name.split(' ')
    for i in range(len(name_split), max(0, int(len(name_split)/2)), -1):
        name = ' '.join(name_split[0:i])
        search_string = ' '.join([artist, name])
        search_result = sp.search(search_string)
        if len(search_result['tracks']['items']) > 0:
            selected_track_id = search_result['tracks']['items'][0]['id']
            for item in search_result['tracks']['items']:
                if item['album']['name'].lower() == album.lower():
                    selected_track_id = item['id']
                    break
            break
    return selected_track_id


def publish_tracks_to_playlist(tracks, playlist_id, token, username):
    track_ids = [track.track_id for track in tracks]
    n = 100
    track_chunks = [track_ids[i:i + n] for i in range(0, len(track_ids), n)]
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    for chunk in track_chunks:
        sp.user_playlist_add_tracks(username, playlist_id, chunk)
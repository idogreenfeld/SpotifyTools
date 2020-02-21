import os
import spotipy
import argparse
import tqdm as tqdm
import pandas as pd
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials

from main_scripts.support_classes import Track


def run(spotipy_client_id, spotipy_client_secret, spotipy_redirect_uri, spotify_username, playlist_name, playlist_file_path):

    os.environ['SPOTIPY_CLIENT_ID'] = spotipy_client_id
    os.environ['SPOTIPY_CLIENT_SECRET'] = spotipy_client_secret
    os.environ['SPOTIPY_REDIRECT_URI'] = spotipy_redirect_uri

    scope = "playlist-modify-public"
    token = util.prompt_for_user_token(spotipy_client_id, scope)

    playlist_id = get_or_create_playlist(playlist_name, token, spotify_username)

    if playlist_file_path.endswith('.wpl'):
        tracks = read_wpl_playlist(playlist_file_path)
    elif playlist_file_path.endswith('.csv'):
        tracks = read_csv_playlist(playlist_file_path)
    else:
        return
    found_tracks, missing_tracks = find_track_ids(tracks)

    save_tracks_to_file(missing_tracks, 'missing_tracks')

    publish_tracks_to_playlist(found_tracks, playlist_id, token, spotify_username)


def read_wpl_playlist(playlist_file_path):
    with open('../' + playlist_file_path, "r", encoding="utf-8") as f:
        lines = [line.rstrip('\n') for line in f if line.startswith('            <media')]
        tracks = [parse_wpl_line(line) for line in lines]
    return tracks


def parse_wpl_line(line):
    parts = line.split('\\')
    name_parts = parts[-1].split('.')[0:-1]
    name = '.'.join(name_parts)
    track = Track(name=name, artist=parts[-3], album=parts[-2])
    return track


def read_csv_playlist(playlist_file_path):
    tracks_df = pd.read_csv('../' + playlist_file_path)
    tracks = [parse_pd_line(row[1]) for row in tracks_df.iterrows()]
    return tracks


def parse_pd_line(row):
    name = ''.join([i for i in row['Name'] if not i.isdigit()])
    track = Track(name=name, artist=row['Artist'], album=row['Album'])
    return track


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

        track_id = get_track_id(album, artist, name, sp)
        if len(track_id) == 0:
            track_id = get_track_id(album, '', name, sp)

        track.track_id = track_id

    found_tracks = [track for track in tracks if len(track.track_id) > 0]
    missing_tracks = [track for track in tracks if len(track.track_id) == 0]

    return found_tracks, missing_tracks


def get_track_id(album, artist, name, sp):

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


def save_tracks_to_file(tracks, save_name):
    tracks_df = pd.DataFrame()
    for track in tracks:
        tracks_df = tracks_df.append({'Name': track.name, 'Artist': track.artist, 'Album': track.album}, ignore_index=True)
        print('Track name: {}, Artist: {}, Album: {}'.format(track.name, track.artist, track.album))
    tracks_df.to_csv('../{}.csv'.format(save_name), encoding='utf-8-sig')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--spotipy_client_id', type=str, required=True)
    parser.add_argument('--spotipy_client_secret', type=str, required=True)
    parser.add_argument('--spotipy_redirect_uri', type=str, required=True)
    parser.add_argument('--spotify_username', type=str, required=True)
    parser.add_argument('--playlist_name', type=str, required=True)
    parser.add_argument('--playlist_file_path', type=str, required=True)

    args = parser.parse_args()

    run(spotipy_client_id=args.spotipy_client_id,
        spotipy_client_secret=args.spotipy_client_secret,
        spotipy_redirect_uri=args.spotipy_redirect_uri,
        spotify_username=args.spotify_username,
        playlist_name=args.playlist_name,
        playlist_file_path=args.playlist_file_path)


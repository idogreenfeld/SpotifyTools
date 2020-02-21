import os
import argparse
import spotipy.util as util

from utils.file_handlers import read_wpl_playlist, read_csv_playlist, save_tracks_to_file
from utils.spotify_access import get_or_create_playlist, find_track_ids, publish_tracks_to_playlist


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


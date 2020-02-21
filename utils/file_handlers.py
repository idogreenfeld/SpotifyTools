import pandas as pd

from utils.support_classes import Track


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


def save_tracks_to_file(tracks, save_name):
    tracks_df = pd.DataFrame()
    for track in tracks:
        tracks_df = tracks_df.append({'Name': track.name, 'Artist': track.artist, 'Album': track.album}, ignore_index=True)
        print('Track name: {}, Artist: {}, Album: {}'.format(track.name, track.artist, track.album))
    tracks_df.to_csv('../{}.csv'.format(save_name), encoding='utf-8-sig')
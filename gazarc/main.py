import html
import json
import os
import pickle
import random

import click
from PyInquirer import prompt

from gazarc import whatapi2
from gazarc.torrentcheck import (TRACKERS, get_torrent_id, get_torrent_tracker,
                                 torrentcheck)

DEFAULT_TRACKER_FOLDER_NAME: TRACKERS = "RED"

redacted_api_params = {
    'tracker': 'RED',
    'config_file': '/Users/nathanjones/gazarc.ini',
}

orpheus_api_params = {
    'tracker': 'OPS',
    'config_file': '/Users/nathanjones/gazarc.ini',
}


def get_torrent_folder_name(torrent):
    artists = torrent['response']['group']['musicInfo']['artists']
    if len(artists) == 1:
        artist = artists[0]['name']
    elif len(artists) == 2:
        artist = ' & '.join(
            list(map(lambda x: x['name'], artists)))
    else:
        artist = 'Various Artists'

    if torrent['response']['torrent']['remastered']:
        year = torrent['response']['group']['year']
        media = torrent['response']['torrent']['media']
        if torrent['response']['torrent']['remasterRecordLabel']:
            label = (
                torrent['response']['torrent']['remasterRecordLabel']
                .replace('/', '-'))
        else:
            label = None
        if torrent['response']['torrent']['remasterCatalogueNumber']:
            catalog_number = (torrent['response']['torrent']
                              ['remasterCatalogueNumber']).replace(
                '/', '-')
        else:
            catalog_number = None
        if (
            torrent['response']['torrent']['remasterYear'] and
            torrent['response']['torrent']['remasterYear'] !=
            torrent['response']['group']['year']
        ):
            if torrent['response']['torrent']['remasterTitle']:
                remaster_text = (
                    f" ({torrent['response']['torrent']['remasterYear']} "
                    f"{torrent['response']['torrent']['remasterTitle']})").replace('/', '-')
            else:
                remaster_text = (
                    f" ({torrent['response']['torrent']['remasterYear']} "
                    "Reissue)").replace('/', '-')
        else:
            remaster_text = None

    else:
        year = torrent['response']['group']['year']
        media = torrent['response']['torrent']['media']
        label = torrent['response']['group']['recordLabel'].replace('/', '-')
        if torrent['response']['group']['catalogueNumber']:
            catalog_number = (torrent['response']['group']
                              ['catalogueNumber']).replace(
                '/', '-')
        else:
            catalog_number = None
        remaster_text = None

    format_ = torrent['response']['torrent']['format']
    title = torrent['response']['group']['name'].replace('/', '-')

    if torrent['response']['torrent']['encoding'] != 'Lossless':
        encoding = f" {torrent['response']['torrent']['encoding']}"
    else:
        encoding = ''

    folder_name = (
        f'{artist} - {year} - {title} - [{media}{encoding}] [{format_}]'
    )
    if torrent['response']['torrent']['hasLog']:
        log_score = torrent['response']['torrent']['logScore']
        folder_name += f' (Log {log_score}%)'
    if remaster_text:
        folder_name += remaster_text
    if label:
        folder_name += f' {{{label}}}'
    if catalog_number:
        folder_name += f' {{{catalog_number}}}'

    return folder_name


@click.command()
@click.option('--path', '-p', default='.', type=str)
def main(path):
    ops_handle = whatapi2.WhatAPI(**orpheus_api_params)
    red_handle = whatapi2.WhatAPI(**redacted_api_params)
    full_path = os.path.abspath(path)
    click.echo(f'running at path: {full_path}')
    for root, dirs, files in os.walk(full_path, topdown=False):
        torrent_dir = os.path.abspath(root)
        tracker_folder_names = {}
        for name in files:
            if '.torrent' in name:
                click.echo()
                click.echo(f'Found {name}')
                torrent_name_no_ext = os.path.splitext(name)[0]
                click.echo('Verifying that torrent data is valid...')
                is_torrent_valid = torrentcheck(torrent_dir, name)
                if is_torrent_valid:
                    click.secho(f'{name} is valid!', fg='green')
                    tracker = get_torrent_tracker(torrent_dir, name)
                    torrent_id = get_torrent_id(name)
                    if tracker == 'OPS':
                        torrent = ops_handle.request('torrent', id=torrent_id)
                    else:
                        torrent = red_handle.request('torrent', id=torrent_id)

                    new_folder_name = html.unescape(
                        get_torrent_folder_name(torrent))
                    tracker_folder_names[tracker] = new_folder_name

                    torrent_json = json.dumps(
                        torrent, sort_keys=True, indent=4)
                    if tracker not in name:
                        torrent_json_filename = (
                            f'[{tracker}] {torrent_name_no_ext}.json')
                    else:
                        torrent_json_filename = f'{torrent_name_no_ext}.json'
                    click.echo(
                        f'Writing torrent json to: {torrent_json_filename}'
                    )
                    json_absolute = os.path.join(
                        torrent_dir,
                        torrent_json_filename
                    )
                    with open(json_absolute, 'w+') as file:
                        file.write(torrent_json)

                    # Prepend track to .torrent filename only if it isn't
                    # already in the filename.
                    if tracker not in name:
                        new_torrent_file_name = f'[{tracker}] {name}'

                        os.rename(
                            src=os.path.join(
                                torrent_dir, name),  # .torrent file
                            dst=os.path.join(
                                torrent_dir, new_torrent_file_name)
                        )
                else:
                    click.secho(f'{name} is invalid!', fg='red')

        # no torrent files in a directory
        if not bool(tracker_folder_names):
            continue

        # single/multiple torrents with same folder name.
        if len(set(tracker_folder_names.values())) == 1:
            new_folder_name = tracker_folder_names[
                random.choice(list(tracker_folder_names))
            ]
        else:
            # Multiple torrents with different folder names
            if DEFAULT_TRACKER_FOLDER_NAME in tracker_folder_names:
                new_folder_name = tracker_folder_names[
                    DEFAULT_TRACKER_FOLDER_NAME]
            else:
                questions = [
                    {
                        'type': 'list',
                        'name': 'tracker',
                        'message': 'Select your preferred folder name',
                        'choices': [
                            {
                                'key': tracker_name,
                                'value': folder_name,
                                'name': f'{tracker_name}: {folder_name}'
                            }
                            for tracker_name, folder_name
                            in tracker_folder_names.items()
                        ]
                    }
                ]
                answer = prompt(questions)
                new_folder_name = answer['tracker']

        new_folder_absolute = os.path.join(
            # parent dir of torrent_dir
            os.path.dirname(torrent_dir),
            new_folder_name,
        )

        if torrent_dir != new_folder_absolute:
            click.echo()
            click.echo(f"Renaming folder to: {new_folder_name}")
            os.rename(src=torrent_dir, dst=new_folder_absolute)
            click.echo(f"setting torrent_dir to {new_folder_absolute}")
            torrent_dir = new_folder_absolute

        tracker_folder_names = {}


if __name__ == '__main__':
    main()

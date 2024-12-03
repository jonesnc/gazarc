import configparser
import time

import requests

headers = {
    'Content-type': 'application/x-www-form-urlencoded',
    'Accept-Charset': 'utf-8',
    'User-Agent': 'whatapi [isaaczafuta]'
}

servers = {
    'OPS': 'https://orpheus.network',
    'RED': 'https://redacted.sh',
}

class LoginException(Exception):
    pass


class RequestException(Exception):
    pass


class ConfigException(Exception):
    pass


class WhatAPI:
    def __init__(self, tracker, config_file):
        self.session = requests.Session()
        self.server = servers[tracker]

        # Parse the config file
        config = configparser.ConfigParser()
        config.read(config_file)
        if tracker not in config.sections():
            raise ConfigException((
                'Invalid config file! Tracker section not found in config '
                'file.'))

        # get the api_key from the config file
        api_key = config[tracker]['api_key']
        self.session.headers.update({
            'Authorization': api_key
        })


    def get_torrent(self, torrent_id):
        """Download the torrent at torrent_id using the authkey and passkey."""
        torrentpage = self.server + '/ajax.php'
        params = {'action': 'download', 'id': torrent_id}
        r = self.session.get(torrentpage, params=params, allow_redirects=False)
        time.sleep(2)
        if (
            r.status_code == 200 and
            'application/x-bittorrent' in r.headers['content-type']
        ):
            return r.content
        return None

    def request(self, action, **kwargs):
        """Make an AJAX request at a given action page."""
        ajaxpage = self.server + '/ajax.php'
        params = {'action': action}
        params.update(kwargs)

        r = self.session.get(ajaxpage, params=params, allow_redirects=False)
        time.sleep(2)
        try:
            json_response = r.json()
            if json_response["status"] != "success":
                raise RequestException
            return json_response
        except ValueError:
            raise RequestException

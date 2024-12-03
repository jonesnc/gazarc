import re
import subprocess
from typing import Literal

TRACKERS = Literal["OPS", "RED"]

def torrentcheck(path, torrent_file_name):
    """Return True if torrent file passes torrentcheck, else return False."""
    sp = subprocess.Popen(
        [
            'torrentcheck',
            '-p',
            path,
            '-t',
            torrent_file_name
        ],
        cwd=path,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    output, _ = sp.communicate()
    str_output = output.decode('utf-8')
    return 'torrent is good' in str_output


def get_torrent_tracker(path, torrent_name) -> TRACKERS:
    sp = subprocess.Popen(
        [
            'transmission-show',
            torrent_name
        ],
        cwd=path,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    output, _ = sp.communicate()
    str_output = output.decode('utf-8')
    tracker = 'RED' if 'flacsfor.me' in str_output else 'OPS'
    return tracker


def get_torrent_id(torrent_name):
    match = re.search(r'(\d*).torrent', torrent_name)
    return match.group(1)

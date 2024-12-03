# gazarc

A command-line utilty that archives torrents downloaded from Gazelle trackers (RED, OPS, etc.).

When executed, it will do the following:

- Check that torrent data is valid. If some torrent data is missing, stop and quit
- Rename the torrent directory to include release info
- Download torrent info and save as a JSON file
- Rename the `.torrent` file to include the tracker abbreviation (`OPS` or `RED`)

Only Redacted and Orpheus are currently supported.

## Installation

### Dependencies

- [torrentcheck](https://github.com/ximellon/torrentcheck). Make sure you can run the `torrentcheck` binary in your shell.
- `Python3`, `pip`
- Create a `~/.gazarc.ini` file with these contents:

```ini
[OPS]
api_key = 123abc

[RED]
api_key = 123abc
```

Replace `123abc` with your API key.

### Install

In the root directory of this project, run:

```bash
$ pip install -e .
```

## Usage

```
Usage: gazarc [OPTIONS]

Options:
  -p, --path TEXT  [required]
  --help           Show this message and exit.
```

### Example usage

```bash
$ cd album-dir
$ gazarc -p .
```

Note: This script has only been run and tested on Python 3.8. It may run on earlier versions of 3, but I haven't tested that.

## TODO

- Publish to PyPI
- Customizable template (Jinja template?)
- Support using a single tracker (using both RED *and* OPS at the same time is the only supported configuration)

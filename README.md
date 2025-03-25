# githubtakeout

## Archive public Git repos and Gists from GitHub

---

- Copyright (c) 2015-2025 [Corey Goldberg](https://github.com/cgoldberg)
- License: [MIT](https://opensource.org/licenses/MIT)
- Development: [https://github.com/cgoldberg/githubtakeout](https://github.com/cgoldberg/githubtakeout)

----

## About:

`githubtakeout.py` is a data export tool for archiving Git repositories hosted on GitHub.
It clones a user's public repos, and creates an archive of each.

By default, it doesn't save commit history or branches (`.git` directory) or "gist"
repositories (both can be enabled with command line options). It also doesn't access
private repositories or secret gists.

## Requirements:
- Python 3.7+
- Git 1.7+
- Python packages:
    - GitPython
    - PyGithub

## Run:

### Clone Repo, Create/Activate Virtual Environment, Install Dependencies, Run:

```
git clone git@github.com:cgoldberg/githubtakeout.git
cd ./githubtakeout
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
./githubtakeout.py <github username>
```

### Usage:

```
usage: githubtakeout.py [-h] [--format FORMAT] [--dir DIR] [--gists] [--history] [--list] username

positional arguments:
  username         GitHub username

options:
  -h, --help       show this help message and exit
  --format FORMAT  archive format (tar, zip)
  --dir DIR        output directory
  --gists          include gists
  --history        include commit history and branches (.git directory)
  --list           list repos only
```

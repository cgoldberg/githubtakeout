# githubtakeout

## Archive your public Git repos and Gists from GitHub

---

- Copyright (c) 2015-2025 [Corey Goldberg](https://github.com/cgoldberg)
- License: [MIT](https://opensource.org/licenses/MIT)
- Development: [https://github.com/cgoldberg/githubtakeout](https://github.com/cgoldberg/githubtakeout)
- Compatibility: Python 3

----

## About:

_githubtakeout_ is a data export tool for public git repositories hosted on GitHub.
It clones your personal repos and gists, and creates a tarball of each.

## Run:

### Clone Repo, Create/Activate Virtual Environment, Install Dependencies:

```
git clone https://github.com/cgoldberg/githubtakeout.git
cd ./githubtakeout
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Usage:

```
usage: githubtakeout.py [-h] [--gists] [--list] [--dir DIR] username

positional arguments:
  username    GitHub username

options:
  -h, --help  show this help message and exit
  --gists     include gists
  --list      list repos only
  --dir DIR   output directory
```

----

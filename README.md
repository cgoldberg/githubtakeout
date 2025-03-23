# githubtakeout

## Archive your public Git repos and Gists from GitHub

---

- Copyright (c) 2015-2025 [Corey Goldberg](https://github.com/cgoldberg)
- License: [MIT](https://opensource.org/licenses/MIT)
- Development: [https://github.com/cgoldberg/githubtakeout](https://github.com/cgoldberg/githubtakeout)

----

## About:

_githubtakeout_ is a data export tool for archiving public Git repositories hosted on GitHub.
It clones your personal repoos, and creates a tarball of each.

By default, it doesn't save commit history or branches (`.git` directory) or Gist repositories
(both can be enabled with command line options).

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
usage: githubtakeout.py [-h] [--gists] [--history] [--list] [--dir DIR] username

positional arguments:
  username    GitHub username

options:
  -h, --help  show this help message and exit
  --gists     include gists
  --history   include commit history and branches (.git directory)
  --list      list repos only
  --dir DIR   output directory
```

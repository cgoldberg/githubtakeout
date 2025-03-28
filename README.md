# githubtakeout

## Archive Git Repos and Gists from GitHub

---

- Copyright (c) 2015-2025 [Corey Goldberg](https://github.com/cgoldberg)
- License: [MIT](https://raw.githubusercontent.com/cgoldberg/githubtakeout/refs/heads/master/LICENSE)
- Development: [GitHub](https://github.com/cgoldberg/githubtakeout)
- Download/Install: [PyPI](https://pypi.org/project/githubtakeout)

----

## About:

`githubtakeout` is a data export tool for archiving Git repositories hosted on GitHub.
It clones a user's repos and creates an archive of each.

It supports public/private repos and public/secret gists. By default, it doesn't save
commit history or branches (`.git` directory), or Gist repositories (both can be enabled
with command line options).

When you run the program, archives of your repos will be saved in a directory named
`backups` inside your current working directory, unless a different location is specified
using the `--dir` option.

Archives are saved in compressed zip format (`.zip`) by default, but can also be saved
as tarballs (`.tar.gz`) using the `--format=tar` option.

## Requirements:

- Python 3.12+
- Git 1.7+
- Python packages:
    - GitPython
    - PyGithub

## Installation:

Install from [PyPI](https://pypi.org/project/githubtakeout):

```
pip install githubtakeout
```

## Authentication:

By default, `githubtakeout` will only retrieve an account's public repos. To access
private repos and secret gists, you need to authenticate.

First, you must create a [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
  on Github (either a fine-grained or classic personal access token). Once you have a token, you can set the `GITHUB_TOKEN` environment variable:

```
$ export GITHUB_TOKEN=<auth token created on GitHub>
```

If you prefer to be prompted for your token each time you run the program, use the `--token` argument.

### CLI Options:

```
usage: githubtakeout [-h] [--dir DIR] [--format FORMAT] [--gists] [--history] [--list] [--token] username

positional arguments:
  username         GitHub username

options:
  -h, --help       show this help message and exit
  --dir DIR        output directory
  --format FORMAT  archive format (tar, zip)
  --gists          include gists
  --history        include commit history and branches (.git directory)
  --list           list repos only
  --token          prompt for auth toke
```


## Usage Examples:

### Install from PyPI with pipx, Run:

```
pipx install githubtakeout
githubtakeout <github username>
```

### Create/Activate Virtual Environment, Install from PyPI, Run:

```
python3 -m venv venv
source venv/bin/activate
pip install githubtakeout
githubtakeout <github username>
```

### Clone Repo, Create/Activate Virtual Environment, Install from Source, Run:

```
git clone git@github.com:cgoldberg/githubtakeout.git
cd ./githubtakeout
python3 -m venv venv
source venv/bin/activate
pip install .
githubtakeout <github username>
```

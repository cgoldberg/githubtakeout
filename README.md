# githubtakeout

## Backup and archive Git Repos and Gists from GitHub

---

- Copyright (c) 2015-2025 [Corey Goldberg][github-home]
- Development: [GitHub][github-repo]
- Download/Install: [PyPI][pypi-githubtakeout]
- License: [MIT][mit-license]

----

## About:

`githubtakeout` is a data export tool for backing up and archiving Git
repositories hosted on GitHub. It clones a user's repos and creates an archive
of each.

It supports public/private repos and public/secret gists. By default, it
doesn't save commit history or branches (`.git` directory), or Gist
repositories (both can be enabled with command line options).

When you run the program, archives of your repos will be saved in a directory
named `backups` inside your current working directory, unless a different
location is specified using the `--dir` option.

Archives are saved in compressed zip format (`.zip`) by default. You can also
save as tarballs (`.tar.gz`) using the `--format=tar` option, or skip archiving
using the `--format=none` option.

## Requirements:

- Python 3.12+
- Git 1.7+

## Installation:

#### Install from [PyPI][pypi-githubtakeout]:

```
pip install githubtakeout
```

## Authentication:

By default, `githubtakeout` will only retrieve an account's public repos. To
access private repos and secret gists, you need to authenticate.

First, you must create a [personal access token][github-pat] on Github (either
a fine-grained or classic personal access token). Once you have a token, you
can set the `GITHUB_TOKEN` environment variable:

```
$ export GITHUB_TOKEN=<access token>
```

If you prefer to be prompted for your token each time you run the program, use
the `--token` argument.

## CLI Options:

```
usage: githubtakeout [-h] [--dir DIR] [--format {tar,zip,none}] [--gists] [--history] [--list] [--token] username

positional arguments:
  username                 github username

options:
  -h, --help               show this help message and exit
  --dir DIR                output directory (default: .)
  --format {tar,zip,none}  archive format (default: zip)
  --gists                  include gists
  --history                include commit history and branches (.git directory)
  --list                   list repos only
  --token                  prompt for auth token
```

## Usage Examples:

#### Install from PyPI with pipx, Run:

```
pipx install githubtakeout
githubtakeout <github username>
```

#### Clone Repo, Create/Activate Virtual Environment, Install from Source, Run:

```
git clone git@github.com:cgoldberg/githubtakeout.git
cd ./githubtakeout
python3 -m venv venv
source venv/bin/activate
pip install .
githubtakeout <github username>
```

[github-home]: https://github.com/cgoldberg
[github-repo]: https://github.com/cgoldberg/sudokubot
[github-pat]: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
[pypi-githubtakeout]: https://pypi.org/project/githubtakeout
[mit-license]: https://raw.githubusercontent.com/cgoldberg/githubtakeout/refs/heads/master/LICENSE

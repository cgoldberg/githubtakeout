# githubtakeout

### Archive your git repos from GitHub

---

- Copyright (c) 2015 [Corey Goldberg](https://github.com/cgoldberg)
- License: [MIT](https://opensource.org/licenses/MIT)
- Development: [https://github.com/cgoldberg/githubtakeout](https://github.com/cgoldberg/githubtakeout)
- Compatibility: Python 2.7

----

### About:

_githubtakeout_ is a data export tool for git repositories hosted on GitHub.  It clones your personal repos and gists, and creates a tarball of each.

### Install:

`pip install githubtakeout`

### Run:

Set environment variables for GITHUBUSER and GITHUBPASSWORD, then invoke `githubtakeout.py` from the command line.

For example, in bash shell:

    $ export GITHUBUSER='USER'
    $ export GITHUBPASSWORD='PASSWORD'
    $ ./githubtakeout.py

or simply:

`$ GITHUBUSER='USER' GITHUBPASSWORD='PASSWORD' ./githubtakeout.py`

----

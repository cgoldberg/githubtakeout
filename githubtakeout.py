#!/usr/bin/env python3

import argparse
import getpass
import logging
import os
import stat
import tarfile
import urllib
import zipfile
import git
import github

from pathlib import Path
from timeit import default_timer
from github.AuthenticatedUser import AuthenticatedUser
from github.Gist import Gist
from github.NamedUser import NamedUser
from github.PaginatedList import PaginatedList
from github.Repository import Repository
from urllib import parse
from typing import cast

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def add_creds(url, username, token):
    # type: (str, str, object) -> str
    if token is None:
        return url
    else:
        username = urllib.parse.quote(username)
        url_parts = urllib.parse.urlparse(url)
        netloc = f"{username}:{token}@{url_parts.netloc}"
        url_parts = url_parts._replace(netloc=netloc)
        return cast(str, urllib.parse.urlunparse(url_parts))


def archive(local_repo_dir, archive_format="zip", is_gist=False):
    # type: (str, str, bool) -> str
    if archive_format not in ("tar", "zip"):
        raise ValueError(f"{archive_format} is not a valid archive format")
    base_name = os.path.basename(local_repo_dir)
    extension = "tar.gz" if archive_format == "tar" else archive_format
    archive_name = f"{base_name}.{extension}"
    if is_gist:
        archive_name = f"gist-{archive_name}"
    parent_dir = os.path.dirname(local_repo_dir)
    archive_path = os.path.join(parent_dir, archive_name)
    logger.info(f"creating archive: {archive_path}")
    if archive_format == "tar":
        with tarfile.open(archive_path, "w:gz") as tar_archive:
            tar_archive.add(local_repo_dir, arcname=base_name)
    elif archive_format == "zip":
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zip_archive:
            repo_path = Path(local_repo_dir)
            for entry in repo_path.rglob("*"):
                path = os.path.join(base_name, entry.relative_to(repo_path))
                zip_archive.write(entry, arcname=path)
    return archive_path


# On windows, you can frequently get permission errors trying to delete
# .git artifacts in the downloaded archive
def safe_unlink(path):
    # type: (Path) -> None
    if not path.exists():
        return

    try:
        path.unlink()
    except PermissionError:
        try:
            # Try to make it writable
            os.chmod(path, stat.S_IWRITE)
            path.unlink()
        except Exception as e:
            logger.info(f"Failed to delete file {path}: {e}")


# shutil.rmtree follows symlinks and doesn't handle read-only files or permission errors cleanly
def safe_rmtree(path):
    # type: (str) -> None
    path = Path(path)
    if not path.exists():
        return

    if not path.is_dir():
        raise ValueError(f"{path} is not a directory")

    for child in path.iterdir():
        if child.is_symlink():
            safe_unlink(child)
        elif child.is_dir():
            safe_rmtree(child)
        else:
            safe_unlink(child)

    try:
        path.rmdir()
    except PermissionError:
        try:
            # Try to make it writable
            os.chmod(path, stat.S_IWRITE)
            path.rmdir()
        except Exception as e:
            logger.info(f"Failed to remove {path}: {e}")


def clone_and_archive_repo(
    repo_url,
    local_repo_dir,
    archive_format,
    include_history,
    is_gist=False,
):
    # type: (str, str, str, bool, bool) -> None
    safe_rmtree(local_repo_dir)
    logger.info(f"cloning repo: {repo_url} to {local_repo_dir}")
    start = default_timer()
    try:
        if include_history:
            git.Repo.clone_from(repo_url, local_repo_dir)
        else:
            # shallow clone (no commit history or branches)
            git.Repo.clone_from(repo_url, local_repo_dir, multi_options=["--depth=1"])
            try:
                safe_rmtree(os.path.join(local_repo_dir, ".git"))
            except FileNotFoundError:
                pass
    except git.GitCommandError as e:
        logger.error(e)
        return
    elapsed = default_timer() - start
    logger.info(f"elapsed time: {elapsed:.3f} secs")
    archive_path = archive(local_repo_dir, archive_format, is_gist)
    size_kb = os.path.getsize(archive_path) / 1024
    logger.info(f"archive size: {size_kb:.2f} KB")
    logger.info("deleting repo")
    safe_rmtree(local_repo_dir)
    elapsed = default_timer() - start
    logger.info(
        f"successfully backed up {repo_url} to {archive_path} in {elapsed:.3f} secs\n\n"
    )


def get_user(username, prompt_token):
    # type: (str, bool) -> tuple[NamedUser | AuthenticatedUser, PaginatedList[Repository], PaginatedList[Gist], str | None]
    if prompt_token:
        token = getpass.getpass("Token:")
        if not token:
            print(f"Error: auth token cannot be empty")
            exit(1)
        auth = github.Auth.Token(token)
        gh = github.Github(auth=auth)
    else:
        token = os.getenv("GITHUB_TOKEN")
        if token is not None:
            auth = github.Auth.Token(token)
            gh = github.Github(auth=auth)
        else:
            gh = github.Github()
    if token is None:
        try:
            user = gh.get_user(username)
        except github.GithubException as e:
            if e.data["status"] == "404":
                print(f'Error: user "{username}" not found on GitHub')
            else:
                raise e
            exit(1)
        repos = user.get_repos()
    else:
        # you need to be authenticated and then call the API
        # with no username to get private repos
        user = gh.get_user()
        repos = user.get_repos(affiliation="owner")
        try:
            # this just makes an API request so we can exit if unauthorized
            _ = repos.totalCount
        except github.GithubException as e:
            if e.data["status"] == "401":
                print(f'Error: invalid auth token for user "{username}" on GitHub')
            else:
                raise e
            exit(1)
    gists = user.get_gists()
    return user, repos, gists, token


def run(
    username,
    base_dir,
    archive_format,
    include_gists,
    include_history,
    list_only,
    prompt_token,
):
    # type: (str, str, str, bool, bool, bool, bool) -> None
    working_dir = os.path.join(base_dir, "backups")
    user, repos, gists, token = get_user(username, prompt_token)
    num_repos = repos.totalCount
    if not list_only:
        logger.info(f"creating archives in: {working_dir}\n")
    logger.info(f'found {num_repos} repos for user "{username}"\n')
    for repo in repos:
        local_repo_dir = os.path.join(working_dir, repo.name)
        url = add_creds(repo.clone_url, username, token)
        if list_only:
            logger.info(url)
        else:
            clone_and_archive_repo(url, local_repo_dir, archive_format, include_history)
    if include_gists:
        num_gists = gists.totalCount
        logger.info("")
        logger.info(f'found {num_gists} gists for user "{username}"\n')
        for gist in gists:
            local_repo_dir = os.path.join(working_dir, gist.id)
            url = add_creds(gist.git_pull_url, username, token)
            if list_only:
                logger.info(url)
            else:
                clone_and_archive_repo(
                    url, local_repo_dir, archive_format, include_history, is_gist=True
                )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="GitHub username")
    parser.add_argument("--dir", default=os.getcwd(), help="output directory")
    parser.add_argument("--format", default="zip", help="archive format (tar, zip)")
    parser.add_argument(
        "--gists", default=False, action="store_true", help="include gists"
    )
    parser.add_argument(
        "--history",
        default=False,
        action="store_true",
        help="include commit history and branches (.git directory)",
    )
    parser.add_argument(
        "--list", default=False, action="store_true", help="list repos only"
    )
    parser.add_argument(
        "--token", default=False, action="store_true", help="prompt for auth token"
    )
    args = parser.parse_args()
    run(
        username=args.username,
        base_dir=args.dir,
        archive_format=args.format,
        include_gists=args.gists,
        include_history=args.history,
        list_only=args.list,
        prompt_token=args.token,
    )


if __name__ == "__main__":
    main()

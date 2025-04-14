#!/usr/bin/env python3

import argparse
import getpass
import logging
import os
import shutil
import stat
import sys
import tarfile
import urllib
import zipfile

from pathlib import Path
from timeit import default_timer

import git
import github


logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def add_creds(url, username, token):
    if token is None:
        new_url = url
    else:
        username = urllib.parse.quote(username)
        url_parts = urllib.parse.urlparse(url)
        netloc = f'{username}:{token}@{url_parts.netloc}'
        new_url = urllib.parse.urlunparse(url_parts._replace(netloc=netloc))
    return new_url


def archive(local_repo_dir, archive_format='zip', is_gist=False):
    if archive_format not in ('tar', 'zip'):
        raise ValueError(f'{archive_format} is not a valid archive format')
    base_name = os.path.basename(local_repo_dir)
    extension = 'tar.gz' if archive_format == 'tar' else archive_format
    archive_name = f'{base_name}.{extension}'
    if is_gist:
        archive_name = f'gist-{archive_name}'
    parent_dir = os.path.dirname(local_repo_dir)
    archive_path = os.path.join(parent_dir, archive_name)
    logger.info(f'creating archive: {archive_path}')
    if archive_format == 'tar':
        with tarfile.open(archive_path, 'w:gz') as tar_archive:
            tar_archive.add(local_repo_dir, arcname=base_name)
    elif archive_format == 'zip':
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zip_archive:
            repo_path = Path(local_repo_dir)
            for entry in repo_path.rglob('*'):
                path = os.path.join(base_name, entry.relative_to(repo_path))
                zip_archive.write(entry, arcname=path)
    return archive_path


def clone(repo_url, local_repo_dir, include_history):
    try:
        if include_history:
            # full clone
            repo = git.Repo.clone_from(repo_url, local_repo_dir)
        else:
            # shallow clone (no commit history or branches)
            repo = git.Repo.clone_from(repo_url, local_repo_dir, multi_options=['--depth=1'])
    except git.GitCommandError as e:
        logger.error(e)
        sys.exit('Error: failed cloning repo')
    finally:
        try:
            # release resources
            repo.close()
        except UnboundLocalError:
            # this occurs if we catch a signal while cloning
            pass



def clone_and_archive_repo(repo_url, local_repo_dir, archive_format, include_history, is_gist=False):
    def remove_readonly(func, path, _):
        # This is necessary so rmtree() doesn't fail if there are any readonly
        # dirs/files when trying to delete. This seems to happen after cloning on
        # Windows. When any error occurs during deletion, we change the permissions
        # and and reattempt removal.
        #
        # give read permissions
        os.chmod(path, stat.S_IREAD)
        # give write permissions
        os.chmod(path, stat.S_IWRITE)
        # try again
        func(path)
    try:
        # delete repo if it already exists
        shutil.rmtree(local_repo_dir, onexc=remove_readonly)
    except FileNotFoundError:
        pass
    repo_name = urllib.parse.urlparse(repo_url).path.lstrip('/')
    logger.info(f'cloning repo: {repo_name} to {local_repo_dir}')
    start = default_timer()
    clone(repo_url, local_repo_dir, include_history)
    if not include_history:
        # delete the .git directory if we are not saving history
        try:
            git_dir = os.path.join(local_repo_dir, '.git')
            shutil.rmtree(git_dir, onexc=remove_readonly)
        except FileNotFoundError:
            pass
    archive_path = archive(local_repo_dir, archive_format, is_gist)
    size_kb = os.path.getsize(archive_path) / 1024
    logger.info(f'archive size: {size_kb:.2f} KB')
    logger.info('deleting repo')
    try:
        # delete repo after archive is created
        shutil.rmtree(local_repo_dir, onexc=remove_readonly)
    except FileNotFoundError:
        pass
    elapsed = default_timer() - start
    base_name = os.path.basename(local_repo_dir)
    logger.info(f'successfully backed up "{base_name}" repo in {elapsed:.3f} secs\n')


def get_user(username, prompt_token):
    if prompt_token:
        token = getpass.getpass('Token:')
        if not token:
            sys.exit('Error: auth token cannot be empty')
        auth = github.Auth.Token(token)
        gh = github.Github(auth=auth)
    else:
        token = os.getenv('GITHUB_TOKEN')
        if token is not None:
            auth = github.Auth.Token(token)
            gh = github.Github(auth=auth)
        else:
            gh = github.Github()
    if token is None:
        try:
            user = gh.get_user(username)
        except github.GithubException as e:
            if e.data['status'] == '404':
                sys.exit(f'Error: user "{username}" not found on GitHub')
            else:
                raise e
        repos = user.get_repos()
    else:
        # you need to be authenticated and then call the API
        # with no username to get private repos
        user = gh.get_user()
        repos = user.get_repos(affiliation='owner')
        try:
            # this just makes an API request so we can exit if unauthorized
            _ = repos.totalCount
        except github.GithubException as e:
            if e.data['status'] == '401':
                sys.exit(f'Error: invalid auth token for user "{username}" on GitHub')
            else:
                raise e
    gists = user.get_gists()
    return user, repos, gists, token


def run(username, base_dir, archive_format, include_gists, include_history, list_only, prompt_token):
    working_dir = os.path.join(base_dir, 'backups')
    user, repos, gists, token = get_user(username, prompt_token)
    num_repos = repos.totalCount
    if not list_only:
        logger.info(f'creating archives in: {working_dir}\n')
    logger.info(f'found {num_repos} repos for user "{username}"\n')
    for repo in repos:
        local_repo_dir = os.path.join(working_dir, repo.name)
        url = add_creds(repo.clone_url, username, token)
        if list_only:
            logger.info(url)
        else:
            clone_and_archive_repo(
                url,
                local_repo_dir,
                archive_format,
                include_history
            )
    if include_gists:
        num_gists = gists.totalCount
        logger.info('')
        logger.info(f'found {num_gists} gists for user "{username}"\n')
        for gist in gists:
            local_repo_dir = os.path.join(working_dir, gist.id)
            url = add_creds(gist.git_pull_url, username, token)
            if list_only:
                logger.info(url)
            else:
                clone_and_archive_repo(
                    url,
                    local_repo_dir,
                    archive_format,
                    include_history,
                    is_gist=True
                )


def main():
    if sys.version_info < (3, 12):
        sys.exit('sorry, this program requires Python 3.12+')
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'username',
        help='github username'
    )
    parser.add_argument(
        '--dir',
        default=os.getcwd(),
        help='output directory'
    )
    parser.add_argument(
        '--format',
        default='zip',
        help='archive format (tar, zip)'
    )
    parser.add_argument(
        '--gists',
        action='store_true',
        default=False,
        help='include gists'
    )
    parser.add_argument(
        '--history',
        action='store_true',
        default=False,
        help='include commit history and branches (.git directory)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        default=False,
        help='list repos only'
    )
    parser.add_argument(
        '--token',
        action='store_true',
        default=False,
        help='prompt for auth token'
    )
    args = parser.parse_args()
    try:
        run(
            username=args.username,
            base_dir=args.dir,
            archive_format=args.format,
            include_gists=args.gists,
            include_history=args.history,
            list_only=args.list,
            prompt_token=args.token
        )
    except KeyboardInterrupt:
        sys.exit('\nexiting program ...')


if __name__ == '__main__':
    main()

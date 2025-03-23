#!/usr/bin/env python3

import argparse
import logging
import os
import shutil
import tarfile

from timeit import default_timer

import git
import github


logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def archive(local_repo_dir, is_gist=False):
    base_name = os.path.basename(local_repo_dir)
    parent_dir = os.path.dirname(local_repo_dir)
    if is_gist:
        name = f'gist-{base_name}.tar.gz'
    else:
        name = f'{base_name}.tar.gz'
    tarball_path = os.path.join(parent_dir, name)
    logger.info(f'creating archive: {tarball_path}')
    with tarfile.open(tarball_path, 'w:gz') as tar:
        tar.add(local_repo_dir, arcname=base_name)
    return tarball_path


def clone_and_archive_repo(repo_url, local_repo_dir, include_history, is_gist=False):
    try:
        shutil.rmtree(local_repo_dir)
    except FileNotFoundError:
        pass
    logger.info(f'cloning repo: {repo_url} to {local_repo_dir}')
    start = default_timer()
    try:
        if include_history:
            git.Repo.clone_from(repo_url, local_repo_dir)
        else:
            # shallow clone (no commit history or branches)
            git.Repo.clone_from(repo_url, local_repo_dir, multi_options=['--depth=1'])
            try:
                shutil.rmtree(os.path.join(local_repo_dir, '.git'))
            except FileNotFoundError:
                pass
    except git.GitCommandError as e:
        logger.error(e)
        return
    elapsed = default_timer() - start
    logger.info(f'elapsed time: {elapsed:.3f} secs')
    tarball_path = archive(local_repo_dir, is_gist=is_gist)
    size_kb = os.path.getsize(tarball_path) / 1024
    logger.info(f'archive size: {size_kb:.2f} KB')
    logger.info('deleting repo')
    try:
        shutil.rmtree(local_repo_dir)
    except FileNotFoundError:
        pass
    logger.info('')

def main(username, base_dir, include_gists=True, include_history=False, list=False):
    working_dir = os.path.join(base_dir, 'github_backups')
    if not list:
        logger.info(f'creating archives in: {working_dir}\n')
    gh = github.Github()
    user = gh.get_user(username)
    repos = user.get_repos()
    num_repos = len([1 for _ in repos])
    logger.info(f'found {num_repos} repos\n')
    for repo in repos:
        local_repo_dir = os.path.join(working_dir, repo.name)
        if list:
            logger.info(repo.clone_url)
        else:
            clone_and_archive_repo(
                repo.clone_url,
                local_repo_dir,
                include_history
            )
    if include_gists:
        gists = user.get_gists()
        num_gists = len([1 for _ in gists])
        logger.info(f'\nfound {num_gists} gists\n')
        for gist in gists:
            local_repo_dir = os.path.join(working_dir, gist.id)
            if list:
                logger.info(gist.git_pull_url)
            else:
                clone_and_archive_repo(
                    gist.git_pull_url,
                    local_repo_dir,
                    include_history,
                    is_gist=True
                )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'username',
        help='GitHub username'
    )
    parser.add_argument(
        '--dir',
        default=os.getcwd(),
        help='output directory'
    )
    parser.add_argument(
        '--gists',
        default=False,
        action='store_true',
        help='include gists'
    )
    parser.add_argument(
        '--history',
        default=False,
        action='store_true',
        help='include commit history and branches (.git directory)'
    )
    parser.add_argument(
        '--list',
        default=False,
        action='store_true',
        help='list repos only'
    )
    args = parser.parse_args()
    main(
        args.username,
        base_dir=args.dir,
        include_gists=args.gists,
        include_history=args.history,
        list=args.list
    )

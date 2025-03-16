#!/usr/bin/env python3

import argparse
import logging
import os
import shutil
import tarfile

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
    tarball_name = os.path.join(parent_dir, name)
    logger.info(f'creating archive: {tarball_name}')
    with tarfile.open(tarball_name, 'w:gz') as tar:
        tar.add(local_repo_dir, arcname=base_name)
    return tarball_name


def clone_and_archive_repo(repo_url, local_repo_dir, include_history, is_gist=False):
    try:
        shutil.rmtree(local_repo_dir)
    except FileNotFoundError:
        pass
    logger.info(f'cloning: {repo_url} to {local_repo_dir}')
    try:
        if include_history:
            git.Repo.clone_from(repo_url, local_repo_dir)
        else:
            # shallow clone (no commit history)
            git.Repo.clone_from(repo_url, local_repo_dir, multi_options=['--depth=1'])
            try:
                shutil.rmtree(f'{local_repo_dir}/.git')
            except FileNotFoundError:
                pass
    except git.GitCommandError as e:
        logger.error(e)
    if is_gist:
        archive(local_repo_dir, is_gist=True)
    else:
        archive(local_repo_dir)
    try:
        shutil.rmtree(local_repo_dir)
    except FileNotFoundError:
        pass


def process_repos(username, base_dir, include_history=False, include_gists=True, list=False):
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
            clone_and_archive_repo(repo.clone_url, local_repo_dir, include_history)
    if include_gists:
        gists = user.get_gists()
        num_gists = len([1 for _ in gists])
        logger.info(f'\nfound {num_gists} gists\n')
        for gist in gists:
            local_repo_dir = os.path.join(working_dir, gist.id)
            if list:
                logger.info(gist.git_pull_url)
            else:
                clone_and_archive_repo(gist.git_pull_url, local_repo_dir, include_history, is_gist=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('username', help='GitHub username')
    parser.add_argument('--gists', default=False, action="store_true", help='include gists')
    parser.add_argument('--history', default=False, action="store_true", help='include commit history (.git directories)')
    parser.add_argument('--list', default=False, action="store_true", help='list repos only')
    parser.add_argument('--dir', default=os.getcwd(), help='output directory')
    args = parser.parse_args()
    process_repos(args.username, args.dir, include_history=args.history, include_gists=args.gists, list=args.list)

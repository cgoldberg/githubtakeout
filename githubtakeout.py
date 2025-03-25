#!/usr/bin/env python3

import argparse
import logging
import os
import shutil
import tarfile
import zipfile

from pathlib import Path
from timeit import default_timer

import git
import github


logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


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
        with tarfile.open(archive_path, 'w:gz') as tar:
            tar.add(local_repo_dir, arcname=base_name)
    elif archive_format == 'zip':
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zip:
            repo_path = Path(local_repo_dir)
            for entry in repo_path.rglob('*'):
                path = os.path.join(base_name, entry.relative_to(repo_path))
                zip.write(entry, arcname=path)
    return archive_path


def clone_and_archive_repo(repo_url, local_repo_dir, archive_format, include_history, is_gist=False):
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
    archive_path = archive(local_repo_dir, archive_format, is_gist)
    size_kb = os.path.getsize(archive_path) / 1024
    logger.info(f'archive size: {size_kb:.2f} KB')
    logger.info('deleting repo')
    try:
        shutil.rmtree(local_repo_dir)
    except FileNotFoundError:
        pass
    logger.info('')

def main(username, base_dir, archive_format, include_gists, include_history, list):
    working_dir = os.path.join(base_dir, 'backups')
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
                archive_format,
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
                    archive_format,
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
        '--archive-format',
        default='zip',
        help='archive format (tar, zip)'
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
        username=args.username,
        base_dir=args.dir,
        archive_format=args.archive_format,
        include_gists=args.gists,
        include_history=args.history,
        list=args.list
    )

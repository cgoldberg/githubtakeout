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


def archive(name, dir):
    file_path = os.path.join(dir, name)
    tarball = f'{file_path}.tar.gz'
    #logger.info(f'creating archive: {tarball}')
    #with tarfile.open(tarball, 'w:gz') as tar:
    #    tar.add(dir)


def clone_repo(remote_url, local_repo):
    logger.info(f'cloning: {remote_url} to {local_repo}')
    try:
        pass
        git.Repo.clone_from(remote_url, local_repo)
    except git.GitCommandError as e:
        logger.error(e)


def clone_repos(username, base_dir, include_gists=True, list=False):
    working_dir = os.path.join(base_dir, 'github_backups')
    if not list:
        logger.info(f'creating archives in: {working_dir}\n')
    gh = github.Github()
    user = gh.get_user(username)
    repos = user.get_repos()
    num_repos = len([1 for _ in repos])
    logger.info(f'found {num_repos} repos\n')
    for repo in repos:
        local_repo = os.path.join(working_dir, repo.name)
        #include_forks = False
        #if repo.source is not None and not include_forks:
        #    pass
        #else:
        if list:
            logger.info(repo.git_url)
        else:
            clone_repo(repo.git_url, local_repo)
            #archive(repo.name, local_repo)
            #shutil.rmtree(local_repo)
    if include_gists:
        gists = user.get_gists()
        num_gists = len([1 for _ in gists])
        logger.info(f'\nfound {num_gists} gists\n')
        for gist in gists:
            if list:
                logger.info(gist.git_pull_url)
            else:
                clone_repo(gist.git_pull_url, local_repo)
                #archive(gist.id, working_dir)
                #shutil.rmtree(local_repo)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('username',
                        help='GitHub username')
    parser.add_argument('--gists', default=False, action="store_true",
                        help='include gists')
    parser.add_argument('--list', default=False, action="store_true",
                        help='list repos only')
    parser.add_argument('--dir', default=os.getcwd(),
                        help='output directory')
    args = parser.parse_args()
    clone_repos(args.username, args.dir, include_gists=args.gists, list=args.list)

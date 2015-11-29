import argparse
import logging
import os
import shutil
import tarfile

import git
from github import Github


logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


try:
    GITHUBUSER = os.environ['GITHUBUSER']
    GITHUBPASSWORD = os.environ['GITHUBPASSWORD']
except KeyError as e:
    raise SystemExit('GITHUBUSER and GITHUBPASSWORD environment'
                     ' variables are required')


def make_gzip_tarball(source_dir, output_dir, tarball_filename):
    output_path = os.path.join(output_dir, tarball_filename)
    with tarfile.open(output_path, 'w:gz') as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))
    return output_path


def clone_repo(repo_url, repo_path):
    logger.info('cloning: {}'.format(repo_url))
    try:
        git.Repo.clone_from(repo_url, repo_path)
    except git.GitCommandError as e:
        logger.error(e)


def archive_repo(repo_name, repos_dir, repo_path):
    tarball_filename = '{}.tar.gz'.format(repo_name)
    logger.info('creating archive: {}'.format(tarball_filename))
    make_gzip_tarball(repo_path, repos_dir, tarball_filename)
    logger.info('deleting repo: {}\n'.format(repo_name))
    shutil.rmtree(repo_path)


def export_repos(include_gists=True):
    repos_dir = 'github_backup'
    github = Github(GITHUBUSER, GITHUBPASSWORD)
    user = github.get_user(GITHUBUSER)
    for repo in user.get_repos():
        repo_path = os.path.join(repos_dir, repo.name)
        # don't include forked repos
        if repo.source is None:
            clone_repo(repo.git_url, repo_path)
            archive_repo(repo.name, repos_dir, repo_path)
    if include_gists:
        for gist in user.get_gists():
            gist_path = os.path.join(repos_dir, gist.id)
            clone_repo(gist.git_pull_url, gist_path)
            archive_repo(gist.name, repos_dir, gist_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', nargs='?', default=os.getcwd(),
                        help='output directory')
    args = parser.parse_args()
    logger.info('cloning repos and storing tarballs in: %s\n' % args.dir)
    export_repos(args.dir)

import argparse
import logging
import os
import shutil
import tarfile

import git
import github


logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


#try:
#    GITHUBUSER = os.environ['GITHUBUSER']
#    GITHUBPASSWORD = os.environ['GITHUBPASSWORD']
#except KeyError:
#    raise SystemExit('GITHUBUSER and GITHUBPASSWORD environment'
#                     ' variables are required')


#def archive(name, dir):
#    tarball = '{}.tar.gz'.format(os.path.join(dir, name))
#    logger.info('creating archive: {}'.format(tarball))
#    with tarfile.open(tarball, 'w:gz') as tar:
#        tar.add(dir)


def clone_repo(remote_url, local_repo):
    logger.info('cloning: {}'.format(remote_url))
    try:
        git.Repo.clone_from(remote_url, local_repo)
    except git.GitCommandError as e:
        logger.error(e)


def clone_repos(working_dir, include_forks=False, include_gists=True):
    username = 'cgoldberg'
    #username = GITHUBUSER
    #password = GITHUBPASSWORD
    #working_dir = 'git_backups'
    #working_dir = os.path.join(backup_dir, working_dir)
    #github = github.Github(username, password)
    gh = github.Github()
    user = gh.get_user(username)
    for repo in user.get_repos():
        if repo.source is not None and not include_forks:
            pass
        else:
            local_repo = os.path.join(working_dir, repo.name)
            clone_repo(repo.git_url, local_repo)
            #archive(repo.name, local_repo)
            #shutil.rmtree(local_repo)
    if include_gists:
        for gist in user.get_gists():
            local_repo = os.path.join(working_dir, gist.id)
            clone_repo(gist.git_pull_url, local_repo)
            #archive(gist.id, working_dir)
            #shutil.rmtree(local_repo)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', nargs='?', default=os.getcwd(),
                        help='output directory')
    parser.add_argument('--gists', default=False, action="store_true",
                        help='include gists')
    args = parser.parse_args()
    logger.info('creating tarballs in: %s\n' % args.dir)
    clone_repos(args.dir, include_gists=args.gists)

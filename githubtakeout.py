from os.path import basename, exists, join
import shutil
import tarfile

from git import Repo
from github import Github



def make_gzip_tarball(source_dir, output_dir, tarball_filename):
    output_path = join(output_dir, tarball_filename)
    with tarfile.open(output_path, 'w:gz') as tar:
        tar.add(source_dir, arcname=basename(source_dir))
    return output_path


def clone_repo(repo_url, repo_path):
    print 'cloning: {}'.format(repo_url)
    Repo.clone_from(repo_url, repo_path)


def get_repos(user_name):
    github = Github()
    user = github.get_user(user_name)
    return user.get_repos()


def archive_repo(repo_name, repos_dir, repo_path):
    tarball_filename = '{}.tar.gz'.format(repo_name)
    print 'creating archive: {}'.format(tarball_filename)
    make_gzip_tarball(repo_path, repos_dir, tarball_filename)
    # delete repo after it's archived
    print 'deleting repo: {}\n'.format(repo_name)
    if exists(repo_path):
        shutil.rmtree(repo_path)

def export_repos(user_name, include_forked_repos=False):
    repos_dir = 'repo_backups'
    # clobber existing repos directory to start fresh
    if exists(repos_dir):
        shutil.rmtree(repos_dir)
    for repo in get_repos(user_name):
        repo_path = join(repos_dir, repo.name)
        if repo.source is None:
            clone_repo(repo.git_url, repo_path)
            archive_repo(repo.name, repos_dir, repo_path)
        else:
            if include_forked_repos:
                clone_repo(repo.git_url, repo_path)
                archive_repo(repo.name, repos_dir, repo_path)


def export_gists(user_name):
    gists_dir = 'gist_backups'
    # clobber existing gists directory to start fresh
    if exists(gists_dir):
        shutil.rmtree(gists_dir)
    github = Github()
    user = github.get_user(user_name)
    for gist in user.get_gists():
        print('cloning: {}'.format(gist.id))
        gist_path = join(gists_dir, gist.id)
        clone_repo(gist.git_pull_url, gist_path)
        archive_repo(gist.name, gists_dir, gist_path)
#
#def archive_
#        tarball_filename = '{}.tar.gz'.format(gist.id)
#        print 'creating archive: {}'.format(tarball_filename)
#        make_gzip_tarball(gist_path, gists_dir, tarball_filename)
#        # delete repo after it's archived
#        print 'deleting repo: {}\n'.format(gist.id)
#        if exists(gist_path):
#            shutil.rmtree(gist_path)



if __name__ == '__main__':
    user = 'cgoldberg'
    export_repos(user)
    export_repos(user)

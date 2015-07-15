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


def archive_repos(user):
    github = Github()
    repos_dir = 'repo_backups'
    # clobber existing directory to start fresh
    if exists(repos_dir):
        shutil.rmtree(repos_dir)
    user = github.get_user(user)
    for repository in user.get_repos():
        print dir(repository)
        print(repository.full_name)
        repo_path = join(repos_dir, repository.name)
        Repo.clone_from(repository.git_url, repo_path)
        tarball_filename = '{}.tar.gz'.format(repository.name)
        make_gzip_tarball(repo_path, repos_dir, tarball_filename)
        # delete repo once we have it archived
        if exists(repo_path):
            shutil.rmtree(repo_path)


def archive_gists(user):
    github = Github()
    gists_dir = 'gist_backups'
    # clobber existing directory to start fresh
    if exists(gists_dir):
        shutil.rmtree(gists_dir)
    user = github.get_user(user)
    for gist in user.get_gists():
        print dir(gist)
        print(gist.id)
        gist_path = join(gists_dir, gist.id)
        Repo.clone_from(gist.git_pull_url, gist_path)
        tarball_filename = '{}.tar.gz'.format(gist.id)
        make_gzip_tarball(gist_path, gists_dir, tarball_filename)
        # delete repo once we have it archived
        if exists(gist_path):
            shutil.rmtree(gist_path)



if __name__ == '__main__':
    archive_repos('cgoldberg')

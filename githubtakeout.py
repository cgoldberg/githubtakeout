from os.path import basename, exists, join
import shutil
import tarfile

from git import Repo  # GitPython
from github import Github  # PyGithub


def make_gzip_tarball(source_dir, output_dir, tarball_filename):
    output_path = join(output_dir, tarball_filename)
    with tarfile.open(output_path, 'w:gz') as tar:
        tar.add(source_dir, arcname=basename(source_dir))
    return output_path


def archive_repos(user):
    github = Github()
    dir = 'repo_backups'
    # clobber existing directory to start fresh
    if exists(dir):
        shutil.rmtree(dir)
    user = github.get_user(user)
    for repository in user.get_repos():
        print repository.full_name
        repo_path = join(dir, repository.name)
        Repo.clone_from(repository.git_url, repo_path)
        tarball_filename = '{}.tar.gz'.format(repository.name)
        make_gzip_tarball(repo_path, dir, tarball_filename)
        # delete repo since we have it archived
        if exists(repo_path):
            shutil.rmtree(repo_path)


if __name__ == '__main__':
    archive_repos('cgoldberg')

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


def clone_repo(repo, repo_path):
    #print repository.get_archive_link()
    print 'cloning: {}'.format(repo.git_url)
    Repo.clone_from(repo.git_url, repo_path)


def get_repos(user_name):
    github = Github()
    user = github.get_user(user_name)
    return user.get_repos()


def archive_repo(repo, repos_dir):
    tarball_filename = '{}.tar.gz'.format(repo.name)
    print 'creating archive: {}'.format(tarball_filename)
    make_gzip_tarball(repo_path, repos_dir, tarball_filename)
    # delete repo after it's archived
    print 'deleting repo: {}\n'.format(repo.name)
    if exists(repo_path):
        shutil.rmtree(repo_path)

def export_repos(user_name, include_forked_repos=False):
    repos_dir = 'repo_backups'
    # clobber existing repos directory to start fresh
    if exists(repos_dir):
        shutil.rmtree(repos_dir)
    for repo in get_repos(user_name):
        if repo.source is None:
            repo_path = join(repos_dir, repo.name)
            clone_repo(repo, repo_path)
            archive_repo(repo, repo_path)


def archive_gists(user_name):
    gists_dir = 'gist_backups'
    # clobber existing gists directory to start fresh
    if exists(gists_dir):
        shutil.rmtree(gists_dir)
    github = Github()
    user = github.get_user(user_name)
    for gist in user.get_gists():
        print('cloning: {}'.format(gist.id))
        gist_path = join(gists_dir, gist.id)
        Repo.clone_from(gist.git_pull_url, gist_path)
        tarball_filename = '{}.tar.gz'.format(gist.id)
        print 'creating archive: {}'.format(tarball_filename)
        make_gzip_tarball(gist_path, gists_dir, tarball_filename)
        # delete repo after it's archived
        print 'deleting repo: {}\n'.format(gist.id)
        if exists(gist_path):
            shutil.rmtree(gist_path)



if __name__ == '__main__':
    user = 'cgoldberg'
    export_repos(user)
    #archive_gists(user)

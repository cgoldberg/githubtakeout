from os.path import basename, join
import shutil
import tarfile

import git
from github import Github


def make_gzip_tarball(source_dir, output_dir, tarball_filename):
    output_path = join(output_dir, tarball_filename)
    with tarfile.open(output_path, 'w:gz') as tar:
        tar.add(source_dir, arcname=basename(source_dir))
    return output_path


def clone_repo(repo_url, repo_path):
    print 'cloning: {}'.format(repo_url)
    try:
        git.Repo.clone_from(repo_url, repo_path)
    except git.GitCommandError as e:
        print(e)


def archive_repo(repo_name, repos_dir, repo_path):
    tarball_filename = '{}.tar.gz'.format(repo_name)
    print 'creating archive: {}'.format(tarball_filename)
    make_gzip_tarball(repo_path, repos_dir, tarball_filename)
    # delete repo after it's archived
    print 'deleting repo: {}\n'.format(repo_name)
    shutil.rmtree(repo_path)


def export_repos(user_name, include_gists=True):
    repos_dir = 'github_backup'
    github = Github(USER, PASSWORD)
    user = github.get_user(user_name)
    for repo in user.get_repos():
        repo_path = join(repos_dir, repo.name)
        # don't include forked repos
        if repo.source is None:
            clone_repo(repo.git_url, repo_path)
            archive_repo(repo.name, repos_dir, repo_path)
    if include_gists:
        for gist in user.get_gists():
            gist_path = join(gists_dir, gist.id)
            clone_repo(gist.git_pull_url, gist_path)
            archive_repo(gist.name, gists_dir, gist_path)


if __name__ == '__main__':
    user = 'cgoldberg'
    export_repos(user)

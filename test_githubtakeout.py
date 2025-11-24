import re
from pathlib import Path

import pytest

import githubtakeout

USER = "cgoldberg"


def test_run_list_1_match(tmp_path, caplog):
    caplog.set_level("INFO")
    repo = "githubtakeout"
    githubtakeout.run(
        username=USER,
        base_dir=tmp_path,
        pattern=repo,
        archive_format="none",
        include_gists=False,
        include_history=False,
        keep=False,
        list_only=True,
        prompt_for_token=False,
    )
    assert "creating archives" not in caplog.text
    assert f"found 1 repos for user '{USER}'" in caplog.text
    assert "gists" not in caplog.text
    assert f"{USER}/{repo}" in caplog.text
    assert not Path(tmp_path / repo).exists()


def test_run_list_0_match(tmp_path, caplog):
    caplog.set_level("INFO")
    repo = "this_repo_does_not_exist"
    githubtakeout.run(
        username=USER,
        base_dir=tmp_path,
        pattern=repo,
        archive_format="none",
        include_gists=False,
        include_history=False,
        keep=False,
        list_only=True,
        prompt_for_token=False,
    )
    assert "creating archives" not in caplog.text
    assert f"found 0 repos for user '{USER}'" in caplog.text
    assert "gists" not in caplog.text


def test_run_list_0_match_with_gists(tmp_path, caplog):
    caplog.set_level("INFO")
    repo = "this_repo_does_not_exist"
    githubtakeout.run(
        username=USER,
        base_dir=tmp_path,
        pattern=repo,
        archive_format="none",
        include_gists=True,
        include_history=False,
        keep=False,
        list_only=True,
        prompt_for_token=False,
    )
    assert "creating archives" not in caplog.text
    assert f"found 0 repos for user '{USER}'" in caplog.text
    assert f"found 0 repos for user '{USER}'" in caplog.text


@pytest.mark.parametrize("archive_format", ["zip", "tar"])
def test_run_archive(archive_format, tmp_path, caplog):
    caplog.set_level("INFO")
    backup_dir = "backups"
    repo = "githubtakeout"
    githubtakeout.run(
        username=USER,
        base_dir=tmp_path,
        pattern=repo,
        archive_format=archive_format,
        include_gists=False,
        include_history=False,
        keep=False,
        list_only=False,
        prompt_for_token=False,
    )
    assert re.search(f"creating archives in: .*{backup_dir}", caplog.text)
    assert f"found 1 repos for user '{USER}'" in caplog.text
    assert "gists" not in caplog.text
    assert re.search(f"cloning repo: {USER}/{repo}.git to: .*{backup_dir}", caplog.text)
    assert "creating archive:" in caplog.text
    assert "archive size:" in caplog.text
    assert "deleting repo" in caplog.text
    assert f"successfully backed up '{repo}' repo" in caplog.text
    assert not Path(tmp_path / repo).exists()
    if archive_format == "tar":
        extension = "tar.gz"
    else:
        extension = archive_format
    assert Path(tmp_path / backup_dir / f"{repo}.{extension}").exists()


def test_run_no_archive_with_history(tmp_path, caplog):
    caplog.set_level("INFO")
    backup_dir = "backups"
    repo = "githubtakeout"
    githubtakeout.run(
        username=USER,
        base_dir=tmp_path,
        pattern=repo,
        archive_format="none",
        include_gists=False,
        include_history=True,
        keep=False,
        list_only=False,
        prompt_for_token=False,
    )
    assert re.search(f"creating archives in: .*{backup_dir}", caplog.text)
    assert f"found 1 repos for user '{USER}'" in caplog.text
    assert "gists" not in caplog.text
    assert re.search(f"cloning repo: {USER}/{repo}.git to: .*{backup_dir}", caplog.text)
    assert "creating archive:" not in caplog.text
    assert "archive size:" not in caplog.text
    assert "deleting repo" not in caplog.text
    assert f"successfully backed up '{repo}' repo" in caplog.text
    assert Path(tmp_path / backup_dir / repo).exists()
    assert Path(tmp_path / backup_dir / repo / ".git").exists()


def test_run_no_archive_without_history(tmp_path, caplog):
    caplog.set_level("INFO")
    backup_dir = "backups"
    repo = "githubtakeout"
    githubtakeout.run(
        username=USER,
        base_dir=tmp_path,
        pattern=repo,
        archive_format="none",
        include_gists=False,
        include_history=False,
        keep=False,
        list_only=False,
        prompt_for_token=False,
    )
    assert re.search("creating archives in: .*backups", caplog.text)
    assert f"found 1 repos for user '{USER}'" in caplog.text
    assert "gists" not in caplog.text
    assert re.search(f"cloning repo: {USER}/{repo}.git to: .*backups", caplog.text)
    assert "creating archive:" not in caplog.text
    assert "archive size:" not in caplog.text
    assert "deleting repo" not in caplog.text
    assert f"successfully backed up '{repo}' repo" in caplog.text
    assert Path(tmp_path / backup_dir / repo).exists()
    assert not Path(tmp_path / backup_dir / repo / ".git").exists()


def test_run_no_archive_pull_with_keep(tmp_path, caplog):
    caplog.set_level("INFO")
    backup_dir = "backups"
    repo = "githubtakeout"
    githubtakeout.run(
        username=USER,
        base_dir=tmp_path,
        pattern=repo,
        archive_format="none",
        include_gists=False,
        include_history=True,
        keep=True,
        list_only=False,
        prompt_for_token=False,
    )
    assert re.search(f"cloning repo: {USER}/{repo}.git to: .*backups", caplog.text)
    assert "pulling changes" not in caplog.text
    assert Path(tmp_path / backup_dir / repo).exists()
    githubtakeout.run(
        username=USER,
        base_dir=tmp_path,
        pattern=repo,
        archive_format="none",
        include_gists=False,
        include_history=True,
        keep=True,
        list_only=False,
        prompt_for_token=False,
    )
    assert re.search(f"pulling changes from repo: {USER}/{repo}.git to: .*backups", caplog.text)
    assert Path(tmp_path / backup_dir / repo).exists()

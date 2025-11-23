import re
from pathlib import Path

import pytest

import githubtakeout


def test_run_list_1_match(tmp_path, caplog):
    caplog.set_level("INFO")
    user = "cgoldberg"
    repo = "githubtakeout"
    githubtakeout.run(
        user,
        tmp_path,
        repo,
        "none",
        False,
        False,
        True,
        False,
    )
    assert "creating archives" not in caplog.text
    assert f"found 1 repos for user '{user}'" in caplog.text
    assert "gists" not in caplog.text
    assert f"{user}/{repo}" in caplog.text
    assert not Path(tmp_path / repo).exists()


def test_run_list_0_match(tmp_path, caplog):
    caplog.set_level("INFO")
    user = "cgoldberg"
    githubtakeout.run(
        user,
        tmp_path,
        "this_repo_does_not_exist",
        "none",
        False,
        False,
        True,
        False,
    )
    assert "creating archives" not in caplog.text
    assert f"found 0 repos for user '{user}'" in caplog.text
    assert "gists" not in caplog.text


def test_run_list_0_match_with_gists(tmp_path, caplog):
    caplog.set_level("INFO")
    user = "cgoldberg"
    githubtakeout.run(
        user,
        tmp_path,
        "this_repo_does_not_exist",
        "none",
        True,
        False,
        True,
        False,
    )
    assert "creating archives" not in caplog.text
    assert f"found 0 repos for user '{user}'" in caplog.text
    assert f"found 0 repos for user '{user}'" in caplog.text


@pytest.mark.parametrize("archive_format", ["zip", "tar"])
def test_run_archive(archive_format, tmp_path, caplog):
    caplog.set_level("INFO")
    backup_dir = "backups"
    user = "cgoldberg"
    repo = "githubtakeout"
    githubtakeout.run(
        user,
        tmp_path,
        repo,
        archive_format,
        False,
        False,
        False,
        False,
    )
    assert re.search(f"creating archives in: .*{backup_dir}", caplog.text)
    assert f"found 1 repos for user '{user}'" in caplog.text
    assert "gists" not in caplog.text
    assert "cloning repo" in caplog.text
    assert f"{user}/{repo}" in caplog.text
    assert "creating archive" in caplog.text
    assert "archive size" in caplog.text
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
    user = "cgoldberg"
    repo = "githubtakeout"
    githubtakeout.run(
        user,
        tmp_path,
        repo,
        "none",
        False,
        False,
        False,
        False,
    )
    assert re.search(f"creating archives in: .*{backup_dir}", caplog.text)
    assert f"found 1 repos for user '{user}'" in caplog.text
    assert "gists" not in caplog.text
    assert "cloning repo" in caplog.text
    assert f"{user}/{repo}" in caplog.text
    assert "creating archive" not in caplog.text
    assert "archive size" not in caplog.text
    assert "deleting repo" not in caplog.text
    assert f"successfully backed up '{repo}' repo" in caplog.text
    assert Path(tmp_path / repo).exists()
    assert Path(tmp_path / repo / ".git").exists()

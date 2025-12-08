import os
import re
from pathlib import Path

import pytest
from dotenv import load_dotenv

import githubtakeout

USER = "cgoldberg"


@pytest.fixture(autouse=True, scope="session")
def require_token():
    load_dotenv()
    required = "GITHUB_TOKEN"
    if not os.getenv(required):
        pytest.skip(
            reason=f"{required} environment variable or .env file is "
            "required to avoid rate limiting"
        )


@pytest.mark.skipif(
    os.getenv("GITHUB_TOKEN"), reason="GITHUB_TOKEN required to avoid rate limiting"
)
def test_run_list_1_match(tmp_path, caplog):
    caplog.set_level("INFO")
    repo = "githubtakeout"
    githubtakeout.run(
        username=USER,
        base_dir=tmp_path,
        pattern=repo,
        skip_pattern=None,
        archive_format="none",
        include_gists=False,
        include_history=False,
        skip_forks=False,
        keep=False,
        list_only=True,
        prompt_for_token=False,
    )
    assert "creating archives" not in caplog.text
    assert f"found 1 repos for user '{USER}'" in caplog.text
    assert not re.search(r"found \d* gists", caplog.text)
    assert f"{USER}/{repo}" in caplog.text
    assert not Path(tmp_path / "backups" / repo).exists()


def test_run_list_0_match(tmp_path, caplog):
    caplog.set_level("INFO")
    repo = "this_repo_does_not_exist"
    githubtakeout.run(
        username=USER,
        base_dir=tmp_path,
        pattern=repo,
        skip_pattern=None,
        archive_format="none",
        include_gists=False,
        include_history=False,
        skip_forks=False,
        keep=False,
        list_only=True,
        prompt_for_token=False,
    )
    assert "creating archives" not in caplog.text
    assert "found 0 repos" in caplog.text
    assert not re.search(r"found \d* gists", caplog.text)
    assert not Path(tmp_path / "backups" / repo).exists()


def test_run_list_0_match_with_gists(tmp_path, caplog):
    caplog.set_level("INFO")
    repo = "this_repo_does_not_exist"
    githubtakeout.run(
        username=USER,
        base_dir=tmp_path,
        pattern=repo,
        skip_pattern=None,
        archive_format="none",
        include_gists=True,
        include_history=False,
        skip_forks=False,
        keep=False,
        list_only=True,
        prompt_for_token=False,
    )
    assert "creating archives" not in caplog.text
    assert "found 0 repos" in caplog.text
    assert re.search(r"found \d* gists", caplog.text)
    assert not Path(tmp_path / "backups" / repo).exists()


def test_run_list_skip_all(tmp_path, caplog):
    caplog.set_level("INFO")
    githubtakeout.run(
        username=USER,
        base_dir=tmp_path,
        pattern=".*",
        skip_pattern=".*",
        archive_format="none",
        include_gists=False,
        include_history=False,
        skip_forks=False,
        keep=False,
        list_only=True,
        prompt_for_token=False,
    )
    assert "creating archives" not in caplog.text
    assert "found 0 repos" in caplog.text


@pytest.mark.parametrize("archive_format", ["zip", "tar"])
def test_run_archive_1_match(archive_format, tmp_path, caplog):
    caplog.set_level("INFO")
    backup_dir = "backups"
    repo = "githubtakeout"
    githubtakeout.run(
        username=USER,
        base_dir=tmp_path,
        pattern=repo,
        skip_pattern=None,
        archive_format=archive_format,
        include_gists=False,
        include_history=False,
        skip_forks=False,
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
    assert not Path(tmp_path / backup_dir / repo).exists()
    if archive_format == "tar":
        extension = "tar.gz"
    else:
        extension = archive_format
    assert Path(tmp_path / backup_dir / f"{repo}.{extension}").exists()


def test_run_no_archive_1_match_with_history(tmp_path, caplog):
    caplog.set_level("INFO")
    backup_dir = "backups"
    repo = "githubtakeout"
    githubtakeout.run(
        username=USER,
        base_dir=tmp_path,
        pattern=repo,
        skip_pattern=None,
        archive_format="none",
        include_gists=False,
        include_history=True,
        skip_forks=False,
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
    for extension in ("tar.gz", "zip"):
        assert not Path(tmp_path / backup_dir / f"{repo}.{extension}").exists()


def test_run_no_archive_1_match_without_history(tmp_path, caplog):
    caplog.set_level("INFO")
    backup_dir = "backups"
    repo = "githubtakeout"
    githubtakeout.run(
        username=USER,
        base_dir=tmp_path,
        pattern=repo,
        skip_pattern=None,
        archive_format="none",
        include_gists=False,
        include_history=False,
        skip_forks=False,
        keep=False,  # this doesn't matter when archive_format is "none"
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
    for extension in ("tar.gz", "zip"):
        assert not Path(tmp_path / backup_dir / f"{repo}.{extension}").exists()


def test_run_archive_1_match_with_history_pull_with_keep(tmp_path, caplog):
    caplog.set_level("INFO")
    backup_dir = "backups"
    repo = "githubtakeout"
    githubtakeout.run(
        username=USER,
        base_dir=tmp_path,
        pattern=repo,
        skip_pattern=None,
        archive_format="none",
        include_gists=False,
        include_history=True,
        skip_forks=False,
        keep=True,
        list_only=False,
        prompt_for_token=False,
    )
    assert f"found 1 repos for user '{USER}'" in caplog.text
    assert "gists" not in caplog.text
    assert re.search(f"cloning repo: {USER}/{repo}.git to: .*backups", caplog.text)
    assert "pulling changes" not in caplog.text
    assert "creating archive:" not in caplog.text
    assert "archive size:" not in caplog.text
    assert "deleting repo" not in caplog.text
    assert f"successfully backed up '{repo}' repo" in caplog.text
    assert Path(tmp_path / backup_dir / repo).exists()
    assert Path(tmp_path / backup_dir / repo / ".git").exists()
    caplog.clear()
    githubtakeout.run(
        username=USER,
        base_dir=tmp_path,
        pattern=repo,
        skip_pattern=None,
        archive_format="zip",
        include_gists=False,
        include_history=True,
        skip_forks=False,
        keep=True,
        list_only=False,
        prompt_for_token=False,
    )
    assert f"found 1 repos for user '{USER}'" in caplog.text
    assert "gists" not in caplog.text
    assert not re.search(f"cloning repo: {USER}/{repo}.git to: .*backups", caplog.text)
    assert re.search(
        f"pulling changes from repo: {USER}/{repo}.git to: .*backups", caplog.text
    )
    assert "creating archive:" in caplog.text
    assert "archive size:" in caplog.text
    assert "deleting repo" not in caplog.text
    assert f"successfully backed up '{repo}' repo" in caplog.text
    assert Path(tmp_path / backup_dir / repo).exists()
    assert Path(tmp_path / backup_dir / repo / ".git").exists()
    assert Path(tmp_path / backup_dir / f"{repo}.zip").exists()

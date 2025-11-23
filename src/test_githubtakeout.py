from pathlib import Path

import pytest

import githubtakeout


def test_run_list(tmp_path, caplog):
    user = "cgoldberg"
    repo = "githubtakeout"
    caplog.set_level("INFO")
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
    assert f"{user}/{repo}" in caplog.text
    assert not Path(tmp_path / repo).exists()


@pytest.mark.parametrize("archive_format", ["zip", "tar"])
def test_run_archive(archive_format, tmp_path, caplog):
    user = "cgoldberg"
    repo = "githubtakeout"
    caplog.set_level("INFO")
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
    assert "creating archives" in caplog.text
    assert f"found 1 repos for user '{user}'" in caplog.text
    assert "cloning repo" in caplog.text
    assert f"{user}/{repo}" in caplog.text
    assert "creating archive" in caplog.text
    assert "archive size" in caplog.text
    assert "deleting repo" in caplog.text
    assert f"successfully backed up '{repo}' repo" in caplog.text
    assert not Path(tmp_path / repo).exists()
    if archive_format == "tar":
        extension = ".tar.gz"
    else:
        extension = archive_format
    assert Path(tmp_path / "backups" / f"{repo}.{extension}").exists()

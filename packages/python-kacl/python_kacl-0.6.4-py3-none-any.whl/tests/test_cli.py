import json
import os
import shutil

import pytest
from click.testing import CliRunner
from freezegun import freeze_time

from kacl.kacl_cli import cli
from tests.snapshot_directory import snapshot_directory


def test_verify():
    runner = CliRunner()
    result = runner.invoke(cli, ["-f", "tests/data/CHANGELOG.md", "verify"])
    assert result.exit_code == 0
    assert result.output == "Success\n"

    result = runner.invoke(cli, ["-f", "tests/data/CHANGELOG_invalid.md", "verify"])
    assert result.exit_code == 10  # spawns 8 errors


def test_verify_invalid_duplicates():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["-f", "tests/data/CHANGELOG_invalid_duplicates.md", "verify"]
    )
    assert result.exit_code == 2


def test_verify_with_json_output():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["-f", "tests/data/CHANGELOG_invalid.md", "verify", "--json"]
    )
    validation_result = json.loads(result.output)

    assert len(validation_result["errors"]) == 10
    assert validation_result["valid"] is False


def test_current(tmp_path, snapshot):
    runner = CliRunner()
    resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data/")
    changelog_file = os.path.join(resources_dir, "CHANGELOG_with_changes.md")

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(
            cli,
            [
                "-f",
                changelog_file,
                "current",
            ],
            catch_exceptions=False,
        )
        assert result.exit_code == 0, result.output
        assert result.output == "1.0.0\n"


def test_next(tmp_path, snapshot):
    runner = CliRunner()
    resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data/")
    changelog_file = os.path.join(resources_dir, "CHANGELOG_with_changes.md")

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(
            cli,
            ["-f", changelog_file, "next", "patch"],
            catch_exceptions=False,
        )
        assert result.exit_code == 0, result.output
        assert result.output == "1.0.1\n"


@freeze_time("2023-01-01")
def test_release_patch(tmp_path, snapshot):
    runner = CliRunner()
    resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data/")
    changelog_file = os.path.join(resources_dir, "CHANGELOG_with_changes.md")

    with runner.isolated_filesystem(temp_dir=tmp_path) as project_root_path:
        shutil.copyfile(changelog_file, os.path.join(project_root_path, "CHANGELOG.md"))
        result = runner.invoke(
            cli,
            [
                "-f",
                "CHANGELOG.md",
                "release",
                "patch",
                "-m",
            ],
            catch_exceptions=False,
        )
        assert result.exit_code == 0, result.output
        snapshot_directory(snapshot=snapshot, directory_path=project_root_path)


@freeze_time("2023-01-01")
def test_release_post_bump(tmp_path, snapshot):
    runner = CliRunner()
    resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data/")
    changelog_file = os.path.join(resources_dir, "CHANGELOG_with_changes.md")

    with runner.isolated_filesystem(temp_dir=tmp_path) as project_root_path:
        shutil.copyfile(changelog_file, os.path.join(project_root_path, "CHANGELOG.md"))
        result = runner.invoke(
            cli,
            [
                "-c",
                os.path.join(resources_dir, "extension-config.yml"),
                "-f",
                "CHANGELOG.md",
                "release",
                "post",
                "-m",
            ],
            catch_exceptions=False,
        )
        assert result.exit_code == 0, result.output
        snapshot_directory(snapshot=snapshot, directory_path=project_root_path)


@freeze_time("2023-01-01")
def test_release_post_manual(tmp_path, snapshot):
    runner = CliRunner()
    resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data/")
    changelog_file = os.path.join(resources_dir, "CHANGELOG_with_changes.md")

    with runner.isolated_filesystem(temp_dir=tmp_path) as project_root_path:
        shutil.copyfile(changelog_file, os.path.join(project_root_path, "CHANGELOG.md"))
        result = runner.invoke(
            cli,
            [
                "-c",
                os.path.join(resources_dir, "extension-config.yml"),
                "-f",
                "CHANGELOG.md",
                "release",
                "2.0.0-hotfix.0",
                "-m",
            ],
            catch_exceptions=False,
        )
        assert result.exit_code == 0, result.output
        snapshot_directory(snapshot=snapshot, directory_path=project_root_path)


@freeze_time("2023-01-01")
def test_release_post_manual_fail(tmp_path, snapshot):
    runner = CliRunner()
    resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data/")
    changelog_file = os.path.join(resources_dir, "CHANGELOG_with_changes.md")

    with runner.isolated_filesystem(temp_dir=tmp_path) as project_root_path:
        shutil.copyfile(changelog_file, os.path.join(project_root_path, "CHANGELOG.md"))
        result = runner.invoke(
            cli,
            [
                "-c",
                os.path.join(resources_dir, "extension-config.yml"),
                "-f",
                "CHANGELOG.md",
                "release",
                "0.5.0-hotfix.0",
                "-m",
            ],
            catch_exceptions=True,
        )
        assert result.exit_code == 1, result.output


@freeze_time("2023-01-01")
def test_release_version_manual_fail_same_base_after_post(tmp_path, snapshot):
    runner = CliRunner()
    resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data/")
    changelog_file = os.path.join(resources_dir, "CHANGELOG_post_with_changes.md")

    with runner.isolated_filesystem(temp_dir=tmp_path) as project_root_path:
        shutil.copyfile(changelog_file, os.path.join(project_root_path, "CHANGELOG.md"))
        result = runner.invoke(
            cli,
            [
                "-c",
                os.path.join(resources_dir, "extension-config.yml"),
                "-f",
                "CHANGELOG.md",
                "release",
                "1.0.0",
                "-m",
            ],
            catch_exceptions=True,
        )
        assert result.exit_code == 1, result.output


@freeze_time("2023-01-01")
def test_release_post_manual_same_base(tmp_path, snapshot):
    runner = CliRunner()
    resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data/")
    changelog_file = os.path.join(resources_dir, "CHANGELOG_with_changes.md")

    with runner.isolated_filesystem(temp_dir=tmp_path) as project_root_path:
        shutil.copyfile(changelog_file, os.path.join(project_root_path, "CHANGELOG.md"))
        result = runner.invoke(
            cli,
            [
                "-c",
                os.path.join(resources_dir, "extension-config.yml"),
                "-f",
                "CHANGELOG.md",
                "release",
                "1.0.0-post.0",
                "-m",
            ],
            catch_exceptions=False,
        )
        assert result.exit_code == 0, result.output


@freeze_time("2023-01-01")
def test_release_minor(tmp_path, snapshot):
    runner = CliRunner()
    resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data/")
    changelog_file = os.path.join(resources_dir, "CHANGELOG_with_changes.md")

    with runner.isolated_filesystem(temp_dir=tmp_path) as project_root_path:
        shutil.copyfile(changelog_file, os.path.join(project_root_path, "CHANGELOG.md"))
        result = runner.invoke(
            cli,
            [
                "-f",
                "CHANGELOG.md",
                "release",
                "minor",
                "-m",
            ],
            catch_exceptions=False,
        )
        assert result.exit_code == 0, result.output
        snapshot_directory(snapshot=snapshot, directory_path=project_root_path)


@freeze_time("2023-01-01")
def test_release_major(tmp_path, snapshot):
    runner = CliRunner()
    resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data/")
    changelog_file = os.path.join(resources_dir, "CHANGELOG_with_changes.md")

    with runner.isolated_filesystem(temp_dir=tmp_path) as project_root_path:
        shutil.copyfile(changelog_file, os.path.join(project_root_path, "CHANGELOG.md"))
        result = runner.invoke(
            cli,
            [
                "-f",
                "CHANGELOG.md",
                "release",
                "major",
                "-m",
            ],
            catch_exceptions=False,
        )
        assert result.exit_code == 0, result.output
        snapshot_directory(snapshot=snapshot, directory_path=project_root_path)


@freeze_time("2023-01-01")
def test_release_custom(tmp_path, snapshot):
    runner = CliRunner()
    resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data/")
    changelog_file = os.path.join(resources_dir, "CHANGELOG_with_changes.md")

    with runner.isolated_filesystem(temp_dir=tmp_path) as project_root_path:
        shutil.copyfile(changelog_file, os.path.join(project_root_path, "CHANGELOG.md"))
        result = runner.invoke(
            cli,
            [
                "-f",
                "CHANGELOG.md",
                "release",
                "2.1.1",
                "-m",
            ],
            catch_exceptions=False,
        )
        assert result.exit_code == 0, result.output
        snapshot_directory(snapshot=snapshot, directory_path=project_root_path)


@freeze_time("2023-01-01")
def test_add_change_security(tmp_path, snapshot):
    runner = CliRunner()
    resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data/")
    changelog_file = os.path.join(resources_dir, "CHANGELOG_with_changes.md")

    with runner.isolated_filesystem(temp_dir=tmp_path) as project_root_path:
        shutil.copyfile(changelog_file, os.path.join(project_root_path, "CHANGELOG.md"))
        result = runner.invoke(
            cli,
            [
                "-f",
                "CHANGELOG.md",
                "add",
                "Security",
                "Important Security Change",
                "-m",
            ],
            catch_exceptions=False,
        )
        assert result.exit_code == 0, result.output
        snapshot_directory(snapshot=snapshot, directory_path=project_root_path)


def test_config(tmp_path, snapshot):
    runner = CliRunner()
    resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data/")

    result = runner.invoke(
        cli,
        [
            "-c",
            os.path.join(resources_dir, "config.yml"),
            "-f",
            "CHANGELOG.md",
            "verify",
        ],
        catch_exceptions=False,
    )
    assert result.exit_code != 0, result.output


@freeze_time("2023-01-01")
def test_squash(tmp_path, snapshot):
    runner = CliRunner()
    resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data/")
    changelog_file = os.path.join(resources_dir, "CHANGELOG_keepachangelog.com.md")

    with runner.isolated_filesystem(temp_dir=tmp_path) as project_root_path:
        shutil.copyfile(changelog_file, os.path.join(project_root_path, "CHANGELOG.md"))
        result = runner.invoke(
            cli,
            [
                "-f",
                "CHANGELOG.md",
                "squash",
                "--from-version",
                "0.0.1",
                "--to-version",
                "0.3.0",
                "-m",
            ],
            catch_exceptions=False,
        )
        assert result.exit_code == 0, result.output
        snapshot_directory(snapshot=snapshot, directory_path=project_root_path)


def test_squash_current(tmp_path, snapshot):
    runner = CliRunner()
    resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data/")
    changelog_file = os.path.join(resources_dir, "CHANGELOG_keepachangelog.com.md")

    with runner.isolated_filesystem(temp_dir=tmp_path) as project_root_path:
        shutil.copyfile(changelog_file, os.path.join(project_root_path, "CHANGELOG.md"))
        result = runner.invoke(
            cli,
            [
                "-f",
                "CHANGELOG.md",
                "squash",
                "--from-version",
                "0.0.1",
                "-m",
            ],
            catch_exceptions=False,
        )
        assert result.exit_code == 0, result.output
        snapshot_directory(snapshot=snapshot, directory_path=project_root_path)


@pytest.mark.skip(reason="No issue tracker openly available, test locally.")
def test_add_comments(tmp_path):
    runner = CliRunner()
    root_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "..",
    )
    resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data/")
    changelog_file = os.path.join(resources_dir, "CHANGELOG_issue_management.md")

    with runner.isolated_filesystem(temp_dir=tmp_path) as project_root_path:
        shutil.copyfile(changelog_file, os.path.join(project_root_path, "CHANGELOG.md"))
        shutil.copytree(
            os.path.join(root_dir, ".git"), os.path.join(project_root_path, ".git")
        )
        result = runner.invoke(
            cli,
            [
                "-f",
                "CHANGELOG.md",
                "add-comments",
                "1.0.0",
                "--jira-username",
                os.getenv("JIRA_USERNAME"),
                "--jira-password",
                os.getenv("JIRA_PASSWORD"),
                "--jira-host",
                os.getenv("JIRA_HOST"),
                "--jira-issue-pattern",
                "JIRA-[0-9]+",
                "--jira-issue-pattern",
                "MYJIRA-[0-9]+",
                "--jira-issue-pattern",
                "[A-Z]+-[0-9]+",
            ],
            catch_exceptions=False,
        )
        assert result.exit_code == 0, result.output


@freeze_time("2023-01-01")
def test_get_no_link_available(tmp_path, snapshot):
    runner = CliRunner()
    resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data/")
    changelog_file = os.path.join(resources_dir, "CHANGELOG_missing_link.md")

    with runner.isolated_filesystem(temp_dir=tmp_path) as project_root_path:
        result = runner.invoke(
            cli,
            [
                "-c",
                os.path.join(resources_dir, "extension-config.yml"),
                "-f",
                changelog_file,
                "get",
                "2.0.0",
            ],
            catch_exceptions=False,
        )
        assert result.exit_code == 0, result.output
        with open(os.path.join(project_root_path, "output.md"), "w") as file:
            file.write(result.output)
        snapshot_directory(snapshot=snapshot, directory_path=project_root_path)


def test_get_link_available(tmp_path, snapshot):
    runner = CliRunner()
    resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data/")
    changelog_file = os.path.join(resources_dir, "CHANGELOG_missing_link.md")

    with runner.isolated_filesystem(temp_dir=tmp_path) as project_root_path:
        result = runner.invoke(
            cli,
            [
                "-c",
                os.path.join(resources_dir, "extension-config.yml"),
                "-f",
                changelog_file,
                "get",
                "1.0.0",
            ],
            catch_exceptions=False,
        )
        assert result.exit_code == 0, result.output
        with open(os.path.join(project_root_path, "output.md"), "w") as file:
            file.write(result.output)
        snapshot_directory(snapshot=snapshot, directory_path=project_root_path)


def test_get_suppress_available_link(tmp_path, snapshot):
    runner = CliRunner()
    resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data/")
    changelog_file = os.path.join(resources_dir, "CHANGELOG_missing_link.md")

    with runner.isolated_filesystem(temp_dir=tmp_path) as project_root_path:
        result = runner.invoke(
            cli,
            [
                "-c",
                os.path.join(resources_dir, "extension-config.yml"),
                "-f",
                changelog_file,
                "get",
                "--no-link",
                "1.0.0",
            ],
            catch_exceptions=False,
        )
        assert result.exit_code == 0, result.output
        with open(os.path.join(project_root_path, "output.md"), "w") as file:
            file.write(result.output)
        snapshot_directory(snapshot=snapshot, directory_path=project_root_path)

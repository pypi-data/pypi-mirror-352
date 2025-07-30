import webbrowser

import pytest

from artefacts.cli.app import (
    hello,
    run,
    run_remote,
    add,
    delete,
)
from artefacts.cli.config import APIConf


def test_hello(cli_runner):
    project_name = "_pytest-project_"
    result = cli_runner.invoke(hello, [project_name])
    assert result.exit_code == 1
    assert result.output == (
        f"Error: No API KEY set. Please run `artefacts config add {project_name}`\n"
    )


def test_configure(cli_runner, mocker):
    # Do not open a browser in test mode.
    mocker.patch("webbrowser.open")
    project_name = "_pytest-project_"
    result = cli_runner.invoke(add, [project_name], input="MYAPIKEY\n")
    # Ensure the script has attempted to open the browser as intended
    webbrowser.open.assert_called_once()

    # Check CLI output
    assert result.output == (
        f"Opening the project settings page: https://app.artefacts.com/{project_name}/settings\n"
        f"Please enter your API KEY for {project_name}: \n"
        f"API KEY saved for {project_name}\n"
        "Would you like to download the generated artefacts.yaml file? This will overwrite any existing config file in the current directory. [y/N]: \n"
    )
    cli_runner.invoke(delete, [project_name])


def test_run(cli_runner):
    result = cli_runner.invoke(run, ["tests", "--config", "myconf.yaml"])
    assert result.exit_code == 1
    assert result.output == ("Error: Project config file myconf.yaml not found.\n")


def test_run_with_conf_invalid_jobname(cli_runner, project_with_key):
    job_name = "invalid_job_name"
    result = cli_runner.invoke(run, [job_name, "--config", "tests/fixtures/warp.yaml"])
    assert result.exit_code == 1
    assert result.output == (
        f"[{job_name}] Connecting to https://app.artefacts.com/api using ApiKey\n"
        f"[{job_name}] Starting tests\n"
        f"[{job_name}] Error: Job name not defined\n"
        "Aborted!\n"
    )


def test_run_with_conf(cli_runner, project_with_key):
    result = cli_runner.invoke(
        run, ["simple_job", "--config", "tests/fixtures/warp.yaml", "--dryrun"]
    )
    assert result.exit_code == 0
    assert result.output == (
        "[simple_job] Connecting to https://app.artefacts.com/api using ApiKey\n"
        "[simple_job] Starting tests\n"
        "[simple_job] Starting scenario 1/2: basic-tests\n"
        "[simple_job] Performing dry run\n"
        "[simple_job] Starting scenario 2/2: other-tests\n"
        "[simple_job] Performing dry run\n"
        "[simple_job] Done\n"
    )


def test_run_with_mode_ros1(cli_runner, project_with_key):
    result = cli_runner.invoke(
        run,
        ["simple_job", "--config", "tests/fixtures/artefacts_ros1.yaml", "--dryrun"],
    )
    assert result.exit_code == 0
    assert result.output == (
        "[simple_job] Connecting to https://app.artefacts.com/api using ApiKey\n"
        "[simple_job] Starting tests\n"
        "[simple_job] Starting scenario 1/2: basic-tests\n"
        "[simple_job] Performing dry run\n"
        "[simple_job] Starting scenario 2/2: other-tests\n"
        "[simple_job] Performing dry run\n"
        "[simple_job] Done\n"
    )


@pytest.mark.skip(
    reason="Non-ROS unsupported in CoPaVa at this time. Non-ROS like Sapien, etc, become unrunnable then."
)
def test_run_with_mode_other(cli_runner, project_with_key):
    result = cli_runner.invoke(
        run,
        ["simple_job", "--config", "tests/fixtures/warp-env-param.yaml", "--dryrun"],
    )
    assert result.exit_code == 0
    assert result.output == (
        "Connecting to https://app.artefacts.com/api using ApiKey\n"
        f"Starting tests for {project_with_key}\n"
        "Starting scenario 1/2: basic-tests\n"
        "performing dry run\n"
        "Starting scenario 2/2: other-tests\n"
        "performing dry run\n"
        "Done\n"
    )


def test_run_remote(cli_runner):
    result = cli_runner.invoke(run_remote, ["tests", "--config", "conf.yaml"])
    assert result.exit_code == 1
    assert result.output == "Error: Project config file conf.yaml not found.\n"


def test_run_remote_with_conf_invalid_jobname(cli_runner, project_with_key):
    result = cli_runner.invoke(
        run_remote, ["invalid_job_name", "--config", "tests/fixtures/warp.yaml"]
    )
    assert result.exit_code == 1
    assert result.output == (
        "Connecting to https://app.artefacts.com/api using ApiKey\n"
        "Error: Can't find a job named 'invalid_job_name' in config 'tests/fixtures/warp.yaml'\n"
    )


def test_APIConf(project_with_key):
    conf = APIConf(project_with_key, "test_version")
    assert conf.headers["Authorization"] == "ApiKey MYAPIKEY"


def test_upload_default_dir(cli_runner, project_with_key, mocker):
    # Note the patch applies to the object loaded in app, rather than the original in utils.
    # https://docs.python.org/3/library/unittest.mock.html#where-to-patch
    sut = mocker.patch("artefacts.cli.app.add_output_from_default")
    result = cli_runner.invoke(
        run, ["simple_job", "--config", "tests/fixtures/warp.yaml", "--dryrun"]
    )
    assert result.exit_code == 0
    # Called twice in this config.
    assert sut.call_count == 2

import pytest

import os

from click.testing import CliRunner


# Normalise locale to ensure tests match. Locale tests would need to set/reset accordingly
# Note: Needs to be done before package initialisation.
os.environ["LANG"] = "en_US.UTF-8"


from tests.utils import docker_mock

from artefacts.cli import WarpJob, WarpRun
from artefacts.cli.app import add_key_to_conf, delete
from artefacts.cli.config import APIConf
from artefacts.cli.utils import read_config


def dockerfile_presence(mocker, value: bool):
    original = os.path.exists

    def exists(path):
        if "dockerfile" in path.lower():
            return value
        else:
            return original(path)

    return mocker.patch("os.path.exists", side_effect=exists, autospec=True)


@pytest.fixture(scope="function")
def dockerfile_available(mocker):
    return dockerfile_presence(mocker, True)


@pytest.fixture(scope="function")
def dockerfile_not_available(mocker):
    return dockerfile_presence(mocker, False)


@pytest.fixture(scope="module")
def docker_mocker(module_mocker):
    test_client = docker_mock.make_fake_api_client()
    module_mocker.patch("docker.APIClient", return_value=test_client)
    yield test_client
    test_client.reset()


@pytest.fixture(scope="module")
def cli_runner():
    """
    Ensure default, normalised environment

    Note: Not using monkeypatch as it is a function fixture.
    """
    userenv = os.environ
    try:
        if os.environ.get("ARTEFACTS_API_URL"):
            del os.environ["ARTEFACTS_API_URL"]
        yield CliRunner()
    finally:
        os.environ = userenv


@pytest.fixture(scope="class")
def project_with_key(cli_runner):
    project_name = "_pytest-project_"
    add_key_to_conf(project_name, "MYAPIKEY")
    yield project_name
    cli_runner.invoke(delete, [project_name])


@pytest.fixture(scope="session")
def sample_artefacts_config():
    return read_config(os.path.join(os.path.dirname(__file__), "..", "artefacts.yaml"))


@pytest.fixture(scope="function")
def artefacts_job(project_with_key):
    return WarpJob(
        project_with_key,
        APIConf(project_with_key, "test_version"),
        "jobname",
        {},
        dryrun=True,
    )


@pytest.fixture(scope="function")
def artefacts_run(artefacts_job):
    return WarpRun(job=artefacts_job, name="test", params={}, run_n=0)

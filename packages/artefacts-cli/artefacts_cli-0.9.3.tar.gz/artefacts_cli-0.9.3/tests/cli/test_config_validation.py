from pathlib import Path
import tempfile

import pytest
import yaml

from artefacts.cli.app import (
    delete,
    run,
    add_key_to_conf,
)


class TempConfigMaker(object):
    """
    Facility to make config files from a base, valid config file.

    Notably to make *invalid* config files.

    Usage examples down this file.
    """

    def __init__(self, overrides: dict):
        """
        Valid overrides:
        - key -> value to add or replace
        - key -> None to delete
        """
        base_config = Path("tests") / Path("fixtures") / Path("warp.yaml")
        with base_config.open() as bc:
            self.config = yaml.load(bc, Loader=yaml.Loader)
        for key, value in overrides.items():
            if value:
                self.config[key] = value
            else:
                del self.config[key]

    def __enter__(self):
        self.fp = tempfile.NamedTemporaryFile(mode="w")
        self.fp.write(yaml.dump(self.config))
        self.fp.flush()
        return self.fp.name

    def __exit__(self, *args):
        self.fp.close()


class TestConfigValidation:
    @pytest.fixture(scope="class", autouse=True)
    def valid_project_name(self, cli_runner):
        project_name = "_pytest-project_"
        add_key_to_conf(project_name, "ANAPIKEY")
        yield project_name
        cli_runner.invoke(delete, [project_name])

    def test_accept_valid_configuration(self, cli_runner, valid_project_name):
        result = cli_runner.invoke(
            run,
            ["simple_job", "--config", "tests/fixtures/warp.yaml", "--dryrun"],
        )
        assert result.exit_code == 0

    def test_invalid_job_section(self, cli_runner, valid_project_name):
        with TempConfigMaker({"jobs": None}) as config_path:
            result = cli_runner.invoke(
                run,
                ["simple_job", "--config", config_path, "--dryrun"],
            )
            assert result.exit_code == 2
            assert "Missing jobs definition" in result.output

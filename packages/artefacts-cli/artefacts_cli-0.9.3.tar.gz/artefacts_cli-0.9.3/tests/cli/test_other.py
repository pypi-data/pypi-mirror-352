from artefacts.cli.other import generate_parameter_output, run_other_tests
from artefacts.cli.parameters import TMP_SCENARIO_PARAMS_YAML, TMP_SCENARIO_PARAMS_JSON
import yaml
import json
import os
from unittest.mock import patch, MagicMock


def test_generate_parameter_output(tmp_path):
    params = {"turtle/speed": 5}
    generate_parameter_output(params)
    file_path = TMP_SCENARIO_PARAMS_YAML
    with open(file_path) as f:
        out_params = yaml.load(f, Loader=yaml.Loader)
    os.remove(file_path)
    assert out_params == params

    generate_parameter_output(params)
    file_path = TMP_SCENARIO_PARAMS_JSON
    with open(file_path) as f:
        ros2_params = json.load(f)
    os.remove(file_path)
    assert ros2_params == params


@patch("artefacts.cli.other.run_and_save_logs")
def test_run_other_tests_sets_env_var(mock_run_save, artefacts_run: MagicMock):
    """
    Test that run_other_tests sets the ARTEFACTS_SCENARIO_PARAMS_FILE environment variable correctly,
    mocking filesystem operations.
    """
    # Setup mock run object and scenario
    artefacts_run.params = {
        "name": "test_scenario",
        "run": "echo 'hello'",
        "params": {"key": "value"},
    }

    # Call the function under test
    run_other_tests(artefacts_run)

    # Assert run_and_save_logs was called
    mock_run_save.assert_called_once()

    # Get the arguments passed to the mock run_and_save_logs
    args, kwargs = mock_run_save.call_args

    # Check the 'env' keyword argument
    passed_env = kwargs.get("env", {})
    assert "ARTEFACTS_SCENARIO_PARAMS_FILE" in passed_env
    assert passed_env["ARTEFACTS_SCENARIO_PARAMS_FILE"] == TMP_SCENARIO_PARAMS_YAML

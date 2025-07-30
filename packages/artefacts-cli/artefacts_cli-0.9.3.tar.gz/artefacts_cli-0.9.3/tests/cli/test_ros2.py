import os
import yaml
from unittest.mock import patch, MagicMock
import pytest

from artefacts.cli import WarpJob, WarpRun
from artefacts.cli.config import APIConf
from artefacts.cli.ros2 import (
    generate_scenario_parameter_output,
    run_ros2_tests,
    ros2_run_and_save_logs,
)
from artefacts.cli.ros2 import (
    LaunchTestFileNotFoundError,
    BadLaunchTestFileError,
)


def test_generate_parameter_output(tmp_path):
    params = {
        "turtle/speed": 5,
        "turtle/color.rgb.r": 255,
        "controller_server/FollowPath.critics": ["RotateToGoal", "Oscillation"],
    }
    file_path = tmp_path / "params.yaml"
    generate_scenario_parameter_output(params, file_path)
    with open(file_path) as f:
        ros2_params = yaml.load(f, Loader=yaml.Loader)
    assert ros2_params == {
        "turtle": {
            "ros__parameters": {
                "speed": 5,
                "color": {"rgb": {"r": 255}},
            }
        },
        "controller_server": {
            "ros__parameters": {
                "FollowPath": {"critics": ["RotateToGoal", "Oscillation"]}
            }
        },
    }


@patch("os.path.exists", return_value=False)
@patch("artefacts.cli.ros2.ros2_run_and_save_logs")
@pytest.mark.ros2
def test_passing_launch_arguments(mock_ros2_run_and_save_logs, _mock_exists):
    os.environ["ARTEFACTS_JOB_ID"] = "test_job_id"
    os.environ["ARTEFACTS_KEY"] = "test_key"
    job = WarpJob(
        "test_project_id",
        APIConf("sdfs", "test_version"),
        "test_jobname",
        {},
        dryrun=True,
    )
    scenario = {
        "name": "test scenario",
        "ros_testfile": "test.launch.py",
        "launch_arguments": {"arg1": "val1", "arg2": "val2"},
    }
    run = WarpRun(job, "scenario name", scenario, 0)

    run_ros2_tests(run)

    mock_ros2_run_and_save_logs.assert_called_once()
    assert (
        " test.launch.py arg1:=val1 arg2:=val2"
        in mock_ros2_run_and_save_logs.call_args[0][0]
    ), (
        "Launch arguments should be passed to the test command after the launch file path"
    )


@pytest.mark.ros2
def test_run_and_save_logs_missing_ros2_launchtest():
    filename = "missing_launchtest.test.py"
    command = [
        "launch_test",
        filename,
    ]
    with pytest.raises(LaunchTestFileNotFoundError):
        ros2_run_and_save_logs(
            " ".join(command),
            shell=True,
            executable="/bin/bash",
            env=os.environ,
            output_path="/tmp/test_log.txt",
        )


@pytest.mark.ros2
def test_run_and_save_logs_bad_ros2_launchtest():
    filename = "bad_launch_test.py"
    command = [
        "launch_test",
        f"tests/fixtures/{filename}",
    ]
    with pytest.raises(BadLaunchTestFileError):
        ros2_run_and_save_logs(
            " ".join(command),
            shell=True,
            executable="/bin/bash",
            env=os.environ,
            output_path="/tmp/test_log.txt",
        )


@patch("artefacts.cli.ros2.glob")
@patch("os.path.isdir", return_value=True)
@patch("artefacts.cli.bagparser.BagFileParser")
@patch("artefacts.cli.ros2.parse_tests_results", return_value=([], True))
@patch("artefacts.cli.ros2.run_and_save_logs", return_value=(0, "", ""))
@pytest.mark.ros2
def test_rosbag_discovered_and_metric_logged(
    mock_run_logs, mock_parse, mock_bag_parser, mock_isdir, mock_glob
):
    # Setup test environment
    os.environ["ARTEFACTS_JOB_ID"] = "test_job_id"
    os.environ["ARTEFACTS_KEY"] = "test_key"

    job = WarpJob(
        "test_project_id",
        APIConf("test_url", "test_version"),
        "test_jobname",
        {},
        dryrun=True,
    )
    scenario = {
        "name": "test scenario",
        "ros_testfile": "test_launch.py",
        "metrics": ["topic1"],
    }
    run = WarpRun(job, "scenario name", scenario, 0)

    # Patch the methods to verify
    run.log_artifacts = MagicMock()
    run.log_metric = MagicMock()

    # mock returns
    preexisting_rosbags = [
        "src/my_test_folder/rosbag2_existing",
        "src/venv/some_rosbag_package/rosbag2_existing",
    ]
    all_rosbags = [
        "src/my_test_folder/rosbag2_existing",
        "src/venv/some_rosbag_package/rosbag2_existing",
        "src/my_test_folder/rosbag2_new",
    ]
    bag_files = ["src/my_test_folder/rosbag2_new/test.mcap"]
    mock_glob.side_effect = [preexisting_rosbags, all_rosbags, bag_files]

    # BagFileParser mock
    mock_bag = MagicMock()
    mock_bag.get_last_message.return_value = (None, MagicMock(data=42.0))
    mock_bag_parser.return_value = mock_bag

    run_ros2_tests(run)

    # Assert the right new rosbag directory was found
    run.log_artifacts.assert_any_call("src/my_test_folder/rosbag2_new", "rosbag")

    # Assert the right metric was logged
    run.log_metric.assert_called_with("topic1", 42.0)

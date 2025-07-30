from artefacts.cli.ros1 import (
    generate_scenario_parameter_output,
    generate_runtime_parameter_output,
    generate_rosbag_args,
)
import yaml
import pytest


def test_generate_parameter_output(tmp_path):
    params = {"turtle/speed": 5}
    file_path = tmp_path / "params.yaml"
    generate_scenario_parameter_output(params, file_path)
    with open(file_path) as f:
        scenario_params = yaml.load(f, Loader=yaml.Loader)
    assert scenario_params == params


def test_generate_runtime_parameter_output(tmp_path):
    params = {"seed": 42}
    file_path = tmp_path / "runtime_params.yaml"
    generate_runtime_parameter_output(params, file_path)
    with open(file_path) as f:
        runtime_params = yaml.load(f, Loader=yaml.Loader)
    assert runtime_params == params


@pytest.mark.parametrize(
    "scenario, expected",
    [
        ({"rosbag_record": "none"}, "none"),
        ({}, "none"),
        ({"rosbag_record": "all"}, "--all"),
        (
            {
                "rosbag_record": "subscriptions",
                "subscriptions": {"pose": "turtle1/pose", "result": "turtle1/odometry"},
            },
            "turtle1/pose turtle1/odometry",
        ),
        (
            {"rosbag_record": ["/turtle(.*)/pose", "/turtle(.*)/odometry"]},
            "--regex /turtle(.*)/pose /turtle(.*)/odometry",
        ),
    ],
)
def test_generate_rosbag_args(scenario, expected):
    assert generate_rosbag_args(scenario) == expected

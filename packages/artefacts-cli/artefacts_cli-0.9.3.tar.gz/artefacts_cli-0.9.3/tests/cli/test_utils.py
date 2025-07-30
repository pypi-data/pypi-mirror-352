import pytest

from artefacts.cli.utils import add_output_from_default, run_and_save_logs


def test_adds_nothing_on_missing_default_output(
    artefacts_run, mocker, project_with_key
):
    path = mocker.patch("artefacts.cli.utils.ARTEFACTS_DEFAULT_OUTPUT_DIR")
    mocked = {
        "exists.return_value": False,
        "is_dir.return_value": True,
    }
    path.configure_mock(**mocked)
    add_output_from_default(artefacts_run)
    assert len(artefacts_run.uploads) == 0


@pytest.mark.ros2
def test_run_and_save_logs_missing_launch_test_command():
    filename = "launchtest.test.py"
    command = [
        "launch_test",
        filename,
    ]
    # launch_test won't be in the path, and an error will be raised
    with pytest.raises(FileNotFoundError):
        run_and_save_logs(" ".join(command), output_path="/tmp/test_log.txt")

from datetime import datetime, timezone

import yaml

from artefacts.cli import generate_scenarios, WarpJob


def test_generate_scenarios():
    with open("tests/fixtures/warp.yaml") as f:
        conf = yaml.load(f, Loader=yaml.Loader)
    jobs = conf["jobs"]
    scenarios, first = generate_scenarios(jobs["simple_job"])
    assert len(scenarios) == 2
    scenarios, first = generate_scenarios(jobs["tests"])
    assert first == 0
    assert len(scenarios) == 5
    jobs["simple_job"]["scenarios"]["defaults"] = {"params": {}}
    scenarios, first = generate_scenarios(jobs["simple_job"])
    assert len(scenarios) == 2
    scenarios, first = generate_scenarios(jobs["simple_job"], 0)
    assert len(scenarios) == 1
    scenarios, first = generate_scenarios(jobs["simple_job"], 1)
    assert len(scenarios) == 1
    scenarios, first = generate_scenarios(jobs["tests"], 1)
    assert len(scenarios) == 3
    scenarios, first = generate_scenarios(jobs["tests"], 0)
    assert len(scenarios) == 2
    # assert 1 == 2


def test_default_params_only():
    with open("tests/fixtures/warp.yaml") as f:
        conf = yaml.load(f, Loader=yaml.Loader)
    jobs = conf["jobs"]
    # testing with just default params
    scenarios, first = generate_scenarios(jobs["default_params_only"])
    assert len(scenarios) == 2
    assert [s["params"] for s in scenarios] == [
        {"seed": 42},
        {"seed": 43},
    ]


def test_settings_params_only():
    with open("tests/fixtures/warp.yaml") as f:
        conf = yaml.load(f, Loader=yaml.Loader)
    jobs = conf["jobs"]
    # testing with just default params
    scenarios, first = generate_scenarios(jobs["settings_params_only"])
    assert len(scenarios) == 2
    assert [s["params"] for s in scenarios] == [
        {"seed": 42},
        {"seed": 43},
    ]


def test_settings_and_default_params():
    with open("tests/fixtures/warp.yaml") as f:
        conf = yaml.load(f, Loader=yaml.Loader)
    jobs = conf["jobs"]
    # testing with both settings and default params
    scenarios, first = generate_scenarios(jobs["settings_and_default_params"])
    assert len(scenarios) == 4
    assert [s["params"] for s in scenarios] == [
        {"gravity": 1.62, "seed": 42},
        {"gravity": 1.62, "seed": 43},
        {"gravity": 0, "seed": 42},
        {"gravity": 0, "seed": 43},
    ]


def test_settings_overwrite_default_params():
    with open("tests/fixtures/warp.yaml") as f:
        conf = yaml.load(f, Loader=yaml.Loader)
    jobs = conf["jobs"]
    # testing with settings that overwrite default params
    scenarios, first = generate_scenarios(jobs["settings_overwrite_default_params"])
    assert len(scenarios) == 2
    assert [s["params"] for s in scenarios] == [
        {"gravity": 1.62, "seed": 42},
        {"gravity": 0, "seed": 42},
    ]


def test_settings_overwrite_full():
    with open("tests/fixtures/warp.yaml") as f:
        conf = yaml.load(f, Loader=yaml.Loader)
    jobs = conf["jobs"]
    # testing with settings that overwrite default params (two scenarios)
    scenarios, first = generate_scenarios(jobs["settings_overwrite_full"])
    assert len(scenarios) == 5
    assert [s["params"] for s in scenarios] == [
        {"gravity": 9.807, "seed": 42},
        {"gravity": 1.62, "seed": 42},
        {"gravity": 0, "seed": 42},
        {"gravity": 1.62, "seed": 42},
        {"gravity": 0, "seed": 42},
    ]


def test_handles_launch_arguments():
    with open("tests/fixtures/warp.yaml") as f:
        conf = yaml.load(f, Loader=yaml.Loader)
    jobs = conf["jobs"]
    scenarios, _ = generate_scenarios(jobs["handles_launch_arguments"])
    assert len(scenarios) == 1
    assert scenarios[0]["launch_arguments"] == {
        "gravity": "9.807",
        "seed": "42",
        "target": "goal",
    }


def test_WarpJob():
    job = WarpJob("project", {}, "jobname", {}, dryrun=True)
    assert job.success is False
    assert job.start < datetime.now(timezone.utc).timestamp()

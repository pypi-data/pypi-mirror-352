import configparser
import os
import subprocess

from artefacts.cli.constants import CONFIG_PATH, CONFIG_DIR


def get_git_revision_hash() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"])
            .decode("ascii")
            .strip()
        )
    except subprocess.CalledProcessError:
        return ""


def get_git_revision_branch() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
            .decode("ascii")
            .strip()
        )
    except subprocess.CalledProcessError:
        return ""


def get_conf_from_file():
    config = configparser.ConfigParser()
    if not os.path.isfile(CONFIG_PATH):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        config["DEFAULT"] = {}
        with open(CONFIG_PATH, "w") as f:
            config.write(f)
    config.read(CONFIG_PATH)
    return config


def get_artefacts_api_url(project_profile):
    return os.environ.get(
        "ARTEFACTS_API_URL",
        project_profile.get(
            "ApiUrl",
            "https://app.artefacts.com/api",
        ),
    )


def add_key_to_conf(project_name, api_key):
    config = get_conf_from_file()
    config[project_name] = {"ApiKey": api_key}
    with open(CONFIG_PATH, "w") as f:
        config.write(f)

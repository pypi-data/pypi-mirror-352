import os
import platform
from typing import Optional

import click

from artefacts.cli.i18n import localise
from artefacts.cli.helpers import (
    get_conf_from_file,
    get_artefacts_api_url,
)


class APIConf:
    def __init__(
        self, project_name: str, api_version: str, job_name: Optional[str] = None
    ) -> None:
        config = get_conf_from_file()
        if project_name in config:
            profile = config[project_name]
        else:
            profile = {}
        self.api_url = get_artefacts_api_url(profile)
        self.api_key = os.environ.get("ARTEFACTS_KEY", profile.get("ApiKey", None))
        if self.api_key is None:
            batch_id = os.environ.get("AWS_BATCH_JOB_ID", None)
            job_id = os.environ.get("ARTEFACTS_JOB_ID", None)
            if batch_id is None or job_id is None:
                raise click.ClickException(
                    localise(
                        "No API KEY set. Please run `artefacts config add {project_name}`".format(
                            project_name=project_name
                        )
                    )
                )
            auth_type = "Internal"
            # Batch id for array jobs contains array index
            batch_id = batch_id.split(":")[0]
            self.headers = {"Authorization": f"{auth_type} {job_id}:{batch_id}"}
        else:
            auth_type = "ApiKey"
            self.headers = {"Authorization": f"{auth_type} {self.api_key}"}
        self.headers["User-Agent"] = (
            f"ArtefactsClient/{api_version} ({platform.platform()}/{platform.python_version()})"
        )
        if job_name:
            click.echo(
                f"[{job_name}] "
                + localise(
                    "Connecting to {api_url} using {auth_type}".format(
                        api_url=self.api_url, auth_type=auth_type
                    )
                )
            )
        else:
            click.echo(
                localise(
                    "Connecting to {api_url} using {auth_type}".format(
                        api_url=self.api_url, auth_type=auth_type
                    )
                )
            )

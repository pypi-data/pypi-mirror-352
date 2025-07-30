import os
from pathlib import Path
import subprocess
import sys
from typing import Union

import click

import artefacts_copava as copava
from artefacts import ARTEFACTS_DEFAULT_OUTPUT_DIR
from artefacts.cli import WarpRun, localise


def run_and_save_logs(
    args,
    output_path,
    shell=False,
    executable=None,
    env=None,
    cwd=None,
    with_output=False,
):
    """
    Run a command and save stdout and stderr to a file in output_path

    Note: explicitly list used named params instead of using **kwargs to avoid typing issue: https://github.com/microsoft/pyright/issues/455#issuecomment-780076232
    """
    output_file = open(output_path, "wb")

    proc = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,  # Capture stdout
        stderr=subprocess.PIPE,  # Capture stderr
        shell=shell,
        executable=executable,
        env=env,
        cwd=cwd,
    )
    # write test-process stdout and stderr into file and stdout
    stderr_content = ""
    stdout_content = ""
    if proc.stdout:
        for line in proc.stdout:
            decoded_line = line.decode()
            sys.stdout.write(decoded_line)
            output_file.write(line)
            stdout_content += decoded_line
    if proc.stderr:
        output_file.write("[STDERR]\n".encode())
        for line in proc.stderr:
            decoded_line = line.decode()
            sys.stderr.write(decoded_line)
            output_file.write(line)
            stderr_content += decoded_line
    proc.wait()
    if with_output:
        return proc.returncode, stdout_content, stderr_content
    return proc.returncode


def ensure_available(package: str) -> None:
    import importlib

    try:
        importlib.import_module(package)
    except ImportError:
        """
        Recommended by the Python community
        https://pip.pypa.io/en/latest/user_guide/#using-pip-from-your-program
        """
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def read_config(filename: str) -> dict:
    try:
        with open(filename) as f:
            return copava.parse(f.read()) or {}
    except FileNotFoundError:
        raise click.ClickException(
            localise(
                "Project config file {file_name} not found.".format(file_name=filename)
            )
        )


# Click callback syntax
def config_validation(context: click.Context, param: str, value: str) -> str:
    if context.params.get("skip_validation", False):
        return value
    config = read_config(value)
    errors = copava.check(config)
    if len(errors) == 0:
        return value
    else:
        raise click.BadParameter(pretty_print_config_error(errors))


def pretty_print_config_error(
    errors: Union[str, list, dict], indent: int = 0, prefix: str = "", suffix: str = ""
) -> str:
    if type(errors) is str:
        header = "  " * indent
        output = header + prefix + errors + suffix
    elif type(errors) is list:
        _depth = indent + 1
        output = []
        for value in errors:
            output.append(pretty_print_config_error(value, indent=_depth, prefix="- "))
        output = os.linesep.join(output)
    elif type(errors) is dict:
        _depth = indent + 1
        output = []
        for key, value in errors.items():
            output.append(pretty_print_config_error(key, indent=indent, suffix=":"))
            output.append(pretty_print_config_error(value, indent=_depth))
        output = os.linesep.join(output)
    else:
        # Must not happen, so broad definition, but we want to know fast.
        raise Exception(f"Unacceptable data type for config error formatting: {errors}")
    return output


def add_output_from_default(run: WarpRun) -> None:
    """
    Add every file found under ARTEFACTS_DEFAULT_OUTPUT_DIR to the set of files
    uploaded to Artefacts for the run argument.

    The default folder is created either directly, or more generally by Artefacts
    toolkit libraries.
    """
    if ARTEFACTS_DEFAULT_OUTPUT_DIR.exists() and ARTEFACTS_DEFAULT_OUTPUT_DIR.is_dir():
        for root, dirs, files in os.walk(ARTEFACTS_DEFAULT_OUTPUT_DIR):
            for file in files:
                run.log_artifacts(Path(root) / Path(file))

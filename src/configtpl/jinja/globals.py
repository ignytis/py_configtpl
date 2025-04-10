import os
import subprocess


def jinja_global_cmd(cmd: str) -> str:
    """
    Runs a system command provided as argument and returns the output
    """
    result = subprocess.run(
        cmd,
        shell=True,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return result.stdout


def jinja_global_env(name: str, default: str | None = None) -> str | None:
    """
    Returns value of an environment variable
    """
    return os.getenv(name, default)

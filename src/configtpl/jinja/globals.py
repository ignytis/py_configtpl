import os


def jinja_global_env(name: str, default: str | None = None) -> str | None:
    """
    Returns value of an environment variable
    """
    return os.getenv(name, default)

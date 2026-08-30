"""Default locations for the data this application reads and writes.

The samples directory and the attendance log are per-deployment state: the
operator swaps the roster, and the log grows at runtime. Neither belongs inside
the installed package, so nothing here uses ``importlib.resources`` -- which is
read-oriented anyway, and can hand back a temporary copy that a write would
silently lose.

Resolution order, highest priority first:

1. an explicit argument passed by the caller (handled by the caller, not here)
2. the ``DOORBELL_DATA_DIR`` environment variable
3. ``<nearest ancestor containing pyproject.toml>/data``
4. ``./data``
"""

import os
from pathlib import Path

from . import config


def project_root(start: Path | None = None) -> Path:
    """Returns the nearest ancestor of *start* holding a pyproject.toml.

    Falls back to the current working directory when there is none, which is the
    normal case for a non-editable install.
    """
    origin = Path(start) if start is not None else Path(__file__).resolve()
    for candidate in (origin, *origin.parents):
        if (candidate / "pyproject.toml").is_file():
            return candidate
    return Path.cwd()


def data_dir() -> Path:
    """Returns the directory holding samples and the attendance log."""
    override = os.environ.get(config.ENV_DATA_DIR)
    if override:
        return Path(override).expanduser()
    return project_root() / config.DATA_DIR_NAME


def default_samples_dir() -> Path:
    """Returns the directory of whitelist images."""
    return data_dir() / config.SAMPLES_DIR_NAME


def default_attendance_file() -> Path:
    """Returns the path of the attendance log."""
    return data_dir() / config.ATTENDANCE_DIR_NAME / config.ATTENDANCE_FILE_NAME

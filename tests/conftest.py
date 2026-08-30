"""Shared fixtures.

Nothing here constructs a ``cv2.VideoCapture`` or calls ``imshow``: the whole
suite runs without a camera, and the parts needing OpenCV or dlib skip
themselves when those are not installed.
"""

import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
REPO_DATA = REPO_ROOT / "data"
FIXTURES = Path(__file__).resolve().parent / "data"


@pytest.fixture
def repo_data() -> Path:
    """The repository's own data directory, used for real sample images."""
    if not REPO_DATA.is_dir():
        pytest.skip("repository data directory is missing")
    return REPO_DATA


@pytest.fixture
def legacy_log(tmp_path: Path) -> Path:
    """A copy of an attendance log written by an earlier version.

    CRLF line endings and no trailing newline, which is exactly the shape the
    appender has to cope with.
    """
    destination = tmp_path / "attendance.csv"
    shutil.copyfile(FIXTURES / "attendance_legacy.csv", destination)
    return destination


@pytest.fixture
def samples_dir(tmp_path: Path, repo_data: Path) -> Path:
    """A samples directory holding one real face plus files that must be ignored."""
    directory = tmp_path / "samples"
    directory.mkdir()
    shutil.copyfile(repo_data / "demo" / "elon_musk1.jpg", directory / "elon_musk.jpg")
    (directory / "README.md").write_text("Put one photo per person here.")
    (directory / "subdir").mkdir()
    return directory

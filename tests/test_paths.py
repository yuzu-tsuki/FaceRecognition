"""Path resolution precedence.

The bug being guarded against is the original one: paths that only resolved when
the process happened to be started from inside DoorBell/.
"""

from pathlib import Path

import pytest

from face_recognition_doorbell import config, paths


@pytest.fixture(autouse=True)
def _clear_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keeps a developer's own DOORBELL_DATA_DIR out of these assertions."""
    monkeypatch.delenv(config.ENV_DATA_DIR, raising=False)


def test_project_root_finds_the_directory_holding_pyproject(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\n")
    nested = tmp_path / "src" / "pkg"
    nested.mkdir(parents=True)

    assert paths.project_root(nested) == tmp_path


def test_project_root_falls_back_to_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A non-editable install has no pyproject.toml above the package."""
    orphan = tmp_path / "no_project_here"
    orphan.mkdir()
    monkeypatch.chdir(orphan)

    assert paths.project_root(orphan) == Path.cwd()


def test_environment_override_wins(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(config.ENV_DATA_DIR, str(tmp_path))

    assert paths.data_dir() == tmp_path
    assert paths.default_samples_dir() == tmp_path / config.SAMPLES_DIR_NAME


def test_data_dir_defaults_under_the_project_root() -> None:
    assert paths.data_dir() == paths.project_root() / config.DATA_DIR_NAME


def test_defaults_are_absolute_and_independent_of_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The headline regression: the same call from two directories agrees."""
    before = paths.default_samples_dir()
    monkeypatch.chdir(tmp_path)

    assert paths.default_samples_dir() == before
    assert before.is_absolute()


def test_attendance_file_sits_under_the_data_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(config.ENV_DATA_DIR, str(tmp_path))

    assert paths.default_attendance_file() == (
        tmp_path / config.ATTENDANCE_DIR_NAME / config.ATTENDANCE_FILE_NAME
    )

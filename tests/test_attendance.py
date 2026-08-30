"""Attendance log behaviour. Standard library only, so this runs anywhere."""

from datetime import datetime, timedelta
from pathlib import Path

from face_recognition_doorbell import config
from face_recognition_doorbell.attendance import AttendanceLog

T0 = datetime(2026, 8, 30, 12, 0, 0)


def rows(path: Path) -> list[str]:
    """Returns the non-empty lines of the log, header included."""
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_missing_log_is_created_with_a_header(tmp_path: Path) -> None:
    log = AttendanceLog(tmp_path / "nested" / "attendance.csv")

    assert log.mark("elon_musk", now=T0) is True
    assert log.path.exists()
    assert rows(log.path)[0] == config.ATTENDANCE_HEADER
    assert len(rows(log.path)) == 2


def test_repeat_inside_the_window_is_suppressed(tmp_path: Path) -> None:
    log = AttendanceLog(tmp_path / "attendance.csv")
    log.mark("elon_musk", now=T0)

    assert log.mark("elon_musk", now=T0) is False
    assert len(rows(log.path)) == 2


def test_suppression_boundary_is_inclusive(tmp_path: Path) -> None:
    """One second short of the window suppresses; exactly the window does not."""
    log = AttendanceLog(tmp_path / "attendance.csv")
    window = config.ATTENDANCE_DEDUPE_SECONDS
    log.mark("elon_musk", now=T0)

    assert log.mark("elon_musk", now=T0 + timedelta(seconds=window - 1)) is False
    assert log.mark("elon_musk", now=T0 + timedelta(seconds=window)) is True


def test_names_match_case_insensitively(tmp_path: Path) -> None:
    log = AttendanceLog(tmp_path / "attendance.csv")
    log.mark("elon_musk", now=T0)

    assert log.mark("ELON_MUSK", now=T0) is False


def test_each_person_gets_their_own_window(tmp_path: Path) -> None:
    log = AttendanceLog(tmp_path / "attendance.csv")
    log.mark("elon_musk", now=T0)

    assert log.mark("donald_trump", now=T0) is True
    assert len(log.entries()) == 2


def test_header_is_not_treated_as_an_entry(tmp_path: Path) -> None:
    log = AttendanceLog(tmp_path / "attendance.csv")
    log.mark("elon_musk", now=T0)

    assert [name for name, _ in log.entries()] == ["elon_musk"]


def test_unparseable_rows_are_skipped(tmp_path: Path) -> None:
    path = tmp_path / "attendance.csv"
    path.write_text(
        f"{config.ATTENDANCE_HEADER}\nno_comma_here\nelon_musk,not a date\n"
        "elon_musk,30/08/2026 12:00:00\n",
        encoding="utf-8",
    )

    assert AttendanceLog(path).entries() == [("elon_musk", T0)]


def test_dedupe_window_is_configurable(tmp_path: Path) -> None:
    log = AttendanceLog(tmp_path / "attendance.csv", dedupe_seconds=300)
    log.mark("elon_musk", now=T0)

    assert log.mark("elon_musk", now=T0 + timedelta(seconds=299)) is False
    assert log.mark("elon_musk", now=T0 + timedelta(seconds=300)) is True


def test_appends_to_a_legacy_log_without_a_trailing_newline(legacy_log: Path) -> None:
    """Regression guard for logs written with a leading-newline appender.

    The fixture ends mid-line, so appending naively would glue the new row onto
    the last existing one.
    """
    assert not legacy_log.read_bytes().endswith(b"\n")
    before = rows(legacy_log)

    assert AttendanceLog(legacy_log).mark("dc_test", now=T0) is True

    after = rows(legacy_log)
    assert len(after) == len(before) + 1
    assert after[-2] == before[-1]
    assert after[-2].endswith("22:45:31")
    assert after[-1] == "dc_test,30/08/2026 12:00:00"


def test_existing_legacy_entries_are_parsed(legacy_log: Path) -> None:
    entries = AttendanceLog(legacy_log).entries()

    assert len(entries) == 3
    assert {name for name, _ in entries} == {"dc_test"}
    assert entries[-1][1] == datetime(2025, 7, 27, 22, 45, 31)

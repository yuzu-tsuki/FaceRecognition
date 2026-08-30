"""Append-only attendance log.

Deliberately depends on nothing heavier than the standard library. Attendance is
the part of this project most likely to be subtly wrong -- suppression windows,
timestamp parsing, trailing newlines -- and it is the only part that can be
tested on a machine where dlib will not build.

Rows are written as plain text rather than through :mod:`csv`, because a name is
always an image filename stem and so cannot contain a comma. Switch to the csv
module if that ever stops being true.
"""

from datetime import datetime
from pathlib import Path

from . import config, paths


class AttendanceLog:
    """A ``name,timestamp`` log with a per-name suppression window."""

    def __init__(
        self,
        csv_path: Path | str | None = None,
        *,
        dedupe_seconds: int = config.ATTENDANCE_DEDUPE_SECONDS,
    ) -> None:
        self.path = (
            Path(csv_path) if csv_path is not None else paths.default_attendance_file()
        )
        self.dedupe_seconds = dedupe_seconds

    def mark(self, name: str, *, now: datetime | None = None) -> bool:
        """Records *name* as present. Returns True iff a row was appended.

        A row is suppressed when the most recent entry for *name* (matched
        case-insensitively) is newer than ``dedupe_seconds``. Pass *now* to make
        the suppression window testable without waiting for real time to pass.
        """
        moment = now if now is not None else datetime.now()
        self._ensure_file()

        last_seen = self._last_seen(name)
        if last_seen is not None:
            if (moment - last_seen).total_seconds() < self.dedupe_seconds:
                return False

        self._append(name, moment)
        return True

    def entries(self) -> list[tuple[str, datetime]]:
        """Returns the parsed log rows, oldest first, excluding the header.

        Rows that do not parse are skipped rather than raising, so one corrupt
        line cannot take the door bell down mid-run.
        """
        if not self.path.exists():
            return []

        parsed: list[tuple[str, datetime]] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            row = line.strip()
            if not row or row == config.ATTENDANCE_HEADER:
                continue
            fields = row.split(",")
            if len(fields) < 2:
                continue
            try:
                moment = datetime.strptime(fields[1].strip(), config.TIMESTAMP_FORMAT)
            except ValueError:
                continue
            parsed.append((fields[0].strip(), moment))
        return parsed

    def _last_seen(self, name: str) -> datetime | None:
        """Returns the timestamp of the most recent entry for *name*, if any."""
        # Scanning backwards and stopping at the first hit preserves the original
        # behaviour: only the latest entry for a name decides suppression.
        for entry_name, moment in reversed(self.entries()):
            if entry_name.lower() == name.lower():
                return moment
        return None

    def _ensure_file(self) -> None:
        """Creates the log and its parent directory with a header if missing.

        The original code opened the log 'r+' and raised FileNotFoundError when
        it did not exist, which made a fresh checkout fail on the first
        recognised face.
        """
        if self.path.exists():
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(config.ATTENDANCE_HEADER + "\n", encoding="utf-8")

    def _append(self, name: str, moment: datetime) -> None:
        """Appends one row, adding a separator if the file lacks a final newline."""
        # Logs written by earlier versions end without a trailing newline, because
        # rows were written with a leading '\n'. Appending blindly would glue the
        # new row onto the last one.
        needs_separator = (
            self.path.exists()
            and self.path.stat().st_size > 0
            and not self.path.read_bytes().endswith(b"\n")
        )
        prefix = "\n" if needs_separator else ""
        row = f"{prefix}{name},{moment.strftime(config.TIMESTAMP_FORMAT)}\n"
        with open(self.path, "a", encoding="utf-8", newline="") as handle:
            handle.write(row)

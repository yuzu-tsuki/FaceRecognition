"""The webcam door bell: camera loop, on-screen drawing, and nothing else.

Recognition lives in :mod:`recognizer` and the log in :mod:`attendance`, so this
module is the only one that needs a camera or a window.
"""

import logging
from pathlib import Path

import cv2
import numpy as np

from . import config, paths
from .attendance import AttendanceLog
from .recognizer import FaceMatch, FaceRecognizer
from .whitelist import WhiteList

_LOG = logging.getLogger(__name__)


class DoorBell:
    """Recognises whitelisted faces from a webcam and logs attendance."""

    def __init__(
        self,
        samples_path: Path | str | None = None,
        attendance_path: Path | str | None = None,
        *,
        camera_index: int = config.DEFAULT_CAMERA_INDEX,
    ) -> None:
        """Builds the whitelist and prepares the attendance log.

        Both paths default to the locations resolved by :mod:`paths`, so the
        door bell runs from any working directory.
        """
        self.samples_path = (
            Path(samples_path) if samples_path is not None else paths.default_samples_dir()
        )
        self.attendance_path = (
            Path(attendance_path)
            if attendance_path is not None
            else paths.default_attendance_file()
        )
        self.camera_index = camera_index

        self._attendance = AttendanceLog(self.attendance_path)
        self.w_list = WhiteList(self.samples_path)
        self._recognizer = FaceRecognizer.from_white_list(self.w_list)

    def view_white_list(self) -> list[tuple]:
        """Returns the whitelisted people as ``(image, name)`` pairs."""
        return self.w_list.get_white_lists()

    def add_sample(self) -> list[str]:
        """Encodes sample images that are not on the whitelist yet.

        Returns the names newly added. Idempotent: re-running adds nothing, where
        the previous version re-read the whole directory and duplicated every
        entry on each call.
        """
        known = set(self.w_list.get_white_list_names())
        added: list[str] = []

        for entry in sorted(self.samples_path.iterdir()):
            if not entry.is_file() or entry.suffix.lower() not in config.IMAGE_SUFFIXES:
                continue
            if entry.name in known:
                continue
            img = cv2.imread(str(entry))
            if img is None:
                _LOG.warning("Could not read %s, skipping.", entry)
                continue
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            if self.w_list.add_white_list(img, entry.name):
                added.append(entry.stem)
                _LOG.info("Added %s to white list.", entry.stem)
            else:
                _LOG.warning("No face found in %s, not added.", entry)

        if added:
            self._recognizer = FaceRecognizer.from_white_list(self.w_list)
        return added

    def mark_attendance(self, name: str) -> bool:
        """Records *name* in the attendance log.

        Returns True iff a row was appended; a repeat sighting inside the
        suppression window is ignored.
        """
        return self._attendance.mark(name)

    def annotate(self, frame: np.ndarray) -> list[FaceMatch]:
        """Draws boxes and labels onto *frame* in place, logging known faces.

        This is the seam that keeps the loop testable: it does everything a
        single frame needs without touching a camera or a window.
        """
        matches = self._recognizer.recognize(frame)

        for match in matches:
            if match.is_known:
                color, label = config.KNOWN_BOX_COLOR, match.name
            else:
                color, label = config.UNKNOWN_BOX_COLOR, config.UNKNOWN_LABEL

            cv2.rectangle(
                frame,
                (match.left, match.top),
                (match.right, match.bottom),
                color,
                config.BOX_THICKNESS,
            )
            cv2.putText(
                frame,
                label,
                (match.left + config.LABEL_OFFSET_X, match.top + config.LABEL_OFFSET_Y),
                cv2.FONT_HERSHEY_PLAIN,
                config.LABEL_FONT_SCALE,
                config.LABEL_COLOR,
                config.BOX_THICKNESS,
            )

            if match.is_known:
                _LOG.info(
                    "Recognized %s, attendance marked: %s",
                    match.name,
                    self.mark_attendance(match.name),
                )

        return matches

    def run_door_bell(self) -> None:
        """Opens the camera and loops until 'q' is pressed or the window closes."""
        cam = cv2.VideoCapture(self.camera_index)

        if not cam.isOpened():
            _LOG.error("Could not open camera %s.", self.camera_index)
            return

        try:
            while True:
                succ, frame = cam.read()
                if not succ:
                    _LOG.error("Could not read frame.")
                    break

                self.annotate(frame)
                cv2.imshow(config.WINDOW_TITLE, frame)

                # waitKey has to run first: it pumps the window's event loop, and
                # getWindowProperty is only meaningful once it has.
                quit_pressed = (
                    cv2.waitKey(config.WAIT_KEY_DELAY_MS) & 0xFF == ord(config.QUIT_KEY)
                )
                window_closed = (
                    cv2.getWindowProperty(config.WINDOW_TITLE, cv2.WND_PROP_VISIBLE) < 1
                )
                if quit_pressed or window_closed:
                    break
        finally:
            cam.release()
            cv2.destroyAllWindows()

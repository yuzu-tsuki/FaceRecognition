"""Face matching, with no camera and no window involved.

Splitting this out of the webcam loop is what makes recognition testable: a test
can hand :meth:`FaceRecognizer.recognize` a still image and assert on the result,
where the loop it came from could only be exercised with real hardware.
"""

from dataclasses import dataclass

import cv2
import face_recognition
import numpy as np

from . import config
from .whitelist import WhiteList


@dataclass(frozen=True)
class FaceMatch:
    """One detected face, in full-resolution frame coordinates."""

    name: str | None  # None means the face matched nobody on the whitelist
    top: int
    right: int
    bottom: int
    left: int
    distance: float

    @property
    def is_known(self) -> bool:
        """True when the face matched somebody on the whitelist."""
        return self.name is not None


class FaceRecognizer:
    """Matches faces in a BGR frame against a set of known encodings."""

    def __init__(
        self,
        encodings: list,
        names: list[str],
        *,
        scale: float = config.FRAME_SCALE,
    ) -> None:
        """Stores the known encodings and the downscale factor to detect at.

        *scale* is a parameter rather than a fixed read of the configured value
        because tests feed still images small enough that downscaling would lose
        the face entirely; they pass ``scale=1.0``.
        """
        if len(encodings) != len(names):
            raise ValueError(
                f"encodings and names must be the same length, "
                f"got {len(encodings)} and {len(names)}"
            )
        self.encodings = encodings
        self.names = names
        self.scale = scale

    @classmethod
    def from_white_list(cls, white_list: WhiteList, **kwargs) -> "FaceRecognizer":
        """Builds a recognizer from an already-encoded :class:`WhiteList`."""
        return cls(
            white_list.get_encoded_faces(),
            [person[1] for person in white_list.get_white_lists()],
            **kwargs,
        )

    def recognize(self, frame_bgr: np.ndarray) -> list[FaceMatch]:
        """Detects and identifies every face in *frame_bgr*.

        Coordinates in the returned matches are scaled back to the full frame,
        so callers never have to know that detection ran on a smaller image.
        """
        if self.scale == 1.0:
            frame_small = frame_bgr
            upscale = 1
        else:
            frame_small = cv2.resize(frame_bgr, (0, 0), None, self.scale, self.scale)
            upscale = round(1 / self.scale)
        frame_small = cv2.cvtColor(frame_small, cv2.COLOR_BGR2RGB)

        locations = face_recognition.face_locations(frame_small)
        encodings = face_recognition.face_encodings(frame_small, locations)

        matches: list[FaceMatch] = []
        for encoding, location in zip(encodings, locations):
            name, distance = self._identify(encoding)
            top, right, bottom, left = (c * upscale for c in location)
            matches.append(
                FaceMatch(
                    name=name,
                    top=top,
                    right=right,
                    bottom=bottom,
                    left=left,
                    distance=distance,
                )
            )
        return matches

    def _identify(self, encoding) -> tuple[str | None, float]:
        """Returns the closest whitelisted name for *encoding*, and its distance."""
        # An empty whitelist would make np.argmin raise on an empty array; treat
        # every face as unknown instead.
        if not self.encodings:
            return None, float("inf")

        is_match = face_recognition.compare_faces(self.encodings, encoding)
        distances = face_recognition.face_distance(self.encodings, encoding)
        closest = int(np.argmin(distances))

        name = self.names[closest] if is_match[closest] else None
        return name, float(distances[closest])

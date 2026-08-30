"""Face matching against still images, with no camera involved.

These exercise the seam that the restructure created: recognition used to live
inside the webcam loop and could only be tested by standing in front of a camera.
"""

from pathlib import Path

import pytest

pytest.importorskip("cv2")
pytest.importorskip("face_recognition")

import cv2  # noqa: E402

from face_recognition_doorbell.recognizer import FaceRecognizer  # noqa: E402
from face_recognition_doorbell.whitelist import WhiteList  # noqa: E402


@pytest.fixture
def recognizer(tmp_path: Path, repo_data: Path) -> FaceRecognizer:
    """A recognizer whose whitelist holds one photo of one person.

    ``scale=1.0`` because these are already small stills; downscaling them the way
    a webcam frame is downscaled can lose the face entirely.
    """
    directory = tmp_path / "samples"
    directory.mkdir()
    (directory / "elon_musk1.jpg").write_bytes(
        (repo_data / "demo" / "elon_musk1.jpg").read_bytes()
    )
    return FaceRecognizer.from_white_list(WhiteList(directory), scale=1.0)


def test_a_second_photo_of_the_same_person_matches(
    recognizer: FaceRecognizer, repo_data: Path
) -> None:
    frame = cv2.imread(str(repo_data / "samples" / "elon_musk.jpg"))

    matches = recognizer.recognize(frame)

    assert len(matches) == 1
    assert matches[0].name == "elon_musk1"
    assert matches[0].is_known is True


def test_a_different_person_is_unknown(
    recognizer: FaceRecognizer, repo_data: Path
) -> None:
    frame = cv2.imread(str(repo_data / "samples" / "donald_trump.jpg"))

    matches = recognizer.recognize(frame)

    assert len(matches) == 1
    assert matches[0].name is None
    assert matches[0].is_known is False


def test_coordinates_land_inside_the_frame(
    recognizer: FaceRecognizer, repo_data: Path
) -> None:
    """Catches a missing or inverted upscale after detection on a resized frame."""
    frame = cv2.imread(str(repo_data / "samples" / "elon_musk.jpg"))
    height, width = frame.shape[:2]

    match = recognizer.recognize(frame)[0]

    assert 0 <= match.left < match.right <= width
    assert 0 <= match.top < match.bottom <= height


def test_an_empty_whitelist_makes_every_face_unknown(repo_data: Path) -> None:
    """np.argmin raises on an empty array, so the empty case is handled up front."""
    recognizer = FaceRecognizer([], [], scale=1.0)
    frame = cv2.imread(str(repo_data / "samples" / "elon_musk.jpg"))

    matches = recognizer.recognize(frame)

    assert len(matches) == 1
    assert matches[0].name is None


def test_mismatched_encodings_and_names_are_rejected() -> None:
    with pytest.raises(ValueError):
        FaceRecognizer([object()], [])

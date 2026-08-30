"""Whitelist loading and encoding. Needs OpenCV and dlib, so it skips without them."""

from pathlib import Path

import pytest

pytest.importorskip("cv2")
pytest.importorskip("face_recognition")

import cv2  # noqa: E402

from face_recognition_doorbell.whitelist import WhiteList  # noqa: E402


def test_non_image_entries_are_ignored(samples_dir: Path) -> None:
    """A README or subdirectory beside the faces must not crash the loader.

    ``cv2.imread`` returns None for those, and the ``cvtColor`` that follows
    raises. The old loader read every ``os.listdir`` entry, so adding any
    documentation to the samples directory broke startup.
    """
    white_list = WhiteList(samples_dir)

    assert white_list.get_white_list_names() == ["elon_musk.jpg"]


def test_display_name_is_the_filename_stem(samples_dir: Path) -> None:
    """The stem becomes the label drawn on screen and the name written to the log."""
    white_list = WhiteList(samples_dir)

    assert [name for _, name in white_list.get_white_lists()] == ["elon_musk"]


def test_all_three_lists_stay_aligned(samples_dir: Path) -> None:
    white_list = WhiteList(samples_dir)

    assert (
        len(white_list.get_white_lists())
        == len(white_list.get_encoded_faces())
        == len(white_list.get_white_list_names())
    )


def test_add_white_list_keeps_the_lists_aligned(samples_dir: Path, repo_data: Path) -> None:
    white_list = WhiteList(samples_dir)
    image = cv2.cvtColor(
        cv2.imread(str(repo_data / "samples" / "donald_trump.jpg")), cv2.COLOR_BGR2RGB
    )

    assert white_list.add_white_list(image, "donald_trump.jpg") is True
    assert (
        len(white_list.get_white_lists())
        == len(white_list.get_encoded_faces())
        == len(white_list.get_white_list_names())
        == 2
    )
    assert white_list.get_white_list_names()[-1] == "donald_trump.jpg"


def test_faceless_images_are_dropped(tmp_path: Path, repo_data: Path) -> None:
    """A person whose face cannot be encoded leaves no gap in the parallel lists."""
    directory = tmp_path / "samples"
    directory.mkdir()
    cv2.imwrite(str(directory / "blank.png"), cv2.imread(str(repo_data / "samples" / "elon_musk.jpg")) * 0)

    white_list = WhiteList(directory)

    assert white_list.get_white_lists() == []
    assert white_list.get_encoded_faces() == []
    assert white_list.get_white_list_names() == []


def test_load_order_is_deterministic(tmp_path: Path, repo_data: Path) -> None:
    directory = tmp_path / "samples"
    directory.mkdir()
    for name in ("b_person.jpg", "a_person.jpg"):
        (directory / name).write_bytes((repo_data / "samples" / "elon_musk.jpg").read_bytes())

    white_list = WhiteList(directory)

    assert white_list.get_white_list_names() == ["a_person.jpg", "b_person.jpg"]

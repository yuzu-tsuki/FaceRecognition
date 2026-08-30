"""Invariants over the tuned constants."""

from face_recognition_doorbell import config


def test_frame_scale_and_upscale_are_reciprocal() -> None:
    """The pair used to be a literal 0.25 and eight literal 4s, three blocks apart.

    Keeping them reciprocal is what stops face boxes from being drawn in the
    wrong place, so it is asserted rather than left to review.
    """
    assert config.FRAME_SCALE * config.FRAME_UPSCALE == 1


def test_image_suffixes_are_lowercase_and_dotted() -> None:
    """WhiteList compares against ``entry.suffix.lower()``, so these must match."""
    assert all(s.startswith(".") and s == s.lower() for s in config.IMAGE_SUFFIXES)


def test_header_matches_the_timestamp_format_arity() -> None:
    """The header must name exactly the two fields each row writes."""
    assert config.ATTENDANCE_HEADER.count(",") == 1

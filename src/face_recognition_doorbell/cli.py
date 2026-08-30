"""Command line entry point for the ``frdb`` console script."""

import argparse
import logging
from typing import Sequence

from . import __version__

_LOG = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Builds the argument parser for the ``frdb`` command."""
    parser = argparse.ArgumentParser(
        prog="frdb",
        description="Recognise whitelisted faces from the webcam and log attendance.",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="log every recognition instead of only warnings",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Runs the door bell. Returns the process exit code."""
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )

    # Imported here rather than at module scope so that --help and --version stay
    # usable on a machine where the OpenCV or dlib stack failed to install.
    from .doorbell import DoorBell

    DoorBell().run_door_bell()
    return 0

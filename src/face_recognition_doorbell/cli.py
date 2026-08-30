"""Command line entry point for the ``frdb`` console script."""

import argparse
import logging
from pathlib import Path
from typing import Sequence

from . import __version__, config, paths

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
        "--samples",
        type=Path,
        default=None,
        metavar="PATH",
        help="directory of whitelist images (default: the resolved data directory)",
    )
    parser.add_argument(
        "--attendance",
        type=Path,
        default=None,
        metavar="PATH",
        help="attendance log to append to (default: the resolved data directory)",
    )
    parser.add_argument(
        "--camera",
        type=int,
        default=config.DEFAULT_CAMERA_INDEX,
        metavar="INDEX",
        help=f"camera index to open (default: {config.DEFAULT_CAMERA_INDEX})",
    )
    parser.add_argument(
        "--list-white-list",
        action="store_true",
        help="print the resolved paths and the whitelisted names, then exit",
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

    samples = args.samples or paths.default_samples_dir()
    attendance = args.attendance or paths.default_attendance_file()

    # Printing what was actually resolved replaces the old guesswork about which
    # directory the process had to be started from.
    print(f"samples:    {samples.resolve()}")
    print(f"attendance: {attendance.resolve()}")

    if not samples.is_dir():
        print(f"error: samples directory does not exist: {samples.resolve()}")
        return 1

    # Imported here rather than at module scope so that --help and --version stay
    # usable on a machine where the OpenCV or dlib stack failed to install.
    from .doorbell import DoorBell

    door_bell = DoorBell(samples, attendance, camera_index=args.camera)

    if args.list_white_list:
        for _, name in door_bell.view_white_list():
            print(name)
        return 0

    door_bell.run_door_bell()
    return 0

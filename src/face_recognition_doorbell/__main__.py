"""Allows ``python -m face_recognition_doorbell`` alongside the ``frdb`` script."""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())

"""Webcam door bell that recognises whitelisted faces and logs attendance.

Deliberately free of re-exports: setuptools reads ``__version__`` from this file
at build time, and importing the camera modules here would drag ``cv2`` into that
path. It also keeps ``face_recognition_doorbell.attendance`` importable on a
machine where ``dlib`` never built.
"""

__version__ = "0.1.0"

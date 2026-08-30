"""Tunable constants.

Literals only: no logic, no filesystem access, no third-party imports. That makes
this module the single place to look for "where does this magic number live", and
keeps it importable on a machine where OpenCV or dlib failed to install.
"""

# Frames are downscaled before detection and the resulting box coordinates are
# scaled back up. The upscale is *derived* rather than written out, so the two
# can never drift apart the way the literal 0.25 and eight literal 4s used to.
FRAME_SCALE: float = 0.25
FRAME_UPSCALE: int = round(1 / FRAME_SCALE)

DEFAULT_CAMERA_INDEX: int = 0
WINDOW_TITLE: str = "Door Bell"
QUIT_KEY: str = "q"
WAIT_KEY_DELAY_MS: int = 1

# Parsing and formatting must agree, so the attendance log has exactly one format.
TIMESTAMP_FORMAT: str = "%d/%m/%Y %H:%M:%S"
ATTENDANCE_HEADER: str = "name,date"
ATTENDANCE_DEDUPE_SECONDS: int = 60

UNKNOWN_LABEL: str = "Unknown"
KNOWN_BOX_COLOR: tuple[int, int, int] = (255, 255, 0)
UNKNOWN_BOX_COLOR: tuple[int, int, int] = (0, 0, 255)
LABEL_COLOR: tuple[int, int, int] = (255, 255, 255)
BOX_THICKNESS: int = 2
LABEL_FONT_SCALE: float = 1.5
LABEL_OFFSET_X: int = 6
LABEL_OFFSET_Y: int = -6

# Everything else in the samples directory is skipped. Without this filter a
# README or a stray subdirectory makes cv2.imread return None, and the cvtColor
# that follows raises.
IMAGE_SUFFIXES: frozenset[str] = frozenset(
    {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
)

DATA_DIR_NAME: str = "data"
SAMPLES_DIR_NAME: str = "samples"
ATTENDANCE_DIR_NAME: str = "attendance"
ATTENDANCE_FILE_NAME: str = "attendance.csv"
ENV_DATA_DIR: str = "DOORBELL_DATA_DIR"

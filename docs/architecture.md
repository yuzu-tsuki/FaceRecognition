# Architecture

## Layout

```
src/face_recognition_doorbell/   the installable package
data/                            samples, demo stills, attendance log
tools/                           developer utilities, never installed
tests/                           pytest suite, no camera required
docs/                            this
```

`tools/` holds things you run while developing; anything meant for users is a
console entry point declared in `pyproject.toml`. There is deliberately no
`scripts/` directory as well — one home for runnables is enough.

## Modules

Each module is placed by its heaviest import, so that the parts most worth
testing stay testable on a machine where dlib will not build.

| Module | Heaviest import | Runs without |
| --- | --- | --- |
| `config.py` | *(none)* | everything |
| `paths.py` | `pathlib`, `os` | everything |
| `attendance.py` | `datetime`, `pathlib` | OpenCV, dlib, camera |
| `recognizer.py` | `numpy`, `face_recognition` | OpenCV GUI, camera |
| `whitelist.py` | `cv2`, `face_recognition` | camera |
| `doorbell.py` | `cv2` including GUI | camera, for `annotate()` |
| `cli.py` | `argparse` | camera, for `--help` |

`cli.py` imports `doorbell` inside `main()` rather than at module scope, so
`frdb --help` and `frdb --version` still work when the OpenCV or dlib stack is
broken.

`__init__.py` holds only a docstring and `__version__`. It stays free of
re-exports because setuptools reads the version from it at build time, and a
re-export would pull `cv2` into that path.

## Data flow

```
camera frame (BGR, full resolution)
        │
        ▼
DoorBell.run_door_bell ──► DoorBell.annotate ──► FaceRecognizer.recognize
        │                        │                      │
        │                        │                      ├─ downscale by FRAME_SCALE
        │                        │                      ├─ detect + encode
        │                        │                      ├─ compare against WhiteList
        │                        │                      └─ scale boxes back up
        │                        │
        │                        ├─ draw box and label onto the frame
        │                        └─ AttendanceLog.mark(name)
        │                                 └─ append unless seen recently
        ▼
cv2.imshow / waitKey
```

`annotate()` is the seam. It does everything one frame needs — recognise, draw,
log — without touching a camera or a window, which is what lets the test suite
exercise recognition from a still image.

## Two invariants worth knowing

**Frame scale.** Detection runs on a downscaled frame, so box coordinates must be
scaled back up. `config.FRAME_UPSCALE` is *derived* as `round(1 / FRAME_SCALE)`
rather than written out, because the two used to be a literal `0.25` and eight
literal `4`s sitting three blocks apart. `tests/test_config.py` asserts they stay
reciprocal.

**Index alignment.** `WhiteList` keeps three parallel lists — `white_list`,
`white_list_names` and `_encoded_faces`. A person whose face cannot be encoded is
dropped from all three, and `add_white_list` appends to all three. Anything that
breaks that alignment mislabels faces.

## Path resolution

Highest priority first:

1. an explicit argument (`--samples`, `--attendance`, or a constructor parameter)
2. the `DOORBELL_DATA_DIR` environment variable
3. `<nearest ancestor containing pyproject.toml>/data`
4. `./data`

Samples and the attendance log are per-deployment mutable state, so they live in
`data/` rather than inside the wheel. `importlib.resources` would be the wrong
tool for them: it is read-oriented, and can hand back a temporary copy that a
write would silently lose.

Before this, the code used relative literals (`'Samples'`,
`'Attendance/Attendance.csv'`) and only worked when started from inside the
`DoorBell/` directory.

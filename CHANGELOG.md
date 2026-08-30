# Changelog

Notable changes to FaceTrack. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-08-30

First tagged release. Everything before this point was untagged development.

This release carries two separate lines of work: a round of recognition and
attendance bug fixes, and a restructure of the repository into an installable
package.

### Added

- Installable package `face_recognition_doorbell` under a `src/` layout, with
  `pyproject.toml` as the single source of dependency truth.
- `frdb` console command, plus `python -m face_recognition_doorbell`. Flags:
  `--samples`, `--attendance`, `--camera`, `--list-white-list`, `--verbose`,
  `--version`.
- `paths.py`, resolving the data directory from an explicit argument, the
  `DOORBELL_DATA_DIR` environment variable, or the nearest project root.
- `config.py`, holding every tunable literal previously written inline.
- `AttendanceLog`, with an injectable clock and a configurable suppression
  window.
- `FaceRecognizer` and `FaceMatch`, performing face matching with no camera or
  window involved, and `DoorBell.annotate`, which handles one frame.
- A pytest suite of 30 tests. None of them open a camera or a window; the tests
  needing OpenCV or dlib skip themselves when those are absent.
- `docs/architecture.md`, `docs/usage.md` and `data/README.md`.

### Changed

- **Breaking: the application is now started with `frdb`**, replacing
  `cd DoorBell && python door_bell_test.py`.
- **Breaking: paths no longer depend on the working directory.** Samples moved
  from `DoorBell/Samples/` to `data/samples/`, and the attendance log from
  `DoorBell/Attendance/Attendance.csv` to `data/attendance/attendance.csv`.
- The attendance log is no longer tracked in git. It is runtime output, created
  on demand with a `name,date` header.
- `requirements.txt` is UTF-8 rather than UTF-16, and forwards to
  `pyproject.toml`. Git no longer treats it as a binary file.
- Python 3.10 or newer is required. The pinned `numpy==2.2.6` already implied
  this; the previously documented 3.9 was never actually supported.
- `setuptools<81` is now a runtime dependency. `face_recognition_models` imports
  `pkg_resources`, which was removed in setuptools 81 and is absent by default
  on Python 3.12 and newer; without the pin, `import face_recognition` fails.

### Fixed

- The whitelist doubled on every launch. `add_sample()` re-read the whole
  samples directory and re-added everybody, and the entry point called it
  unconditionally before each run. It is now idempotent.
- A non-image file in the samples directory crashed startup. Every directory
  entry was passed to `cv2.imread`, which returns `None` for a README or a
  subdirectory, and the `cvtColor` that followed raised.
- `add_white_list` did not append to `white_list_names`, so the three parallel
  lists drifted apart after a person was added at runtime, mislabelling faces.
- A person whose face could not be encoded left the whitelist and its encodings
  misaligned by one, shifting every subsequent name.
- Attendance timestamps failed to parse when the row kept its trailing newline
  from `readlines()`.
- The attendance log was opened `'r+'` and raised `FileNotFoundError` when it did
  not exist, so a fresh checkout failed on the first recognised face.
- The face comparison demo had never run: all three of its image paths pointed at
  files that did not exist. It is now `tools/compare_faces_demo.py` and works.
- The frame downscale factor and the eight coordinate upscale multiplications
  could drift apart. The upscale is now derived from the scale, and a test
  asserts they stay reciprocal.
- The attendance log is read and written as UTF-8 rather than the platform
  default encoding.
- README install instructions referenced a `conda.yml` that does not exist, and
  its usage section never named an entry point.

### Removed

- `DoorBell/door_bell_test.py`, superseded by the `frdb` console script. It ran
  on import, so merely importing it opened the webcam.
- The empty `__init__.py` at the repository root, which was never an importable
  package.
- `images/donald_trump1.jpg` and `images/elon_musk2.jpg`, byte-identical
  duplicates of the two files now under `data/samples/`.

[0.1.0]: https://github.com/yuzu-tsuki/FaceRecognition/releases/tag/v0.1.0

# Usage

## Install

Python 3.10 or newer (the pinned numpy 2.2 requires it).

```sh
git clone https://github.com/daechan0615/FaceRecognition
cd FaceRecognition
python -m pip install -e .
```

`pip install -r requirements.txt` does the same thing — that file now forwards to
`pyproject.toml`, which is the single source of dependency truth.

Add the test dependencies with `python -m pip install -e ".[dev]"`.

### About the setuptools pin

`face_recognition_models` does `from pkg_resources import resource_filename` when
imported. `pkg_resources` ships with setuptools, was removed in setuptools 81,
and is no longer installed by default on Python 3.12+. The project therefore
depends on `setuptools<81`. Without it, `import face_recognition` fails with a
misleading "Please install `face_recognition_models`" message even though the
package is installed.

## Run

```sh
frdb
```

Press `q` or close the window to stop. `python -m face_recognition_doorbell` is
equivalent.

The working directory does not matter — the command prints the paths it resolved
before starting:

```
samples:    C:\...\FaceRecognition\data\samples
attendance: C:\...\FaceRecognition\data\attendance\attendance.csv
```

### Options

| Flag | Meaning |
| --- | --- |
| `--samples PATH` | directory of whitelist images |
| `--attendance PATH` | attendance log to append to |
| `--camera INDEX` | camera to open (default 0) |
| `--list-white-list` | print the resolved paths and known names, then exit |
| `-v`, `--verbose` | log every recognition |
| `--version` | print the version |

`--list-white-list` is the quickest way to check a setup, because it needs no
camera:

```sh
frdb --list-white-list
```

## Managing the whitelist

Drop one photo per person into `data/samples/`. The filename without its
extension becomes the person's name, so `elon_musk.jpg` is recognised as
`elon_musk` and logged under that name.

Photos should contain exactly one clearly visible face. A photo whose face
cannot be encoded is skipped with a warning rather than stopping startup.

To keep the roster somewhere else:

```sh
frdb --samples /path/to/faces
# or, for the whole data directory:
DOORBELL_DATA_DIR=/path/to/data frdb
```

## The attendance log

`data/attendance/attendance.csv` is created on first use with a `name,date`
header:

```
name,date
elon_musk,30/08/2026 12:00:00
```

Timestamps are `dd/mm/YYYY HH:MM:SS`. The same person is not logged twice within
60 seconds; change `ATTENDANCE_DEDUPE_SECONDS` in `config.py` to adjust that.

The log is untracked runtime output. Deleting it is safe — it is recreated.

## Tests

```sh
python -m pytest
```

Nothing in the suite opens a camera or a window. Tests needing OpenCV or dlib
skip themselves when those are not installed, so the attendance, path and config
tests still run on a machine where dlib will not build.

## The comparison demo

```sh
python tools/compare_faces_demo.py
```

Opens three windows showing a reference face, a second photo of the same person
(a match), and a different person (not a match), each labelled with its distance.
Press any key to close.

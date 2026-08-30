<div id="top">

<!-- HEADER STYLE: CLASSIC -->
<div align="center">


# FACETRACK

<em>Unlocking Secure Identities with Precision and Speed</em>

<!-- BADGES -->
<img src="https://img.shields.io/github/last-commit/daechan0615/FaceRecognition?style=flat&logo=git&logoColor=white&color=0080ff" alt="last-commit">
<img src="https://img.shields.io/github/languages/top/daechan0615/FaceRecognition?style=flat&color=0080ff" alt="repo-top-language">
<img src="https://img.shields.io/github/languages/count/daechan0615/FaceRecognition?style=flat&color=0080ff" alt="repo-language-count">

<em>Built with the tools and technologies:</em>

<img src="https://img.shields.io/badge/Markdown-000000.svg?style=flat&logo=Markdown&logoColor=white" alt="Markdown">
<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/OpenCV-5C3EE8.svg?style=flat&logo=OpenCV&logoColor=white" alt="OpenCV">
<img src="https://img.shields.io/badge/NumPy-013243.svg?style=flat&logo=NumPy&logoColor=white" alt="NumPy">

</div>
<br>

---

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Usage](#usage)
    - [Testing](#testing)
- [Project Structure](#project-structure)
- [Documentation](#documentation)

---

## Overview

FaceTrack is an intelligent attendance system built to automate check-ins by recognizing and tracking students' faces in real time. Powered by libraries like OpenCV, NumPy, and face_recognition, it streamlines the attendance process with accuracy and efficiency, eliminating the need for manual roll calls or sign-ins. Whether in classrooms, training sessions, or events, FaceTrack provides a reliable solution for seamless attendance management.

**Why FaceTrack?**

This project simplifies attendance tracking with an easy-to-use, automated workflow. The core features include:

- 🧠 **Face Detection & Encoding:** Identifies and encodes student faces for accurate recognition.
- 🖥️ **Real-Time Processing:** Captures live video streams to mark attendance instantly.
- 🔍 **Visualization & Annotation:** Displays annotated faces for verification and transparency.
- 📋 **Automated Attendance Logs:** Generates organized records without manual intervention.
- ⚙️ **Seamless Integration:** Can be adapted for schools, universities, or training platforms.

---

## Getting Started

### Prerequisites

- **Python:** 3.10 or newer (the pinned numpy 2.2 requires it)
- **Package Manager:** pip
- **Hardware:** a webcam, to run the door bell itself

### Installation

1. **Clone the repository:**

    ```sh
    git clone https://github.com/daechan0615/FaceRecognition
    ```

2. **Navigate to the project directory:**

    ```sh
    cd FaceRecognition
    ```

3. **Install the project:**

    ```sh
    python -m pip install -e .
    ```

    `pip install -r requirements.txt` does the same thing — that file forwards to
    `pyproject.toml`, which is the single source of dependency truth.

### Usage

Run the door bell:

```sh
frdb
```

Press `q` or close the window to stop. The working directory does not matter; the
command prints the sample and attendance paths it resolved before it starts.

Check a setup without a camera:

```sh
frdb --list-white-list
```

To enrol somebody, drop one photo of them into `data/samples/`. The filename
without its extension becomes the name that is recognised and logged, so
`elon_musk.jpg` is logged as `elon_musk`.

See [docs/usage.md](docs/usage.md) for every flag, the attendance log format, and
how to point the application at a different data directory.

### Testing

```sh
python -m pytest
```

Nothing in the suite opens a camera or a window. The tests that need OpenCV or
dlib skip themselves when those are not installed.

---

## Project Structure

```
src/face_recognition_doorbell/   the installable package
├── cli.py                       the frdb command
├── config.py                    tunable constants, no logic
├── paths.py                     where samples and the log live
├── whitelist.py                 loads and encodes the sample images
├── recognizer.py                face matching, no camera or window
├── attendance.py                the append-only log, standard library only
└── doorbell.py                  the webcam loop and on-screen drawing
data/                            samples, demo stills, attendance log
tools/                           developer utilities, never installed
tests/                           pytest suite, no camera required
docs/                            architecture and usage notes
```

---

## Documentation

- [docs/usage.md](docs/usage.md) — installing, running, flags, managing the whitelist
- [docs/architecture.md](docs/architecture.md) — module split, data flow, path resolution
- [data/README.md](data/README.md) — what lives in each data directory

---

<div align="left"><a href="#top">⬆ Return</a></div>

---

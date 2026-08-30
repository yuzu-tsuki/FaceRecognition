# Data

Everything here is per-deployment state, not part of the installed package. The
application resolves this directory at runtime, so it is never bundled into a
wheel.

## `samples/`

The whitelist: one photo per person, containing exactly one clearly visible face.

**Filenames are load-bearing.** The name without its extension becomes the label
drawn on screen and the name written to the attendance log, so
`elon_musk.jpg` produces `elon_musk`. Renaming a file renames the person.

Anything that is not a recognised image (`.jpg`, `.jpeg`, `.png`, `.webp`,
`.bmp`) is ignored, which is why this README sits here rather than inside
`samples/`. A person whose face cannot be encoded is dropped from the whitelist
with a warning rather than breaking startup.

## `demo/`

Stills used only by `tools/compare_faces_demo.py`. Not part of the whitelist.

## `attendance/`

Where the attendance log is written. `attendance.csv` is created on first use
with a `name,date` header and is deliberately untracked: it is runtime output,
and tracking an append-only log guarantees merge conflicts.

Rows look like:

```
elon_musk,30/08/2026 12:00:00
```

A repeat sighting of the same person within 60 seconds is suppressed.

## Pointing elsewhere

Set `DOORBELL_DATA_DIR` to use a different data directory entirely, or pass
`--samples` and `--attendance` to override either path individually.

#!/usr/bin/env python3
"""Make the AI Judge Laugh -- one office-life joke, one line, <= 200 chars.

Writes the entry line to $MAKEFUN_OUTPUT_DIR/entry.txt (default /output).
Python 3 stdlib only, no network, no reads outside the repo, deterministic.
"""

import os
import sys
import tempfile

LINE = "The office plant died, so HR replaced it with a plastic one: the first hire that thrives on neglect and never asks for a raise."


def main() -> int:
    line = LINE
    if not 1 <= len(line) <= 200:
        raise SystemExit("entry line must be 1-200 characters")
    if not line.strip() or line != line.strip():
        raise SystemExit("entry line must not be blank or padded with whitespace")
    if "\n" in line or "\r" in line:
        raise SystemExit("entry line must be a single line")
    if any(ord(c) < 32 for c in line):
        raise SystemExit("entry line must not contain control characters")

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    # Clean only the contents of the output folder, never the folder itself.
    for name in os.listdir(out_dir):
        path = os.path.join(out_dir, name)
        if os.path.isfile(path) or os.path.islink(path):
            os.remove(path)

    fd, tmp = tempfile.mkstemp(dir=out_dir, prefix=".entry-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())
        with open(tmp, "r", encoding="utf-8") as f:
            if f.read() != line:
                raise SystemExit("read-back mismatch")
        os.replace(tmp, os.path.join(out_dir, "entry.txt"))
        dir_fd = os.open(out_dir, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
        # Validate the artifact on disk, not just the constant in memory:
        # a corrupted or truncated write must fail the run, not ship.
        with open(os.path.join(out_dir, "entry.txt"), "r", encoding="utf-8") as f:
            written = f.read()
        if written != line:
            raise SystemExit("written entry differs from the line")
        if not 1 <= len(written) <= 200 or "\n" in written or "\r" in written:
            raise SystemExit("written entry fails the gate")
    except BaseException:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise
    return 0


if __name__ == "__main__":
    sys.exit(main())

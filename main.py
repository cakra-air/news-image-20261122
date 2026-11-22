"""Write the day's news image to /output/entry.png.

The page is baked into the repository as entry.png.  This entrypoint only
copies those bytes: no network, no randomness, identical output every run.
"""

import os
import shutil
from pathlib import Path

SOURCE = Path(__file__).resolve().with_name("entry.png")
TARGET = Path("/output/entry.png")


def main():
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, TARGET)
    os.chmod(TARGET, 0o644)


if __name__ == "__main__":
    main()

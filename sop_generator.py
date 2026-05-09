import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from sop_generator.cli import main  # noqa: E402


if __name__ == "__main__":
    main()

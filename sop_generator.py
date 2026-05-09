import sys
from pathlib import Path

_SRC_DIR = Path(__file__).parent / "src"
_PACKAGE_DIR = _SRC_DIR / "sop_generator"

if __name__ == "sop_generator":
    __path__ = [str(_PACKAGE_DIR)]


if __name__ == "__main__":
    sys.path.insert(0, str(_SRC_DIR))
    from sop_generator.cli import main

    main()

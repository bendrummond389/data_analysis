import argparse
import shutil
from pathlib import Path
from typing import List, Set

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
ARTIFACT_PATTERNS = {
    "directories": {
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        "logs",
        "dist",
        "build",
        "data_analysis.egg-info",
    },
    "files": {"*.pyc", "*.pyo", "*.pyd", ".DS_Store", "Thumbs.db", "*.log"},
    "exclude_dirs": {".git", ".venv", ".idea", "data/raw", "data/cleaned"},
}


def find_artifacts(root: Path, dry_run: bool = False) -> List[Path]:
    found = []

    for path in root.rglob("*"):
        if any(excl in path.parts for excl in ARTIFACT_PATTERNS["exclude_dirs"]):
            continue

        # Check directory patterns
        if path.is_dir() and path.name in ARTIFACT_PATTERNS["directories"]:
            found.append(path)
            if not dry_run:
                shutil.rmtree(path)

        # Check file patterns
        elif path.is_file() and any(
            path.match(pattern) for pattern in ARTIFACT_PATTERNS["files"]
        ):
            found.append(path)
            if not dry_run:
                path.unlink()

    return found


def main():
    parser = argparse.ArgumentParser(description="Clean project artifacts")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be deleted"
    )
    args = parser.parse_args()

    artifacts = find_artifacts(PROJECT_ROOT, args.dry_run)

    print(f"Found {len(artifacts)} artifacts to clean:")
    for artifact in artifacts:
        print(f" - {artifact.relative_to(PROJECT_ROOT)}")

    if args.dry_run:
        print("\nDry run completed - no files were deleted")
    else:
        print("\nSuccessfully cleaned project artifacts")


if __name__ == "__main__":
    main()

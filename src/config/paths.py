from pathlib import Path
from typing import List, Optional


def find_project_root(marker: str = "README.md", max_depth: int = 5) -> Path:
    """Find project root by looking for a marker file."""
    current_path = Path(__file__).resolve()
    for _ in range(max_depth):
        if (current_path / marker).exists():
            return current_path
        current_path = current_path.parent
    raise FileNotFoundError(f"Project root not found within {max_depth} levels")


def find_nearest_config(
    start_path: Optional[Path] = None,
    config_name: str = "database.yaml",
    search_depth: int = 5,
) -> Path:
    """
    Search upward from start_path to find the nearest config file.

    Args:
        start_path: Path to start searching from (defaults to caller's location)
        config_name: Name of config file to look for
        search_depth: Maximum directory levels to search

    Returns:
        Path to found config file

    Raises:
        FileNotFoundError: If no config found in hierarchy
    """
    if start_path is None:
        # Default to caller's directory
        import inspect

        frame = inspect.stack()[1]
        start_path = Path(frame.filename).parent.resolve()

    current_path = start_path
    for _ in range(search_depth):
        config_candidate = current_path / "config" / config_name
        if config_candidate.exists():
            return config_candidate.resolve()

        # Stop if we reach project root
        if (current_path / "README.md").exists():
            break

        current_path = current_path.parent

    # Fallback to project root config
    root_config = current_path / "config" / config_name
    if root_config.exists():
        return root_config

    raise FileNotFoundError(
        f"No {config_name} found in hierarchy starting from {start_path}"
    )


def create_symlink(source: Path, target: Path):
    """
    Creates a symbolic link at 'target' pointing to 'source'.

    Args:
        source (Path): The directory or file to link to.
        target (Path): The location where the symlink will be created.
    """
    source = source.resolve()
    target = target.resolve()

    # Ensure the source exists
    if not source.exists():
        raise FileNotFoundError(f"Source path does not exist: {source}")

    # If the target already exists, notify the user
    if target.exists():
        print(
            f"{target} already exists. Delete it or rename it before creating a symlink."
        )
        return

    # Create the symlink
    target.symlink_to(source, target_is_directory=source.is_dir())
    print(f"Symlink created: {target} -> {source}")


def find_project_root(
    start_path: Optional[Path] = None,
    search_depth: int = 5,
) -> Path:
    """
    Search upward from start_path to find the root of a competition directory.

    This function assumes:
    1. Each competition subdirectory sits directly under 'competitions/'.
    2. That subdirectory typically has 'config', 'data', 'db', and 'notebooks'.

    You can customize 'required_dirs' or the logic below to match your needs.

    Args:
        start_path (Path, optional): Directory to start searching from.
                                     Defaults to the caller's location.
        search_depth (int): Maximum number of levels to climb.
        required_dirs (List[str], optional): List of directory names that must
                                             exist for us to consider this path
                                             a valid competition root.

    Returns:
        Path: Path to the discovered competition root directory.

    Raises:
        FileNotFoundError: If no competition root is found within search_depth.
    """
    if start_path is None:
        # Default to caller's directory
        import inspect

        frame = inspect.stack()[1]
        start_path = Path(frame.filename).parent.resolve()

    current_path = start_path

    for _ in range(search_depth):
        # Check if the parent folder is 'projects'
        if current_path.parent.name == "projects":
            return current_path.resolve()

        # Climb up one level
        current_path = current_path.parent

    raise FileNotFoundError(
        f"No competition root found within {search_depth} levels starting from {start_path}"
    )

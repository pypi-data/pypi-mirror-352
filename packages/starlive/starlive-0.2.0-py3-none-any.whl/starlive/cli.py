#!/usr/bin/env python3
"""
CLI entry points for StarLive console scripts.
"""

import sys
from pathlib import Path


def _add_project_root_to_path():
    """Add project root to sys.path if we're in development mode."""
    # Try to find project root (where pyproject.toml is)
    current_dir = Path(__file__).parent
    project_root = None

    # Walk up the directory tree to find pyproject.toml
    for parent in [current_dir, *list(current_dir.parents)]:
        if (parent / "pyproject.toml").exists():
            project_root = parent
            break

    if project_root and str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        return project_root
    return None


def test_main():
    """Entry point for starlive-test command."""
    try:
        from scripts.test import main

        return main()
    except ImportError:
        # Try adding project root to path for development mode
        project_root = _add_project_root_to_path()
        if project_root:
            try:
                from scripts.test import main

                return main()
            except ImportError:
                pass

        print("Error: scripts module not found")
        print("Make sure you're running from the project root or in development mode")
        print("Try: cd /path/to/starlive && uv pip install -e .")
        return 1


def dev_main():
    """Entry point for starlive-dev command."""
    try:
        from examples.app_factory import main

        return main()
    except ImportError:
        # Try adding project root to path for development mode
        project_root = _add_project_root_to_path()
        if project_root:
            try:
                from examples.app_factory import main

                return main()
            except ImportError:
                pass

        print("Error: examples module not found")
        print("Make sure you're running from the project root or in development mode")
        print("Try: cd /path/to/starlive && uv pip install -e .")
        return 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        sys.exit(test_main())
    elif len(sys.argv) > 1 and sys.argv[1] == "dev":
        sys.exit(dev_main())
    else:
        print("Usage: python -m starlive.cli [test|dev]")
        sys.exit(1)

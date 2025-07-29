#!/usr/bin/env python3
"""
Test runner script for StarLive.

This script provides a unified interface for running tests across different frameworks
and test types, following Python testing best practices.
"""

import argparse
import subprocess
import sys
from importlib.util import find_spec
from pathlib import Path
from typing import List, Optional


def run_tests(
    framework: str = "both",
    test_type: str = "unit",
    verbose: bool = False,
    file_pattern: Optional[str] = None,
    coverage: bool = False,
    parallel: bool = False,
) -> int:
    """Run tests for the specified framework and type."""

    # Base pytest command
    cmd = ["python", "-m", "pytest"]

    if verbose:
        cmd.append("-v")

    if coverage:
        cmd.extend(["--cov=src", "--cov-report=term-missing", "--cov-report=html"])

    if parallel:
        cmd.extend(["-n", "auto"])  # requires pytest-xdist

    # Framework selection
    framework_args = []
    if framework != "both":
        framework_args = [f"--framework={framework}"]

    # Test type selection
    test_files = []
    if test_type == "unit":
        test_files = [
            "tests/test_unified.py",
            "tests/test_helpers.py",
        ]
    elif test_type == "e2e":
        test_files = [
            "tests/test_e2e_frameworks.py",
            "tests/e2e/",
        ]
        # E2E tests typically need more time
        cmd.extend(["--timeout=60"])
    elif test_type == "all":
        test_files = ["tests/"]
    elif test_type == "unified":
        test_files = ["tests/test_unified.py"]
    elif test_type == "integration":
        test_files = ["tests/test_e2e_frameworks.py"]
    else:
        # Custom test file/pattern
        test_files = [f"tests/{test_type}"]

    # Apply file pattern filter
    if file_pattern:
        test_files = [f for f in test_files if file_pattern in f]
        if not test_files:
            print(f"No test files match pattern: {file_pattern}")
            return 1

    # Add test files to command
    cmd.extend(test_files)

    # Add framework args
    cmd.extend(framework_args)

    # Add additional pytest options for better output
    cmd.extend(
        [
            "--tb=short",
            "--strict-markers",
            "--strict-config",
        ]
    )

    print(f"Running tests for framework: {framework}, type: {test_type}")
    if file_pattern:
        print(f"File pattern: {file_pattern}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)

    # Run the tests
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent.parent, check=False)

        if result.returncode == 0:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Some tests failed!")
            if not verbose:
                print("Run with -v for more details")

        return result.returncode
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        return 130
    except Exception as e:
        print(f"\n💥 Error running tests: {e}")
        return 1


def install_dependencies() -> bool:
    """Install test dependencies."""
    print("Installing test dependencies...")

    commands = [
        ["uv", "sync", "--dev"],
        ["uv", "pip", "install", "-e", ".[fastapi]"],
    ]

    for cmd in commands:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=False)
        if result.returncode != 0:
            print(f"Warning: Command failed: {' '.join(cmd)}")
            return False

    print("✅ Dependencies installation completed.\n")
    return True


def check_framework_availability() -> List[str]:
    """Check which frameworks are available."""
    available_frameworks = ["starlette"]  # Always available

    if find_spec("fastapi") is not None:
        available_frameworks.append("fastapi")
        print("✅ FastAPI is available")
    else:
        print("❌ FastAPI not available (install with: uv add fastapi)")

    if find_spec("playwright") is not None:
        print("✅ Playwright is available for E2E tests")
    else:
        print("❌ Playwright not available (install with: uv add playwright)")

    return available_frameworks


def list_test_files() -> None:
    """List available test files."""
    test_dir = Path(__file__).parent.parent / "tests"

    print("📋 Available test files:")

    # Unit test files
    unit_files = list(test_dir.glob("test_*.py"))
    if unit_files:
        print("\n  Unit tests:")
        for test_file in sorted(unit_files):
            print(f"    - {test_file.name}")

    # E2E test files
    e2e_dir = test_dir / "e2e"
    if e2e_dir.exists():
        e2e_files = list(e2e_dir.glob("test_*.py"))
        if e2e_files:
            print("\n  E2E tests:")
            for test_file in sorted(e2e_files):
                print(f"    - e2e/{test_file.name}")

    print(f"\n📁 Test directory: {test_dir}")


def validate_environment() -> bool:
    """Validate that the test environment is properly set up."""
    issues = []

    # Check Python version
    if sys.version_info < (3, 12):
        issues.append(f"Python 3.12+ required, got {sys.version}")

    # Check if we're in the right directory
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        issues.append("pyproject.toml not found - run from project root")

    # Check if package is installed
    if find_spec("starlive") is None:
        issues.append("starlive package not installed - run 'uv sync --dev'")

    if issues:
        print("❌ Environment validation failed:")
        for issue in issues:
            print(f"  - {issue}")
        return False

    print("✅ Environment validation passed")
    return True


def main() -> int:
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description="StarLive Test Runner - Unified testing interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Run unit tests for both frameworks
  %(prog)s -f starlette            # Run tests for Starlette only
  %(prog)s -f fastapi              # Run tests for FastAPI only
  %(prog)s -t e2e                  # Run E2E tests
  %(prog)s -t unified              # Run only unified tests
  %(prog)s --coverage              # Run with coverage report
  %(prog)s --parallel              # Run tests in parallel
  %(prog)s --list-tests            # List available test files
        """,
    )

    parser.add_argument(
        "--framework",
        "-f",
        choices=["starlette", "fastapi", "both"],
        default="both",
        help="Framework to test (default: both)",
    )

    parser.add_argument(
        "--type",
        "-t",
        choices=["unit", "e2e", "all", "unified", "legacy", "integration"],
        default="unit",
        help="Type of tests to run (default: unit)",
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    parser.add_argument(
        "--coverage", "-c", action="store_true", help="Run with coverage report"
    )

    parser.add_argument(
        "--parallel",
        "-p",
        action="store_true",
        help="Run tests in parallel (requires pytest-xdist)",
    )

    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install test dependencies before running tests",
    )

    parser.add_argument(
        "--check-deps", action="store_true", help="Check framework availability"
    )

    parser.add_argument(
        "--list-tests", action="store_true", help="List available test files"
    )

    parser.add_argument("--pattern", help="File pattern to filter tests")

    parser.add_argument(
        "--validate-env", action="store_true", help="Validate test environment setup"
    )

    args = parser.parse_args()

    # Handle info commands first
    if args.validate_env:
        return 0 if validate_environment() else 1

    if args.list_tests:
        list_test_files()
        return 0

    if args.check_deps:
        available = check_framework_availability()
        print(f"\n🔧 Available frameworks: {', '.join(available)}")
        return 0

    # Install dependencies if requested
    if args.install_deps:
        if not install_dependencies():
            return 1

    # Validate environment before running tests
    if not validate_environment():
        print("\n💡 Try running with --install-deps to fix dependencies")
        return 1

    # Warn about FastAPI if not available and testing both/fastapi
    if args.framework in ["both", "fastapi"]:
        available = check_framework_availability()
        if "fastapi" not in available:
            if args.framework == "fastapi":
                print("❌ FastAPI not available but requested for testing")
                return 1
            else:
                print("⚠️ FastAPI not available, will skip FastAPI tests")

    # Run the tests
    return run_tests(
        framework=args.framework,
        test_type=args.type,
        verbose=args.verbose,
        file_pattern=args.pattern,
        coverage=args.coverage,
        parallel=args.parallel,
    )


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Test runner script for the OHDSI WebAPI MCP server."""

import argparse
import subprocess
import sys


def run_command(cmd: list[str]) -> int:
    """Run a command and return its exit code."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Run tests for OHDSI WebAPI MCP server")
    parser.add_argument("test_type", choices=["all", "unit", "integration", "coverage"], help="Type of tests to run")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--coverage-html", action="store_true", help="Generate HTML coverage report")

    args = parser.parse_args()

    # Base command
    base_cmd = ["poetry", "run", "pytest"]

    if args.verbose:
        base_cmd.append("-v")

    # Determine which tests to run
    if args.test_type == "unit":
        cmd = base_cmd + ["tests/unit/"]

    elif args.test_type == "integration":
        cmd = base_cmd + ["tests/integration/"]

    elif args.test_type == "coverage":
        cmd = base_cmd + [
            "--cov=src",
            "--cov-report=term",
            "--cov-report=xml",
        ]
        if args.coverage_html:
            cmd.append("--cov-report=html")

    else:  # all tests
        cmd = base_cmd + [
            "--cov=src",
            "--cov-report=term",
        ]

    # Run the tests
    exit_code = run_command(cmd)

    if args.test_type == "coverage" and args.coverage_html:
        print("\n📊 HTML coverage report generated in: htmlcov/index.html")

    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())

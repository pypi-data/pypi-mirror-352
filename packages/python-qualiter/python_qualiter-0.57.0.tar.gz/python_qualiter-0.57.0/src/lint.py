#!/usr/bin/env python3
"""
Code Linting Script

This script runs multiple linting tools on Python files:
- isort:   Sort imports
- black:   Format code
- mypy:    Type checking
- flake8:  Style guide enforcement
- pylint:  Static code analysis
- vulture: Dead code detection

Supports file wildcards like 'folder/*.py'.
"""

import argparse
import glob
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

LINE_LENGTH = 180

# Emoji constants
SUCCESS_EMOJI = "✅"
FAILURE_EMOJI = "❌"


@dataclass
class LinterConfig:
    """Configuration for a linter tool."""

    name: str
    cmd_base: List[str]
    options: Optional[List[str]] = None

    def get_command(self, file_path: str) -> List[str]:
        """Build the full command for this linter."""
        cmd = self.cmd_base + [file_path]
        if self.options:
            cmd.extend(self.options)
        return cmd


@dataclass
class LinterResult:
    """Result of running a linter."""

    name: str
    success: bool
    output: str


def run_linter(cmd: List[str]) -> Tuple[bool, str]:
    """
    Run a linter command and return the result.

    Args:
        cmd: Command to run as a list of strings

    Returns:
        Tuple of (success, output)
    """
    if not cmd:
        return False, "Error: Empty command provided"

    try:
        # Check if the command executable exists
        if not shutil.which(cmd[0]):
            return (
                False,
                f"Error: Command '{cmd[0]}' not found in PATH. Is it installed?",
            )

        if cmd[0] == "ruff":
            cmd = [cmd[0], cmd[2], cmd[1]]  # Adjust command as necessary for ruff

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=60,  # Set a reasonable timeout (60 seconds)
        )

        # Process the output
        output = result.stdout or ""
        error = result.stderr or ""
        combined_output = output + error

        # Check return code
        if result.returncode != 0:
            return False, combined_output

        return True, combined_output

    except subprocess.TimeoutExpired:
        return False, f"Error: Command '{' '.join(cmd)}' timed out after 60 seconds"

    except subprocess.SubprocessError as e:
        return False, f"Subprocess error while running '{' '.join(cmd)}': {str(e)}"

    except FileNotFoundError:
        return False, f"Error: Command '{cmd[0]}' not found. Is it installed?"

    except PermissionError:
        return False, f"Error: Permission denied when running '{cmd[0]}'"

    except OSError as e:
        return False, f"OS error while running '{' '.join(cmd)}': {str(e)}"


def get_linter_configs() -> List[LinterConfig]:
    """Get the configuration for all supported linters."""
    return [
        LinterConfig(name="isort", cmd_base=["isort"]),
        LinterConfig(name="black", cmd_base=["black"]),
        LinterConfig(
            name="mypy",
            cmd_base=["mypy"],
            options=[
                "--ignore-missing-imports",
                "--explicit-package-bases",
                "--namespace-packages",
                "--implicit-optional",
            ],
        ),
        LinterConfig(
            name="flake8",
            cmd_base=["flake8"],
            options=["--ignore=E203,E501,W503,W605"],
        ),
        LinterConfig(
            name="pylint",
            cmd_base=["pylint"],
            options=[
                "--disable=E0501,E0401,E0611,W1203,W1202,C0103,R0902,W0212,W0012,W0613,R0913,R0917",
            ],
        ),
        LinterConfig(
            name="vulture",
            cmd_base=["vulture"],
            options=["--min-confidence", "100", "--exclude", "**/cli.py"],
        ),
        LinterConfig(name="ruff", cmd_base=["ruff"], options=["check"]),
    ]


def lint_file(file_path: str, verbose: bool = False) -> List[LinterResult]:
    """
    Run all linters on the specified file.

    Args:
        file_path: Path to the file to lint
        verbose: Whether to print detailed output

    Returns:
        List of LinterResult objects
    """
    file = Path(file_path)

    if not file.exists():
        if verbose:
            print(f"Error: File '{file_path}' does not exist")
        return []

    if not file.is_file():
        if verbose:
            print(f"Error: '{file_path}' is not a file")
        return []

    linter_configs = get_linter_configs()
    results: List[LinterResult] = []

    for config in linter_configs:

        cmd = config.get_command(file_path)

        success, output = run_linter(cmd)
        results.append(LinterResult(config.name, success, output))

        # Print detailed output only in verbose mode
        if verbose and not success:
            print(f"\n{config.name} found issues in {file_path}:")
            print(output)

    return results


def expand_file_patterns(patterns: List[str]) -> List[str]:
    """
    Expand file patterns to a list of existing Python files.
    Searches recursively through all subdirectories but excludes venv directories.

    Args:
        patterns: List of file paths or wildcards

    Returns:
        List of matched file paths (all Python files including those in subfolders, excluding venv)
    """
    files = []
    for pattern in patterns:
        if os.path.isdir(pattern):
            dir_pattern = os.path.join(pattern, "**", "*.py")
            matched_files = glob.glob(dir_pattern, recursive=True)
            files.extend(matched_files)
            continue

        # Handle file or wildcard patterns
        # If pattern doesn't explicitly have *.py,
        # check if it's meant to match directories
        if (
            not pattern.endswith(".py")
            and "*" in pattern
            and not pattern.endswith("**/*.py")
        ):
            # Try the original pattern
            original_matches = glob.glob(pattern, recursive=True)

            # For each match that is a directory, search it recursively for Python files
            for match in original_matches:
                if os.path.isdir(match):
                    dir_pattern = os.path.join(match, "**", "*.py")
                    matched_files = glob.glob(dir_pattern, recursive=True)
                    files.extend(matched_files)

        # Always try the original pattern as well
        matched_files = glob.glob(pattern, recursive=True)
        for file in matched_files:
            if file.endswith(".py"):
                files.append(file)

    # Filter out files from venv directories
    filtered_files = []
    for file in files:
        # Check if the file path contains '/venv/' or '\venv\' or similar variations
        if (
            "/venv/" not in file
            and "\\venv\\" not in file
            and not file.endswith("/venv")
            and not file.endswith("\\venv")
        ):
            # Also check for path components to handle paths like foo/venv/bar
            if not any(part == "venv" for part in file.split(os.sep)):
                filtered_files.append(file)

    # Remove duplicates and sort
    return sorted(list(set(filtered_files)))


def print_results_matrix(all_results: Dict[str, List[LinterResult]]) -> bool:
    """
    Print a matrix of results with files as rows and linters as columns.

    Args:
        all_results: Dictionary mapping file paths to lists of LinterResult objects

    Returns:
        True if all linters passed for all files, False otherwise
    """
    if not all_results:
        print("No results to display.")
        return False

    # Get all unique linter names
    linter_names: set[str] = set()
    for results in all_results.values():
        for result in results:
            linter_names.add(result.name)
    linter_names = set(sorted(list(linter_names)))

    # Build the header
    header = "File".ljust(40) + " | "
    header += " | ".join(name.ljust(8) for name in linter_names)
    header_line = "=" * len(header)

    # Print the header
    print("\n" + header_line)
    print("LINTING RESULTS MATRIX")
    print(header_line)
    print(header)
    print("-" * len(header))

    # Print each file's results
    all_passed = True

    for file_path, results in all_results.items():
        # Create a dict for easy lookup of results by linter name
        result_dict = {r.name: r.success for r in results}

        # Truncate file path if too long
        display_path = file_path
        if len(display_path) > 38:
            display_path = "..." + display_path[-35:]

        row = display_path.ljust(40) + " | "

        # Add results for each linter
        for linter in linter_names:
            success = result_dict.get(linter, None)
            if success is None:
                cell = "N/A".ljust(8)
            elif success:
                cell = SUCCESS_EMOJI.ljust(8)
            else:
                cell = FAILURE_EMOJI.ljust(8)
                all_passed = False

            row += cell + " | "

        print(row)

    # Print summary
    print(header_line)
    if all_passed:
        print(f"{SUCCESS_EMOJI} ALL FILES PASSED ALL LINTERS")
    else:
        print(f"{FAILURE_EMOJI} SOME LINTERS FAILED")
    print(header_line)

    return all_passed


def print_failure_details(all_results: Dict[str, List[LinterResult]]) -> None:
    """
    Print detailed information about linter failures.

    Args:
        all_results: Dictionary mapping file paths to lists of LinterResult objects
    """
    print("\n" + "=" * LINE_LENGTH)
    print("DETAILED FAILURE INFORMATION")
    print("=" * LINE_LENGTH)

    found_failures = False

    for file_path, results in all_results.items():
        file_failures = [r for r in results if not r.success]

        if file_failures:
            found_failures = True
            print(f"\nFile: {file_path}")
            print("-" * LINE_LENGTH)

            for result in file_failures:
                print(f"\n{result.name} found issues:")
                print(result.output.strip() or "No detailed output available")

    if not found_failures:
        print("No linter failures to report.")


def main() -> int:
    """Main function to parse arguments and run linting."""
    parser = argparse.ArgumentParser(description="Run multiple linters on Python files")
    parser.add_argument(
        "files",
        nargs="+",
        help="Paths to Python files to lint (supports wildcards like 'folder/*.py')",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "--details",
        "-d",
        action="store_true",
        help="Show detailed failure messages after the results matrix",
    )

    args = parser.parse_args()

    # Expand file patterns
    files = expand_file_patterns(args.files)

    if not files:
        print("No Python files found matching the provided patterns.")
        return 1

    print(f"Found {len(files)} Python files to lint")

    # Run linting on all files and collect results
    all_results = {}

    for file_path in files:
        if args.verbose:
            print(f"\nLinting file: {file_path}")

        results = lint_file(file_path, args.verbose)
        all_results[file_path] = results

    # Print the matrix of results
    all_passed = print_results_matrix(all_results)

    # Print detailed failure information if requested
    if args.details:
        print_failure_details(all_results)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

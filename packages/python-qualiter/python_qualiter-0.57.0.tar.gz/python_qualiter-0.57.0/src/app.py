#!/usr/bin/env python3
"""
Linting CLI Wrapper

This script provides a modern Click-based CLI interface for the linting script.
It wraps the original linting functionality while adding additional features.
"""

import importlib.util
import os
import sys
from typing import List, Optional

import click

# Import the linting script dynamically
# Assuming the script is named 'linting_script.py' and in the same directory
SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "lint.py")


def import_linting_script():
    """Import the linting script module dynamically."""
    spec = importlib.util.spec_from_file_location("linting_script", SCRIPT_PATH)

    linting_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(linting_module)
    return linting_module


# Import the linting module
try:
    linting = import_linting_script()
except Exception as e:
    print(f"Error importing linting script: {e}")
    sys.exit(1)


@click.group()
@click.version_option(version="0.54.8")
@click.option(
    "--config", "-c", type=click.Path(exists=True), help="Path to configuration file"
)
def cli(config):
    """Code Linting Tool.

    A modern CLI wrapper for the Python code linting script.
    """
    if config:
        click.echo(f"Using configuration from: {config}")
        # Configuration loading would go here in a future implementation


@cli.command()
@click.argument("files", nargs=-1, required=True)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option(
    "--details",
    "-d",
    is_flag=True,
    help="Show detailed failure messages after the results matrix",
)
@click.option(
    "--enable",
    "-e",
    multiple=True,
    help="Enable only specific linters (can be used multiple times)",
)
@click.option(
    "--disable",
    "-x",
    multiple=True,
    help="Disable specific linters (can be used multiple times)",
)
@click.option(
    "--fix",
    "-f",
    is_flag=True,
    help="Apply auto-fixes where possible (currently for isort and black)",
)
def lint(files, verbose, details, enable, disable, fix):
    """Run linters on specified Python files.

    Supports file wildcards like 'folder/*.py'.
    """
    # Expand file patterns
    expanded_files = linting.expand_file_patterns(list(files))

    if not expanded_files:
        click.echo("No Python files found matching the provided patterns.")
        return 1

    click.echo(f"Found {len(expanded_files)} Python files to lint")

    if fix:
        click.echo("Running auto-fix for supported linters...")
        for file_path in expanded_files:
            for linter in ["isort", "black", "ruff"]:
                cmd = [linter, file_path]
                try:
                    if verbose:
                        click.echo(f"Running {linter} to fix {file_path}")
                    linting.subprocess.run(cmd, check=False, capture_output=not verbose)
                except Exception as exc:
                    click.echo(f"Error running {linter} fix: {exc}", err=True)

    all_results = {}

    for file_path in expanded_files:
        if verbose:
            click.echo(f"\nLinting file: {file_path}")

        # Get linter configs based on enable/disable options
        linter_configs = get_enabled_linters(enable, disable)
        results = lint_file(file_path, linter_configs, verbose)
        all_results[file_path] = results

    all_passed = print_results_matrix(all_results)

    if details:
        print_failure_details(all_results)

    exit_code = 0 if all_passed else 1
    sys.exit(exit_code)


def get_enabled_linters(enabled: Optional[List[str]], disabled: Optional[List[str]]):
    """
    Get linter configurations based on enabled/disabled lists.

    Args:
        enabled: List of linter names to enable (if None, all are enabled)
        disabled: List of linter names to disable

    Returns:
        List of LinterConfig objects for enabled linters
    """
    all_configs = linting.get_linter_configs()

    if enabled:
        # Only include specified linters
        configs = [config for config in all_configs if config.name in enabled]
    else:
        # Include all linters by default
        configs = all_configs.copy()

    if disabled:
        # Remove disabled linters
        configs = [config for config in configs if config.name not in disabled]

    return configs


def lint_file(file_path: str, linter_configs, verbose: bool = False):
    """
    Run linters on the specified file.

    Args:
        file_path: Path to the file to lint
        linter_configs: List of linter configurations to use
        verbose: Whether to print detailed output

    Returns:
        List of LinterResult objects
    """
    file = linting.Path(file_path)

    if not file.exists():
        if verbose:
            click.echo(f"Error: File '{file_path}' does not exist")
        return []

    if not file.is_file():
        if verbose:
            click.echo(f"Error: '{file_path}' is not a file")
        return []

    results = []

    for config in linter_configs:
        cmd = config.get_command(file_path)
        success, output = linting.run_linter(cmd)
        results.append(linting.LinterResult(config.name, success, output))

        # Print detailed output only in verbose mode
        if verbose and not success:
            click.echo(f"\n{config.name} found issues in {file_path}:")
            click.echo(output)

    return results


def print_results_matrix(all_results):
    """
    Print a matrix of results with files as rows and linters as columns.

    Args:
        all_results: Dictionary mapping file paths to lists of LinterResult objects

    Returns:
        True if all linters passed for all files, False otherwise
    """
    if not all_results:
        click.echo("No results to display.")
        return False

    # Get all unique linter names
    linter_names = set()
    for results in all_results.values():
        for result in results:
            linter_names.add(result.name)
    linter_names = sorted(list(linter_names))

    # Build the header
    header = "File".ljust(40) + " | "
    header += " | ".join(name.ljust(8) for name in linter_names)
    header_line = "=" * len(header)

    # Print the header
    click.echo("\n" + header_line)
    click.echo("LINTING RESULTS MATRIX")
    click.echo(header_line)
    click.echo(header)
    click.echo("-" * len(header))

    # Print each file's results
    all_passed = True
    failures_count = 0
    total_checks = 0

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
            total_checks += 1 if success is not None else 0

            if success is None:
                cell = "N/A".ljust(8)
            elif success:
                cell = linting.SUCCESS_EMOJI.ljust(8)
            else:
                cell = linting.FAILURE_EMOJI.ljust(8)
                failures_count += 1
                all_passed = False

            row += cell + " | "

        click.echo(row)

    # Print summary
    click.echo(header_line)
    if all_passed:
        click.echo(f"{linting.SUCCESS_EMOJI} ALL FILES PASSED ALL LINTERS")

    else:
        click.echo(
            f"{linting.FAILURE_EMOJI} {failures_count} FAILURES OUT OF {total_checks} CHECKS"
        )

    click.echo(header_line)

    return all_passed


def print_failure_details(all_results):
    """
    Print detailed information about linter failures.

    Args:
        all_results: Dictionary mapping file paths to lists of LinterResult objects
    """
    click.echo("\n" + "=" * linting.LINE_LENGTH)
    click.echo("DETAILED FAILURE INFORMATION")
    click.echo("=" * linting.LINE_LENGTH)

    found_failures = False

    for file_path, results in all_results.items():
        file_failures = [r for r in results if not r.success]

        if file_failures:
            found_failures = True
            click.echo(f"\nFile: {file_path}")
            click.echo("-" * linting.LINE_LENGTH)

            for result in file_failures:
                click.echo(f"\n{result.name} found issues:")
                click.echo(result.output.strip() or "No detailed output available")

    if not found_failures:
        click.echo("No linter failures to report.")


@cli.command()
@click.option("--list-linters", is_flag=True, help="List all available linters")
@click.option(
    "--check-installs", is_flag=True, help="Check if all linters are installed"
)
def info(list_linters, check_installs):
    """Show information about the linting script."""

    if list_linters:
        click.echo("Available linters:")
        for config in linting.get_linter_configs():
            options_str = " ".join(config.options) if config.options else ""
            click.echo(f"  - {config.name}: {' '.join(config.cmd_base)} {options_str}")

    elif check_installs:
        click.echo("Checking if linters are installed...")
        all_installed = True

        for config in linting.get_linter_configs():
            try:
                result = linting.subprocess.run(
                    [config.cmd_base[0], "--version"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0:
                    version = (
                        result.stdout.strip()
                        or result.stderr.strip()
                        or "Unknown version"
                    )
                    click.echo(f"✅ {config.name}: {version}")
                else:
                    click.echo(f"❌ {config.name}: Not installed or not working")
                    all_installed = False
            except Exception:
                click.echo(f"❌ {config.name}: Not installed")
                all_installed = False

        if all_installed:
            click.echo(f"\n{linting.SUCCESS_EMOJI} All linters are installed!")

        else:
            click.echo(
                f"\n{linting.FAILURE_EMOJI} Some linters are missing or not working."
            )

    else:
        click.echo(
            """
Code Linting Script

This script runs multiple linting tools on Python files:
- isort:   Sort imports
- black:   Format code
- mypy:    Type checking
- flake8:  Style guide enforcement
- pylint:  Static code analysis
- vulture: Dead code detection

Usage:
  python lint_cli.py lint <files> [options]
  python lint_cli.py info [options]
        """
        )


if __name__ == "__main__":

    sys.exit(cli())

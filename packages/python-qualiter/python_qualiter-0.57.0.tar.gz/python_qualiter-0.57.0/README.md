# Python Code Linting Tool

A modern Click-based CLI tool for running multiple linting tools on Python files with a clean visual output.

## Features

- **Multiple Linters**: Runs isort, black, mypy, flake8, pylint, and vulture in a single command
- **Visual Matrix**: Displays results in a clean matrix format with files as rows and linters as columns
- **Auto-fix Mode**: Automatically applies fixes for isort and black
- **Linter Selection**: Enable or disable specific linters as needed
- **Detailed Reporting**: Option to show detailed failure information
- **Installation Checking**: Verify if all required linters are installed
- **Recursive Search**: Automatically finds all Python files in directories and subdirectories (excluding virtual environments)

## Installation

### From PyPI

```bash
pip install python-qualiter
```

### From Source (Development)

1. Clone this repository:
   ```bash
   git clone https://gitlab.com/rbacovic/python-qualiter.git
   cd python-qualiter
   ```

2. Ensure you have Python 3.6+ and Poetry installed.

3. Install Poetry (if not already installed):
   ```bash
   # On Unix/macOS
   curl -sSL https://install.python-poetry.org | python3 -
   
   # On Windows (PowerShell)
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
   
   # Alternative: using pip
   pip install poetry
   ```

4. Install dependencies and activate virtual environment:
   ```bash
   poetry install
   poetry shell
   ```

## Usage

### Basic Linting

Run linting on Python files:

```bash
python-qualiter lint path/to/your/file.py
```

If you're developing and using Poetry:

```bash
poetry run python-qualiter lint path/to/your/file.py
```

Run on multiple files or using wildcards:

```bash
python-qualiter lint file1.py file2.py
python-qualiter lint folder/*.py
```

Run on a directory (recursively checks all Python files):

```bash
python-qualiter lint your_project_folder/
```

### Command Options

**Linting Command:**

```bash
python-qualiter lint [OPTIONS] FILES...
```

Options:
- `-v, --verbose`: Show detailed output during linting
- `-d, --details`: Show detailed failure messages after the results matrix
- `-e, --enable TEXT`: Enable only specific linters (can be used multiple times)
- `-x, --disable TEXT`: Disable specific linters (can be used multiple times)
- `-f, --fix`: Apply auto-fixes where possible (currently for isort and black)
- `-c, --config PATH`: Path to configuration file (for future implementation)
- `--help`: Show help message

**Info Command:**

```bash
python-qualiter info [OPTIONS]
```

Options:
- `--list-linters`: List all available linters
- `--check-installs`: Check if all linters are installed
- `--help`: Show help message

### Examples

Check all linters and show detailed errors:
```bash
python-qualiter lint my_file.py --details
```

Only run specific linters:
```bash
python-qualiter lint my_file.py --enable black --enable isort
```

Disable specific linters:
```bash
python-qualiter lint my_file.py --disable pylint
```

Auto-fix issues (where possible):
```bash
python-qualiter lint my_file.py --fix
```

Check if all linters are installed:
```bash
python-qualiter info --check-installs
```

Lint an entire project directory (recursively):
```bash
python-qualiter lint my_project/ --fix
```

### Development Usage with Poetry

If you're working on the project itself:

```bash
# Activate the Poetry virtual environment
poetry shell

# Run the tool directly
python-qualiter lint my_file.py

# Or run without activating the shell
poetry run python-qualiter lint my_file.py
```

## Output Format

The tool displays a matrix with files as rows and linters as columns:

```
===========================================================================
LINTING RESULTS MATRIX
===========================================================================
File                                     | black    | flake8   | isort    | mypy     | pylint   | vulture  
---------------------------------------------------------------------------
my_file.py                               | ✅       | ✅       | ✅       | ❌       | ✅       | ✅       
another_file.py                          | ✅       | ❌       | ✅       | ✅       | ❌       | ✅       
===========================================================================
❌ 3 FAILURES OUT OF 12 CHECKS
===========================================================================
```

If you use the `--details` option, you'll also see detailed failure information:

```
===========================================================================
DETAILED FAILURE INFORMATION
===========================================================================

File: my_file.py
---------------------------------------------------------------------------

mypy found issues:
my_file.py:42: error: Incompatible types in assignment (expression has type "str", variable has type "int")

File: another_file.py
---------------------------------------------------------------------------

flake8 found issues:
another_file.py:15:80: E501 line too long (88 > 79 characters)

pylint found issues:
another_file.py:27:0: C0103: Variable name "x" doesn't conform to snake_case naming style (invalid-name)
```

## Supported Linters

| Linter   | Purpose                 | Auto-fix Support |
|----------|-------------------------|-----------------|
| [isort](https://pycqa.github.io/isort/)    | Sort imports            | Yes             |
| [black](https://black.readthedocs.io/en/stable/)    | Format code             | Yes             |
| [mypy](https://mypy.readthedocs.io/en/stable/)     | Type checking           | No              |
| [flake8](https://flake8.pycqa.org/en/latest/)   | Style guide enforcement | No              |
| [pylint](https://pylint.pycqa.org/en/latest/)   | Static code analysis    | No              |
| [vulture](https://github.com/jendrikseipp/vulture)  | Dead code detection     | No              |

## Configuration

The tool includes default configurations for each linter in the `pyproject.toml` file. You can customize these settings by modifying the tool-specific sections:

- `[tool.black]` - Black formatter settings
- `[tool.isort]` - Import sorting configuration
- `[tool.mypy]` - Type checking options
- `[tool.pylint]` - Pylint analysis settings
- `[tool.ruff]` - Ruff linter configuration
- `[tool.vulture]` - Dead code detection settings

A future update will add support for custom configuration files using the `--config` option.

## Development

### Setting up Development Environment

1. Clone the repository:
   ```bash
   git clone https://gitlab.com/rbacovic/python-qualiter.git
   cd python-qualiter
   ```

2. Install Poetry and dependencies:
   ```bash
   poetry install
   ```

3. Activate the virtual environment:
   ```bash
   poetry shell
   ```

### Running Tests

```bash
# Run tests with Poetry
poetry run pytest -v

# Or with activated shell
pytest -v

# For more detailed test output
poetry run pytest -s -vv -x
```

### Building and Publishing

```bash
# Build the package
poetry build

# Publish to PyPI (requires proper credentials)
poetry publish

# Build and publish in one command
poetry publish --build
```

## Extending

To add a new linter:

1. Open `lint.py`
2. Add your linter configuration to the `get_linter_configs()` function:
   ```python
   LinterConfig(
       name="new_linter",
       cmd_base=["new_linter_command"],
       options=["--your-option", "value"]
   )
   ```
3. Add the new linter to the project dependencies in `pyproject.toml`

## Troubleshooting

If you encounter issues:

1. Make sure all linters are installed:
   ```bash
   python-qualiter info --check-installs
   ```

2. Run in verbose mode for more detailed output:
   ```bash
   python-qualiter lint my_file.py --verbose
   ```

3. If your file paths contain spaces, make sure to quote them:
   ```bash
   python-qualiter lint "path with spaces/my_file.py"
   ```

4. If no files are found, check that your patterns are correct:
   ```bash
   python-qualiter lint my_folder/*.py --verbose
   ```

5. For development issues with Poetry:
   ```bash
   # Clear Poetry cache
   poetry cache clear --all .
   
   # Rebuild lock file
   rm poetry.lock && poetry install
   
   # Check Poetry installation
   poetry --version
   ```

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Set up development environment with Poetry:
   ```bash
   poetry install
   poetry shell
   ```
4. Make your changes
5. Run tests to ensure they pass:
   ```bash
   poetry run pytest -v
   ```
6. Commit your changes (`git commit -m 'Add some amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request
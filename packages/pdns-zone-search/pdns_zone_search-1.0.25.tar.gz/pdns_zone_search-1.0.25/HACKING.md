# Developer Guide

This guide will help you set up a development environment, run tests, and build distribution packages for this project.

## Table of Contents
1. [Setting Up the Development Environment](#setup)
2. [Running Tests](#tests)
3. [Building Distribution Packages](#distribution)

<a id="setup"></a>
## 1. Setting Up the Development Environment

This project uses pip's editable install mode for development. This allows you to make changes to the source code without reinstalling the package.

### Prerequisites

- Python 3.11 or later
- pip (latest version recommended)
- git (for cloning the repository)

### Steps to Set Up

1. Clone the repository:
```shell script
git clone <repository-url>
   cd <repository-directory>
```


2. Create and activate a virtual environment (optional but recommended):
```shell script
python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
```


3. Install the package in editable mode with development dependencies:
```shell script
pip install -e ".[dev]"
```


   This command:
   - Installs the package in editable mode (`-e`)
   - Installs all development dependencies defined in the `[dev]` extra in pyproject.toml

### What Does Editable Mode Do?

When you install a package with `-e`, pip creates a special link to your source code instead of copying files into the site-packages directory. This means:

- Changes to your source code take effect immediately without reinstalling
- You can test code changes quickly
- Import statements in your code work exactly as they would in a normal installation

### Verifying the Installation

To verify that your editable installation works, you can run Python and import your package:

```python
import your_package_name
print(your_package_name.__version__)
```


<a id="tests"></a>
## 2. Running Tests

This project uses pytest for testing. The development dependencies (`[dev]`) you installed earlier include pytest and pytest-cov for code coverage.

### Running Basic Tests

To run the basic test suite:

```shell script
pytest
```


This will discover and run all test files in the project (files that match the pattern `test_*.py`).

### Running Tests with Coverage

To run tests with code coverage:

```shell script
pytest --cov=your_package_name
```


Replace `your_package_name` with the actual name of your package.

### Coverage Reports

You can generate different types of coverage reports:

1. Terminal report (default):
```shell script
pytest --cov=your_package_name
```


2. HTML report (provides detailed interactive coverage information):
```shell script
pytest --cov=your_package_name --cov-report=html
```

   This generates a report in the `htmlcov/` directory. Open `htmlcov/index.html` in a browser to view it.

3. XML report (useful for CI systems):
```shell script
pytest --cov=your_package_name --cov-report=xml
```


4. Multiple report types simultaneously:
```shell script
pytest --cov=your_package_name --cov-report=term --cov-report=html
```


### Branch Coverage

For more comprehensive coverage testing, you can enable branch coverage:

```shell script
pytest --cov=your_package_name --cov-branch
```


This checks whether each possible branch in the code has been executed, rather than just each line.

### Running Specific Tests

To run a specific test file:
```shell script
pytest tests/test_specific_file.py
```


To run a specific test function:
```shell script
pytest tests/test_file.py::test_function_name
```


To run tests matching a pattern:
```shell script
pytest -k "pattern"
```


<a id="distribution"></a>
## 3. Building Distribution Packages

This project uses flit-core as a build backend (specified in pyproject.toml), but to build distribution packages, you'll need to install the full flit package.

### Installing Flit

The full flit package provides the command-line interface needed to build and publish packages:

```shell script
pip install flit
```


Note: `flit-core` (which might be installed as part of your dependencies) does not include the command-line tools.

### Building Packages

To build distribution packages:

```shell script
flit build
```


This command:
- Reads your `pyproject.toml` configuration
- Creates a source distribution (`.tar.gz`) and a wheel (`.whl`) in the `dist/` directory

### Inspecting Built Packages

You can see the files that were included in your packages by:

1. Looking at the contents of the `dist/` directory:
```shell script
ls -l dist/
```


2. Examining the contents of the wheel (it's just a ZIP file):
```shell script
unzip -l dist/your_package-x.y.z-py3-none-any.whl
```


### Publishing Packages

If you have permission to publish this package to PyPI:

```shell script
flit publish
```


For a test run without actually uploading:

```shell script
flit publish --repository testpypi
```


### Alternative: Using Python Build

If you prefer not to install the full flit package, you can use Python's `build` module:

```shell script
pip install build
python -m build
```


This also builds both source and wheel distributions in the `dist/` directory.

## Additional Development Tips

### Project Structure

The basic structure of this project is:

```
project_root/
├── your_package_name/      # Main package source code
│   ├── __init__.py
│   └── ...
├── tests/                  # Test files
│   ├── __init__.py
│   └── test_*.py
├── pyproject.toml          # Project configuration
└── README.md               # Project documentation
```


### Managing Dependencies

All dependencies are specified in `pyproject.toml`:

- `dependencies` - Regular dependencies needed for the package to function
- `[project.optional-dependencies]` - Optional dependency sets including:
  - `dev` - Development tools (pytest, etc.)
  - Other optional feature sets if defined

### Pre-commit Hooks

If this project uses pre-commit hooks, you can install them with:

```shell script
pre-commit install
```


This will ensure that code quality checks run automatically before each commit.

### Code Formatting

This project may use Black for code formatting. To format your code:

```shell script
black your_package_name tests
```


### Type Checking

If this project uses type annotations, you can check them with mypy:

```shell script
mypy your_package_name
```


### Documentation

To build documentation (if the project uses Sphinx):

```shell script
cd docs
make html
```


# Gradle-Bio

A collection of Android project snippets and templates.

## Installation

```bash
pip install gradle-bio
```

## Usage

After installation, all Android project files will be directly available in your Python environment's site-packages directory. You can access them in two ways:

### 1. Direct File Access

The Android project files are installed directly in your virtual environment at:
```
<your-venv-path>/lib/python<version>/site-packages/gradle_bio_projects/
```

You can navigate to this directory and use the files directly.

### 2. Using the Python API

```python
import gradle_bio

# Get the path to the Android project files
projects_path = gradle_bio.get_projects_path()
print(f"Android project files are located at: {projects_path}")

# List all available projects
projects = gradle_bio.list_projects()
print(projects)

# Get the path to a specific project
from gradle_bio.utils import get_project_dir
project_dir = get_project_dir("5 intents")
print(project_dir)
```

### 3. Command Line Interface

You can also use the command line interface to explore the projects:

```bash
# Show all available projects and their location
python -m gradle_bio

# Show the structure of a specific project
python -m gradle_bio --structure "5 intents"

# Show the path to the installed project files
python -m gradle_bio --path
```

## Project Structure

This package contains the following Android project directories:

- 1 check
- 2 alert
- 3 progress
- 4 canvas
- 5 intents
- 6 Animations
- 7 Menu
- 8 Frag
- 9 shared
- 10 Database

All files within these directories are preserved with their original structure and content.

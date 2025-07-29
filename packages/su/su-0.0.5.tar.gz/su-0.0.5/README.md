# su
Debugging tools

To install:	```pip install su```

## Overview

The `su` package provides a set of utilities designed to facilitate debugging Python applications. It includes functionality for managing and configuring the Python debugger (`pdb`), handling project paths, and dynamically adding debugging breakpoints. The package leverages environment variables and file manipulation to enhance the debugging experience.

## Features

- **Project Path Configuration**: Automatically sets up a project path using an environment variable `PY_PROJ_FOLDER`.
- **PDB Configuration Management**: Allows for the initialization and dynamic modification of `.pdbrc` files, which are used to configure the Python debugger (`pdb`).
- **Breakpoint Management**: Facilitates adding breakpoints to the code dynamically.
- **Debugging Shortcuts**: Provides aliases and shortcuts for common debugging tasks within `pdb`.

## Usage

### Initialization

To start using the debugging tools, you first need to initialize the `.pdbrc` file in your project directory:

```python
from su import init
init()
```

This will create a `.pdbrc` file with predefined debugging commands.

### Adding Custom Commands

You can add custom commands or configurations to the `.pdbrc` file:

```python
from su import add
add('alias my_alias print("Hello, Debugging World!")')
```

### Initializing and Adding in One Step

For convenience, you can initialize and add commands in one step:

```python
from su import init_and_add
init_and_add('alias my_alias print("Hello, Debugging World!")')
```

### Printing the Current `.pdbrc` Configuration

To see the current configuration of your `.pdbrc` file:

```python
from su import print_pdbrc
print_pdbrc()
```

### Working with Breakpoints

To add a breakpoint programmatically:

```python
from su import add_breakpoint
add_breakpoint('my_script.py', lineno=25)
```

### Using the Bugger Class

The `Bugger` class provides methods to manage debugging configurations relative to a specific project path:

```python
from su import Bugger

# Create a Bugger instance for the current project
bugger = Bugger(relative_root='src')

# Initialize .pdbrc in the project
bugger.init()

# Add a breakpoint in 'example.py' at line 10
bugger.add_breakpoint('example.py', lineno=10)

# Print the current .pdbrc file
bugger.print_pdbrc()
```

## Installation

To install the `su` package, run the following command:

```bash
pip install su
```

Ensure that your environment is properly configured with the necessary paths and variables, such as `PY_PROJ_FOLDER`, to use all features of the `su` package effectively.
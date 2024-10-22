# omnicli (sdk-python)

Python SDK for building Omni commands.

## Overview

`omnicli` is a Python package that provides functionality to help build commands that will be executed by Omni. It offers various utilities and helpers that make it easier to work with Omni's features from within Python.

## Installation

```bash
pip install omnicli
```

## Features

### Argument Parsing

The SDK can read omni-parsed arguments from environment variables into a familiar Python format:

```python
from omnicli import parse_args

try:
    args = parse_args()

    # Access your command's arguments as attributes
    if args.verbose:
        print("Verbose mode enabled")

    if args.input_file:
        print(f"Processing file: {args.input_file}")

except ArgListMissingError:
    print("No Omni CLI arguments found. Make sure 'argparser: true' is set for your command.")
```

The resulting arguments can be used the same as they would have been when coming from using 'argparse.ArgumentParser().parse_args()', as they will be returned as an 'argparse.Namespace' object, with their values in the expected types.

### Integration with omni

The argument parser of omni needs to be enabled for your command. This can be done as part of the [metadata](https://omnicli.dev/reference/custom-commands/path/metadata-headers) of your command, which can either be provided as a separate file:

```
your-repo
└── commands
    ├── your-command.py
    └── your-command.metadata.yaml
```

```yaml
# your-command.metadata.yaml
argparser: true
```

Or as part of your python command headers:

```python
# your-command.py
#
# argparser: true

import os
...
```

## Requirements

- Python 3.8 or higher
- No additional dependencies required

## Development

To set up for development:

```bash
# Clone the repository
git clone https://github.com/omnicli/sdk-python.git
cd omnicli

# Install dependencies
omni up

# Run tests
omni test
```

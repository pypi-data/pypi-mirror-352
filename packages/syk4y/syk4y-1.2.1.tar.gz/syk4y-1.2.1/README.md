# Syk4y utility package

A simple utility package for organization Syk4y

## Installation

```bash
pip install syk4y
```

## Usage

```python
from syk4y.printer import inspect

# Example usage
data = {'a': 1, 'b': [2, 3], 'c': {'d': 4}}
inspect(data)
```

## Features
- Recursively inspects and prints the structure of any Python variable
- Supports lists, tuples, dicts, sets, namedtuples, dataclasses, enums, tensors (PyTorch), arrays (NumPy), and more
- Handles cyclic references and max recursion depth
- Colorful output (with `termcolor`)
- Designed for debugging and data exploration

## License

This project is licensed under the MIT License - see the LICENSE file for details.
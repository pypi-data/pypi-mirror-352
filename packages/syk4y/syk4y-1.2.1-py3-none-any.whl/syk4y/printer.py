from typing import Any, Set
import sys
from collections import namedtuple
import uuid

try:
    import torch # type: ignore
except ImportError:
    torch = None

try:
    import numpy as np # type: ignore
except ImportError:
    np = None

try:
    from termcolor import colored
except ImportError:
    def colored(text, *args, **kwargs):
        return text

def format_memory_size(size_bytes: int) -> str:
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

def inspect(
    var: Any,
    prefix: str = "Variable",
    indent: int = 1,
    max_depth: int = 10,
    file=sys.stdout,
    visited: Set[int] = None,
    _current_depth: int = 0
) -> None:
    """
    Recursively prints the structure of a variable with enhanced formatting and type handling.
    Supports tensors, arrays, lists, tuples, dicts, sets, named tuples, and more.

    Args:
        var: The variable to analyze
        indent: Current indentation level for formatting
        prefix: Label for the current variable
        max_depth: Maximum recursion depth to prevent infinite recursion
        file: Output file or stream (default: sys.stdout)
        visited: Set of object IDs to detect cyclic references
        _current_depth: Internal depth counter
    """
    if visited is None:
        visited = set()

    indent_str = "  " * indent
    var_id = id(var)

    # Handle cyclic references
    if var_id in visited:
        print(colored(f"{indent_str}{prefix}: <Cyclic Reference>", "red"), file=file)
        return

    # Stop if max depth is reached
    if _current_depth > max_depth:
        print(colored(f"{indent_str}{prefix}: <Max Depth Reached>", "yellow"), file=file)
        return

    # Add current object to visited set
    if isinstance(var, (list, tuple, dict, set)):
        visited.add(var_id)

    # Handle None
    if var is None:
        print(colored(f"{indent_str}{prefix}: None", "cyan"), file=file)
        return

    # Get type name
    type_name = type(var).__name__

    # Helper to print type info
    def print_type_info(shape=None, dtype=None, extra=""):
        mem_size = ""
        if shape is not None and dtype is not None:
            try:
                item_size = np.dtype(dtype).itemsize if np is not None else 8
                total_elements = 1
                for dim in shape:
                    total_elements *= dim
                mem_size = f", memory={format_memory_size(total_elements * item_size)}"
            except Exception:
                pass
        shape_str = f"shape={tuple(shape)}" if shape is not None else ""
        dtype_str = f", dtype={str(dtype)}" if dtype is not None else ""
        print(colored(f"{indent_str}{prefix}: {type_name}({shape_str}{dtype_str}{mem_size}{extra})", "green"), file=file)

    # Handle PyTorch Tensor
    if torch is not None and isinstance(var, torch.Tensor):
        shape = tuple(var.shape)
        dtype = str(var.dtype)
        device = str(var.device)
        print(colored(f"{indent_str}{prefix}: Tensor(shape={shape}, dtype={dtype}, device={device})", "green"), file=file)
        return

    # Handle NumPy Array
    elif np is not None and isinstance(var, np.ndarray):
        shape = tuple(var.shape)
        dtype = str(var.dtype)
        print(colored(f"{indent_str}{prefix}: ndarray(shape={shape}, dtype={dtype})", "green"), file=file)
        return

    # Handle List
    elif isinstance(var, list):
        # Check if all elements are tensors or arrays for concise summary
        is_tensor_list = torch is not None and all(isinstance(item, torch.Tensor) for item in var)
        is_array_list = np is not None and all(isinstance(item, np.ndarray) for item in var)
        if is_tensor_list:
            print(colored(f"{indent_str}{prefix}: List(length={len(var)})", "magenta"), file=file)
            for i, item in enumerate(var):
                shape = tuple(item.shape)
                dtype = str(item.dtype)
                device = str(item.device)
                print(colored(f"{indent_str}  [{i}]: Tensor(shape={shape}, dtype={dtype}, device={device})", "green"), file=file)
            return
        elif is_array_list:
            print(colored(f"{indent_str}{prefix}: List(length={len(var)})", "magenta"), file=file)
            for i, item in enumerate(var):
                shape = tuple(item.shape)
                dtype = str(item.dtype)
                print(colored(f"{indent_str}  [{i}]: ndarray(shape={shape}, dtype={dtype})", "green"), file=file)
            return
        # Default recursive behavior, but suppress values for tensors/arrays
        print(colored(f"{indent_str}{prefix}: List(length={len(var)})", "magenta"), file=file)
        for i, item in enumerate(var):
            if (torch is not None and isinstance(item, torch.Tensor)):
                shape = tuple(item.shape)
                dtype = str(item.dtype)
                device = str(item.device)
                print(colored(f"{indent_str}  [{i}]: Tensor(shape={shape}, dtype={dtype}, device={device})", "green"), file=file)
            elif (np is not None and isinstance(item, np.ndarray)):
                shape = tuple(item.shape)
                dtype = str(item.dtype)
                print(colored(f"{indent_str}  [{i}]: ndarray(shape={shape}, dtype={dtype})", "green"), file=file)
            else:
                inspect(item, indent + 1, f"[{i}]", max_depth, file, visited, _current_depth + 1)

    # Handle Tuple
    elif isinstance(var, tuple):
        is_namedtuple = isinstance(var, tuple) and hasattr(var, "_fields")
        tuple_type = "NamedTuple" if is_namedtuple else "Tuple"
        extra = f", fields={var._fields}" if is_namedtuple else ""
        print(colored(f"{indent_str}{prefix}: {tuple_type}(length={len(var)}{extra})", "magenta"), file=file)
        for i, item in enumerate(var):
            key = var._fields[i] if is_namedtuple else f"[{i}]"
            inspect(item, indent + 1, key, max_depth, file, visited, _current_depth + 1)

    # Handle Dictionary
    elif isinstance(var, dict):
        print(colored(f"{indent_str}{prefix}: Dict(keys={len(var)})", "magenta"), file=file)
        for key, value in sorted(var.items(), key=str):
            inspect(value, indent + 1, f"[{key}]", max_depth, file, visited, _current_depth + 1)

    # Handle Set and FrozenSet
    elif isinstance(var, (set, frozenset)):
        set_type = "FrozenSet" if isinstance(var, frozenset) else "Set"
        print(colored(f"{indent_str}{prefix}: {set_type}(length={len(var)})", "magenta"), file=file)
        for i, item in enumerate(sorted(var, key=str)):
            inspect(item, indent + 1, f"[item{i}]", max_depth, file, visited, _current_depth + 1)

    # Handle bytes and bytearray
    elif isinstance(var, (bytes, bytearray)):
        value_preview = var[:16].hex() + ("..." if len(var) > 16 else "")
        print(colored(f"{indent_str}{prefix}: {type_name}(length={len(var)}, hex={value_preview})", "cyan"), file=file)

    # Handle dataclasses
    elif hasattr(var, "__dataclass_fields__"):
        from dataclasses import fields
        print(colored(f"{indent_str}{prefix}: Dataclass({type_name})", "magenta"), file=file)
        for f in fields(var):
            inspect(getattr(var, f.name), indent + 1, f.name, max_depth, file, visited, _current_depth + 1)

    # Handle Enum
    elif hasattr(var, "__class__") and hasattr(var.__class__, "__mro__") and any(b.__name__ == "Enum" for b in var.__class__.__mro__):
        print(colored(f"{indent_str}{prefix}: Enum({var.name}={var.value})", "cyan"), file=file)

    # Handle range
    if isinstance(var, range):
        print(colored(f"{indent_str}{prefix}: range({var.start}, {var.stop}, {var.step})", "cyan"), file=file)
        return

    # Handle generators and iterators 
    elif hasattr(var, "__iter__") and not isinstance(var, (str, bytes, bytearray, list, tuple, dict, set, frozenset, range, np.ndarray if np else tuple, torch.Tensor if torch else tuple)):
        try:
            import itertools
            preview = list(itertools.islice(var, 5))
            print(colored(f"{indent_str}{prefix}: {type_name}(iterator, preview={preview})", "cyan"), file=file)
        except Exception:
            print(colored(f"{indent_str}{prefix}: {type_name}(iterator)", "cyan"), file=file)

    # Handle functions, modules, file-like objects
    if hasattr(var, "__call__"):
        print(colored(f"{indent_str}{prefix}: Function({getattr(var, '__name__', type_name)})", "yellow"), file=file)
        return
    if hasattr(var, "read") and hasattr(var, "write"):
        print(colored(f"{indent_str}{prefix}: FileLike({getattr(var, 'name', type_name)})", "yellow"), file=file)
        return
    if type_name == "module":
        print(colored(f"{indent_str}{prefix}: Module({getattr(var, '__name__', type_name)})", "yellow"), file=file)
        return

    # Handle Exception objects
    if isinstance(var, BaseException):
        print(colored(f"{indent_str}{prefix}: Exception({type_name}, args={var.args})", "red"), file=file)
        return

    # Remove from visited set after processing
    visited.discard(var_id)

    # Handle memoryview
    if isinstance(var, memoryview):
        print(colored(f"{indent_str}{prefix}: memoryview(length={len(var)})", "cyan"), file=file)
        return

    # Handle user-defined objects with __dict__ or __slots__
    elif hasattr(var, "__dict__") or hasattr(var, "__slots__"):
        # Check if there are any attributes to show
        has_attrs = False
        if hasattr(var, "__dict__") and var.__dict__:
            has_attrs = True
        if hasattr(var, "__slots__"):
            for slot in var.__slots__:
                if hasattr(var, slot):
                    has_attrs = True
                    break
        if has_attrs:
            print(colored(f"{indent_str}{prefix}: Object({type_name})", "yellow"), file=file)
            # Inspect __dict__ attributes
            if hasattr(var, "__dict__"):
                for key, value in sorted(var.__dict__.items()):
                    inspect(value, indent + 1, key, max_depth, file, visited, _current_depth + 1)
            # Inspect __slots__ attributes
            if hasattr(var, "__slots__"):
                for slot in var.__slots__:
                    if hasattr(var, slot):
                        inspect(getattr(var, slot), indent + 1, slot, max_depth, file, visited, _current_depth + 1)
            return
        # else fall through to fallback

    # Fallback for unhandled types
    if type_name == "Tensor":
        shape = getattr(var, 'shape', None)
        dtype = getattr(var, 'dtype', None)
        device = getattr(var, 'device', None)
        shape_str = f"shape={tuple(shape)}" if shape is not None else ""
        dtype_str = f", dtype={str(dtype)}" if dtype is not None else ""
        device_str = f", device={str(device)}" if device is not None else ""
        print(colored(f"{indent_str}{prefix}: Tensor({shape_str}{dtype_str}{device_str})", "green"), file=file)
        return
    print(colored(f"{indent_str}{prefix}: {type_name}", "yellow"), file=file)
    return

# Example usage
if __name__ == "__main__":
    # Create sample data
    Point = namedtuple("Point", ["x", "y"])
    sample_data = {
        "tensor": torch.tensor([[1, 2], [3, 4]]) if torch else None,
        "array": np.array([1, 2, 3]) if np else None,
        "list": [1, [2, 3], {"a": 4}],
        "tuple": (5, Point(6, 7)),
        "set": {8, 9},
        "complex": 3 + 4j,
        "string": "example"
    }

    inspect(sample_data, prefix="SampleData")
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
    if visited is None:
        visited = set()
    indent_str = "  " * indent
    var_id = id(var)
    if var_id in visited:
        print(colored(f"{indent_str}{prefix}: <Cyclic Reference>", "red"), file=file)
        return
    if _current_depth > max_depth:
        print(colored(f"{indent_str}{prefix}: <Max Depth Reached>", "yellow"), file=file)
        return
    if isinstance(var, (list, tuple, dict, set, frozenset)):
        visited.add(var_id)
    if var is None:
        print(colored(f"{indent_str}{prefix}: None", "cyan"), file=file)
        return
    type_name = type(var).__name__
    # PyTorch Tensor
    if torch is not None and isinstance(var, torch.Tensor):
        size = var.element_size() * var.nelement() if hasattr(var, 'element_size') and hasattr(var, 'nelement') else None
        size_str = f", size={format_memory_size(size)}" if size else ""
        print(colored(f"{indent_str}{prefix}: Tensor(shape={tuple(var.shape)}, dtype={str(var.dtype)}, device={str(var.device)}{size_str})", "green"), file=file)
        return
    # NumPy Array
    if np is not None and isinstance(var, np.ndarray):
        size = var.nbytes if hasattr(var, 'nbytes') else None
        size_str = f", size={format_memory_size(size)}" if size else ""
        print(colored(f"{indent_str}{prefix}: ndarray(shape={tuple(var.shape)}, dtype={str(var.dtype)}{size_str})", "green"), file=file)
        return
    # List
    if isinstance(var, list):
        is_tensor_list = torch is not None and all(isinstance(item, torch.Tensor) for item in var)
        is_array_list = np is not None and all(isinstance(item, np.ndarray) for item in var)
        print(colored(f"{indent_str}{prefix}: List(length={len(var)})", "magenta"), file=file)
        if len(var) > 20:
            print(colored(f"{indent_str}  <List too long to display>", "yellow"), file=file)
            return
        for i, item in enumerate(var):
            if is_tensor_list:
                print(colored(f"{indent_str}  [{i}]: Tensor(shape={tuple(item.shape)}, dtype={str(item.dtype)}, device={str(item.device)})", "green"), file=file)
            elif is_array_list:
                print(colored(f"{indent_str}  [{i}]: ndarray(shape={tuple(item.shape)}, dtype={str(item.dtype)})", "green"), file=file)
            elif torch is not None and isinstance(item, torch.Tensor):
                print(colored(f"{indent_str}  [{i}]: Tensor(shape={tuple(item.shape)}, dtype={str(item.dtype)}, device={str(item.device)})", "green"), file=file)
            elif np is not None and isinstance(item, np.ndarray):
                print(colored(f"{indent_str}  [{i}]: ndarray(shape={tuple(item.shape)}, dtype={str(item.dtype)})", "green"), file=file)
            else:
                inspect(item, f"[{i}]", indent + 1, max_depth, file, visited, _current_depth + 1)
        return
    # Tuple (including namedtuple)
    if isinstance(var, tuple):
        is_namedtuple = hasattr(var, "_fields")
        tuple_type = "NamedTuple" if is_namedtuple else "Tuple"
        extra = f", fields={var._fields}" if is_namedtuple else ""
        print(colored(f"{indent_str}{prefix}: {tuple_type}(length={len(var)}{extra})", "magenta"), file=file)
        for i, item in enumerate(var):
            key = var._fields[i] if is_namedtuple else f"[{i}]"
            inspect(item, key, indent + 1, max_depth, file, visited, _current_depth + 1)
        return
    # Dict
    if isinstance(var, dict):
        print(colored(f"{indent_str}{prefix}: Dict(keys={len(var)})", "magenta"), file=file)
        if len(var) > 20:
            print(colored(f"{indent_str}  <Dict too large to display>", "yellow"), file=file)
            return
        for key, value in sorted(var.items(), key=str):
            inspect(value, f"[{key}]", indent + 1, max_depth, file, visited, _current_depth + 1)
        return
    # Set/FrozenSet
    if isinstance(var, (set, frozenset)):
        set_type = "FrozenSet" if isinstance(var, frozenset) else "Set"
        print(colored(f"{indent_str}{prefix}: {set_type}(length={len(var)})", "magenta"), file=file)
        if len(var) > 20:
            print(colored(f"{indent_str}  <Set too large to display>", "yellow"), file=file)
            return
        for i, item in enumerate(sorted(var, key=str)):
            inspect(item, f"[item{i}]", indent + 1, max_depth, file, visited, _current_depth + 1)
        return
    # bytes/bytearray
    if isinstance(var, (bytes, bytearray)):
        value_preview = var[:16].hex() + ("..." if len(var) > 16 else "")
        print(colored(f"{indent_str}{prefix}: {type_name}(length={len(var)}, hex={value_preview})", "cyan"), file=file)
        return
    # dataclass
    if hasattr(var, "__dataclass_fields__"):
        from dataclasses import fields
        print(colored(f"{indent_str}{prefix}: Dataclass({type_name})", "magenta"), file=file)
        for f in fields(var):
            inspect(getattr(var, f.name), f.name, indent + 1, max_depth, file, visited, _current_depth + 1)
        return
    # Enum
    if hasattr(var, "__class__") and hasattr(var.__class__, "__mro__") and any(b.__name__ == "Enum" for b in var.__class__.__mro__):
        print(colored(f"{indent_str}{prefix}: Enum({var.name}={var.value})", "cyan"), file=file)
        return
    # range
    if isinstance(var, range):
        print(colored(f"{indent_str}{prefix}: range({var.start}, {var.stop}, {var.step})", "cyan"), file=file)
        return
    # generator/iterator
    if hasattr(var, "__iter__") and not isinstance(var, (str, bytes, bytearray, list, tuple, dict, set, frozenset, range, *(tuple([np.ndarray] if np else [])), *(tuple([torch.Tensor] if torch else [])))):
        try:
            import itertools
            preview = list(itertools.islice(var, 5))
            print(colored(f"{indent_str}{prefix}: {type_name}(iterator, preview={preview})", "cyan"), file=file)
        except Exception:
            print(colored(f"{indent_str}{prefix}: {type_name}(iterator)", "cyan"), file=file)
        return
    # function/callable
    if hasattr(var, "__call__"):
        print(colored(f"{indent_str}{prefix}: Function({getattr(var, '__name__', type_name)})", "yellow"), file=file)
        return
    # file-like
    if hasattr(var, "read") and hasattr(var, "write"):
        print(colored(f"{indent_str}{prefix}: FileLike({getattr(var, 'name', type_name)})", "yellow"), file=file)
        return
    # module
    if type_name == "module":
        print(colored(f"{indent_str}{prefix}: Module({getattr(var, '__name__', type_name)})", "yellow"), file=file)
        return
    # Exception
    if isinstance(var, BaseException):
        print(colored(f"{indent_str}{prefix}: Exception({type_name}, args={var.args})", "red"), file=file)
        return
    # memoryview
    if isinstance(var, memoryview):
        print(colored(f"{indent_str}{prefix}: memoryview(length={len(var)})", "cyan"), file=file)
        return
    # user-defined object with __dict__ or __slots__
    if hasattr(var, "__dict__") or hasattr(var, "__slots__"):
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
            if hasattr(var, "__dict__"):
                for key, value in sorted(var.__dict__.items()):
                    inspect(value, key, indent + 1, max_depth, file, visited, _current_depth + 1)
            if hasattr(var, "__slots__"):
                for slot in var.__slots__:
                    if hasattr(var, slot):
                        inspect(getattr(var, slot), slot, indent + 1, max_depth, file, visited, _current_depth + 1)
            return
    # Print value for small/primitive types
    if isinstance(var, (int, float, bool)):
        print(colored(f"{indent_str}{prefix}: {type_name} = {var}", "yellow"), file=file)
        return
    if isinstance(var, str):
        if len(var) > 80:
            print(colored(f"{indent_str}{prefix}: str(length={len(var)}) = '{var[:77]}...'", "yellow"), file=file)
        else:
            print(colored(f"{indent_str}{prefix}: str = '{var}'", "yellow"), file=file)
        return
    # fallback
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

    inspect(sample_data, "SampleData")
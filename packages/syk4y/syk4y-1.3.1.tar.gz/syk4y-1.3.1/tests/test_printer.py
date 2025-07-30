import io
import types
import pytest
from collections import namedtuple
from syk4y.printer import inspect

def get_output(var, **kwargs):
    buf = io.StringIO()
    inspect(var, file=buf, **kwargs)
    return buf.getvalue()

def test_primitive_types():
    assert 'int(42)' in get_output(42)
    assert 'float(3.14)' in get_output(3.14)
    assert 'bool(True)' in get_output(True)
    assert "str('hello')" in get_output('hello')

def test_list_tuple_dict_set():
    assert 'List(length=2)' in get_output([1,2])
    assert 'Tuple(length=2)' in get_output((1,2))
    assert 'Dict(keys=2)' in get_output({'a':1,'b':2})
    assert 'Set(length=2)' in get_output({1,2})

def test_namedtuple():
    Point = namedtuple('Point', ['x','y'])
    out = get_output(Point(1,2))
    assert 'NamedTuple' in out and 'fields' in out

def test_bytes_bytearray():
    assert 'bytes(length=4' in get_output(b'abcd')
    assert 'bytearray(length=4' in get_output(bytearray(b'abcd'))

def test_exception():
    out = get_output(ValueError('fail'))
    assert 'Exception(ValueError' in out and 'fail' in out

def test_object_with_slots_and_dict():
    class A:
        __slots__ = ['x']
        def __init__(self): self.x = 1
    class B:
        def __init__(self): self.y = 2
    assert 'Object(A)' in get_output(A())
    assert 'Object(B)' in get_output(B())

def test_function_module_filelike():
    def f(): pass
    assert 'Function(f)' in get_output(f)
    import sys
    assert 'Module(sys)' in get_output(sys)
    class F:
        def read(self): pass
        def write(self): pass
        name = 'fakefile'
    assert 'FileLike(fakefile)' in get_output(F())

def test_iterators_generators():
    it = iter([1,2,3])
    out = get_output(it)
    assert 'iterator' in out
    def gen(): yield 1
    assert 'iterator' in get_output(gen())

def test_fallback():
    class Weird:
        pass
    assert 'Weird(' in get_output(Weird())

def test_memoryview():
    mv = memoryview(b'hello')
    assert 'memoryview(length=5)' in get_output(mv)

def test_cyclic_references():
    a = []
    a.append(a)
    out = get_output(a)
    assert '<Cyclic Reference>' in out

def test_max_depth():
    nested = {}
    current = nested
    for i in range(11):
        current['next'] = {}
        current = current['next']
    out = get_output(nested, max_depth=10)
    assert '<Max Depth Reached>' in out

def test_dataclass():
    from dataclasses import dataclass

    @dataclass
    class Example:
        x: int
        y: str

    out = get_output(Example(1, 'test'))
    assert 'Dataclass(Example)' in out

def test_enum():
    from enum import Enum

    class Color(Enum):
        RED = 1
        GREEN = 2

    out = get_output(Color.RED)
    assert 'Enum(RED=1)' in out

def test_range():
    r = range(1, 10, 2)
    assert 'range(1, 10, 2)' in get_output(r)

def test_iterator_preview():
    it = iter([1, 2, 3, 4, 5, 6])
    out = get_output(it)
    assert 'iterator, preview=[1, 2, 3, 4, 5]' in out

def test_fallback_unhandled():
    class Unhandled:
        pass

    out = get_output(Unhandled())
    assert 'Unhandled(' in out

from typing import final

from observables.observable_object import ComputedProperty, Value
from observables.typed_wrappers import DictLikeWrapper, Int, ObjectWrapper, String


def test_int():
    b = Value(3)
    a = Int(4) + 5 + b
    assert a.value == 12
    b.value += 3
    assert a.value == 15
    assert b < a
    assert a < a + 1


def test_float():
    b = Value(2)
    a = Int(6) / b
    assert abs(a.value - 3) <= 1e-8
    b.value = 3
    assert abs(a.value - 2) <= 1e-8


def test_string():
    a = Value(99)
    a_num = Int(a)
    st = String() + "There are " + a_num.str() + " bottles of beer"
    assert "99" in st
    a.value //= 2
    assert "49" in st


def test_dict_wrapper():
    a = Value(99)
    b = ComputedProperty(lambda: a.value // 3)
    d = DictLikeWrapper(dict[str, object], a=a, b=b, c=40)
    assert d["b"] == 33
    assert d["c"] == 40
    d["u"] = 50
    assert d["u"] == 50
    a.value += 33
    assert d["b"] == 44
    d["c"] = a
    assert d["c"] == 132

    d["v"] = lambda: a.value // 2
    assert d["v"] == 66
    d["w"] = lambda: lambda: "xyz"
    callback = d["w"]
    assert callable(callback) and callback() == "xyz"


def test_object_wrapper():
    a = Value(99)
    b = ComputedProperty(lambda: a.value // 3)

    @final
    class Scratchpad:
        def __init__(self, a: int, b: int, c: int):
            self.a = a
            self.b = b
            self.c = c

    d = ObjectWrapper(Scratchpad, a=a, b=b, c=40)
    assert d.b == 33
    assert d.c == 40
    d.u = 50
    assert d.u == 50
    a.value += 33
    assert d.b == 44
    d.c = a
    assert d.c == 132

    d.v = lambda: a.value // 2
    assert d.v == 66
    d.w = lambda: lambda: "xyz"
    callback = d.w
    assert callable(callback) and callback() == "xyz"


def test_wrapped_computed():
    v = Value(5)
    d = DictLikeWrapper(dict[str, int])
    d["a"] = lambda: v.value + 10
    assert d["a"] == 15
    v.value += 3
    assert d["a"] == 18

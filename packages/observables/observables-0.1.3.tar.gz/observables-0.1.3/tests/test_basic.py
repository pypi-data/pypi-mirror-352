import gc
from typing import Any, Callable
from weakref import finalize

from observables.observable_object import ComputedProperty, ObservableList, Value


def test_observation():
    v = Value(2)
    q: list[int] = []
    token = v.observe(q.append)

    v.value += 5
    assert q == [7]
    v.value -= 3
    assert q == [7, 4]

    token.destroy()
    v.value += 5
    assert q == [7, 4]  # did not update because the token was destroyed


def test_computed():
    v = Value(2)
    w = Value(3)
    summ = ComputedProperty(lambda: v.value + w.value, [v, w])

    assert summ.value == 5
    v.value += 2
    assert summ.value == 7
    w.value -= 3
    assert summ.value == 4


def test_dependency_resolution():
    a = Value(2)
    b = ComputedProperty(lambda: a.value + 1)

    assert b.value == 3
    a.value += 1
    assert b.value == 4


def test_deep_computed():
    a = Value(2)
    b = Value(3)
    c = ComputedProperty(lambda: a.value + b.value)
    d = ComputedProperty(lambda: c.value * 2)

    assert d.value == 10
    assert len(list(c.dependencies())) == 2
    assert len(list(d.dependencies())) == 1  # d must not depend on a or b
    a.value += 1
    assert d.value == 12


def test_list():
    history: list[list[int]] = []
    a = Value(2)
    xs = ObservableList([a, 3])
    assert list(xs.value) == [2, 3]
    _ = xs.observe(history.append)
    xs.value.append(4)
    assert len(list(xs.dependencies())) == 3
    assert len(history) == 1 and history[-1] == [2, 3, 4]
    xs.value[1] -= 1
    assert len(history) == 2 and history[-1] == [2, 2, 4]
    _ = xs.value.pop()
    assert len(history) == 3 and history[-1] == [2, 2]
    assert len(list(xs.dependencies())) == 2


def test_gc():
    counts = [0, 0]

    class CountingValueMixin:
        def __init__(self, i: int, *args: Any):
            counts[i] += 1
            super().__init__(*args)

            def decrease():
                counts[i] -= 1

            self.__finalizer = finalize(self, decrease)

    class CountingValue(CountingValueMixin, Value[int]):  # pyright: ignore[reportUnsafeMultipleInheritance]
        def __init__(self, value: int) -> None:
            super().__init__(0, value)

    class CountingCallback(CountingValueMixin, ComputedProperty[int]):  # pyright: ignore[reportUnsafeMultipleInheritance]
        def __init__(self, value: Callable[[], int]) -> None:
            super().__init__(1, value)

    # Create some observables and delete them
    for i in range(10000):
        a = CountingValue(i)
        b = CountingCallback(lambda: a.value * 2)  # noqa: B023
        a.value += 1
        assert b.value == (i + 1) * 2

    assert counts[0] <= 1, "Values() get garbage collected"
    assert counts[1] <= 1, "Callbacks() get garbage collected"

    # Create some observables and delete them
    for i in range(10000):
        a = CountingValue(i)
        # make an observer to make sure these dont stop GC
        b = a.observe(lambda v: None)

    # observers may require an explicit call to GC due to circular references
    _ = gc.collect()
    assert counts[0] <= 1, "Values() get garbage collected"


def test_list_dependency():
    xs = ObservableList([1, 2, 3])
    xxss = ComputedProperty(lambda: xs.value + xs.value)
    assert xxss.value == [1, 2, 3, 1, 2, 3]
    xs.value[1] += 3
    assert xxss.value == [1, 5, 3, 1, 5, 3]
    xs.value.append(7)
    assert xxss.value == [1, 5, 3, 7, 1, 5, 3, 7]

__all__ = ["Constant", "Value", "ComputedProperty", "ObservableList"]


from collections.abc import Iterable, Iterator, Sequence
from typing import Any, Callable, Optional, SupportsIndex, TypeVar, Union, cast, overload

from observables.observable_generic import EditableObservableObject, ObservableObject

T = TypeVar("T")
V = TypeVar("V")


class Constant(ObservableObject[T]):
    """
    Constant observable is a very thin wrapper around its object that can be used when an Observable is needed
    in some context, but the functionality of it is unneeded.
    """

    def __init__(self, value: T) -> None:
        self.__value = value
        super().__init__()

    def dependencies(self) -> Iterable["tuple[str, ObservableObject[Any]]"]:
        return []

    def update(self, key: Optional[str]) -> None:
        # Constant can never change, so this function cannot be called and thus is unnecessary.
        pass

    @property
    def value(self) -> T:
        return self.__value


class Value(EditableObservableObject[T]):
    """
    Value observable holds a value of type T. It can be updated through direct modification of obj.value.
    Whenever the value changes, all users of this value are immediately notified.
    """

    def __init__(self, value: T) -> None:
        self.__value = value
        super().__init__()

    def dependencies(self) -> Iterable["tuple[str, ObservableObject[Any]]"]:
        return []

    def update(self, key: Optional[str]) -> None:
        # Observable object has no dependencies, so this is unnecessary.
        pass

    @property
    def value(self) -> T:
        self.notify_read()
        return self.__value

    @value.setter
    def value(self, new_value: T) -> None:
        self.__value = new_value
        self.receive_update("_")


class ComputedProperty(ObservableObject[T]):
    """
    ComputedProperty observable holds a callback that returns a value of type T. Its value is the return value
    of this callback. It is computed lazily, only rerunning the callback whenever any of its dependencies change,
    which means the callback can be relatively slow.
    ComputedProperty tries to automatically determine the list of dependencies which cause it to rerun. If it fails,
    the list of dependencies can be passed manually at initialization instead.
    """

    def __init__(self, callback: Callable[[], T], dependencies: Optional[Iterable[ObservableObject[Any]]] = None):
        with self.dependency_resolution(dependencies) as found_dependencies:
            self.__callback = callback
            self.__value = callback()
        self.__dependencies = [(str(i), d) for i, d in enumerate(found_dependencies)]
        super().__init__()

    def dependencies(self) -> Iterable["tuple[str, ObservableObject[Any]]"]:
        return self.__dependencies

    def update(self, key: Optional[str]) -> None:
        self.__value = self.__callback()

    @property
    def value(self) -> T:
        self.notify_read()
        return self.__value


class ObservableList(ObservableObject[list[V]]):
    """
    ObservableList observable holds a list of either values or other observables of type V,
    and triggers dependents' updates whenever any value in the list changes, or the structure of the list changes.
    If the values in the list change, but the structure does not, it will only rerun the needed dependencies.
    """

    class ListWrapper(list[T]):
        def __init__(self, owner: ObservableObject[list[T]], values: list[ObservableObject[T]], static: list[T]):
            super().__init__()
            self.__owner = owner
            self.__values = values
            self.__static = static
            self.__structure_changed = False

        def __set(self, key: SupportsIndex, value: Union[T, ObservableObject[T]]) -> None:
            if isinstance(value, ObservableObject):
                self.__values[key] = value
            elif isinstance(self.__values[key], EditableObservableObject):
                cast(EditableObservableObject[T], self.__values[key]).value = value
            else:
                raise RuntimeError(
                    f"Attempted to change the object {self.__values[key].name} to {value}, "
                    "but the object is not editable!"
                )

        def __update_structure(self):
            if self.__structure_changed:
                self.__owner.reload_dependencies()
                self.__structure_changed = False

        @overload
        def __getitem__(self, k: SupportsIndex) -> T: ...

        @overload
        def __getitem__(self, k: slice) -> list[T]: ...

        def __getitem__(self, k: Union[SupportsIndex, slice]) -> Union[T, list[T]]:
            return self.__static[k]

        @overload
        def __setitem__(self, k: SupportsIndex, v: Union[T, ObservableObject[T]]) -> None: ...

        @overload
        def __setitem__(self, k: slice, v: Union[Iterable[T], bytes]) -> None: ...

        def __setitem__(
            self,
            k: Union[SupportsIndex, slice],
            v: Union[T, ObservableObject[T], Iterable[Union[T, ObservableObject[T]]], bytes],
        ) -> None:
            if isinstance(k, slice):
                for i, item in zip(range(k.start, k.stop, k.step), cast(Iterable[Union[T, ObservableObject[T]]], v)):
                    self.__set(i, item)
            else:
                self.__set(k, cast(Union[T, ObservableObject[T]], v))
            self.__update_structure()

        def __add__(self, other: Sequence[T]) -> list[T]:  # pyright: ignore[reportIncompatibleMethodOverride]
            return self.__static + list(other)

        def __iadd__(self, other: Iterable[Union[T, ObservableObject[T]]]) -> "ObservableList.ListWrapper[T]":
            for i in other:
                self.__append(i)
            self.__update_structure()
            return self

        def __append(self, other: Union[T, ObservableObject[T]]) -> None:
            self.__structure_changed = True
            if isinstance(other, ObservableObject):
                i = cast(ObservableObject[T], other)
                self.__values.append(i)
                self.__static.append(i.value)
            else:
                from observables.observable_object import Value

                self.__values.append(Value(other))
                self.__static.append(other)

        def append(self, other: Union[T, ObservableObject[T]]) -> None:
            self.__append(other)
            self.__update_structure()

        def extend(self, other: Iterable[Union[T, ObservableObject[T]]]) -> None:
            self += other

        def pop(self, index: SupportsIndex = -1) -> T:
            _ = self.__values.pop(index)
            self.__structure_changed = True
            value = self.__static.pop(index)
            self.__update_structure()
            return value

        def __delitem__(self, key: Union[SupportsIndex, slice], /) -> None:
            del self.__values[key]
            del self.__static[key]
            self.__structure_changed = True
            self.__update_structure()

        def __iter__(self) -> Iterator[T]:
            return iter(self.__static)

        def __len__(self) -> int:
            return len(self.__static)

        def __str__(self) -> str:
            return f"ObservableList({self.__static})"

        def __repr__(self) -> str:
            return f"ObservableList({self.__static})"

        def __eq__(self, other: object) -> bool:
            return self.__static == other

    def __init__(self, values: Sequence[Union[V, ObservableObject[V]]]):
        self.__values = [cast(ObservableObject[V], x) if isinstance(x, ObservableObject) else Value(x) for x in values]
        self.__values_computed = [cast(V, x.value) if isinstance(x, ObservableObject) else x for x in values]
        self.__dependencies: dict[str, ObservableObject[V]] = {}
        super().__init__()

    def dependencies(self) -> Iterable["tuple[str, ObservableObject[Any]]"]:
        self.__dependencies = {str(i): cast(ObservableObject[V], j) for i, j in enumerate(self.__values)}
        return self.__dependencies.items()

    def update(self, key: Optional[str]) -> None:
        if key is None:
            # The list itself changed. The list wrapper must recompute the static list.
            return
        assert key in self.__dependencies
        self.__values_computed[int(key)] = self.__dependencies[key].value

    @property
    def value(self) -> list[V]:
        self.notify_read()
        return ObservableList.ListWrapper(self, self.__values, self.__values_computed)

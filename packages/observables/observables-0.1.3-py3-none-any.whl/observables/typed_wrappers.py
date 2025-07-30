__all__ = ["Int", "Float", "String", "Bool", "ObjectWrapperGeneric", "DictLikeWrapper", "ObjectWrapper"]


import abc
import math
import weakref
from collections.abc import Iterable
from typing import Any, Callable, Generic, Optional, TypeVar, Union, cast, overload

from observables.observable_generic import ObservableObject, ObserverToken
from observables.observable_object import ComputedProperty, Value

T_co = TypeVar("T_co", covariant=True)
AnySupplier = Union[T_co, Callable[[], T_co], ObservableObject[T_co]]
AnySupplierBase = Union[T_co, ObservableObject[T_co]]


def _recv_supplier(s: AnySupplier[T_co]) -> T_co:
    if isinstance(s, ObservableObject):
        return cast(T_co, s.value)
    if callable(s):
        return cast(Callable[[], T_co], s)()
    return s


def _recv_supplier_base(s: AnySupplierBase[T_co]) -> T_co:
    if isinstance(s, ObservableObject):
        return cast(T_co, s.value)
    return s


def _to_observable(s: AnySupplier[T_co]) -> ObservableObject[T_co]:
    if isinstance(s, ObservableObject):
        return cast(ObservableObject[T_co], s)
    elif callable(s):
        return ComputedProperty(cast(Callable[[], T_co], s))
    return Value(s)


class Int(ObservableObject[int]):
    """
    Generic wrapper around any int value to add arithmetic operators.
    Can be initialized using ObservableObject, callback, or the value itself.
    """

    def __init__(self, value: AnySupplier[int] = 0) -> None:
        self.__value = _to_observable(value)
        super().__init__()

    def dependencies(self) -> Iterable["tuple[str, ObservableObject[Any]]"]:
        return self.__value.dependencies()

    @property
    def value(self) -> int:
        return self.__value.value

    def update(self, key: Optional[str]) -> None:
        self.__value.update(key)

    def __add__(self, other: AnySupplier[int]) -> "Int":
        return Int(lambda: self.value + _recv_supplier(other))

    def __sub__(self, other: AnySupplier[int]) -> "Int":
        return Int(lambda: self.value - _recv_supplier(other))

    def __mul__(self, other: AnySupplier[int]) -> "Int":
        return Int(lambda: self.value - _recv_supplier(other))

    def __truediv__(self, other: AnySupplier[Union[float, int]]) -> "Float":
        return Float(lambda: self.value / _recv_supplier(other))

    def __floordiv__(self, other: AnySupplier[int]) -> "Int":
        return Int(lambda: self.value // _recv_supplier(other))

    def __mod__(self, other: AnySupplier[int]) -> "Int":
        return Int(lambda: self.value % _recv_supplier(other))

    def __neg__(self) -> "Int":
        return Int(lambda: -self.value)

    def __pos__(self) -> "Int":
        return self

    def __pow__(self, other: AnySupplier[int]) -> "Int":
        return Int(lambda: self.value ** _recv_supplier(other))

    def __invert__(self) -> "Int":
        return Int(lambda: ~self.value)

    def __and__(self, other: AnySupplier[int]) -> "Int":
        return Int(lambda: self.value & _recv_supplier(other))

    def __or__(self, other: AnySupplier[int]) -> "Int":
        return Int(lambda: self.value | _recv_supplier(other))

    def __xor__(self, other: AnySupplier[int]) -> "Int":
        return Int(lambda: self.value ^ _recv_supplier(other))

    def __lshift__(self, other: AnySupplier[int]) -> "Int":
        return Int(lambda: self.value << _recv_supplier(other))

    def __rshift__(self, other: AnySupplier[int]) -> "Int":
        return Int(lambda: self.value >> _recv_supplier(other))

    def eq(self, other: AnySupplier[int]) -> "Bool":
        import traceback

        traceback.print_stack()
        v = Bool(lambda: self.value == _recv_supplier(other))
        return v

    def __neq__(self, other: AnySupplier[int]) -> "Bool":
        return Bool(lambda: self.value != _recv_supplier(other))

    def __gt__(self, other: AnySupplier[int]) -> "Bool":
        return Bool(lambda: self.value > _recv_supplier(other))

    def __gte__(self, other: AnySupplier[int]) -> "Bool":
        return Bool(lambda: self.value >= _recv_supplier(other))

    def __lt__(self, other: AnySupplier[int]) -> "Bool":
        return Bool(lambda: self.value < _recv_supplier(other))

    def __lte__(self, other: AnySupplier[int]) -> "Bool":
        return Bool(lambda: self.value <= _recv_supplier(other))

    def __abs__(self) -> "Int":
        return Int(lambda: abs(self.value))

    def __int__(self) -> int:
        return self.value

    def __index__(self) -> int:
        return self.value

    def __float__(self) -> float:
        return self.value

    def __round__(self, ndigits: Optional[AnySupplier[int]] = None) -> "Int":
        return self

    def __trunc__(self) -> "Int":
        return self

    def __floor__(self) -> "Int":
        return self

    def __ceil__(self) -> "Int":
        return self

    def __bool__(self) -> bool:
        return bool(self.value)

    def str(self) -> "String":
        return String(lambda: str(self.value))


class Float(ObservableObject[float]):
    """
    Generic wrapper around any float value to add arithmetic operators.
    Can be initialized using ObservableObject, callback, or the value itself.
    """

    def __init__(self, value: AnySupplier[float] = 0.0) -> None:
        self.__value = _to_observable(value)
        super().__init__()

    def dependencies(self) -> Iterable["tuple[str, ObservableObject[Any]]"]:
        return self.__value.dependencies()

    @property
    def value(self) -> float:
        return self.__value.value

    def update(self, key: Optional[str]) -> None:
        self.__value.update(key)

    def __add__(self, other: AnySupplier[float]) -> "Float":
        return Float(lambda: self.value + _recv_supplier(other))

    def __sub__(self, other: AnySupplier[float]) -> "Float":
        return Float(lambda: self.value - _recv_supplier(other))

    def __mul__(self, other: AnySupplier[float]) -> "Float":
        return Float(lambda: self.value - _recv_supplier(other))

    def __truediv__(self, other: AnySupplier[float]) -> "Float":
        return Float(lambda: self.value / _recv_supplier(other))

    def __floordiv__(self, other: AnySupplier[float]) -> "Float":
        return Float(lambda: self.value // _recv_supplier(other))

    def __mod__(self, other: AnySupplier[float]) -> "Float":
        return Float(lambda: self.value % _recv_supplier(other))

    def __neg__(self) -> "Float":
        return Float(lambda: -self.value)

    def __pos__(self) -> "Float":
        return self

    def __pow__(self, other: AnySupplier[float]) -> "Float":
        return Float(lambda: self.value ** _recv_supplier(other))

    def eq(self, other: AnySupplier[float]) -> "Bool":
        return Bool(lambda: self.value == _recv_supplier(other))

    def __neq__(self, other: AnySupplier[float]) -> "Bool":
        return Bool(lambda: self.value != _recv_supplier(other))

    def __gt__(self, other: AnySupplier[float]) -> "Bool":
        return Bool(lambda: self.value > _recv_supplier(other))

    def __gte__(self, other: AnySupplier[float]) -> "Bool":
        return Bool(lambda: self.value >= _recv_supplier(other))

    def __lt__(self, other: AnySupplier[float]) -> "Bool":
        return Bool(lambda: self.value < _recv_supplier(other))

    def __lte__(self, other: AnySupplier[float]) -> "Bool":
        return Bool(lambda: self.value <= _recv_supplier(other))

    def __abs__(self) -> "Float":
        return Float(lambda: abs(self.value))

    def __int__(self) -> int:
        return int(self.value)

    def __float__(self) -> float:
        return self.value

    @overload
    def __round__(self, ndigits: None = None) -> "Int": ...

    @overload
    def __round__(self, ndigits: AnySupplier[int]) -> "Float": ...

    def __round__(self, ndigits: Optional[AnySupplier[int]] = None) -> Union["Int", "Float"]:
        if ndigits is None:
            return Int(lambda: round(self.value))
        return Float(lambda: round(self.value, _recv_supplier(ndigits)))

    def __trunc__(self) -> "Int":
        return Int(lambda: math.trunc(self.value))

    def __floor__(self) -> "Int":
        return Int(lambda: math.floor(self.value))

    def __ceil__(self) -> "Int":
        return Int(lambda: math.ceil(self.value))

    def __bool__(self) -> bool:
        raise RuntimeError(
            "Should not call bool() on floats! This can cause floating point errors. "
            "Directly use `Float(...) == 0` if this is intended."
        )

    def str(self) -> "String":
        return String(lambda: str(self.value))


class Bool(ObservableObject[bool]):
    """
    Generic wrapper around any boolean value to add arithmetic operators.
    Can be initialized using ObservableObject, callback, or the value itself.
    """

    def __init__(self, value: AnySupplier[bool] = False) -> None:
        self.__value = _to_observable(value)
        super().__init__()

    def dependencies(self) -> Iterable["tuple[str, ObservableObject[Any]]"]:
        return self.__value.dependencies()

    @property
    def value(self) -> bool:
        return self.__value.value

    def update(self, key: Optional[str]) -> None:
        self.__value.update(key)

    def __bool__(self) -> bool:
        return self.value

    def __invert__(self) -> "Bool":
        return Bool(lambda: not self)

    def __and__(self, other: AnySupplier[bool]) -> "Bool":
        return Bool(lambda: self.value and _recv_supplier(other))

    def __or__(self, other: AnySupplier[bool]) -> "Bool":
        return Bool(lambda: self.value or _recv_supplier(other))

    def __xor__(self, other: AnySupplier[bool]) -> "Bool":
        return Bool(lambda: self.value ^ _recv_supplier(other))

    def str(self) -> "String":
        return String(lambda: str(self.value))


class String(ObservableObject[str]):
    """
    Generic wrapper around any string value to add arithmetic operators.
    Can be initialized using ObservableObject, callback, or the value itself.
    """

    def __init__(self, value: AnySupplier[str] = "") -> None:
        self.__value = _to_observable(value)
        super().__init__()

    def dependencies(self) -> Iterable["tuple[str, ObservableObject[Any]]"]:
        return self.__value.dependencies()

    @property
    def value(self) -> str:
        return self.__value.value

    def update(self, key: Optional[str]) -> None:
        self.__value.update(key)

    def __add__(self, other: AnySupplier[str]) -> "String":
        return String(lambda: self.value + _recv_supplier(other))

    def __contains__(self, other: AnySupplier[str]) -> "Bool":
        return Bool(lambda: _recv_supplier(other) in self.value)


class ObjectWrapperGeneric(Generic[T_co], abc.ABC):
    """
    Generic 'wrapper' object.
    Can be used to easily add observable consumption functionality to any third-party object.
    WARNING: if ObjectWrapperGeneric is garbage collected, its hooks also die with it.
    So make sure to keep references to your wrapper.
    """

    def __init__(self, constructor: Callable[..., T_co], /, *args: object, **kwargs: object):
        args_parsed = [_recv_supplier_base(a) for a in args]
        kwargs_parsed = {k: _recv_supplier_base(v) for k, v in kwargs.items()}
        self.__object = constructor(*args_parsed, **kwargs_parsed)
        self.__tokens: dict[str, ObserverToken[object]] = {}
        for k, v in kwargs.items():
            if isinstance(v, ObservableObject):
                self._add_token(k, v)

    @property
    def value(self) -> T_co:
        return self.__object

    def _add_token(self, k: str, v: ObservableObject[object]) -> None:
        if k in self.__tokens:
            self.__tokens[k].destroy()

        ref_to_this = weakref.ref(self)

        def recv_value(val: object):
            if obj := ref_to_this():
                obj._set_key(k, val)

        self.__tokens[k] = v.observe(recv_value)

    @abc.abstractmethod
    def _set_key(self, key: str, value: object) -> None:
        pass

    def _del_key(self, key: str) -> None:
        if token := self.__tokens.pop(key, None):
            token.destroy()

    def destroyTokens(self) -> None:
        for token in self.__tokens.values():
            token.destroy()
        self.__tokens.clear()

    def __del__(self):
        self.destroyTokens()


class DictLikeWrapper(ObjectWrapperGeneric[T_co]):
    """
    A wrapper around any third-party object behaving like a dict (i.e. allowing obj["target"] = value syntax).
    Will add hooks to update the object whenever any observables linked to it change.
    After creation, any functions are automatically added to the object as observables
    instead of directly as functions; this can be circumvented by passing the functions under a lambda if needed.
    WARNING: if DictLikeWrapper is garbage collected, its hooks also die with it.
    So make sure to keep references to your wrapper.
    """

    def _set_key(self, key: str, value: object) -> None:
        self.value[key] = value  # pyright: ignore[reportIndexIssue]

    def __setitem__(self, key: str, value: object) -> None:
        if isinstance(value, ObservableObject):
            self._add_token(key, value)
        elif callable(value):
            value = ComputedProperty(value)
            self._add_token(key, value)
        self._set_key(key, _recv_supplier(value))

    def __getitem__(self, key: str) -> object:
        return cast(object, self.value[key])  # pyright: ignore[reportIndexIssue]

    def __delitem__(self, key: str) -> None:
        self._del_key(key)
        del self.value[key]  # pyright: ignore[reportIndexIssue]


class ObjectWrapper(ObjectWrapperGeneric[T_co]):
    """
    A wrapper around any third-party object behaving like a class object (i.e. allowing obj.target = value syntax).
    Will add hooks to update the object whenever any observables linked to it change.
    After creation, any functions are automatically added to the object as observables
    instead of directly as functions; this can be circumvented by passing the functions under a lambda if needed.
    WARNING: if ObjectWrapper is garbage collected, its hooks also die with it.
    So make sure to keep references to your wrapper.
    """

    def _set_key(self, key: str, value: object) -> None:
        setattr(self.value, key, value)

    def __setattr__(self, key: str, value: object) -> None:
        if key.startswith("_"):
            super().__setattr__(key, value)
            return
        if isinstance(value, ObservableObject):
            self._add_token(key, value)
        elif callable(value):
            value = ComputedProperty(value)
            self._add_token(key, value)
        self._set_key(key, _recv_supplier(value))

    def __getattr__(self, key: str) -> object:
        if key.startswith("_"):
            return super().__getattribute__(key)
        return getattr(self.value, key)

    def __delitem__(self, key: str) -> None:
        self._del_key(key)
        delattr(self.value, key)

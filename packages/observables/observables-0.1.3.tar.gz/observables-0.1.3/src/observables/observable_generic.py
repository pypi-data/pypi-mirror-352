__all__ = ["ObservableObject", "ObserverToken", "EditableObservableObject"]

import abc
import contextlib
from collections.abc import Generator, Iterable
from typing import Any, Callable, ClassVar, Generic, Optional, TypeVar
from weakref import WeakKeyDictionary, ref

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


class ObserverToken(Generic[T]):
    """
    ObserverToken manages one result of calling observe() on an Observable so it can be cleaned up when needed.
    WARNING: If the ObserverToken gets garbage collected, its managed callback hook will still exist.
    Normally this is fine, but if you need to clean up the hook make sure to keep the reference to the token.
    """

    def __init__(self, owner: "ObservableObject[T]", new_value: bool, callback: Callable[[T], object]):
        self.__callback = callback
        self.__new_value = new_value
        self.__owner = owner

    def __call__(self, value: T) -> None:
        _ = self.__callback(value)

    def destroy(self):
        self.__owner.remove_observer(self, self.__new_value)


class ObservableObject(Generic[T_co], abc.ABC):
    """
    ObservableObject manages an abstract value of type T and updates to that value can be listened to.
    In addition, other observables can listen to those updates and update their values accordingly on demand.
    """

    _generated_id: ClassVar[int] = 0

    def __init__(self):
        self.__name = self.__generate_name()
        self.__observers: set[ObserverToken[T_co]] = set()
        self.__observers_old: set[ObserverToken[T_co]] = set()

        DependencyBus.instance().register(self)

    def __repr__(self) -> str:
        return self.name

    def observe(self, callback: Callable[[T_co], object]) -> ObserverToken[T_co]:
        token = ObserverToken(self, True, callback)
        self.__observers.add(token)
        return token

    def observe_old(self, callback: Callable[[T_co], object]) -> ObserverToken[T_co]:
        token = ObserverToken(self, False, callback)
        self.__observers_old.add(token)
        return token

    def remove_observer(self, o: ObserverToken[T_co], new_value: bool):
        if new_value:
            self.__observers.discard(o)
        else:
            self.__observers_old.discard(o)

    def __generate_name(self) -> str:
        ObservableObject._generated_id += 1
        return f"{type(self).__name__}[{type(self.value).__name__}]-{ObservableObject._generated_id}"

    @property
    def name(self) -> str:
        return self.__name

    @abc.abstractmethod
    def dependencies(self) -> Iterable["tuple[str, ObservableObject[Any]]"]:
        """
        Returns a list of all dependencies with their name.
        Must return a valid result when ObservableObject.__init__ is called.
        If this is changed at runtime, reload_dependencies must be called.
        """

    def reload_dependencies(self):
        DependencyBus.instance().reload_dependencies(self)
        self.receive_update(None)

    @property
    @abc.abstractmethod
    def value(self) -> T_co:
        pass

    def receive_update(self, key: Optional[str]) -> None:
        for o in self.__observers_old:
            o(self.value)
        self.update(key)
        for o in self.__observers:
            o(self.value)
        DependencyBus.instance().dispatch(self)

    @abc.abstractmethod
    def update(self, key: Optional[str]) -> None:
        """
        Called when this observable is changed in some way.
        If the observable itself is changed, key = None, otherwise key is the name of the dependency that triggered it.
        """

    def notify_read(self):
        DependencyBus.instance().process_read(self)

    @contextlib.contextmanager
    def dependency_resolution(
        self, dependencies: Optional[Iterable["ObservableObject[Any]"]]
    ) -> Generator[Iterable["ObservableObject[Any]"], None, None]:
        if dependencies is not None:
            yield dependencies
        else:
            DependencyBus.instance().detect_dependencies()
            lst: list[ObservableObject[Any]] = []
            yield lst
            lst.clear()
            lst.extend(DependencyBus.instance().get_dependencies())


class EditableObservableObject(ObservableObject[T], abc.ABC):
    """
    EditableObservableObject is similar to ObservableObject, but also allows modification of the value.
    """

    @property
    @abc.abstractmethod
    def value(self) -> T:
        pass

    @value.setter
    @abc.abstractmethod
    def value(self, value: T, /) -> None:
        pass

    def set(self, value: T, /) -> None:
        self.value = value


WeakDependencyListT = set[tuple[str, ref[ObservableObject[Any]]]]
DependencyListT = set[tuple[str, ObservableObject[Any]]]


class DependencyBus:
    the_instance: ClassVar[Optional["DependencyBus"]] = None

    def __init__(self):
        # Each object's garbage collection should not be stopped by its dependency existing,
        # so both of these are weak references
        self.dependency_map: WeakKeyDictionary[ObservableObject[Any], WeakDependencyListT] = WeakKeyDictionary()
        # Each object's garbage collection should be stopped by its dependents existing,
        # but not by another reference to the same object existing, so first is weak and second is strong
        self.per_object_deps: WeakKeyDictionary[ObservableObject[Any], DependencyListT] = WeakKeyDictionary()
        self.circular_checker: list[ObservableObject[Any]] = []
        self.read_objects: set[ObservableObject[Any]] = set()
        self.read_check_mode: bool = False

    def register(self, obj: ObservableObject[Any]):
        for key, dep in obj.dependencies():
            self.register_dependency(obj, key, dep)

    def register_dependency(self, dependent: ObservableObject[Any], key: str, dependency: ObservableObject[Any]):
        if dependency not in self.dependency_map:
            self.dependency_map[dependency] = set()
        self.dependency_map[dependency].add((key, ref(dependent)))

        if dependent not in self.per_object_deps:
            self.per_object_deps[dependent] = set()
        self.per_object_deps[dependent].add((key, dependency))

    @staticmethod
    def instance() -> "DependencyBus":
        if DependencyBus.the_instance is None:
            DependencyBus.the_instance = DependencyBus()
        return DependencyBus.the_instance

    def dispatch(self, o: ObservableObject[Any]) -> None:
        if o in self.circular_checker:
            e = (
                "An update caused a circular dependency dispatch. This is most likely a programmer error. "
                "The following objects were involved: "
            )
            e += "; ".join([x.name for x in self.circular_checker])
            raise RuntimeError(e)

        self.circular_checker.append(o)
        if o in self.dependency_map:
            for k, s in self.dependency_map[o]:
                if (dep := s()) is not None:
                    dep.receive_update(k)
        oo = self.circular_checker.pop()
        assert o is oo

    def process_read(self, o: ObservableObject[Any]) -> None:
        if self.read_check_mode:
            self.read_objects.add(o)

    def detect_dependencies(self) -> None:
        if self.read_check_mode:
            e = (
                "Automatic dependency resolution was called recursively. This happens if a ComputedProperty "
                "creates a new ComputedProperty upon calling, and indicates a programmer error."
            )
            raise RuntimeError(e)

        self.read_check_mode = True

    def get_dependencies(self) -> set[ObservableObject[Any]]:
        self.read_check_mode = False
        dependencies = set(self.read_objects)
        self.read_objects = set()
        return dependencies

    def reload_dependencies(self, obj: ObservableObject[Any]) -> None:
        if obj in self.per_object_deps:
            for s, dep in self.per_object_deps[obj]:
                assert dep in self.dependency_map
                self.dependency_map[dep].discard((s, ref(obj)))
        self.per_object_deps[obj] = set()
        self.register(obj)

"""Pythonic wrappers around JADX Java objects."""

from __future__ import annotations

import weakref

import jpype

_registry: weakref.WeakValueDictionary[int, _BaseWrapper] = weakref.WeakValueDictionary()

_java_types: dict[str, type] = {}


def _resolve_java_types() -> None:
    """Resolve JADX Java classes via JPype. Called once when JVM is running."""
    if _java_types:
        return
    _java_types["JavaClass"] = jpype.JClass("jadx.api.JavaClass")
    _java_types["JavaMethod"] = jpype.JClass("jadx.api.JavaMethod")
    _java_types["JavaField"] = jpype.JClass("jadx.api.JavaField")
    _java_types["JavaPackage"] = jpype.JClass("jadx.api.JavaPackage")
    _java_types["System"] = jpype.JClass("java.lang.System")


def _java_identity(java_obj: jpype.JObject) -> int:
    """Stable identity key using Java's System.identityHashCode."""
    _resolve_java_types()
    return int(_java_types["System"].identityHashCode(java_obj))


class _BaseWrapper:
    __slots__ = ("_java", "_cache", "__weakref__")

    def __init__(self, java_obj: jpype.JObject) -> None:
        self._java = java_obj
        self._cache: dict[str, object] = {}

    @property
    def java(self) -> jpype.JObject:
        return self._java


class JavaClass(_BaseWrapper):
    __slots__ = ()

    @property
    def name(self) -> str:
        return str(self._java.getName())

    @property
    def full_name(self) -> str:
        return str(self._java.getRawName())

    @property
    def package(self) -> str:
        return str(self._java.getPackage())

    @property
    def code(self) -> str:
        if "code" not in self._cache:
            self._cache["code"] = str(self._java.getCode())
        return self._cache["code"]  # type: ignore[return-value]

    @property
    def smali(self) -> str:
        if "smali" not in self._cache:
            self._cache["smali"] = str(self._java.getSmali())
        return self._cache["smali"]  # type: ignore[return-value]

    @property
    def methods(self) -> list[JavaMethod]:
        return [_wrap(m) for m in self._java.getMethods()]  # type: ignore[misc]

    @property
    def fields(self) -> list[JavaField]:
        return [_wrap(f) for f in self._java.getFields()]  # type: ignore[misc]

    @property
    def inner_classes(self) -> list[JavaClass]:
        return [_wrap(c) for c in self._java.getInnerClasses()]  # type: ignore[misc]

    @property
    def declaring_class(self) -> JavaClass | None:
        dc = self._java.getDeclaringClass()
        if dc is None:
            return None
        return _wrap(dc)  # type: ignore[return-value]

    @property
    def top_class(self) -> JavaClass:
        return _wrap(self._java.getTopParentClass())  # type: ignore[return-value]

    @property
    def dependencies(self) -> list[JavaClass]:
        return [_wrap(d) for d in self._java.getDependencies()]  # type: ignore[misc]

    @property
    def is_inner(self) -> bool:
        return bool(self._java.isInner())


class JavaMethod(_BaseWrapper):
    __slots__ = ()

    @property
    def name(self) -> str:
        return str(self._java.getName())

    @property
    def full_name(self) -> str:
        return str(self._java.getFullName())

    @property
    def code(self) -> str:
        if "code" not in self._cache:
            self._cache["code"] = str(self._java.getCodeStr())
        return self._cache["code"]  # type: ignore[return-value]

    @property
    def callers(self) -> list[JavaMethod]:
        if "callers" not in self._cache:
            _resolve_java_types()
            self._cache["callers"] = [
                _wrap(node)  # type: ignore[misc]
                for node in self._java.getUseIn()
                if isinstance(node, _java_types["JavaMethod"])
            ]
        return self._cache["callers"]  # type: ignore[return-value]

    @property
    def callees(self) -> list[JavaMethod]:
        if "callees" not in self._cache:
            _resolve_java_types()
            self._cache["callees"] = [
                _wrap(node)  # type: ignore[misc]
                for node in self._java.getUsed()
                if isinstance(node, _java_types["JavaMethod"])
            ]
        return self._cache["callees"]  # type: ignore[return-value]

    @property
    def override_related(self) -> list[JavaMethod]:
        return [_wrap(m) for m in self._java.getOverrideRelatedMethods()]  # type: ignore[misc]

    @property
    def declaring_class(self) -> JavaClass:
        return _wrap(self._java.getDeclaringClass())  # type: ignore[return-value]


class JavaField(_BaseWrapper):
    __slots__ = ()

    @property
    def name(self) -> str:
        return str(self._java.getName())

    @property
    def full_name(self) -> str:
        return str(self._java.getFullName())

    @property
    def type(self) -> str:
        return str(self._java.getType().toString())

    @property
    def callers(self) -> list[JavaMethod]:
        if "callers" not in self._cache:
            _resolve_java_types()
            self._cache["callers"] = [
                _wrap(node)  # type: ignore[misc]
                for node in self._java.getUseIn()
                if isinstance(node, _java_types["JavaMethod"])
            ]
        return self._cache["callers"]  # type: ignore[return-value]

    @property
    def declaring_class(self) -> JavaClass:
        return _wrap(self._java.getDeclaringClass())  # type: ignore[return-value]


class JavaPackage(_BaseWrapper):
    __slots__ = ()

    @property
    def name(self) -> str:
        return str(self._java.getName())

    @property
    def classes(self) -> list[JavaClass]:
        return [_wrap(c) for c in self._java.getClasses()]  # type: ignore[misc]

    @property
    def sub_packages(self) -> list[JavaPackage]:
        return [_wrap(p) for p in self._java.getSubPackages()]  # type: ignore[misc]


def _wrap(java_obj: jpype.JObject) -> JavaClass | JavaMethod | JavaField | JavaPackage:
    key = _java_identity(java_obj)
    if key in _registry:
        return _registry[key]

    _resolve_java_types()

    if isinstance(java_obj, _java_types["JavaClass"]):
        wrapper: _BaseWrapper = JavaClass(java_obj)
    elif isinstance(java_obj, _java_types["JavaMethod"]):
        wrapper = JavaMethod(java_obj)
    elif isinstance(java_obj, _java_types["JavaField"]):
        wrapper = JavaField(java_obj)
    elif isinstance(java_obj, _java_types["JavaPackage"]):
        wrapper = JavaPackage(java_obj)
    else:
        raise TypeError(f"Unknown JADX type: {type(java_obj)}")

    _registry[key] = wrapper
    return wrapper  # type: ignore[return-value]

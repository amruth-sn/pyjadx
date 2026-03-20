"""Jadx decompiler — main entry point."""

from __future__ import annotations

import logging
from pathlib import Path

import jpype

from pyjadx._errors import DecompilationError
from pyjadx._jvm import ensure_jvm
from pyjadx._types import JavaClass, JavaPackage, _wrap

logger = logging.getLogger(__name__)

_MODE_MAP = {
    "auto": "AUTO",
    "restructure": "RESTRUCTURE",
    "simple": "SIMPLE",
    "fallback": "FALLBACK",
}


class Jadx:
    def __init__(
        self,
        path: str,
        *,
        threads: int | None = None,
        mode: str = "auto",
        code_cache: bool = False,
    ) -> None:
        self._path = str(Path(path).resolve())
        self._threads = threads
        self._mode = mode
        self._code_cache = code_cache
        self._jadx: jpype.JObject | None = None

    def load(self) -> Jadx:
        if self._jadx is not None:
            return self
        ensure_jvm()

        JadxArgs = jpype.JClass("jadx.api.JadxArgs")
        JadxDecompiler = jpype.JClass("jadx.api.JadxDecompiler")
        DecompilationMode = jpype.JClass("jadx.api.DecompilationMode")
        InMemoryCodeCache = jpype.JClass("jadx.api.impl.InMemoryCodeCache")
        File = jpype.JClass("java.io.File")

        args = JadxArgs()
        args.getInputFiles().add(File(self._path))

        if self._threads is not None:
            args.setThreadsCount(self._threads)

        mode_str = _MODE_MAP.get(self._mode)
        if mode_str is None:
            raise ValueError(
                f"Invalid mode: {self._mode!r}. Use one of {list(_MODE_MAP.keys())}"
            )
        args.setDecompilationMode(DecompilationMode.valueOf(mode_str))

        if not self._code_cache:
            args.setCodeCache(InMemoryCodeCache())

        try:
            jadx = JadxDecompiler(args)
            jadx.load()
        except Exception as exc:
            raise DecompilationError(f"Failed to load {self._path}: {exc}") from exc

        self._jadx = jadx
        return self

    def close(self) -> None:
        if self._jadx is not None:
            self._jadx.close()
            self._jadx = None

    def __enter__(self) -> Jadx:
        self.load()
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    @property
    def classes(self) -> list[JavaClass]:
        if self._jadx is None:
            raise DecompilationError("Decompiler not loaded — call load() or use as context manager")
        return [_wrap(c) for c in self._jadx.getClasses()]  # type: ignore[misc]

    @property
    def packages(self) -> list[JavaPackage]:
        if self._jadx is None:
            raise DecompilationError("Decompiler not loaded — call load() or use as context manager")
        return [_wrap(p) for p in self._jadx.getPackages()]  # type: ignore[misc]

    @property
    def class_count(self) -> int:
        return len(self.classes)

    def search_class(self, full_name: str) -> JavaClass | None:
        if self._jadx is None:
            raise DecompilationError("Decompiler not loaded — call load() or use as context manager")
        result = self._jadx.searchJavaClassByOrigFullName(full_name)
        if result is None:
            return None
        return _wrap(result)  # type: ignore[return-value]

    def decompile_all(self) -> None:
        for cls in self.classes:
            _ = cls.code

    @property
    def java(self) -> jpype.JObject:
        if self._jadx is None:
            raise DecompilationError("Decompiler not loaded — call load() or use as context manager")
        return self._jadx

"""Adaptive JVM lifecycle management."""

from __future__ import annotations

import logging

import jpype

from pyjadx._errors import JVMError
from pyjadx._jars import resolve_jars

logger = logging.getLogger(__name__)

_initialized = False


def ensure_jvm(jadx_home: str | None = None) -> None:
    global _initialized
    if _initialized:
        return

    jar_paths = resolve_jars(jadx_home=jadx_home)
    str_paths = [str(p) for p in jar_paths]

    if jpype.isJVMStarted():
        for path in str_paths:
            jpype.addClassPath(path)
        logger.info("Added %d JADX JARs to existing JVM classpath", len(str_paths))
    else:
        try:
            jpype.startJVM(classpath=str_paths)
        except Exception as exc:
            raise JVMError(f"Failed to start JVM: {exc}") from exc
        logger.info("Started JVM with %d JADX JARs", len(str_paths))

    _initialized = True

"""pyjadx — Python bindings for JADX."""

from __future__ import annotations

from pyjadx._decompiler import Jadx
from pyjadx._errors import (
    DecompilationError,
    JarResolutionError,
    JVMError,
    PyjadxError,
)
from pyjadx._jvm import ensure_jvm as _ensure_jvm
from pyjadx._types import JavaClass, JavaField, JavaMethod, JavaPackage

from pyjadx._jars import JADX_VERSION

__version__ = "0.1.0"

__all__: list[str] = [
    "__version__",
    "JADX_VERSION",
    "start",
    "Jadx",
    "JavaClass",
    "JavaMethod",
    "JavaField",
    "JavaPackage",
    "PyjadxError",
    "JVMError",
    "JarResolutionError",
    "DecompilationError",
]


def start(jadx_home: str | None = None) -> None:
    """Ensure the JVM is running with JADX JARs on the classpath."""
    _ensure_jvm(jadx_home=jadx_home)

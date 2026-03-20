"""pyjadx — Python bindings for JADX."""

from __future__ import annotations

from pyjadx._errors import (
    DecompilationError,
    JarResolutionError,
    JVMError,
    PyjadxError,
)
from pyjadx._jvm import ensure_jvm as _ensure_jvm

__version__ = "0.1.0"
JADX_VERSION = "1.5.5"

__all__: list[str] = [
    "__version__",
    "JADX_VERSION",
    "DecompilationError",
    "JarResolutionError",
    "JVMError",
    "PyjadxError",
    "start",
]


def start(jadx_home: str | None = None) -> None:
    """Ensure the JVM is running with JADX JARs on the classpath."""
    _ensure_jvm(jadx_home=jadx_home)

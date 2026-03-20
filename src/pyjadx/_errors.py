"""pyjadx exception hierarchy."""

from __future__ import annotations


class PyjadxError(Exception):
    """Base exception for all pyjadx errors."""


class JVMError(PyjadxError):
    """JVM startup failed, classpath issues, or JPype errors."""


class JarResolutionError(PyjadxError):
    """JADX JARs not found, download failed, or integrity check failed."""


class DecompilationError(PyjadxError):
    """JADX failed to load or decompile a target."""

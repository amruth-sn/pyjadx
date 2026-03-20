from __future__ import annotations

import pytest

from pyjadx._jvm import ensure_jvm


@pytest.mark.jvm
def test_ensure_jvm_starts():
    ensure_jvm()
    import jpype
    assert jpype.isJVMStarted()


@pytest.mark.jvm
def test_ensure_jvm_idempotent():
    ensure_jvm()
    ensure_jvm()
    import jpype
    assert jpype.isJVMStarted()


@pytest.mark.jvm
def test_ensure_jvm_loads_jadx_classes():
    ensure_jvm()
    import jpype
    JadxArgs = jpype.JClass("jadx.api.JadxArgs")
    assert JadxArgs is not None

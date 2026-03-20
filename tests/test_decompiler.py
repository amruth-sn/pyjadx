from __future__ import annotations

from pathlib import Path

import pytest

from pyjadx import Jadx


@pytest.mark.jvm
def test_jadx_context_manager(hello_dex: Path):
    with Jadx(str(hello_dex)) as jadx:
        assert jadx.class_count > 0


@pytest.mark.jvm
def test_jadx_manual_lifecycle(hello_dex: Path):
    jadx = Jadx(str(hello_dex))
    jadx.load()
    assert jadx.class_count > 0
    jadx.close()


@pytest.mark.jvm
def test_jadx_classes_are_top_level(hello_dex: Path):
    with Jadx(str(hello_dex)) as jadx:
        for cls in jadx.classes:
            assert not cls.is_inner


@pytest.mark.jvm
def test_jadx_search_class(hello_dex: Path):
    with Jadx(str(hello_dex)) as jadx:
        cls = jadx.search_class("Hello")
        assert cls is not None
        assert cls.name == "Hello"


@pytest.mark.jvm
def test_jadx_search_class_not_found(hello_dex: Path):
    with Jadx(str(hello_dex)) as jadx:
        assert jadx.search_class("DoesNotExist") is None


@pytest.mark.jvm
def test_jadx_packages(hello_dex: Path):
    with Jadx(str(hello_dex)) as jadx:
        pkgs = jadx.packages
        assert isinstance(pkgs, list)


@pytest.mark.jvm
def test_jadx_java_escape_hatch(hello_dex: Path):
    with Jadx(str(hello_dex)) as jadx:
        assert jadx.java is not None


@pytest.mark.jvm
def test_jadx_decompile_all(hello_dex: Path):
    with Jadx(str(hello_dex)) as jadx:
        jadx.decompile_all()
        for cls in jadx.classes:
            assert len(cls.code) > 0


@pytest.mark.jvm
def test_jadx_multi_dex(multi_dex: Path):
    with Jadx(str(multi_dex)) as jadx:
        names = {cls.name for cls in jadx.classes}
        assert "Caller" in names
        assert "Greeter" in names


@pytest.mark.jvm
def test_jadx_mode_simple(hello_dex: Path):
    with Jadx(str(hello_dex), mode="simple") as jadx:
        assert jadx.class_count > 0
        cls = jadx.search_class("Hello")
        assert cls is not None
        assert len(cls.code) > 0


@pytest.mark.jvm
def test_jadx_threads(hello_dex: Path):
    with Jadx(str(hello_dex), threads=1) as jadx:
        assert jadx.class_count > 0


@pytest.mark.jvm
def test_jadx_search_class_no_package(hello_dex: Path):
    """Hello.java has no package declaration, so short name == full name."""
    with Jadx(str(hello_dex)) as jadx:
        cls = jadx.search_class("Hello")
        assert cls is not None
        assert cls.full_name == "Hello"

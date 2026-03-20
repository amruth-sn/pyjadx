from __future__ import annotations

from pathlib import Path

import pytest

from pyjadx import Jadx, JavaClass, JavaField, JavaMethod


@pytest.mark.jvm
def test_class_name(hello_dex: Path):
    with Jadx(str(hello_dex)) as jadx:
        cls = jadx.search_class("Hello")
        assert cls is not None
        assert cls.name == "Hello"
        assert isinstance(cls.full_name, str)
        assert "Hello" in cls.full_name


@pytest.mark.jvm
def test_class_code_lazy(hello_dex: Path):
    with Jadx(str(hello_dex)) as jadx:
        cls = jadx.search_class("Hello")
        assert cls is not None
        code = cls.code
        assert isinstance(code, str)
        assert "greet" in code


@pytest.mark.jvm
def test_class_code_cached(hello_dex: Path):
    with Jadx(str(hello_dex)) as jadx:
        cls = jadx.search_class("Hello")
        assert cls is not None
        code1 = cls.code
        code2 = cls.code
        assert code1 is code2


@pytest.mark.jvm
def test_class_methods(hello_dex: Path):
    with Jadx(str(hello_dex)) as jadx:
        cls = jadx.search_class("Hello")
        assert cls is not None
        methods = cls.methods
        assert isinstance(methods, list)
        assert len(methods) > 0
        assert all(isinstance(m, JavaMethod) for m in methods)


@pytest.mark.jvm
def test_class_smali(hello_dex: Path):
    with Jadx(str(hello_dex)) as jadx:
        cls = jadx.search_class("Hello")
        assert cls is not None
        smali = cls.smali
        assert isinstance(smali, str)
        assert len(smali) > 0


@pytest.mark.jvm
def test_method_name_and_code(hello_dex: Path):
    with Jadx(str(hello_dex)) as jadx:
        cls = jadx.search_class("Hello")
        assert cls is not None
        greet = None
        for m in cls.methods:
            if m.name == "greet":
                greet = m
                break
        assert greet is not None
        assert isinstance(greet.code, str)
        assert len(greet.code) > 0


@pytest.mark.jvm
def test_method_declaring_class(hello_dex: Path):
    with Jadx(str(hello_dex)) as jadx:
        cls = jadx.search_class("Hello")
        assert cls is not None
        for m in cls.methods:
            assert m.declaring_class is cls


@pytest.mark.jvm
def test_method_java_escape_hatch(hello_dex: Path):
    with Jadx(str(hello_dex)) as jadx:
        cls = jadx.search_class("Hello")
        assert cls is not None
        m = cls.methods[0]
        assert m.java is not None


@pytest.mark.jvm
def test_field_properties(multi_dex: Path):
    with Jadx(str(multi_dex)) as jadx:
        cls = jadx.search_class("Greeter")
        assert cls is not None
        fields = cls.fields
        assert isinstance(fields, list)
        if len(fields) > 0:
            f = fields[0]
            assert isinstance(f, JavaField)
            assert isinstance(f.name, str)
            assert isinstance(f.type, str)
            assert f.declaring_class is cls


@pytest.mark.jvm
def test_cross_references(multi_dex: Path):
    with Jadx(str(multi_dex)) as jadx:
        greeter = jadx.search_class("Greeter")
        assert greeter is not None
        greet_method = None
        for m in greeter.methods:
            if m.name == "greet":
                greet_method = m
                break
        assert greet_method is not None
        callers = greet_method.callers
        assert isinstance(callers, list)
        assert all(isinstance(c, JavaMethod) for c in callers)


@pytest.mark.jvm
def test_referential_integrity(hello_dex: Path):
    with Jadx(str(hello_dex)) as jadx:
        cls = jadx.search_class("Hello")
        assert cls is not None
        if cls.methods:
            assert cls.methods[0].declaring_class is cls


@pytest.mark.jvm
def test_class_is_inner(hello_dex: Path):
    with Jadx(str(hello_dex)) as jadx:
        cls = jadx.search_class("Hello")
        assert cls is not None
        assert cls.is_inner is False


@pytest.mark.jvm
def test_package_wrapper(multi_dex: Path):
    with Jadx(str(multi_dex)) as jadx:
        pkgs = jadx.packages
        assert isinstance(pkgs, list)

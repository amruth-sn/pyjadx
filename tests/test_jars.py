from __future__ import annotations

import hashlib
from pathlib import Path
from unittest.mock import patch

import pytest

from pyjadx._errors import JarResolutionError
from pyjadx._jars import (
    _download_jar,
    JADX_VERSION,
    JarEntry,
    JarManifest,
    resolve_jars,
    _cache_dir,
    _jar_url,
)


def test_cache_dir_default():
    d = _cache_dir()
    assert d == Path.home() / ".pyjadx" / "jars" / JADX_VERSION


def test_jar_url_format():
    entry = JarEntry(
        group="io.github.skylot", artifact="jadx-core",
        version=JADX_VERSION, sha256="fake",
    )
    url = _jar_url(entry)
    assert "repo1.maven.org" in url
    assert "jadx-core" in url
    assert JADX_VERSION in url
    assert url.endswith(".jar")


def test_jar_url_dots_to_slashes():
    entry = JarEntry(
        group="io.github.skylot", artifact="jadx-core",
        version="1.5.5", sha256="fake",
    )
    url = _jar_url(entry)
    assert "/io/github/skylot/" in url


def test_jar_manifest_has_all_required_artifacts():
    manifest = JarManifest.for_version(JADX_VERSION)
    names = {entry.artifact for entry in manifest.entries}
    assert "jadx-core" in names
    assert "jadx-dex-input" in names
    assert "jadx-input-api" in names


def test_resolve_jars_jadx_home(tmp_path: Path):
    lib_dir = tmp_path / "lib"
    lib_dir.mkdir()
    (lib_dir / "jadx-core-1.5.5.jar").write_bytes(b"fake")
    (lib_dir / "jadx-dex-input-1.5.5.jar").write_bytes(b"fake")
    jars = resolve_jars(jadx_home=str(tmp_path))
    assert len(jars) >= 2
    assert all(j.exists() for j in jars)


def test_resolve_jars_jadx_home_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    lib_dir = tmp_path / "lib"
    lib_dir.mkdir()
    (lib_dir / "jadx-core-1.5.5.jar").write_bytes(b"fake")
    monkeypatch.setenv("JADX_HOME", str(tmp_path))
    jars = resolve_jars()
    assert len(jars) >= 1


def test_resolve_jars_cached(tmp_path: Path):
    cache = tmp_path / ".pyjadx" / "jars" / JADX_VERSION
    cache.mkdir(parents=True)
    (cache / "jadx-core-1.5.5.jar").write_bytes(b"fake")
    with patch("pyjadx._jars._cache_dir", return_value=cache):
        jars = resolve_jars()
    assert len(jars) >= 1


def test_download_jar_checksum_mismatch(tmp_path: Path):
    dest = tmp_path / "bad.jar"
    with patch("pyjadx._jars.urllib.request.urlretrieve") as mock_retrieve:
        mock_retrieve.side_effect = lambda url, filename: Path(filename).write_bytes(b"wrong content")
        with pytest.raises(JarResolutionError):
            _download_jar("https://example.com/fake.jar", dest, expected_sha256="0" * 64)
    assert not dest.exists()


def test_download_jar_success(tmp_path: Path):
    content = b"valid jar content"
    expected = hashlib.sha256(content).hexdigest()
    dest = tmp_path / "good.jar"
    with patch("pyjadx._jars.urllib.request.urlretrieve") as mock_retrieve:
        mock_retrieve.side_effect = lambda url, filename: Path(filename).write_bytes(content)
        _download_jar("https://example.com/fake.jar", dest, expected_sha256=expected)
    assert dest.exists()
    assert dest.read_bytes() == content

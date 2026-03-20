"""JAR resolution: find or download JADX JARs for the JVM classpath."""

from __future__ import annotations

import hashlib
import logging
import os
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

from pyjadx._errors import JarResolutionError

logger = logging.getLogger(__name__)

JADX_VERSION = "1.5.5"

_MAVEN_CENTRAL = "https://repo1.maven.org/maven2"
_GOOGLE_MAVEN = "https://dl.google.com/dl/android/maven2"


@dataclass
class JarEntry:
    group: str
    artifact: str
    version: str
    sha256: str
    base_url: str = _MAVEN_CENTRAL


@dataclass
class JarManifest:
    entries: list[JarEntry] = field(default_factory=list)

    @classmethod
    def for_version(cls, version: str) -> JarManifest:
        if version != JADX_VERSION:
            msg = f"unsupported JADX version: {version}"
            raise JarResolutionError(msg)
        return cls(entries=list(_JADX_1_5_5_ENTRIES))


_JADX_1_5_5_ENTRIES: list[JarEntry] = [
    JarEntry(
        group="io.github.skylot",
        artifact="jadx-core",
        version="1.5.5",
        sha256="0aafcca972eabaf2e40dc7cd7593c1a2062cbf8c8fcbcbef6172836c06f9fc52",
    ),
    JarEntry(
        group="io.github.skylot",
        artifact="jadx-dex-input",
        version="1.5.5",
        sha256="0b24d4dc30411a83d5c101ea42c6487a0fa5a9b26040e3f8794272491a2d4165",
    ),
    JarEntry(
        group="io.github.skylot",
        artifact="jadx-input-api",
        version="1.5.5",
        sha256="36ca994ab67f8a4cecd080ed98cd04cde0af7d9807da49e45523783cb4ca159e",
    ),
    JarEntry(
        group="io.github.skylot",
        artifact="jadx-zip",
        version="1.5.5",
        sha256="f38eab046b9d17c912ff36d1268c2b2441a3050fe33d338231b2a35f259519e4",
    ),
    JarEntry(
        group="com.android.tools.smali",
        artifact="smali-baksmali",
        version="3.0.9",
        sha256="e7d0166945565a87f3997d1aea8779202dbb6cb0585a39ee20bab8a2f5ba87f6",
        base_url=_GOOGLE_MAVEN,
    ),
    JarEntry(
        group="com.android.tools.smali",
        artifact="smali-dexlib2",
        version="3.0.9",
        sha256="8b547506f62f91d74b70f4beb4989b99e1ff61fc50b2525e9796ca35f0a351dc",
        base_url=_GOOGLE_MAVEN,
    ),
    JarEntry(
        group="com.android.tools.smali",
        artifact="smali-util",
        version="3.0.9",
        sha256="4673762894ba4156081fc5c642f74d6e78aef8b1a9c7702d691e3171d8cc1153",
        base_url=_GOOGLE_MAVEN,
    ),
    JarEntry(
        group="com.google.guava",
        artifact="guava",
        version="33.5.0-jre",
        sha256="1e301f0c52ac248b0b14fdc3d12283c77252d4d6f48521d572e7d8c4c2cc4ac7",
    ),
    JarEntry(
        group="com.google.guava",
        artifact="failureaccess",
        version="1.0.3",
        sha256="cbfc3906b19b8f55dd7cfd6dfe0aa4532e834250d7f080bd8d211a3e246b59cb",
    ),
    JarEntry(
        group="com.google.code.gson",
        artifact="gson",
        version="2.13.2",
        sha256="dd0ce1b55a3ed2080cb70f9c655850cda86c206862310009dcb5e5c95265a5e0",
    ),
    JarEntry(
        group="org.slf4j",
        artifact="slf4j-api",
        version="2.0.17",
        sha256="7b751d952061954d5abfed7181c1f645d336091b679891591d63329c622eb832",
    ),
    JarEntry(
        group="org.slf4j",
        artifact="slf4j-simple",
        version="2.0.17",
        sha256="ddfea59ac074c6d3e24ac2c38622d2d963895e17f70b38ed4bdae4d780be6964",
    ),
    JarEntry(
        group="com.google.code.findbugs",
        artifact="jsr305",
        version="3.0.2",
        sha256="766ad2a0783f2687962c8ad74ceecc38a28b9f72a2d085ee438b7813e928d0c7",
    ),
]


def _cache_dir() -> Path:
    return Path.home() / ".pyjadx" / "jars" / JADX_VERSION


def _jar_url(entry: JarEntry) -> str:
    group_path = entry.group.replace(".", "/")
    return (
        f"{entry.base_url}/{group_path}/{entry.artifact}"
        f"/{entry.version}/{entry.artifact}-{entry.version}.jar"
    )


def _download_jar(url: str, dest: Path, expected_sha256: str) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".tmp")
    try:
        urllib.request.urlretrieve(url, filename=str(tmp))
        data = tmp.read_bytes()
        actual = hashlib.sha256(data).hexdigest()
        if actual != expected_sha256:
            tmp.unlink(missing_ok=True)
            msg = (
                f"SHA-256 mismatch for {dest.name}: "
                f"expected {expected_sha256}, got {actual}"
            )
            raise JarResolutionError(msg)
        tmp.rename(dest)
    except JarResolutionError:
        raise
    except Exception as exc:
        tmp.unlink(missing_ok=True)
        msg = f"failed to download {url}: {exc}"
        raise JarResolutionError(msg) from exc


def resolve_jars(jadx_home: str | None = None) -> list[Path]:
    home = jadx_home or os.environ.get("JADX_HOME")
    if home:
        lib_dir = Path(home) / "lib"
        return sorted(lib_dir.glob("*.jar"))

    manifest = JarManifest.for_version(JADX_VERSION)
    cache = _cache_dir()
    cache.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for entry in manifest.entries:
        jar_name = f"{entry.artifact}-{entry.version}.jar"
        dest = cache / jar_name
        if not dest.exists():
            url = _jar_url(entry)
            logger.info("downloading %s", url)
            _download_jar(url, dest, entry.sha256)
        paths.append(dest)
    return paths

# pyjadx

Python bindings for [JADX](https://github.com/skylot/jadx) via JPype. Decompile Android APK and DEX files to Java source from Python.

```python
from pyjadx import Jadx

with Jadx("app.apk") as jadx:
    for cls in jadx.classes:
        print(cls.full_name)
        print(cls.code)
```

## Why pyjadx?

JADX is the leading open-source Android decompiler — it produces clean Java/Kotlin source from Dalvik bytecode, preserving class hierarchies, generics, exception handling, and annotations. pyjadx brings this into Python without subprocess overhead: JADX runs in-process via JPype.

## Install

```bash
pip install pyjadx
```

**Requirements:** JDK 11+ (JADX JARs are downloaded automatically on first use).

## Quick start

```python
from pyjadx import Jadx

with Jadx("app.apk") as jadx:
    # All top-level classes (inner classes via cls.inner_classes)
    for cls in jadx.classes:
        print(cls.full_name, len(cls.methods), "methods")

    # Search by fully qualified name
    main = jadx.search_class("com.example.MainActivity")
    if main:
        print(main.code)

    # Method-level decompilation
    for method in main.methods:
        print(f"{method.name}: {method.code}")

    # Cross-references
    for method in main.methods:
        print(f"{method.name} called by: {[c.name for c in method.callers]}")

    # Package navigation
    for pkg in jadx.packages:
        print(pkg.name, len(pkg.classes), "classes")
```

## Supported inputs

| Format | Example |
|--------|---------|
| APK | `Jadx("app.apk")` |
| DEX | `Jadx("classes.dex")` |
| Multi-DEX APK | Handled transparently — all classes merged |

## API reference

### `Jadx(path, *, threads=None, mode="auto", code_cache=False)`

Main entry point. Use as a context manager or call `load()`/`close()` manually.

| Parameter | Description |
|-----------|-------------|
| `path` | Path to APK or DEX file |
| `threads` | JADX thread pool size (`None` = CPU count) |
| `mode` | `"auto"`, `"restructure"`, `"simple"`, or `"fallback"` |
| `code_cache` | `False` = in-memory cache (default), `True` = disk-backed |

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `classes` | `list[JavaClass]` | Top-level classes across all DEX files |
| `packages` | `list[JavaPackage]` | Package-level navigation |
| `class_count` | `int` | Number of top-level classes |
| `java` | `JObject` | Escape hatch to underlying `jadx.api.JadxDecompiler` |

**Methods:**

| Method | Description |
|--------|-------------|
| `load()` | Load and resolve classes (called by `__enter__`) |
| `close()` | Release resources (called by `__exit__`) |
| `decompile_all()` | Eagerly decompile all classes |
| `search_class(name)` | Find class by fully qualified name |

### `JavaClass`

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | Short name (`"MainActivity"`) |
| `full_name` | `str` | Fully qualified (`"com.example.MainActivity"`) |
| `package` | `str` | Package name |
| `code` | `str` | Decompiled Java source (lazy, cached) |
| `smali` | `str` | Smali disassembly (lazy, cached) |
| `methods` | `list[JavaMethod]` | Methods in this class |
| `fields` | `list[JavaField]` | Fields in this class |
| `inner_classes` | `list[JavaClass]` | Inner/anonymous classes |
| `declaring_class` | `JavaClass \| None` | Parent class (if inner) |
| `top_class` | `JavaClass` | Outermost enclosing class |
| `dependencies` | `list[JavaClass]` | Classes this class depends on |
| `is_inner` | `bool` | Whether this is an inner class |
| `java` | `JObject` | Escape hatch to `jadx.api.JavaClass` |

### `JavaMethod`

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | Method name |
| `full_name` | `str` | Fully qualified with class |
| `code` | `str` | Decompiled source (lazy, cached) |
| `callers` | `list[JavaMethod]` | Methods that call this one (lazy, cached) |
| `callees` | `list[JavaMethod]` | Methods this one calls (lazy, cached) |
| `override_related` | `list[JavaMethod]` | Bidirectional override chain |
| `declaring_class` | `JavaClass` | Class this method belongs to |
| `java` | `JObject` | Escape hatch to `jadx.api.JavaMethod` |

### `JavaField`

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | Field name |
| `full_name` | `str` | Fully qualified with class |
| `type` | `str` | Field type as string |
| `callers` | `list[JavaMethod]` | Methods referencing this field (lazy, cached) |
| `declaring_class` | `JavaClass` | Class this field belongs to |
| `java` | `JObject` | Escape hatch to `jadx.api.JavaField` |

### `JavaPackage`

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | Full package name |
| `classes` | `list[JavaClass]` | Classes in this package |
| `sub_packages` | `list[JavaPackage]` | Sub-packages |
| `java` | `JObject` | Escape hatch to `jadx.api.JavaPackage` |

## Escape hatch

Every wrapper exposes its underlying JADX Java object via `.java`. This lets you call any JADX API we haven't wrapped yet:

```python
with Jadx("app.apk") as jadx:
    cls = jadx.search_class("com.example.Foo")
    # Call JADX Java API directly
    code_info = cls.java.getCodeInfo()
```

## JVM coexistence

pyjadx coexists with other JPype consumers (e.g., [PyGhidra](https://github.com/NationalSecurityAgency/ghidra/tree/master/Ghidra/Features/PyGhidra)) in the same process. If a JVM is already running, `pyjadx.start()` adds JADX JARs to the existing classpath. If not, it starts one.

```python
import pyghidra
pyghidra.start()  # starts JVM for Ghidra

import pyjadx
pyjadx.start()    # adds JADX JARs to existing JVM — no conflict
```

## Configuration

**Custom JADX installation:**

```python
# Via environment variable
# export JADX_HOME=/opt/jadx

# Or at runtime
import pyjadx
pyjadx.start(jadx_home="/opt/jadx")
```

**JAR caching:** JADX JARs are auto-downloaded from Maven Central on first use and cached at `~/.pyjadx/jars/<version>/`.

## License

MIT

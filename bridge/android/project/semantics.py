"""Bounded, local projections. Free-form code, strings, keys and payloads stay in the input."""

from __future__ import annotations

import io
import json
import re
import struct
from pathlib import PurePosixPath
from urllib.parse import urlsplit

from .layout import inspect_xml
from .model import HIDDEN, SENSITIVE, Report, identifier, safe_literal
from .xmltree import plain

HTTP = re.compile(
    r'@(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s*\(\s*"([^"\n]{1,1024})"'
)
SYMBOL = re.compile(r"\b(class|interface|object|fun|fragment)\s+([A-Za-z_$][\w$]*)")
BILLING = re.compile(
    r"\b(BillingClient|PurchasesUpdatedListener|onPurchasesUpdated|launchBillingFlow|queryPurchasesAsync|acknowledgePurchase|ProductDetails|BillingResult)\b"
)
FRAMEWORKS = {
    "androidx.compose.": "Jetpack Compose",
    "com.facebook.react": "React Native",
    "org.apache.cordova": "Cordova",
    "package:flutter/": "Flutter",
    "UnityEngine": "Unity",
    "android.webkit.WebView": "WebView",
}
KNOWN_ABIS = {
    "armeabi",
    "armeabi-v7a",
    "arm64-v8a",
    "x86",
    "x86_64",
    "mips",
    "mips64",
    "riscv64",
}


def route(text: str) -> dict:
    try:
        parsed = urlsplit(text)
        segments = parsed.path.split("/")
        # Free-form token-like segments, URI userinfo, parameter values and fragments are excluded.
        path = "/".join(
            s
            if re.fullmatch(
                r"(?:[a-zA-Z][a-zA-Z_-]{0,28}|v\d{1,3}|\{[a-zA-Z_]{1,32}\}|)", s
            )
            and not SENSITIVE.search(s)
            else "{redacted}"
            for s in segments
        )
        return {
            "route": path,
            "host": parsed.hostname
            if parsed.hostname
            and re.fullmatch(r"[A-Za-z0-9.-]{1,200}", parsed.hostname)
            else None,
            "query_names": [
                identifier(part.split("=")[0])
                for part in parsed.query.split("&")
                if part and "=" in part
            ],
        }
    except ValueError:
        return {"route": HIDDEN, "host": None, "query_names": []}


def source(report: Report, f: dict, data: bytes) -> None:
    text = data.decode("utf-8-sig")
    lang = {
        "kt": "Kotlin",
        "kts": "Kotlin DSL",
        "java": "Java",
        "dart": "Dart",
        "cs": "C#",
        "smali": "Smali",
        "ts": "TypeScript",
        "tsx": "TypeScript",
        "js": "JavaScript",
        "jsx": "JavaScript",
    }.get(f["type"])
    if lang:
        report.fact(f, "technology", "source extension", {"name": lang})
    frameworks = set()
    pending_compose = False
    for i, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith(("//", "*", "#")) or len(line) > 16384:
            if len(line) > 16384:
                report.issue(f["id"], f"Line {i} exceeded source scanner limit")
            continue
        loc = f"line {i}"
        if SENSITIVE.search(line) and re.search(
            r'[:=]\s*["\']\S|BEGIN .*PRIVATE KEY', line
        ):
            report.fact(
                f,
                "sensitive",
                loc,
                {"kind": "possible credential literal", "value": "[redacted]"},
            )
        for key, name in FRAMEWORKS.items():
            if key in line and name not in frameworks:
                report.fact(
                    f,
                    "technology",
                    loc + " " + name,
                    {"name": name},
                    "PARTIALLY_ANALYZED",
                    "inferred",
                )
                frameworks.add(name)
        pending_compose = pending_compose or "@Composable" in line
        for match in SYMBOL.finditer(line):
            kind, name = match.groups()
            compose = pending_compose and kind == "fun"
            report.fact(
                f,
                "source-symbol",
                f"{loc}:{match.start() + 1}",
                {
                    "kind": kind,
                    "name": name,
                    "compose_declaration": compose,
                    "language": lang,
                },
                "PARTIALLY_ANALYZED",
            )
            if compose:
                pending_compose = False
        java = re.search(
            r"\b(?:public|private|protected)\s+(?:(?:final|static|synchronized|abstract)\s+)*[\w.$<>\[\],?]+\s+([A-Za-z_$][\w$]*)\s*\(",
            line,
        )
        if java:
            report.fact(
                f,
                "source-symbol",
                f"{loc}:{java.start(1) + 1}",
                {"kind": "method", "name": java[1], "language": lang},
                "PARTIALLY_ANALYZED",
            )
        for match in re.finditer(r"\bsetContentView\(\s*R\.layout\.(\w+)\s*\)", line):
            report.fact(
                f,
                "layout-binding",
                f"{loc}:{match.start() + 1}",
                {
                    "symbol": "@layout/" + match[1],
                    "kind": "setContentView source expression",
                },
                "PARTIALLY_ANALYZED",
                "inferred",
            )
        for match in HTTP.finditer(line):
            method, url = match.groups()
            report.fact(
                f,
                "endpoint",
                f"{loc}:{match.start() + 1}",
                dict(
                    **route(url),
                    method=method,
                    kind="Retrofit annotation candidate",
                    caller=None,
                    request=None,
                    response=None,
                    authentication=None,
                    screen=None,
                ),
                "PARTIALLY_ANALYZED",
                "inferred",
            )
        for match in re.finditer(r'\bbaseUrl\s*\(\s*"(https?://[^"\s]+)"', line):
            report.fact(
                f,
                "endpoint",
                f"base {loc}:{match.start() + 1}",
                dict(**route(match[1]), method=None, kind="base URL literal"),
                "PARTIALLY_ANALYZED",
                "inferred",
            )
        for pattern, cat in [
            (BILLING, "billing"),
            (
                re.compile(
                    r"\b(RoomDatabase|SQLiteOpenHelper|DataStore|SharedPreferences)\b"
                ),
                "storage",
            ),
            (
                re.compile(
                    r"\b(setOnClickListener|setOnLongClickListener|setOnTouchListener|setContentView|findNavController|navigate)\b"
                ),
                "interaction",
            ),
        ]:
            for m in pattern.finditer(line):
                report.fact(
                    f,
                    cat,
                    f"{loc}:{m.start() + 1}",
                    {"reference": m[1], "behavior": "UNKNOWN"},
                    "PARTIALLY_ANALYZED",
                    "inferred",
                )
        for m in re.finditer(
            r"""\b(?:implementation|api|compileOnly|runtimeOnly)\s*\(?\s*["']([\w.-]+):([\w.-]+):([\w.+-]+)["']""",
            line,
        ):
            report.fact(
                f,
                "dependency",
                f"{loc}:{m.start() + 1}",
                {
                    "name": f"{m[1]}:{m[2]}",
                    "version": m[3],
                    "kind": "Gradle declaration",
                    "license": None,
                    "compatibility": None,
                },
            )
        refs = re.findall(
            r"\bR\.(layout|drawable|string|id|menu|navigation|color|dimen|style|font)\.(\w+)",
            line,
        )
        f["dependencies"].extend("@" + k + "/" + v for k, v in refs)
    f.update(decoding="source pattern scan", status="PARTIALLY_ANALYZED")


def dex(report: Report, f: dict, data: bytes) -> None:
    from loguru import logger

    logger.disable("androguard")
    from androguard.core.dex import DEX

    if (
        len(data) < 112
        or not data.startswith(b"dex\n")
        or data[7] != 0
        or int.from_bytes(data[32:36], "little") != len(data)
    ):
        raise ValueError("Invalid standalone DEX header")
    vm = DEX(data)
    families = set()
    for cls in vm.get_classes():
        name = cls.get_name()
        annotations = cls.get_annotations()
        for prefix, family in (
            ("Landroidx/compose/", "Jetpack Compose"),
            ("Lcom/facebook/react/", "React Native"),
            ("Lorg/apache/cordova/", "Cordova"),
            ("Lio/flutter/", "Flutter"),
            ("Lcom/unity3d/", "Unity"),
        ):
            if name.startswith(prefix) and family not in families:
                report.fact(
                    f,
                    "technology",
                    name,
                    {"name": family, "marker": name},
                    "PARTIALLY_ANALYZED",
                    "inferred",
                )
                families.add(family)
        report.fact(
            f,
            "class",
            name,
            {
                "name": name,
                "superclass": cls.get_superclassname(),
                "interfaces": cls.get_interfaces(),
                "flags": cls.get_access_flags_string(),
                "annotations": annotations,
                "language_evidence": "Kotlin metadata"
                if "Lkotlin/Metadata;" in annotations
                else None,
            },
        )
        for member in cls.get_fields():
            key = name + "->" + member.get_name() + ":" + member.get_descriptor()
            report.fact(
                f,
                "field",
                key,
                {
                    "owner": name,
                    "name": member.get_name(),
                    "descriptor": member.get_descriptor(),
                },
            )
        for method in cls.get_methods():
            signature = name + "->" + method.get_name() + method.get_descriptor()
            flags = method.get_access_flags_string()
            refs, unsupported = set(), set()
            for _, ins in method.get_instructions_idx():
                opcode = ins.get_name()
                if opcode.startswith("invoke-"):
                    if opcode.split("/")[0] in {
                        "invoke-direct",
                        "invoke-super",
                        "invoke-static",
                        "invoke-interface",
                        "invoke-virtual",
                    }:
                        owner, label, proto = vm.get_cm_method(ins.get_ref_kind())
                        refs.add(owner + "->" + label + "".join(proto))
                    else:
                        unsupported.add(opcode)
            for family, prefixes in (
                (
                    "billing",
                    ("Lcom/android/billingclient/", "Lcom/android/vending/billing/"),
                ),
                (
                    "storage",
                    (
                        "Landroid/database/sqlite/",
                        "Landroid/content/SharedPreferences;",
                    ),
                ),
            ):
                used = sorted(x for x in refs if x.startswith(prefixes))
                if used:
                    report.fact(
                        f,
                        family,
                        signature,
                        {
                            "caller": signature,
                            "references": used,
                            "behavior": "UNKNOWN",
                        },
                        "PARTIALLY_ANALYZED",
                    )
            report.fact(
                f,
                "method",
                signature,
                {
                    "owner": name,
                    "name": method.get_name(),
                    "descriptor": method.get_descriptor(),
                    "flags": flags,
                    "direct_references": sorted(refs),
                    "unresolved_opcodes": sorted(unsupported),
                    "reflection_reference": any(
                        x.startswith("Ljava/lang/reflect/") for x in refs
                    ),
                },
                "PARTIALLY_ANALYZED" if unsupported else "ANALYZED",
            )
    f.update(
        decoding="DEX declarations and standard invoke operands",
        status="PARTIALLY_ANALYZED",
    )


def resource_table(report: Report, f: dict, data: bytes) -> None:
    from loguru import logger

    logger.disable("androguard")
    from androguard.core.axml import ARSCParser

    table = ARSCParser(data)
    for package in table.get_packages_names():
        seen = set()
        for locale in sorted(table.get_locales(package)):
            for n in plain(table.get_public_resources(package, locale)):
                ident = n.get("id", "").replace("0x", "@").upper()
                if ident in seen:
                    continue
                seen.add(ident)
                symbol = f"@{n.get('type')}/{n.get('name')}"
                report.fact(
                    f,
                    "resource-id",
                    package + ":" + ident,
                    {"package": package, "numeric": ident, "symbol": symbol},
                )
            for idx, n in enumerate(plain(table.get_string_resources(package, locale))):
                name = n.get("name", "")
                value = (
                    HIDDEN
                    if SENSITIVE.search(name)
                    else safe_literal(n.text, report.labels)
                )
                report.fact(
                    f,
                    "value",
                    f"{package}:{locale}:{idx}",
                    {
                        "symbol": "@string/" + name,
                        "kind": "string",
                        "value": value,
                        "qualifier": "default" if locale == "\x00\x00" else locale,
                    },
                )
    f.update(
        decoding="compiled public resource IDs and string tables",
        status="PARTIALLY_ANALYZED",
    )


def inspect(report: Report, f: dict, data: bytes) -> None:
    name, category, ext = f["name"], f["category"], f["type"]
    p = PurePosixPath(f["location"])
    try:
        if category == "library":
            abi = next((part for part in p.parts if part in KNOWN_ABIS), None)
            elf_machine = (
                struct.unpack("<H" if data[5:6] == b"\x01" else ">H", data[18:20])[0]
                if data.startswith(b"\x7fELF") and len(data) >= 20
                else None
            )
            report.fact(
                f,
                "dependency",
                "packaged file",
                {
                    "name": name,
                    "kind": ext,
                    "abi": abi,
                    "elf_machine": elf_machine,
                    "version": None,
                    "license": None,
                    "compatibility": None,
                },
            )
        for marker, label in (
            ("libflutter.so", "Flutter"),
            ("flutter_assets", "Flutter"),
            ("libreactnative.so", "React Native"),
            ("index.android.bundle", "React Native"),
            ("libunity.so", "Unity"),
            ("cordova.js", "Cordova"),
        ):
            if marker in p.parts:
                report.fact(
                    f,
                    "technology",
                    "path:" + marker,
                    {"name": label, "marker": marker},
                    "PARTIALLY_ANALYZED",
                    "inferred",
                )
        if ext == "xml" or ext == "svg":
            inspect_xml(report, f, data)
        elif ext == "dex":
            dex(report, f, data)
        elif name == "resources.arsc":
            resource_table(report, f, data)
        elif (
            category == "code"
            or ext == "gradle"
            or name.endswith(".gradle.kts")
            or ext == "properties"
        ):
            source(report, f, data)
        elif ext in {"png", "jpg", "jpeg", "webp", "gif", "avif", "bmp", "ico"}:
            from PIL import Image

            with Image.open(io.BytesIO(data)) as img:
                report.fact(
                    f,
                    "visual",
                    "header",
                    {
                        "format": img.format,
                        "width_px": img.width,
                        "height_px": img.height,
                        "nine_patch": name.endswith(".9.png"),
                        "density": f["qualifier"],
                    },
                )
            f.update(status="ANALYZED", decoding="image header")
        elif ext in {"otf", "ttf", "ttc", "woff", "woff2"}:
            report.fact(
                f,
                "visual",
                "font header",
                {"format": ext, "header_hex": data[:4].hex(), "dimensions": None},
            )
        elif ext == "json":
            tree = json.loads(data)
            if (
                isinstance(tree, dict)
                and {"v", "layers", "fr", "ip", "op"} <= tree.keys()
            ):
                report.fact(
                    f,
                    "visual",
                    "animation",
                    {
                        "format": "Lottie",
                        "width_px": tree.get("w")
                        if isinstance(tree.get("w"), int)
                        else None,
                        "height_px": tree.get("h")
                        if isinstance(tree.get("h"), int)
                        else None,
                    },
                )
            todo = [(tree, "$")]
            while todo:
                node, loc = todo.pop()
                if isinstance(node, dict):
                    for idx, (key, value) in enumerate(node.items()):
                        child = f"{loc}/field[{idx}]"
                        if SENSITIVE.search(key):
                            report.fact(
                                f,
                                "sensitive",
                                child,
                                {
                                    "kind": "possible credential field",
                                    "value": "[redacted]",
                                },
                            )
                        elif isinstance(value, (list, dict)):
                            todo.append((value, child))
                elif isinstance(node, list):
                    todo.extend(
                        (v, f"{loc}[{i}]")
                        for i, v in enumerate(node)
                        if isinstance(v, (list, dict))
                    )
            f.update(status="PARTIALLY_ANALYZED", decoding="JSON structural scan")
        elif data.startswith(b"SQLite format 3\x00"):
            report.fact(
                f, "storage", "header", {"format": "SQLite 3", "contents": "unexamined"}
            )
            f.update(status="PARTIALLY_ANALYZED", decoding="database header")
        elif ext in {"pem", "p12", "pfx", "jks", "keystore", "key"} or name == ".env":
            report.fact(
                f,
                "sensitive",
                "file",
                {
                    "kind": "possible private configuration or key material",
                    "value": "[redacted]",
                },
            )
    except ImportError as exc:
        dependency = "Pillow" if exc.name == "PIL" else "androguard==4.1.3"
        f.update(
            status="NOT_SUPPORTED",
            decoding=f"Missing optional parser. Install {dependency}",
        )
        report.issue(f["id"], f["decoding"], "NOT_SUPPORTED")
    except Exception as exc:  # noqa: BLE001 - isolate third-party parser failures per occurrence
        # Parser messages may contain literal input. Retain type and occurrence only.
        reason = "Semantic parser failed (" + type(exc).__name__ + ")"
        if isinstance(exc, ValueError) and exc.args == (
            "Report fact budget exhausted",
        ):
            reason = "Report fact budget exhausted"
        f.update(status="PARTIALLY_ANALYZED", decoding=reason)
        report.issue(f["id"], reason)

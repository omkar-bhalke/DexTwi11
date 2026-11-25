"""Project declaration-level facts from XML. Missing declarations stay unknown."""

from __future__ import annotations

import re

from . import xmltree
from .model import (
    COL,
    DIM,
    HIDDEN,
    SENSITIVE,
    Report,
    identifier,
    resource,
    safe_literal,
)

ANDROID = "{http://schemas.android.com/apk/res/android}"
UI = {
    "id",
    "text",
    "hint",
    "contentDescription",
    "textSize",
    "fontFamily",
    "textFontWeight",
    "textStyle",
    "textColor",
    "background",
    "backgroundTint",
    "layout_width",
    "layout_height",
    "x",
    "y",
    "translationX",
    "translationY",
    "layout_gravity",
    "gravity",
    "radius",
    "strokeWidth",
    "strokeColor",
    "elevation",
    "alpha",
    "visibility",
    "enabled",
    "clickable",
    "src",
    "icon",
    "animation",
    "onClick",
    "orientation",
    "weightSum",
    "layout_weight",
    "style",
    "layout",
    "inputType",
    "maxLines",
    "textAlignment",
    "drawableStart",
    "drawableEnd",
    "drawableLeft",
    "drawableRight",
    "tint",
    "name",
    "class",
    "startDestination",
    "destination",
}
DANGEROUS = {
    "CAMERA": "Camera access",
    "RECORD_AUDIO": "Microphone access",
    "ACCESS_FINE_LOCATION": "Precise location",
    "ACCESS_COARSE_LOCATION": "Approximate location",
    "READ_CONTACTS": "Read contacts",
    "WRITE_CONTACTS": "Edit contacts",
    "READ_PHONE_STATE": "Phone state",
    "READ_SMS": "Read SMS",
    "SEND_SMS": "Send SMS",
    "READ_EXTERNAL_STORAGE": "Shared storage",
    "POST_NOTIFICATIONS": "Post notifications",
    "READ_MEDIA_IMAGES": "Shared images",
    "BLUETOOTH_CONNECT": "Paired Bluetooth devices",
}
ENUM = re.compile(r"[a-zA-Z_][\w|-]{0,70}\Z", re.ASCII)
COMPONENT = {"activity", "activity-alias", "service", "receiver", "provider"}
PREFIXES = (
    "padding",
    "layout_margin",
    "layout_constraint",
    "layout_align",
    "layout_to",
)


def local(name: str) -> str:
    return name.split("}")[-1]


def attr(node, name):
    return node.get(ANDROID + name)


def ui_attributes(node, labels) -> dict:
    result = {}
    for raw, v in node.attrib.items():
        k = local(raw)
        if k not in UI and not k.startswith(PREFIXES):
            continue
        if "}" in raw and not raw.startswith(ANDROID):
            k = "{" + raw.split("}")[0][1:] + "}" + k
        if k in {"text", "hint", "contentDescription"}:
            value = safe_literal(v, labels)
        elif resource(v) or DIM.fullmatch(v) or COL.fullmatch(v):
            value = v
        elif k in {"name", "class", "onClick", "fontFamily"}:
            value = identifier(v)
        elif ENUM.fullmatch(v):
            value = v
        else:
            value = HIDDEN
        result[k] = value
    return result


def manifest(report: Report, f: dict, root) -> None:
    if local(root.tag) != "manifest":
        raise ValueError("Invalid manifest root")
    app = root.find("application")
    sdk = root.find("uses-sdk")
    m = {
        "package": identifier(root.get("package")),
        "split": identifier(root.get("split")),
        "config_for_split": identifier(
            root.get("configForSplit") or attr(root, "configForSplit")
        ),
        "uses_splits": [
            identifier(attr(n, "name")) for n in root.findall("uses-split")
        ],
        "label": safe_literal(attr(app, "label"), report.labels)
        if app is not None
        else None,
        "version_name": identifier(attr(root, "versionName")),
        "version_code": identifier(attr(root, "versionCode")),
        "min_sdk": identifier(attr(sdk, "minSdkVersion")) if sdk is not None else None,
        "target_sdk": identifier(attr(sdk, "targetSdkVersion"))
        if sdk is not None
        else None,
    }
    report.fact(f, "package", "manifest", m)
    for i, n in enumerate(root.iter()):
        if not isinstance(n.tag, str):
            continue
        tag = local(n.tag)
        loc = f"{tag}[{i}]"
        if tag in (
            "uses-permission",
            "uses-permission-sdk-23",
            "permission",
            "permission-group",
        ):
            name = identifier(attr(n, "name"))
            purpose = DANGEROUS.get((name or "").removeprefix("android.permission."))
            report.fact(
                f,
                "permission",
                loc,
                {
                    "kind": tag,
                    "name": name,
                    "known_runtime_permission_purpose": purpose,
                    "protection_level": identifier(attr(n, "protectionLevel")),
                    "max_sdk": identifier(attr(n, "maxSdkVersion")),
                },
            )
        if tag in COMPONENT:
            filters = []
            for filt in n.findall("intent-filter"):
                filters.append(
                    {
                        "actions": [
                            identifier(attr(a, "name")) for a in filt.findall("action")
                        ],
                        "categories": [
                            identifier(attr(a, "name"))
                            for a in filt.findall("category")
                        ],
                        "data": [
                            {
                                k: identifier(attr(a, k))
                                for k in (
                                    "scheme",
                                    "host",
                                    "port",
                                    "mimeType",
                                    "pathPrefix",
                                )
                            }
                            for a in filt.findall("data")
                        ],
                    }
                )
            report.fact(
                f,
                "component",
                loc,
                {
                    "kind": tag,
                    "name": identifier(attr(n, "name")),
                    "filters": filters,
                    "declarations": {
                        k: identifier(attr(n, k))
                        for k in (
                            "exported",
                            "enabled",
                            "permission",
                            "authorities",
                            "grantUriPermissions",
                            "readPermission",
                            "writePermission",
                            "targetActivity",
                        )
                    },
                },
            )
        if tag == "application":
            report.fact(
                f,
                "security",
                loc,
                {
                    k: identifier(attr(n, k))
                    for k in (
                        "allowBackup",
                        "debuggable",
                        "usesCleartextTraffic",
                        "networkSecurityConfig",
                        "fullBackupContent",
                        "dataExtractionRules",
                    )
                },
            )


def inspect_xml(report: Report, f: dict, data: bytes) -> None:
    root, fmt = xmltree.parse(
        data, report.target["format"] == "aab" or "/manifest/" in f["location"]
    )
    f["decoding"] = fmt
    if f["category"] == "manifest":
        manifest(report, f, root)
    tag = local(root.tag)
    if tag == "resources":
        for idx, n in enumerate(root):
            if not isinstance(n.tag, str):
                continue
            name = identifier(n.get("name"))
            kind = identifier(n.get("type") or local(n.tag))
            if not name or not kind:
                continue
            value = (n.text or "").strip()
            ref = f"@{kind}/{name}"
            safe = resource(value) or (
                value
                if kind in {"dimen", "color", "integer", "bool"}
                and (
                    DIM.fullmatch(value)
                    or COL.fullmatch(value)
                    or value in ("true", "false")
                )
                else safe_literal(value, report.labels)
            )
            report.fact(
                f,
                "value",
                f"child[{idx}]",
                {
                    "symbol": ref,
                    "kind": kind,
                    "value": HIDDEN if SENSITIVE.search(name) else safe,
                    "qualifier": f["qualifier"],
                    "parent": identifier(n.get("parent")),
                },
            )
            if SENSITIVE.search(name):
                report.fact(
                    f,
                    "sensitive",
                    f"child[{idx}]",
                    {"kind": "possible credential field", "value": "[redacted]"},
                )
    if tag == "vector":
        report.fact(
            f,
            "visual",
            "vector",
            {
                "format": "Android vector",
                "dimensions": [
                    v if v and (DIM.fullmatch(v) or resource(v)) else None
                    for v in (attr(root, "width"), attr(root, "height"))
                ],
                "viewport": [
                    v if v and DIM.fullmatch(v) else None
                    for v in (attr(root, "viewportWidth"), attr(root, "viewportHeight"))
                ],
            },
        )
    if tag == "network-security-config":
        for i, n in enumerate(root.iter()):
            if local(n.tag) in {
                "base-config",
                "domain-config",
                "certificates",
                "pin-set",
            }:
                report.fact(
                    f,
                    "security",
                    f"node[{i}]",
                    {
                        "kind": local(n.tag),
                        "cleartext": identifier(n.get("cleartextTrafficPermitted")),
                        "certificate_source": identifier(n.get("src")),
                    },
                )
    is_ui = f["category"] in {"layout", "navigation", "menu"}
    if is_ui:
        screen = report.fact(
            f,
            "layout",
            "root",
            {
                "symbol": f["resource"],
                "qualifier": f["qualifier"],
                "kind": f["category"],
            },
        )
    queue = [(root, None, "0")]
    refs = set()
    while queue:
        n, parent, index = queue.pop()
        if not isinstance(n.tag, str):
            continue
        refs.update(ref for v in n.attrib.values() if (ref := resource(v)))
        if is_ui:
            attrs = ui_attributes(n, report.labels)
            el = report.fact(
                f,
                "element",
                index,
                {
                    "layout": screen["id"],
                    "parent": parent["id"] if parent else None,
                    "children": [],
                    "element_type": local(n.tag),
                    "attributes": attrs,
                    "runtime_bounds_px": None,
                    "normalized_coordinates": None,
                    "source": f["location"] + "#" + index,
                },
            )
            if parent:
                parent["data"]["children"].append(el["id"])
            if attrs.get("onClick"):
                report.fact(
                    f,
                    "interaction",
                    index,
                    {
                        "element": el["id"],
                        "callback": attrs["onClick"],
                        "kind": "android:onClick declaration",
                        "effect": "UNKNOWN",
                    },
                    "PARTIALLY_ANALYZED",
                )
            if f["category"] == "navigation":
                report.fact(
                    f,
                    "navigation",
                    index,
                    {
                        "kind": local(n.tag),
                        "destination": attrs.get("destination"),
                        "name": attrs.get("name"),
                        "id": attrs.get("id"),
                        "start": attrs.get("startDestination"),
                    },
                )
        queue.extend(
            (child, el if is_ui else None, f"{index}.{i}")
            for i, child in reversed(list(enumerate(n)))
        )
    f["dependencies"] = sorted(refs)
    f["status"] = "PARTIALLY_ANALYZED" if "warnings" in fmt else "ANALYZED"
    if "warnings" in fmt:
        report.issue(
            f["id"],
            "Binary XML decoder flagged a noncanonical encoding. Recovered declarations need corroboration.",
        )

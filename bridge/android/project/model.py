"""Report-local evidence, deterministic identities, and safe scalar projections."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Any

SCHEMA = "rea.android-project/1"
HIDDEN = "[withheld]"
STATES = (
    "DISCOVERED",
    "ANALYZED",
    "VERIFIED",
    "PARTIALLY_ANALYZED",
    "UNKNOWN",
    "NOT_SUPPORTED",
    "REQUIRES_RUNTIME",
    "REQUIRES_USER_INPUT",
)
SENSITIVE = re.compile(
    r"(?i)password|passwd|secret|(?:api|private|access|merchant)[_-]?key|(?:auth|access|refresh|session|purchase)[_-]?token|authorization|credential|bearer|BEGIN .*PRIVATE KEY"
)
IDENT = re.compile(r"[\w.$:/+?@{}#-]{1,240}\Z", re.ASCII)
RESOURCE = re.compile(r"[@?]\+?(?:[\w.]+:)?[\w]+/[\w.]+\Z")
DIM = re.compile(r"-?\d+(?:\.\d+)?(?:dp|dip|sp|px|pt|in|mm|%|%p)?\Z")
COL = re.compile(r"#[0-9a-fA-F]{3,8}\Z")


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def item_id(*parts: Any) -> str:
    return digest(canonical(parts))[:32]


def identifier(value: str | None) -> str | None:
    return value if value and IDENT.fullmatch(value) else None


def resource(value: str | None) -> str | None:
    if value and (
        RESOURCE.fullmatch(value) or re.fullmatch(r"[@?](?:0x)?[\da-fA-F]{8}", value)
    ):
        return value
    return None


def safe_literal(value: str | None, allowed: frozenset[str]) -> str | None:
    if value is None:
        return None
    return resource(value) or (
        value if value in allowed and not SENSITIVE.search(value) else HIDDEN
    )


@dataclass
class Report:
    target: dict[str, Any]
    labels: frozenset[str] = field(default_factory=frozenset, repr=False)
    files: list[dict] = field(default_factory=list)
    facts: list[dict] = field(default_factory=list)
    issues: list[dict] = field(default_factory=list)
    max_facts: int = 150000
    _occurrences: Counter = field(default_factory=Counter, init=False, repr=False)

    def unique_id(self, *parts: Any) -> str:
        base = item_id(*parts)
        self._occurrences[base] += 1
        ordinal = self._occurrences[base]
        return base if ordinal == 1 else item_id(base, ordinal)

    def issue(
        self, location: str, reason: str, status: str = "PARTIALLY_ANALYZED"
    ) -> None:
        self.issues.append(
            {
                "id": self.unique_id("issue", location, reason),
                "category": "limitation",
                "location": location,
                "status": status,
                "evidence": location,
                "confidence": "observed",
                "reason": reason,
                "dependencies": [],
                "reconstruction_status": "PENDING_REVIEW",
            }
        )

    def fact(
        self,
        file: dict,
        category: str,
        locator: str,
        data: dict,
        status: str = "ANALYZED",
        confidence: str = "observed",
    ) -> dict:
        if len(self.facts) >= self.max_facts:
            raise ValueError("Report fact budget exhausted")
        row = {
            "id": self.unique_id(file["id"], category, locator),
            "category": category,
            "location": locator,
            "status": status,
            "evidence": file["id"],
            "confidence": confidence,
            "dependencies": [],
            "reconstruction_status": "PENDING_REVIEW",
            "data": data,
        }
        self.facts.append(row)
        return row

    def export(self) -> dict:
        return {
            "schema": SCHEMA,
            "target": self.target,
            "files": self.files,
            "observations": self.facts,
            "element_specification": {
                "identity": "id; data.attributes.id is the original Android ID when declared",
                "hierarchy": ["layout", "element_type", "parent", "children", "source"],
                "attributes": "Missing keys represent unknown or undeclared values. Resource tokens retain their source spelling.",
                "static_fields": [
                    "text",
                    "hint",
                    "textSize",
                    "fontFamily",
                    "textFontWeight",
                    "textStyle",
                    "textColor",
                    "background",
                    "layout_width",
                    "layout_height",
                    "layout_margin*",
                    "padding*",
                    "x",
                    "y",
                    "translationX",
                    "translationY",
                    "textAlignment",
                    "layout_gravity",
                    "gravity",
                    "radius",
                    "strokeColor",
                    "strokeWidth",
                    "elevation",
                    "alpha",
                    "visibility",
                    "enabled",
                    "clickable",
                    "icon",
                    "src",
                    "animation",
                    "onClick",
                ],
                "geometry": "dp, sp, px and other explicit units are preserved. Runtime rectangles use physical pixels.",
                "behavior": "A callback declaration does not establish execution or effects.",
            },
            "limitations": self.issues,
            "coverage": {
                "file_occurrences": len(self.files),
                "hashed": sum(bool(x["sha256"]) for x in self.files),
                "file_statuses": dict(
                    sorted(Counter(x["status"] for x in self.files).items())
                ),
                "observation_categories": dict(
                    sorted(Counter(x["category"] for x in self.facts).items())
                ),
                "inventory_scope": "Enumerated files, nested APK members and explicit omissions",
                "runtime_behavior": "REQUIRES_RUNTIME",
            },
            "approval": {
                "state": "AWAITING_USER_DECISION",
                "actions": ["YES", "NO", "REVIEW", "EXPORT"],
            },
            "reconstruction_plan": [
                "Review layout variants, resource references, substitutions and unresolved observations.",
                "Confirm scope and rights for the UI specifications. Select YES for this report digest.",
                "Generate a native Android layout project. Review the generated mapping for every element.",
                "Supply authorized navigation, backend, storage and billing contracts for unresolved behavior.",
                "Build and exercise on a controlled emulator. Compare matched screenshots and record results.",
            ],
        }


def file_category(path: str) -> tuple[str, str | None, str | None]:
    p = PurePosixPath(path)
    parts = p.parts
    if p.name == "AndroidManifest.xml":
        return "manifest", None, None
    if "res" in parts:
        idx = len(parts) - 1 - parts[::-1].index("res")
        if len(parts) == idx + 3:
            kind, _, qualifier = parts[idx + 1].partition("-")
            return kind, qualifier or "default", f"@{kind}/{p.name.split('.')[0]}"
    ext = p.suffix.lower()
    groups = {
        "dex": ("dex",),
        "code": ("java", "kt", "kts", "dart", "cs", "js", "ts", "tsx", "jsx", "smali"),
        "font": ("otf", "ttf", "woff", "woff2", "ttc"),
        "image": ("png", "jpg", "jpeg", "gif", "webp", "svg", "avif"),
        "audio": ("mp3", "ogg", "wav", "m4a"),
        "video": ("mp4", "webm", "mkv"),
        "database": ("db", "sqlite", "sqlite3"),
        "library": ("aar", "jar", "so"),
        "configuration": ("json", "xml", "gradle", "properties", "toml", "yaml", "yml"),
        "package": ("apk",),
        "signature": ("rsa", "dsa", "sf", "ec"),
    }
    if p.name.lower().startswith(("license", "licence", "notice", "copying")):
        return "license", None, None
    return (
        next(
            (k for k, exts in groups.items() if ext[1:] in exts),
            "asset" if "assets" in parts else "other",
        ),
        None,
        None,
    )

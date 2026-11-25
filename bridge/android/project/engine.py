"""Assemble a single report from local files and existing REA signing Evidence."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path

from .inputs import FORMATS, Inventory, Limits
from .model import Report, item_id, safe_literal
from .semantics import inspect
from .xmltree import plain

ROOT = Path(__file__).resolve().parents[3]
BRIDGE = ROOT / "bridge/android/project-evidence.mjs"


def file_hash(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def signing(report: Report, row: dict, path: Path) -> None:
    if not (ROOT / "dist/domain/evidence.js").is_file() or not shutil.which("node"):
        report.issue(
            row["id"],
            "Signing requires built REA. Run npm ci and npm run build:cached in the repository.",
            "NOT_SUPPORTED",
        )
        return
    try:
        proc = subprocess.run(
            ["node", str(BRIDGE), "signature", str(path.resolve())],
            cwd=path.parent,
            capture_output=True,
            timeout=90,
            check=True,
        )
        evidence = json.loads(proc.stdout)
        if (
            evidence["operation"] != "inspect_apk_signature"
            or evidence["subject"]["digest"]["sha256"] != row["sha256"]
            or not re.fullmatch(r"ev_[0-9a-f]{64}", evidence["evidence_id"])
        ):
            raise ValueError("Subject or Evidence identity mismatch")
        payload = evidence["normalized_result"]
        schemes = {}
        for k, v in payload["schemes"].items():
            schemes[k] = {
                "present": v["present"],
                "signers": [
                    {
                        "fingerprint": (s.get("certificate") or {}).get(
                            "sha256_fingerprint"
                        ),
                        "content_digest_matches": [
                            d["matches_apk"] for d in s.get("digests", [])
                        ],
                    }
                    for s in v["signers"]
                ],
            }
        report.fact(
            row,
            "signature",
            "REA APK signing Evidence",
            {
                "rea_evidence_id": evidence["evidence_id"]
                if row["id"] == "input"
                else None,
                "provider": evidence["provider"]["id"],
                "provenance": "REA signing service; nested temporary paths are excluded from persistent identity",
                "artifact_sha256": row["sha256"],
                "schemes": schemes,
                "scope": "Declared schemes, certificates and selected content digests",
                "limitations": evidence["limitations"],
            },
        )
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError):
        report.issue(
            row["id"],
            "REA signature operation failed or returned mismatched evidence",
            "UNKNOWN",
        )


def link_resources(report: Report) -> None:
    by_id = {f["id"]: f for f in report.files}
    symbols = defaultdict(set)
    numeric = defaultdict(set)
    values = defaultdict(set)

    def scope(f):
        p = f["location"].split("/")
        if "src" in p:
            return tuple(f["container"]), "/".join(p[: p.index("src") + 2])
        if report.target["format"] == "aab":
            return tuple(f["container"]), p[0]
        return tuple(f["container"]), ""

    for f in report.files:
        if f["resource"] and f["category"] != "values":
            symbols[scope(f), f["resource"]].add(f["id"])
    for obs in report.facts:
        d = obs["data"]
        if obs["category"] in {"resource-id", "value"}:
            key = scope(by_id[obs["evidence"]])
            if obs["category"] == "resource-id":
                numeric[key, d["numeric"]].add(d["symbol"])
            else:
                symbols[key, d["symbol"]].add(obs["evidence"])
                if d["qualifier"] == "default":
                    values[key, d["symbol"]].add(d["value"])
    for f in report.files:
        key = scope(f)
        refs = sorted(set(f["dependencies"]))
        rows = []
        for ref in refs:
            mapped = numeric.get((key, ref.upper()), set()) or {ref.replace("@+", "@")}
            targets = sorted({t for s in mapped for t in symbols.get((key, s), set())})
            rows.append(
                {
                    "reference": ref,
                    "symbols": sorted(mapped),
                    "candidates": targets,
                    "status": "DISCOVERED" if targets else "UNKNOWN",
                }
            )
            for t in targets:
                by_id[t]["used_by"].append(f["id"])
        f["dependencies"] = rows
    callbacks = defaultdict(list)
    for obs in report.facts:
        if obs["category"] in {"method", "source-symbol"} and obs["data"].get(
            "kind", "method"
        ) in {"method", "fun"}:
            callbacks[obs["data"]["name"]].append(obs["id"])
    for obs in report.facts:
        if obs["category"] == "interaction" and obs["data"].get("callback"):
            obs["data"]["name_matched_method_candidates"] = callbacks.get(
                obs["data"]["callback"], []
            )
            obs["data"]["effect"] = "UNKNOWN"
        if obs["category"] != "package":
            continue
        d = obs["data"]
        key = scope(by_id[obs["evidence"]])
        label = d.get("label") or ""
        candidates = numeric.get((key, label.upper()), set()) or {label}
        labels = {v for s in candidates for v in values.get((key, s), set()) if v}
        d["default_label"] = next(iter(labels)) if len(labels) == 1 else None


def split_relationships(report: Report) -> None:
    packages = [o for o in report.facts if o["category"] == "package"]
    for o in packages:
        d = o["data"]
        if not d["split"] and not d["uses_splits"]:
            continue
        needs = {x for x in d["uses_splits"] if x}
        if d["split"]:
            needs.add(d["config_for_split"])
        for name in sorted(needs, key=lambda n: n or ""):
            matches = [
                p
                for p in packages
                if p is not o
                and p["data"]["split"] == name
                and d["package"]
                and p["data"]["package"] == d["package"]
                and p["data"]["version_code"] == d["version_code"]
            ]
            o["dependencies"].extend(p["id"] for p in matches)
            if len(matches) != 1:
                report.issue(
                    o["id"],
                    "Missing or ambiguous matching split dependency: "
                    + (name or "base"),
                    "UNKNOWN",
                )


def runtime_observation(
    report: Report, path: Path, image: Path | None, screen: str | None
) -> None:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 8 << 20:
        raise ValueError("Expected a UI Automator XML file under 8 MiB")
    content = path.read_bytes()
    root = plain(content)
    if root.tag != "hierarchy":
        raise ValueError("Runtime input must be a UI Automator hierarchy")
    row = {"id": item_id("runtime", hashlib.sha256(content).hexdigest())}
    capture = {
        "hierarchy_sha256": hashlib.sha256(content).hexdigest(),
        "screen": screen,
        "screenshot": None,
        "association": "Caller-supplied capture; package, timestamp and workflow identity are unverified",
    }
    if image:
        from PIL import Image

        if image.is_symlink() or not image.is_file():
            raise ValueError("Screenshot must be a regular file")
        with Image.open(image) as img:
            img.verify()
            capture["screenshot"] = {
                "sha256": file_hash(image),
                "dimensions_px": [img.width, img.height],
            }
    observation = report.fact(row, "runtime", "capture", capture)
    for i, n in enumerate(root.iter("node")):
        coords = re.fullmatch(
            r"\[(-?\d+),(-?\d+)\]\[(-?\d+),(-?\d+)\]", n.get("bounds", "")
        )
        report.fact(
            row,
            "runtime-element",
            f"node[{i}]",
            {
                "capture": observation["id"],
                "element_type": n.get("class"),
                "resource": n.get("resource-id"),
                "bounds_px": list(map(int, coords.groups())) if coords else None,
                "text": safe_literal(n.get("text"), report.labels),
                "clickable": n.get("clickable"),
                "enabled": n.get("enabled"),
            },
        )


def analyze(
    path: Path,
    *,
    labels=frozenset(),
    limits=None,
    progress=lambda n: None,
    runtime=None,
    screenshot=None,
    screen=None,
    sign=True,
    rea_evidence=(),
) -> dict:
    if path.is_symlink() or not (path.is_file() or path.is_dir()):
        raise ValueError("Select a regular Android package or a directory")
    path = path.resolve()
    fmt = "directory" if path.is_dir() else path.suffix.lower().lstrip(".")
    if not path.is_dir() and "." + fmt not in FORMATS:
        raise ValueError(
            "Supported inputs are APK, APKS, XAPK, AAB or an Android directory"
        )
    target = {
        "name": path.name,
        "format": fmt,
        "bytes": None,
        "sha256": None,
        "hash_scope": "entire file",
    }
    report = Report(target, frozenset(labels))

    def signature(r, f, p):
        if sign:
            signing(r, f, p)
        else:
            r.issue(f["id"], "Signature analysis disabled for this run", "UNKNOWN")

    inventory = Inventory(report, inspect, signature, limits or Limits(), progress)
    if path.is_dir():
        inventory.directory(path)
    else:
        before = path.stat()
        target.update(bytes=before.st_size, sha256=file_hash(path))
        inventory.archive(path, (), "." + fmt)
        if fmt in {"apk", "aab"}:
            signature(report, {"id": "input", "sha256": target["sha256"]}, path)
        after = path.stat()
        if (before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        ):
            raise ValueError("Input changed during analysis. Select a stable copy.")
    for path_to_evidence in rea_evidence:
        if (
            path_to_evidence.is_symlink()
            or not path_to_evidence.is_file()
            or path_to_evidence.stat().st_size > 32 << 20
        ):
            raise ValueError("Expected a regular REA Evidence JSON file under 32 MiB")
        try:
            proc = subprocess.run(
                ["node", str(BRIDGE), "import", str(path_to_evidence.resolve())],
                capture_output=True,
                check=True,
                timeout=90,
            )
            evidence = json.loads(proc.stdout)
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            raise ValueError(
                "Cannot authenticate the selected Evidence with built REA"
            ) from exc
        subjects = [
            f["id"]
            for f in report.files
            if f["sha256"] and f["sha256"] == evidence["artifact_sha256"]
        ]
        if target["sha256"] and target["sha256"] == evidence["artifact_sha256"]:
            subjects.append("input")
        if not subjects:
            raise ValueError(
                "REA Evidence subject digest does not match this input or any member"
            )
        for subject in subjects:
            report.fact(
                {"id": subject},
                "provider-evidence",
                evidence["rea_evidence_id"],
                evidence,
            )
    link_resources(report)
    split_relationships(report)
    if runtime:
        runtime_observation(report, runtime, screenshot, screen)
    elif screenshot or screen:
        raise ValueError("Runtime associations require an accompanying hierarchy")
    return report.export()

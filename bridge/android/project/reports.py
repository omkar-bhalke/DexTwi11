"""Three views of the same report snapshot. Local HTML uses DOM text nodes."""

from __future__ import annotations

import hashlib
import html
import json
import shutil
from collections import Counter
from contextlib import contextmanager
from pathlib import Path

from .engine import file_hash
from .model import SCHEMA, canonical, digest

QUESTION = (
    "Application analysis is complete. I have prepared the screen inventory, layout specifications, UI element mapping, "
    "assets, functionality, API contracts, dependencies, permissions, billing analysis, and reconstruction plan.\n\n"
    "Would you like to begin authorized application reconstruction?"
)
SECTIONS = [
    (
        "Application overview",
        "package technology",
        "Review observed package declarations and technology indicators.",
    ),
    (
        "Package information",
        "package signature",
        "Each declaration retains its source manifest. Signature posture is reported by the existing REA provider.",
    ),
    (
        "Original technology stack",
        "technology",
        "Source extensions, annotations and runtime filenames provide different levels of evidence.",
    ),
    (
        "Screen inventory",
        "layout component source-symbol",
        "A layout variant, component or function is a screen candidate. One-to-one correspondence requires corroboration.",
    ),
    (
        "Layout hierarchy",
        "hierarchy",
        "The parent and ordered children identify the declared hierarchy in each layout variant.",
    ),
    (
        "UI element inventory",
        "element",
        "An element location is the zero-based child path from the layout root.",
    ),
    (
        "UI dimensions and typography",
        "element runtime-element",
        "Static units retain their declarations. Runtime captures use physical pixels.",
    ),
    (
        "Asset inventory",
        "files visual value resource-id",
        "All file occurrences are listed. Resolved references identify candidate uses.",
    ),
    (
        "Source and DEX analysis",
        "class field method source-symbol provider-evidence",
        "Method descriptors distinguish overloads. Recovered declarations describe compiled or supplied evidence.",
    ),
    (
        "Functionality mapping",
        "interaction",
        "Source patterns and callback declarations need execution or additional code to establish effects.",
    ),
    (
        "API inventory",
        "endpoint",
        "Routes describe source declarations. Authentication, payloads and responses are unknown unless independently observed.",
    ),
    (
        "Library inventory",
        "dependency",
        "A packaged library or Gradle declaration alone cannot establish its license or execution.",
    ),
    (
        "Permission analysis",
        "permission",
        "Declared permissions are distinct from runtime grants. Purpose annotations cover a subset of Android permissions.",
    ),
    (
        "Security findings",
        "security sensitive signature",
        "Credential findings disclose a location and type with a redacted value.",
    ),
    (
        "Billing analysis",
        "billing",
        "Purchase references are declarations. Merchant configuration, verification and entitlement require owner evidence.",
    ),
    (
        "Navigation architecture",
        "navigation component layout-binding",
        "Navigation XML and intent-filter declarations identify possible transitions.",
    ),
    (
        "Database and local storage",
        "storage",
        "Storage API references and database headers do not disclose stored records.",
    ),
    (
        "Runtime observations",
        "runtime runtime-element",
        "Each capture represents one caller-supplied state. Matched screenshot hashes identify observed pixels.",
    ),
    (
        "Missing information",
        "limitations",
        "Unresolved references also appear on individual file records. Dynamic behavior requires further evidence.",
    ),
    (
        "Reconstruction dependencies",
        "dependency value resource-id",
        "Review variants, referenced resources, unsupported views and service contracts.",
    ),
    (
        "Compatibility risks",
        "limitations",
        "Validate platform, theme, language, density and configuration selection on target devices.",
    ),
    (
        "Reuse authorization",
        "rights",
        "Every file starts with REQUIRES_USER_INPUT. This report grants no asset or library rights.",
    ),
    (
        "Reconstruction plan",
        "plan",
        "Explicit approval binds the generator to a particular report.",
    ),
    (
        "Coverage statistics",
        "coverage",
        "Hash coverage counts bytes read. Observation categories count evidence, independently of behavioral coverage.",
    ),
]


@contextmanager
def new_directory(path: Path):
    if not path.parent.is_dir():
        raise ValueError("Choose an existing output parent")
    path.mkdir(mode=0o700)
    try:
        yield path
    except BaseException:
        shutil.rmtree(path)
        raise


def json_file(path: Path, obj) -> str:
    h = hashlib.sha256()
    encoder = json.JSONEncoder(
        ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False
    )
    with path.open("wb") as stream:
        for part in encoder.iterencode(obj):
            b = part.encode()
            h.update(b)
            stream.write(b)
        stream.write(b"\n")
        h.update(b"\n")
    return h.hexdigest()


def read_report(folder: Path, expected: str | None = None) -> tuple[dict, str]:
    path = folder / "report.json"
    if path.is_symlink() or not path.is_file():
        raise ValueError("Expected a regular report.json in the selected directory")
    raw = path.read_bytes()
    identity = digest(raw)
    if expected and expected != identity:
        raise ValueError("Report SHA-256 differs from the reviewed digest")
    r = json.loads(raw)
    if r.get("schema") != SCHEMA:
        raise ValueError("Unsupported report schema")
    return r, identity


def table_cell(value) -> str:
    return (
        html.escape(str(value))
        .replace("|", "&#124;")
        .replace("\n", " ")
        .replace("\r", " ")
    )


def layout_trees(report: dict) -> list[dict]:
    files = {f["id"]: f for f in report["files"]}
    trees = {}
    for row in report["observations"]:
        d = row["data"]
        if row["category"] == "layout":
            source = files[row["evidence"]]
            trees[row["id"]] = {
                "location": source["location"],
                "status": source["status"],
                "evidence": row["id"],
                "qualifier": d["qualifier"],
                "tree": [],
            }
        elif row["category"] == "element":
            attrs = d["attributes"]
            width, height = attrs.get("layout_width"), attrs.get("layout_height")
            size = f" ({width or '?'} × {height or '?'})" if width or height else ""
            name = " ".join(
                str(x)
                for x in (d["element_type"], attrs.get("id"), attrs.get("text"))
                if x
            )
            depth = row["location"].count(".")
            trees[d["layout"]]["tree"].append("  " * min(depth, 128) + name + size)
    return list(trees.values())


def markdown(r: dict, dest: Path, trees: list[dict]) -> None:
    with dest.open("w", encoding="utf-8") as w:
        w.write("# Android application analysis\n\n")
        w.write(
            f"**{table_cell(r['target']['name'])}** · {r['target']['format']} · {len(r['files'])} file occurrences\n\n"
        )
        w.write("Input SHA-256: `" + str(r["target"]["sha256"]) + "`\n\n")
        for title, filters, note in SECTIONS:
            keys = filters.split()
            counts = {
                k: r["coverage"]["observation_categories"].get(k, 0) for k in keys
            }
            w.write(f"## {title}\n\n{note}\n\n")
            if "hierarchy" in keys:
                if not trees:
                    w.write("No XML layout trees were recovered.\n\n")
                for tree in trees:
                    w.write(
                        "### "
                        + table_cell(tree["location"])
                        + "\n\n<pre>"
                        + html.escape("\n".join(tree["tree"]))
                        + "</pre>\n\n"
                    )
            elif "coverage" in keys:
                w.write(json.dumps(r["coverage"], ensure_ascii=True) + "\n\n")
            elif "plan" in keys:
                w.write(
                    "\n".join("- " + step for step in r["reconstruction_plan"]) + "\n\n"
                )
            elif "limitations" in keys:
                reasons = Counter(i["reason"] for i in r["limitations"])
                w.write(
                    "".join(f"- {table_cell(k)} ({v})\n" for k, v in reasons.items())
                    or "No processing limitations recorded.\n"
                )
                w.write("\n")
            elif "rights" in keys:
                w.write(
                    "Original asset and library reuse requires a separate rights decision.\n\n"
                )
            else:
                if "files" in keys:
                    counts["files"] = len(r["files"])
                w.write(
                    ", ".join(f"{k}: {v}" for k, v in counts.items())
                    + ". See the evidence ledger below.\n\n"
                )
        w.write("## Evidence ledger\n\n")
        for name, rows in (
            ("File inventory", r["files"]),
            ("Observations", r["observations"]),
            ("Processing limitations", r["limitations"]),
        ):
            w.write(
                f"### {name}\n\n| Category | Location | Status | Evidence and details |\n| --- | --- | --- | --- |\n"
            )
            for row in rows:
                data = {
                    k: v
                    for k, v in row.items()
                    if k not in {"category", "location", "status"}
                }
                w.write(
                    "| "
                    + " | ".join(
                        table_cell(x)
                        for x in (
                            row["category"],
                            row["location"],
                            row["status"],
                            json.dumps(data, ensure_ascii=True),
                        )
                    )
                    + " |\n"
                )
            w.write("\n")
        w.write(
            "## Reconstruction decision\n\n"
            + QUESTION
            + "\n\nYES · NO · REVIEW · EXPORT\n"
        )


def publish(report: dict, dest: Path) -> str:
    with new_directory(dest):
        sha = json_file(dest / "report.json", report)
        trees = layout_trees(report)
        markdown(report, dest / "report.md", trees)
        template = Path(__file__).with_name("viewer.html").read_text(encoding="utf-8")
        payload = (
            canonical(
                {"report": report, "sections": SECTIONS, "digest": sha, "trees": trees}
            )
            .decode()
            .replace("<", "\\u003c")
            .replace(">", "\\u003e")
            .replace("&", "\\u0026")
        )
        (dest / "report.html").write_text(
            template.replace("{{PAYLOAD}}", payload), encoding="utf-8"
        )
        (dest / "SHA256SUMS").write_text(
            "".join(
                f"{file_hash(dest / n)}  {n}\n"
                for n in ("report.json", "report.md", "report.html")
            ),
            encoding="ascii",
        )
    return sha

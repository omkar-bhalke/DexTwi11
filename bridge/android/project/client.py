"""CLI and MCP share artifact admission, reporting and decision checks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .engine import analyze
from .inputs import ChangedInput, Limits
from .reconstruct import decide, generate
from .reports import QUESTION, new_directory, publish, read_report
from .validation import validate
from .visual import compare


def checked_output(src: Path, dest: Path):
    if dest.exists() or dest.is_symlink():
        raise FileExistsError("Output must be a new directory")
    if src.is_dir() and dest.resolve().is_relative_to(src.resolve()):
        raise ValueError("Place the report outside the selected input tree")


def export_report(folder: Path, destination: Path) -> dict:
    import shutil

    read_report(folder)
    with new_directory(destination):
        for n in ("report.html", "report.json", "report.md", "SHA256SUMS"):
            shutil.copyfile(folder / n, destination / n)
    return {"destination": str(destination)}


def cli(args=None) -> int:
    parser = argparse.ArgumentParser(
        prog="rea android-project",
        description="Local Android project analysis and approved layout reconstruction",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    a = sub.add_parser(
        "analyze",
        help="Inventory an Android package or directory and publish three report formats",
    )
    a.add_argument("input", type=Path)
    a.add_argument("--out", required=True, type=Path)
    a.add_argument(
        "--approved-ui-text",
        type=Path,
        help="JSON array of reviewed, non-sensitive UI strings allowed in the reports",
    )
    a.add_argument("--runtime-xml", type=Path)
    a.add_argument("--screenshot", type=Path)
    a.add_argument(
        "--screen", help="Caller-provided screen identifier for the hierarchy capture"
    )
    a.add_argument("--max-entries", type=int, default=Limits.entries)
    a.add_argument("--max-total-mib", type=int, default=Limits.total >> 20)
    a.add_argument("--max-parse-mib", type=int, default=Limits.parse >> 20)
    a.add_argument(
        "--rea-evidence",
        action="append",
        default=[],
        type=Path,
        help="Attach a complete, subject-matched REA Android Evidence JSON record",
    )
    a.add_argument("--without-signature", action="store_true")
    a.add_argument("--quiet", action="store_true")
    r = sub.add_parser("review", help="Read a report or search its retained evidence")
    r.add_argument("report", type=Path)
    r.add_argument("--category")
    r.add_argument("--find")
    r.add_argument("--offset", type=int, default=0)
    r.add_argument("--limit", type=int, default=50)
    d = sub.add_parser(
        "decide", help="Record a human YES or NO bound to the displayed SHA-256"
    )
    d.add_argument("report", type=Path)
    d.add_argument("decision", choices=["YES", "NO"])
    d.add_argument("--sha256", required=True)
    d.add_argument("--destination", type=Path)
    d.add_argument(
        "--asset-grants",
        type=Path,
        help="JSON map of reviewed file IDs to authorized local bitmap paths",
    )
    g = sub.add_parser(
        "reconstruct",
        help="Generate the native layout project approved for this report",
    )
    g.add_argument("report", type=Path)
    g.add_argument("--sha256", required=True)
    e = sub.add_parser(
        "export", help="Copy three reports and their checksums into a new folder"
    )
    e.add_argument("report", type=Path)
    e.add_argument("--out", type=Path, required=True)
    c = sub.add_parser("compare", help="Compare a pair of local screenshots")
    c.add_argument("original", type=Path)
    c.add_argument("candidate", type=Path)
    c.add_argument("--out", type=Path, required=True)
    v = sub.add_parser(
        "validate",
        help="Verify generated sources and XML. Optionally build with a selected Gradle executable",
    )
    v.add_argument("project", type=Path)
    v.add_argument("--out", type=Path, required=True)
    v.add_argument("--gradle", type=Path)
    m = sub.add_parser("mcp", help="Serve the project tools over MCP stdio")
    m.add_argument("--input-root", required=True, type=Path)
    m.add_argument("--output-root", required=True, type=Path)
    opt = parser.parse_args(args)
    try:
        if opt.command == "analyze":
            checked_output(opt.input, opt.out)
            if min(opt.max_entries, opt.max_total_mib, opt.max_parse_mib) < 1:
                raise ValueError("Analysis budgets must be positive")
            labels = (
                json.loads(opt.approved_ui_text.read_text())
                if opt.approved_ui_text
                else []
            )
            if not isinstance(labels, list) or not all(
                isinstance(s, str) and len(s) <= 512 for s in labels
            ):
                raise ValueError(
                    "UI text file must be an array of strings of at most 512 characters"
                )

            def progress(n):
                if not opt.quiet:
                    print(
                        json.dumps({"event": "inventory", "files": n}),
                        file=sys.stderr,
                        flush=True,
                    )

            report = analyze(
                opt.input,
                labels=labels,
                limits=Limits(
                    entries=opt.max_entries,
                    total=opt.max_total_mib << 20,
                    parse=opt.max_parse_mib << 20,
                ),
                runtime=opt.runtime_xml,
                screenshot=opt.screenshot,
                screen=opt.screen,
                progress=progress,
                sign=not opt.without_signature,
                rea_evidence=opt.rea_evidence,
            )
            sha = publish(report, opt.out)
            result = overview(report, sha, opt.out)
        elif opt.command == "review":
            report, sha = read_report(opt.report)
            result = (
                search(report, opt.category, opt.find, opt.offset, opt.limit)
                if opt.find or opt.category
                else overview(report, sha, opt.report)
            )
        elif opt.command == "decide":
            result = decide(
                opt.report,
                opt.decision,
                opt.sha256,
                opt.destination,
                json.loads(opt.asset_grants.read_text()) if opt.asset_grants else None,
            )
        elif opt.command == "reconstruct":
            result = generate(opt.report, opt.sha256)
        elif opt.command == "validate":
            result = validate(opt.project, opt.out, opt.gradle)
            if result["checks"]["build"] == "FAILED":
                print(json.dumps(result, indent=2))
                return 1
        elif opt.command == "compare":
            result = compare(opt.original, opt.candidate, opt.out)
        elif opt.command == "export":
            result = export_report(opt.report, opt.out)
        else:
            from .server import serve

            serve(opt.input_root, opt.output_root)
            return 0
        print(json.dumps(result, indent=2, ensure_ascii=True))
        return 0
    except KeyboardInterrupt:
        print('{"error":"cancelled"}', file=sys.stderr)
        return 130
    except ImportError as exc:
        print(
            json.dumps(
                {
                    "error": "Optional dependency unavailable",
                    "module": exc.name,
                    "install": "See the Android project guide",
                }
            ),
            file=sys.stderr,
        )
        return 2
    except (
        ChangedInput,
        OSError,
        ValueError,
        TypeError,
        KeyError,
        RuntimeError,
    ) as exc:
        print(
            json.dumps({"error": type(exc).__name__, "message": str(exc)}),
            file=sys.stderr,
        )
        return 2


def overview(report, sha, folder):
    return {
        "target": report["target"],
        "packages": [
            x["data"] for x in report["observations"] if x["category"] == "package"
        ],
        "architectures": sorted(
            {
                x["data"]["abi"]
                for x in report["observations"]
                if x["category"] == "dependency" and x["data"].get("abi")
            }
        ),
        "signatures": [
            x["data"] for x in report["observations"] if x["category"] == "signature"
        ],
        "coverage": report["coverage"],
        "limitations": len(report["limitations"]),
        "report_sha256": sha,
        "reports": [
            str(folder / n) for n in ("report.html", "report.json", "report.md")
        ],
        "question": QUESTION,
        "actions": report["approval"]["actions"],
    }


def search(report, category=None, query=None, offset=0, limit=50):
    if offset < 0 or not 1 <= limit <= 200:
        raise ValueError("Use a nonnegative offset and a limit from 1 through 200")
    rows = []
    total = 0
    for group in ("files", "observations", "limitations"):
        for row in report[group]:
            if category and category not in (group, row["category"]):
                continue
            if (
                query
                and query.casefold()
                not in json.dumps(row, ensure_ascii=False).casefold()
            ):
                continue
            if offset <= total < offset + limit:
                rows.append(row)
            total += 1
    return {
        "total": total,
        "offset": offset,
        "rows": rows,
        "next_offset": offset + limit if offset + limit < total else None,
    }

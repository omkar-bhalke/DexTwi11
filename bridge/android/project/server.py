"""Optional MCP stdio adapter. Only the human CLI can grant reconstruction approval."""

from __future__ import annotations

import re
from pathlib import Path

from .client import checked_output, overview, search
from .engine import analyze
from .reconstruct import generate
from .reports import publish, read_report


def serve(input_root: Path, output_root: Path) -> None:
    from mcp.server.fastmcp import FastMCP

    input_root, output_root = (
        input_root.resolve(strict=True),
        output_root.resolve(strict=True),
    )
    if (
        not input_root.is_dir()
        or not output_root.is_dir()
        or output_root.is_relative_to(input_root)
        or input_root.is_relative_to(output_root)
    ):
        raise ValueError(
            "Select separate input and output directories outside one another"
        )
    host = FastMCP("REA Android projects")

    def receipt_folder(name):
        if not re.fullmatch(r"[A-Za-z0-9][\w.-]{0,80}", name):
            raise ValueError("Choose a simple output directory name")
        folder = output_root / name
        if folder.is_symlink():
            raise ValueError("Symlinks cannot select a report")
        return folder

    @host.tool()
    def analyze_android_project(relative_input: str, report_name: str) -> dict:
        """Analyze a caller-selected input under the configured root. Publish JSON, HTML and Markdown. Stop for review."""
        src = (input_root / relative_input).resolve(strict=True)
        if not src.is_relative_to(input_root):
            raise ValueError("Input is outside configured root")
        out = receipt_folder(report_name)
        checked_output(src, out)
        report = analyze(src)
        return overview(report, publish(report, out), out)

    @host.tool()
    def read_android_project(
        report_name: str,
        category: str = "",
        query: str = "",
        offset: int = 0,
        limit: int = 40,
    ) -> dict:
        """Page report evidence by category or search text, with the report digest."""
        report, sha = read_report(receipt_folder(report_name))
        return dict(report_sha256=sha, **search(report, category, query, offset, limit))

    @host.tool()
    def reconstruct_approved_android_project(
        report_name: str, report_sha256: str, destination_name: str
    ) -> dict:
        """Generate layout resources only when the human's local YES matches the digest and destination."""
        return generate(
            receipt_folder(report_name), report_sha256, receipt_folder(destination_name)
        )

    host.run(transport="stdio")

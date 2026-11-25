"""Validate generator output and optionally build a fresh snapshot of the generated files."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path, PurePosixPath

from .engine import file_hash
from .reconstruct import CHECKS
from .reports import json_file, new_directory
from .xmltree import plain


def validate(project: Path, out: Path, gradle: Path | None = None) -> dict:
    """Build in a temporary workspace to keep the checked source and receipts intact."""
    if out.resolve().is_relative_to(project.resolve()):
        raise ValueError("Place validation output outside the generated project")
    receipt = json.loads((project / "reconstruction.json").read_text())
    sources = receipt["generated_files"]
    results = {k: "UNTESTED" for k in CHECKS}
    with (
        new_directory(out),
        tempfile.TemporaryDirectory(prefix="rea-validate-") as temp,
    ):
        stage = Path(temp)
        for name, expected in sources.items():
            parts = PurePosixPath(name)
            if (
                parts.is_absolute()
                or ".." in parts.parts
                or "\\" in name
                or ":" in name
            ):
                raise ValueError("Invalid generated file path")
            src = project / name
            if (
                src.is_symlink()
                or not src.resolve().is_relative_to(project.resolve())
                or not src.is_file()
            ):
                raise ValueError("Missing or redirected generated file")
            copy = stage / name
            copy.parent.mkdir(exist_ok=True, parents=True)
            shutil.copyfile(src, copy)
            if file_hash(copy) != expected:
                raise ValueError("Generated source changed since reconstruction")
            if copy.suffix == ".xml":
                plain(copy.read_bytes())
        report = {
            "report_sha256": receipt["report_sha256"],
            "source_integrity": "PASSED",
            "xml_parsing": "PASSED",
            "checks": results,
        }
        if gradle:
            exe = gradle.resolve(strict=True)
            try:
                result = subprocess.run(
                    [str(exe), "--no-daemon", "--console=plain", ":app:assembleDebug"],
                    cwd=stage,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=900,
                    check=False,
                )
                apk = stage / "app/build/outputs/apk/debug/app-debug.apk"
                results["build"] = (
                    "PASSED" if result.returncode == 0 and apk.is_file() else "FAILED"
                )
                report["build_exit_code"] = result.returncode
                if results["build"] == "PASSED":
                    shutil.copyfile(apk, out / "app-debug.apk")
                    report["debug_apk_sha256"] = file_hash(out / "app-debug.apk")
            except subprocess.TimeoutExpired:
                results["build"] = "FAILED"
                report["build_error"] = "Gradle deadline reached"
        json_file(out / "validation.json", report)
    return report

"""Bounded streaming traversal. Archive member names never become host paths."""

from __future__ import annotations

import hashlib
import os
import re
import stat
import tempfile
import zipfile
import zlib
from collections import Counter
from collections.abc import Callable
from contextlib import nullcontext
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import BinaryIO

from .model import Report, canonical, digest, file_category, item_id

CHUNK = 256 * 1024
FORMATS = {".apk", ".apks", ".xapk", ".aab"}
READ_ERRORS = (
    OSError,
    EOFError,
    ValueError,
    RuntimeError,
    NotImplementedError,
    zipfile.BadZipFile,
    zlib.error,
)


@dataclass
class Limits:
    entries: int = 100000
    total: int = 2 << 30
    member: int = 512 << 20
    parse: int = 12 << 20


class ChangedInput(Exception):
    """A whole report must be retried if a file changes after producing observations."""


class Inventory:
    def __init__(
        self,
        report: Report,
        inspect: Callable,
        signature: Callable,
        limits: Limits,
        progress: Callable[[int], None],
    ):
        self.report, self.inspect, self.signature, self.limits = (
            report,
            inspect,
            signature,
            limits,
        )
        self.progress = progress
        self.read_bytes = 0
        self.identities: Counter = Counter()
        self.top_files: list[dict] = []

    def row(self, container: tuple[str, ...], path: str, size: int | None) -> dict:
        if len(self.report.files) >= self.limits.entries:
            raise OverflowError(
                "File occurrence limit reached. Remaining entries were not enumerated."
            )
        key = (container, path)
        self.identities[key] += 1
        n = self.identities[key]
        cat, qualifier, symbol = file_category(path)
        identifier = item_id("file", container, path, n)
        row = {
            "id": identifier,
            "category": cat,
            "container": list(container),
            "location": path,
            "occurrence": n,
            "name": PurePosixPath(path).name,
            "type": PurePosixPath(path).suffix.lower().lstrip("."),
            "bytes": size,
            "sha256": None,
            "qualifier": qualifier,
            "resource": symbol,
            "status": "DISCOVERED",
            "decoding": "unexamined",
            "evidence": identifier,
            "confidence": "observed",
            "dependencies": [],
            "used_by": [],
            "reuse": "REQUIRES_USER_INPUT",
            "reconstruction_status": "PENDING_REVIEW",
        }
        self.report.files.append(row)
        if not container:
            self.top_files.append(row)
        if len(self.report.files) % 250 == 0:
            self.progress(len(self.report.files))
        if n > 1:
            self.report.issue(
                identifier, "Duplicate path. Occurrences retain separate identities."
            )
        return row

    def fail(self, row: dict, message: str, status: str = "PARTIALLY_ANALYZED") -> None:
        row.update(status=status, decoding=message)
        self.report.issue(row["id"], message, status)

    def read(self, row: dict, stream: BinaryIO, nested: bool) -> None:
        size = row["bytes"]
        if (
            size is None
            or size > self.limits.member
            or size > self.limits.total - self.read_bytes
        ):
            self.fail(row, "Member or cumulative decompressed byte budget exceeded")
            return
        h, count = hashlib.sha256(), 0
        # Only parseable small members are retained in RAM. Nested APKs spool to disk.
        buf = bytearray()
        with (
            tempfile.TemporaryDirectory(prefix="rea-project-")
            if nested
            else nullcontext() as directory
        ):
            tmp = Path(directory, "member.apk") if nested else None
            with tmp.open("wb") if tmp else nullcontext() as spool:
                while chunk := stream.read(CHUNK):
                    count += len(chunk)
                    self.read_bytes += len(chunk)
                    if (
                        count > size
                        or count > self.limits.member
                        or self.read_bytes > self.limits.total
                    ):
                        self.fail(row, "Read size exceeded declaration or budget")
                        return
                    h.update(chunk)
                    if spool:
                        spool.write(chunk)
                    elif size <= self.limits.parse:
                        buf.extend(chunk)
            if count != size:
                self.fail(row, "Read size differs from declared size")
                return
            row.update(sha256=h.hexdigest(), decoding="hashed", status="DISCOVERED")
            if nested:
                nested_id = (*row["container"], row["id"])
                self.archive(tmp, nested_id, ".apk")
                self.signature(self.report, row, tmp)
            elif size <= self.limits.parse:
                self.inspect(self.report, row, bytes(buf))
            else:
                self.fail(row, "Hashed. Semantic parser byte budget exceeded.")

    def archive(self, path: Path, container: tuple[str, ...], fmt: str) -> None:
        root = container[-1] if container else "input"
        try:
            # ZipFile loads its central directory before infolist() can enforce row budgets.
            # CPython's tail reader also resolves the ZIP64 trailer for this admission check.
            with path.open("rb") as raw:
                tail = zipfile._EndRecData(raw)
                if tail is None:
                    raise zipfile.BadZipFile("Missing central directory")
                if (
                    tail[zipfile._ECD_SIZE] > 16 << 20
                    or tail[zipfile._ECD_ENTRIES_TOTAL] > 250000
                ):
                    self.report.issue(
                        root,
                        "ZIP central directory exceeds admission budget; member list is unknown",
                    )
                    return
            with zipfile.ZipFile(path) as archive:
                entries = archive.infolist()
                names = {e.filename for e in entries}
                valid = (
                    "AndroidManifest.xml" in names
                    if fmt == ".apk"
                    else "BundleConfig.pb" in names
                    and "base/manifest/AndroidManifest.xml" in names
                    if fmt == ".aab"
                    else any(n.lower().endswith(".apk") for n in names)
                )
                if not valid:
                    self.report.issue(
                        root,
                        f"Missing required {fmt} structure or base manifest",
                        "UNKNOWN",
                    )
                for e in sorted(entries, key=lambda x: x.filename):
                    raw = e.orig_filename
                    if e.is_dir() and not (
                        e.external_attr >> 16 and stat.S_ISLNK(e.external_attr >> 16)
                    ):
                        continue
                    row = self.row(container, raw, e.file_size)
                    if (
                        raw.startswith(("/", "\\"))
                        or "\\" in raw
                        or ".." in raw.split("/")
                        or re.match(r"^[A-Za-z]:", raw)
                        or "\x00" in raw
                        or stat.S_ISLNK(e.external_attr >> 16)
                    ):
                        self.fail(row, "Unsafe path or symbolic link", "NOT_SUPPORTED")
                    elif e.flag_bits & 1:
                        self.fail(
                            row, "Encrypted archive member", "REQUIRES_USER_INPUT"
                        )
                    else:
                        try:
                            with archive.open(e) as member:
                                self.read(
                                    row,
                                    member,
                                    fmt in (".apks", ".xapk")
                                    and raw.lower().endswith(".apk"),
                                )
                        except READ_ERRORS as exc:
                            self.fail(row, f"Member read failed ({type(exc).__name__})")
        except READ_ERRORS as exc:
            self.report.issue(
                root, f"Unreadable archive ({type(exc).__name__})", "UNKNOWN"
            )
        except OverflowError as exc:
            self.report.issue(root, str(exc))

    def directory(self, path: Path) -> None:
        def walk(directory: Path):
            try:
                children = sorted(directory.iterdir())
            except OSError as exc:
                self.report.issue(
                    directory.relative_to(path).as_posix(),
                    f"Directory unreadable ({type(exc).__name__})",
                )
                return
            for child in children:
                name = child.relative_to(path).as_posix()
                try:
                    info = child.lstat()
                except OSError:
                    self.fail(self.row((), name, None), "Cannot stat entry")
                    continue
                if stat.S_ISDIR(info.st_mode):
                    if child.name == ".git":
                        self.report.issue(
                            name,
                            "Version control metadata outside application scope",
                            "NOT_SUPPORTED",
                        )
                    else:
                        yield from walk(child)
                else:
                    yield child, name, info

        try:
            for child, name, info in walk(path):
                row = self.row((), name, info.st_size)
                if not stat.S_ISREG(info.st_mode):
                    self.fail(row, "Symbolic link or special file", "NOT_SUPPORTED")
                    continue
                try:
                    flags = (
                        os.O_RDONLY
                        | getattr(os, "O_NOFOLLOW", 0)
                        | getattr(os, "O_NONBLOCK", 0)
                    )
                    with os.fdopen(os.open(child, flags), "rb") as stream:
                        before = os.fstat(stream.fileno())
                        if not os.path.samestat(info, before) or not stat.S_ISREG(
                            before.st_mode
                        ):
                            raise ValueError("File changed during open")
                        self.read(row, stream, name.lower().endswith(".apk"))
                        after = os.fstat(stream.fileno())
                        if (before.st_mtime_ns, before.st_ctime_ns) != (
                            after.st_mtime_ns,
                            after.st_ctime_ns,
                        ):
                            raise ChangedInput(
                                "Input changed during analysis. Select a stable copy."
                            )
                except READ_ERRORS as exc:
                    self.fail(
                        row, f"Unstable or unreadable file ({type(exc).__name__})"
                    )
                    row["sha256"] = None
        except (OverflowError, RecursionError) as exc:
            self.report.issue(
                "input", "Directory traversal limit reached: " + type(exc).__name__
            )
        complete = all(r["sha256"] for r in self.top_files) and not any(
            i["location"] == "input" or i["reason"].startswith("Directory unreadable")
            for i in self.report.issues
        )
        ordered = sorted(
            (r["location"], r["bytes"], r["sha256"]) for r in self.top_files
        )
        self.report.target.update(
            bytes=sum(r["bytes"] or 0 for r in self.top_files),
            sha256=digest(canonical(ordered)) if complete else None,
            hash_scope="canonical JSON of sorted [path, bytes, sha256] file triples; excludes .git",
        )
        if not any(r["category"] in ("manifest", "package") for r in self.report.files):
            self.report.issue(
                "input", "Directory contains no Android manifest or APK", "UNKNOWN"
            )

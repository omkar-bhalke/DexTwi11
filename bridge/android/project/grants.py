"""Resolve explicit, per-occurrence bitmap reuse grants against the reviewed inventory."""

from __future__ import annotations

import hashlib
import io
from pathlib import Path


def bind_assets(report: dict, grants: dict[str, str] | None) -> dict:
    if grants is None:
        return {}
    if not isinstance(grants, dict):
        raise TypeError("Asset grants must map file IDs to local bitmap paths")
    indexed = {r["id"]: r for r in report["files"]}
    bound = {}
    for identifier, value in grants.items():
        f = indexed.get(identifier)
        if (
            not f
            or not isinstance(value, str)
            or not f["sha256"]
            or f["type"] not in {"jpg", "jpeg", "png", "webp"}
        ):
            raise ValueError("Grant must name an inventoried, hashed PNG, JPEG or WebP")
        if f["name"].endswith(".9.png"):
            raise ValueError("Nine-patch conversion is unsupported")
        p = Path(value)
        if (
            p.is_symlink()
            or not p.is_file()
            or p.stat().st_size != f["bytes"]
            or f["bytes"] > 32 << 20
        ):
            raise ValueError(
                "Granted bitmap must be a regular matching file under 32 MiB"
            )
        with p.open("rb") as stream:
            if hashlib.file_digest(stream, "sha256").hexdigest() != f["sha256"]:
                raise ValueError("Granted bitmap does not match the report hash")
        bound[identifier] = {"path": str(p.resolve()), "sha256": f["sha256"]}
    return bound


def write_bitmap(grant: dict, dest: Path) -> None:
    from PIL import Image

    with Path(grant["path"]).open("rb") as stream:
        content = stream.read((32 << 20) + 1)
    if hashlib.sha256(content).hexdigest() != grant["sha256"]:
        raise ValueError("Granted bitmap changed after approval")
    with Image.open(io.BytesIO(content), formats=("JPEG", "PNG", "WEBP")) as image:
        if (
            image.width * image.height > 16_000_000
            or getattr(image, "n_frames", 1) != 1
        ):
            raise ValueError("Select a still bitmap under 16 megapixels")
        pixels = image.convert("RGBA")
        pixels.info.clear()
        dest.parent.mkdir(exist_ok=True, parents=True)
        pixels.save(dest, "PNG")

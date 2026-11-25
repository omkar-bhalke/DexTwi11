"""Compare paired owner-supplied screenshots at their original pixel sizes."""

from __future__ import annotations

import math
from pathlib import Path

from .engine import file_hash
from .reports import json_file, new_directory


def compare(original: Path, candidate: Path, dest: Path) -> dict:
    from PIL import Image, ImageChops, ImageStat

    def load(p):
        with Image.open(p) as source:
            if source.width * source.height > 16_000_000:
                raise ValueError("Screenshot exceeds the 16 megapixel comparison limit")
            image = source.convert("RGBA")
            background = Image.new("RGBA", image.size, "white")
            background.alpha_composite(image)
            return background.convert("RGB")

    a, b = load(original), load(candidate)
    report = {
        "original": {"sha256": file_hash(original), "dimensions_px": a.size},
        "candidate": {"sha256": file_hash(candidate), "dimensions_px": b.size},
        "metrics": None,
        "scope": "One frame. Pixel similarity describes visible rendering only.",
    }
    with new_directory(dest):
        side = Image.new("RGB", (a.width + b.width, max(a.height, b.height)), "#e0e3df")
        side.paste(a, (0, 0))
        side.paste(b, (a.width, 0))
        side.save(dest / "side-by-side.png")
        if a.size == b.size:
            diff = ImageChops.difference(a, b)
            diff.save(dest / "difference.png")
            channels = diff.split()
            changed = ImageChops.lighter(
                ImageChops.lighter(channels[0], channels[1]), channels[2]
            )
            total = a.width * a.height
            unequal = total - changed.histogram()[0]
            stats = ImageStat.Stat(diff)
            report["metrics"] = {
                "changed_pixels": unequal,
                "total_pixels": total,
                "exact_pixel_fraction": 1 - unequal / total,
                "mean_absolute_error_rgb": sum(stats.mean) / 3,
                "root_mean_square_error_rgb": math.sqrt(
                    sum(v * v for v in stats.rms) / 3
                ),
                "changed_bounds_px": diff.getbbox(),
            }
        else:
            report["limitation"] = (
                "Physical dimensions differ. Match screen configuration to compute pixel metrics."
            )
        json_file(dest / "comparison.json", report)
    return report

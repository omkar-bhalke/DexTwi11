"""Generate an original, constrained platform-Views preview after a human decision."""

from __future__ import annotations

import json
import os
import re
import tempfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

from .engine import file_hash
from .grants import bind_assets, write_bitmap
from .layout import ANDROID
from .model import COL, HIDDEN
from .reports import json_file, new_directory, read_report

VIEWS = {
    "LinearLayout",
    "FrameLayout",
    "RelativeLayout",
    "ScrollView",
    "HorizontalScrollView",
    "TextView",
    "Button",
    "EditText",
    "ImageView",
    "ImageButton",
    "CheckBox",
    "RadioButton",
    "RadioGroup",
    "Switch",
    "ProgressBar",
    "SeekBar",
    "Space",
    "View",
}
GROUPS = {
    "LinearLayout",
    "FrameLayout",
    "RelativeLayout",
    "ScrollView",
    "HorizontalScrollView",
    "RadioGroup",
}
LENGTH = re.compile(r"(-?\d+(?:\.\d+)?)(dp|dip|sp|px)\Z")
ET.register_namespace("android", ANDROID[1:-1])


def decide(
    folder: Path,
    decision: str,
    sha: str,
    output: Path | None,
    grants: dict | None = None,
) -> dict:
    if decision not in {"YES", "NO"}:
        raise ValueError("Decision must be YES or NO")
    report, _ = read_report(folder, sha)
    if not re.fullmatch(r"[0-9a-f]{64}", sha):
        raise ValueError("Provide the full reviewed report SHA-256")
    if decision == "YES" and (
        output is None or output.exists() or not output.parent.is_dir()
    ):
        raise ValueError(
            "YES requires an unused output directory under an existing parent"
        )
    approved_assets = bind_assets(report, grants) if decision == "YES" else {}
    receipt = {
        "assets": approved_assets,
        "decision": decision,
        "report_sha256": sha,
        "destination": str(output.resolve()) if output and decision == "YES" else None,
    }
    # Atomic replacement makes a later NO revoke the previous approval.
    with tempfile.NamedTemporaryFile(
        "w", dir=folder, delete=False, encoding="utf-8"
    ) as tmp:
        try:
            json.dump(receipt, tmp, sort_keys=True)
            tmp.flush()
            os.fsync(tmp.fileno())
        except BaseException:
            Path(tmp.name).unlink(missing_ok=True)
            raise
    try:
        os.replace(tmp.name, folder / "decision.json")
    finally:
        Path(tmp.name).unlink(missing_ok=True)
    return receipt


def write_xml(path: Path, root) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(root)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def write_project(dest: Path, screens: list[tuple[str, str]]) -> None:
    (
        dest / "settings.gradle"
    ).write_text("""pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
dependencyResolutionManagement { repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS); repositories { google(); mavenCentral() } }
rootProject.name = 'ReviewedLayouts'
include ':app'
""")
    (
        dest / "app/build.gradle"
    ).write_text("""plugins { id 'com.android.application' version '8.7.3' }
android {
    namespace 'org.rea.reviewed'
    compileSdk 35
    defaultConfig { applicationId 'org.rea.reviewed'; minSdk 23; targetSdk 35; versionCode 1; versionName '1.0' }
}
""")
    main = dest / "app/src/main"
    manifest = ET.Element("manifest")
    app = ET.SubElement(
        manifest,
        "application",
        {
            ANDROID + "label": "Reviewed layouts",
            ANDROID + "theme": "@android:style/Theme.Material.Light",
        },
    )
    activity = ET.SubElement(
        app,
        "activity",
        {ANDROID + "name": ".PreviewActivity", ANDROID + "exported": "true"},
    )
    intent = ET.SubElement(activity, "intent-filter")
    ET.SubElement(intent, "action", {ANDROID + "name": "android.intent.action.MAIN"})
    ET.SubElement(
        intent, "category", {ANDROID + "name": "android.intent.category.LAUNCHER"}
    )
    write_xml(main / "AndroidManifest.xml", manifest)
    path = main / "java/org/rea/reviewed/PreviewActivity.java"
    path.parent.mkdir(parents=True)
    names = ", ".join(json.dumps(name) for name, _ in screens)
    ids = ", ".join("R.layout." + symbol for _, symbol in screens)
    path.write_text(
        """package org.rea.reviewed;

import android.app.Activity;
import android.os.Bundle;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;

public final class PreviewActivity extends Activity {
    private static final String[] LABELS = {LABEL_VALUES};
    private static final int[] LAYOUTS = {LAYOUT_VALUES};
    private int selected = -1;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        selected = state == null ? (LAYOUTS.length == 1 ? 0 : -1) : state.getInt("selected", -1);
        render();
    }

    @Override public void onSaveInstanceState(Bundle state) {
        super.onSaveInstanceState(state);
        state.putInt("selected", selected);
    }

    private void render() {
        if (selected >= 0 && selected < LAYOUTS.length) {
            setTitle(LABELS[selected]);
            setContentView(LAYOUTS[selected]);
            return;
        }
        setTitle("Reviewed layouts");
        ScrollView scroll = new ScrollView(this);
        LinearLayout list = new LinearLayout(this);
        list.setOrientation(LinearLayout.VERTICAL);
        scroll.addView(list);
        for (int i = 0; i < LAYOUTS.length; i++) {
            final int index = i;
            Button button = new Button(this);
            button.setText(LABELS[i]);
            button.setOnClickListener(view -> { selected = index; render(); });
            list.addView(button);
        }
        setContentView(scroll);
    }

    @Override public void onBackPressed() {
        if (selected >= 0 && LAYOUTS.length > 1) { selected = -1; render(); }
        else super.onBackPressed();
    }
}
""".replace("LABEL_VALUES", names).replace("LAYOUT_VALUES", ids),
        encoding="utf-8",
    )


def reviewed_value(k: str, v, values: dict):
    if not isinstance(v, str) or v == HIDDEN:
        return None
    v = values.get(v, v)
    if not isinstance(v, str) or v == HIDDEN:
        return None
    if k in {"text", "hint", "contentDescription"} and not v.startswith(("@", "?")):
        # Let AAPT read the literal as a quoted Android string.
        return (
            '"' + v.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
        )
    if k in {"layout_width", "layout_height"}:
        if v in {"-1", "match_parent", "fill_parent"}:
            return "match_parent"
        if v in {"-2", "wrap_content"}:
            return "wrap_content"
    if (
        k
        in {
            "layout_width",
            "layout_height",
            "textSize",
            "elevation",
            "translationX",
            "translationY",
        }
        or k
        in {
            p + s
            for p in ("layout_margin", "padding")
            for s in (
                "",
                "Left",
                "Right",
                "Top",
                "Bottom",
                "Start",
                "End",
                "Horizontal",
                "Vertical",
            )
        }
    ) and LENGTH.fullmatch(v):
        return v.replace("dip", "dp")
    if (
        k in {"textColor", "background", "tint", "backgroundTint"}
        and COL.fullmatch(v)
        and len(v) in (4, 5, 7, 9)
    ):
        return v
    if k == "fontFamily" and v in {
        "sans-serif",
        "sans-serif-light",
        "sans-serif-medium",
        "serif",
        "monospace",
    }:
        return v
    if k == "inputType" and v in {
        "text",
        "textMultiLine",
        "textEmailAddress",
        "number",
        "phone",
        "textPassword",
    }:
        return v
    if k == "orientation":
        return {
            "0": "horizontal",
            "1": "vertical",
            "horizontal": "horizontal",
            "vertical": "vertical",
        }.get(v)
    if k in {"clickable", "enabled"} and v in {"true", "false"}:
        return v
    if k == "visibility":
        return {
            "0": "visible",
            "1": "invisible",
            "2": "gone",
            "visible": "visible",
            "invisible": "invisible",
            "gone": "gone",
        }.get(v)
    if k == "textStyle" and v in {"bold", "italic", "normal", "bold|italic"}:
        return v
    if k in {"gravity", "layout_gravity"} and all(
        t
        in {
            "start",
            "end",
            "top",
            "bottom",
            "center",
            "center_horizontal",
            "center_vertical",
            "left",
            "right",
        }
        for t in v.split("|")
    ):
        return v
    if k in {"alpha", "layout_weight", "weightSum"} and re.fullmatch(r"\d+(\.\d+)?", v):
        return v
    return None


def generate(folder: Path, expected: str, destination: Path | None = None) -> dict:
    if not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise ValueError("Provide the full reviewed report SHA-256")
    report, sha = read_report(folder, expected)
    receipt = json.loads((folder / "decision.json").read_text())
    if receipt.get("decision") != "YES" or receipt.get("report_sha256") != sha:
        raise ValueError("Reconstruction requires explicit YES for this exact report")
    dest = Path(receipt["destination"])
    if destination is not None and dest != destination.resolve():
        raise ValueError("Destination differs from the approved path")
    if dest.is_relative_to(folder.resolve()):
        raise ValueError("Select a destination outside the analysis report")
    files = {f["id"]: f for f in report["files"]}
    elements = defaultdict(list)
    layouts = []
    values = defaultdict(set)

    def scope(f):
        parts = f["location"].split("/")
        base = tuple(parts[: parts.index("res")]) if "res" in parts else ()
        return tuple(f["container"]), base

    for o in report["observations"]:
        d = o["data"]
        if o["category"] == "layout" and d["kind"] == "layout":
            layouts.append(o)
        elif o["category"] == "element":
            elements[d["layout"]].append(o)
        elif o["category"] == "value" and d["qualifier"] == "default":
            values[scope(files[o["evidence"]]), d["symbol"]].add(d["value"])
    if not layouts:
        raise ValueError("No supported XML layout was identified for this generator")
    mapping = []
    screens = []
    with new_directory(dest):
        res = dest / "app/src/main/res"
        grants = receipt.get("assets", {})
        for file_id, grant in grants.items():
            if (
                not re.fullmatch(r"[0-9a-f]{32}", file_id)
                or files[file_id]["sha256"] != grant["sha256"]
            ):
                raise ValueError("Asset grant differs from the reviewed inventory")
            write_bitmap(grant, res / "drawable-nodpi" / ("asset_" + file_id + ".png"))
        for i, layout in enumerate(layouts, 1):
            local_values = {
                k[1]: next(iter(v))
                for k, v in values.items()
                if k[0] == scope(files[layout["evidence"]]) and len(v) == 1
            }
            dependencies = {
                d["reference"]: d for d in files[layout["evidence"]]["dependencies"]
            }
            for reference, link in dependencies.items():
                if len(link["symbols"]) == 1 and link["symbols"][0] in local_values:
                    local_values[reference] = local_values[link["symbols"][0]]
            view_ids = {
                d["data"]["attributes"]["id"].replace("@+", "@"): "view_" + d["id"]
                for d in elements[layout["id"]]
                if isinstance(d["data"]["attributes"].get("id"), str)
            }
            ids = {}
            root = None
            name = "screen_" + str(i)
            for o in elements[layout["id"]]:
                d = o["data"]
                original = d["element_type"]
                t = original.removeprefix("android.widget.").removeprefix(
                    "android.view."
                )
                children = d["children"]
                if t not in VIEWS or (children and t not in GROUPS):
                    t = "LinearLayout" if children else "View"
                node = ET.Element(t)
                ids[o["id"]] = node
                if d["parent"]:
                    ids[d["parent"]].append(node)
                else:
                    root = node
                attrs = d["attributes"]
                omitted = []
                for k, v in attrs.items():
                    projected = reviewed_value(k, v, local_values)
                    if (
                        k == "id"
                        and isinstance(v, str)
                        and v.replace("@+", "@") in view_ids
                    ):
                        projected = "@+id/" + view_ids[v.replace("@+", "@")]
                    if k in {"src", "background"}:
                        candidates = [
                            x
                            for x in dependencies.get(v, {}).get("candidates", [])
                            if x in grants
                        ]
                        if len(candidates) == 1:
                            projected = "@drawable/asset_" + candidates[0]
                    if projected is not None:
                        node.set(ANDROID + k, projected)
                    else:
                        omitted.append(k)
                for k in ("layout_width", "layout_height"):
                    if ANDROID + k not in node.attrib:
                        node.set(
                            ANDROID + k,
                            "match_parent"
                            if k == "layout_width" and not d["parent"]
                            else "wrap_content",
                        )
                if (
                    t in ("ImageView", "ImageButton")
                    and ANDROID + "src" not in node.attrib
                ):
                    node.set(ANDROID + "src", "@drawable/replacement_image")
                if (
                    t == "LinearLayout"
                    and t != original
                    and ANDROID + "orientation" not in node.attrib
                ):
                    node.set(ANDROID + "orientation", "vertical")
                mapping.append(
                    {
                        "element": o["id"],
                        "layout": layout["id"],
                        "generated": name,
                        "original_type": original,
                        "generated_type": t,
                        "omitted_attributes": sorted(omitted),
                    }
                )
            if root is None:
                raise ValueError("Layout lacks its root element")
            write_xml(res / "layout" / (name + ".xml"), root)
            # All variants can be reviewed independent of host device configuration.
            screens.append((f"Layout {i} ({layout['data']['qualifier']})", name))
        vector = ET.Element(
            "vector",
            {
                ANDROID + "width": "24dp",
                ANDROID + "height": "24dp",
                ANDROID + "viewportWidth": "24",
                ANDROID + "viewportHeight": "24",
            },
        )
        ET.SubElement(
            vector,
            "path",
            {ANDROID + "fillColor": "#64756A", ANDROID + "pathData": "M2,3h20v18h-20z"},
        )
        ET.SubElement(
            vector,
            "path",
            {
                ANDROID + "fillColor": "#FFFFFF",
                ANDROID + "pathData": "M4,18l5,-7l4,5l3,-4l4,6z",
            },
        )
        write_xml(res / "drawable/replacement_image.xml", vector)
        write_project(dest, screens)
        generated_files = {
            p.relative_to(dest).as_posix(): file_hash(p)
            for p in sorted(dest.rglob("*"))
            if p.is_file()
        }
        json_file(
            dest / "reconstruction.json",
            {
                "report_sha256": sha,
                "layouts": len(screens),
                "elements": mapping,
                "generated_files": generated_files,
                "approved_bitmap_ids": sorted(grants),
                "scope": "Native layout preview with a generated screen selector. Unresolved images use a new placeholder vector.",
                "unresolved": [
                    "Business actions and navigation",
                    "User-owned backend and billing",
                    "Runtime variants and theme inheritance",
                ],
            },
        )
        json_file(
            dest / "validation.json", {"checks": {name: "UNTESTED" for name in CHECKS}}
        )
    return {"destination": str(dest), "layouts": len(screens), "elements": len(mapping)}


CHECKS = (
    "build",
    "install",
    "launch",
    "navigation",
    "rendering",
    "buttons",
    "input_validation",
    "orientation",
    "densities",
    "android_versions",
    "api_integration",
    "permissions",
    "storage",
    "error_handling",
    "billing_sandbox",
)

import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import warnings
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "bridge/android"))
from project.client import checked_output, export_report, search
from project.engine import analyze, file_hash
from project.inputs import Limits
from project.reconstruct import decide, generate
from project.reports import publish
from project.validation import validate
from project.visual import compare

FIXTURE = ROOT / "examples/android-project/source"
LABELS = json.loads((FIXTURE.parent / "approved-ui-text.json").read_text())
A = 'xmlns:android="http://schemas.android.com/apk/res/android"'


def archive(entries):
    b = io.BytesIO()
    with warnings.catch_warnings(), ZipFile(b, "w", ZIP_DEFLATED) as z:
        warnings.simplefilter("ignore", UserWarning)
        for name, content in entries:
            z.writestr(name, content)
    return b.getvalue()


def facts(r, category):
    return [o for o in r["observations"] if o["category"] == category]


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.folder = self.root / "report"
        self.out = self.root / "generated"

    def sample(self, **opts):
        return analyze(FIXTURE, labels=LABELS, **opts)

    def stage(self):
        return publish(self.sample(), self.folder)

    def test_directory_digest_reproducible_across_locations(self):
        src = self.root / "source"
        shutil.copytree(FIXTURE, src)
        r = self.sample()
        self.assertEqual(r, analyze(src, labels=LABELS))
        self.assertEqual(len(r["target"]["sha256"]), 64)
        self.assertEqual(r["coverage"]["file_occurrences"], r["coverage"]["hashed"])

    def test_elements_units_references_and_event_candidates(self):
        r = self.sample()
        self.assertEqual(len(facts(r, "layout")), 2)
        self.assertEqual(len(facts(r, "element")), 8)
        title = next(
            o for o in facts(r, "element") if o["data"]["attributes"].get("textSize")
        )
        self.assertEqual(title["data"]["attributes"]["textSize"], "28sp")
        self.assertIsNone(title["data"]["runtime_bounds_px"])
        self.assertTrue(title["data"]["parent"])
        click = next(
            o
            for o in facts(r, "interaction")
            if o["data"].get("callback") == "saveDraft"
        )
        self.assertTrue(click["data"]["name_matched_method_candidates"])
        self.assertEqual(click["data"]["effect"], "UNKNOWN")
        drawable = next(f for f in r["files"] if f["name"] == "note.xml")
        self.assertTrue(drawable["used_by"])

    def test_credential_and_uri_values_do_not_enter_exports(self):
        src = self.root / "src"
        src.mkdir()
        (src / "network.kt").write_text(
            '@GET("https://person:CANARY@notes.example/v1/notes?key=CANARY")\nfun listNotes() {}\nval apiKey = "CANARY"'
        )
        (src / "data.json").write_text('{"merchant_key":"CANARY"}')
        (src / "AndroidManifest.xml").write_text(
            f'<manifest {A} package="demo"><application android:label="CANARY"/></manifest>'
        )
        r = analyze(src)
        self.assertEqual(facts(r, "endpoint")[0]["data"]["route"], "/v1/notes")
        self.assertEqual(len(facts(r, "sensitive")), 2)
        publish(r, self.folder)
        for fn in self.folder.iterdir():
            self.assertNotIn(b"CANARY", fn.read_bytes())

    def test_zip_occurrences_unsafe_names_and_encryption(self):
        p = self.root / "duplicate.apk"
        payload = archive(
            [
                ("AndroidManifest.xml", "<manifest/>"),
                ("assets/a", "x"),
                ("assets/a", "y"),
                ("../unsafe", "no"),
            ]
        )
        p.write_bytes(payload)
        r = analyze(p, sign=False)
        duplicate = [f for f in r["files"] if f["location"] == "assets/a"]
        self.assertEqual([x["occurrence"] for x in duplicate], [1, 2])
        self.assertEqual(len({x["id"] for x in duplicate}), 2)
        self.assertTrue(any(x["status"] == "NOT_SUPPORTED" for x in r["files"]))
        b = bytearray(archive([("AndroidManifest.xml", "<manifest/>")]))
        for magic, rel in ((b"PK\x03\x04", 6), (b"PK\x01\x02", 8)):
            b[b.index(magic) + rel] |= 1
        p.write_bytes(b)
        self.assertEqual(
            analyze(p, sign=False)["files"][0]["status"], "REQUIRES_USER_INPUT"
        )

    def test_split_archives_and_missing_base(self):
        base = archive(
            [
                (
                    "AndroidManifest.xml",
                    f'<manifest {A} package="test.app" android:versionCode="1"/>',
                )
            ]
        )
        feature = archive(
            [
                (
                    "AndroidManifest.xml",
                    f'<manifest {A} package="test.app" android:versionCode="1" split="feature"/>',
                )
            ]
        )
        for ext in ("apks", "xapk"):
            p = self.root / ("set." + ext)
            p.write_bytes(
                archive(
                    [("base.apk", base), ("feature.apk", feature), ("metadata", "x")]
                )
            )
            r = analyze(p, sign=False)
            self.assertEqual(len(facts(r, "package")), 2)
            f = next(o for o in facts(r, "package") if o["data"]["split"])
            self.assertEqual(len(f["dependencies"]), 1)
            self.assertEqual(len(r["files"]), 5)
        p.write_bytes(archive([("feature.apk", feature)]))
        self.assertTrue(
            any(
                "split dependency" in i["reason"]
                for i in analyze(p, sign=False)["limitations"]
            )
        )

    def test_split_directory_and_incomplete_bundle(self):
        d = self.root / "splits"
        d.mkdir()
        (d / "base.apk").write_bytes(
            archive([("AndroidManifest.xml", '<manifest package="owner.app"/>')])
        )
        self.assertEqual(len(facts(analyze(d, sign=False), "package")), 1)
        p = self.root / "bad.aab"
        p.write_bytes(archive([("base/assets/raw", "hello")]))
        self.assertTrue(
            any(
                "required" in i["reason"] for i in analyze(p, sign=False)["limitations"]
            )
        )

    def test_invalid_archive_unsupported_format_and_dtd(self):
        p = self.root / "bad.apk"
        p.write_bytes(b"not a zip")
        self.assertEqual(analyze(p, sign=False)["limitations"][0]["status"], "UNKNOWN")
        unknown = self.root / "bad.zip"
        unknown.write_bytes(p.read_bytes())
        with self.assertRaises(ValueError):
            analyze(unknown)
        p.write_bytes(
            archive(
                [
                    (
                        "AndroidManifest.xml",
                        '<!DOCTYPE m [<!ENTITY a "x">]><manifest>&a;</manifest>',
                    )
                ]
            )
        )
        r = analyze(p, sign=False)
        self.assertEqual(facts(r, "package"), [])
        self.assertEqual(r["files"][0]["status"], "PARTIALLY_ANALYZED")

    def test_crc_and_limits_keep_failures_visible(self):
        p = self.root / "bad.apk"
        b = bytearray(archive([("AndroidManifest.xml", "<manifest/>")]))
        b[b.index(b"PK\x01\x02") + 16] ^= 127
        p.write_bytes(b)
        self.assertIsNone(analyze(p, sign=False)["files"][0]["sha256"])
        p.write_bytes(
            archive([("AndroidManifest.xml", "<manifest/>"), ("assets/a", "abc")])
        )
        r = analyze(p, limits=Limits(entries=1), sign=False)
        self.assertTrue(any("not enumerated" in i["reason"] for i in r["limitations"]))
        r = analyze(p, limits=Limits(total=1), sign=False)
        self.assertEqual(r["coverage"]["hashed"], 0)

    def test_large_member_is_hashed_without_buffering_semantics(self):
        p = self.root / "budget.apk"
        p.write_bytes(
            archive(
                [
                    ("AndroidManifest.xml", "<manifest/>"),
                    ("assets/payload", "z" * 64000),
                ]
            )
        )
        r = analyze(p, limits=Limits(parse=1000), sign=False)
        self.assertEqual(r["coverage"]["hashed"], 2)
        self.assertTrue(
            any("parser byte budget" in i["reason"] for i in r["limitations"])
        )

    def test_symlink_and_output_boundary(self):
        d = self.root / "directory"
        d.mkdir()
        (d / "link").symlink_to(FIXTURE, target_is_directory=True)
        r = analyze(d)
        self.assertEqual(r["coverage"]["hashed"], 0)
        self.assertIsNone(r["target"]["sha256"])
        with self.assertRaises(ValueError):
            checked_output(d, d / "output")

    def test_all_formats_are_deterministic_and_searchable(self):
        r = self.sample()
        sha = publish(r, self.folder)
        other = self.root / "r2"
        self.assertEqual(publish(r, other), sha)
        for fn in self.folder.iterdir():
            self.assertEqual(fn.read_bytes(), (other / fn.name).read_bytes())
        self.assertEqual(file_hash(self.folder / "report.json"), sha)
        self.assertGreater(search(r, "element", "EditText", 0, 1)["total"], 1)
        export_report(self.folder, self.out)
        self.assertEqual(file_hash(self.out / "report.json"), sha)
        with self.assertRaises(FileExistsError):
            publish(r, self.folder)

    def test_decision_and_approval_binding(self):
        sha = self.stage()
        with self.assertRaises(FileNotFoundError):
            generate(self.folder, sha)
        with self.assertRaises(ValueError):
            decide(self.folder, "YES", "a" * 64, self.out)
        decide(self.folder, "YES", sha, self.out)
        with self.assertRaises(ValueError):
            generate(self.folder, sha, self.root / "other")
        decide(self.folder, "NO", sha, None)
        with self.assertRaises(ValueError):
            generate(self.folder, sha)
        self.assertFalse(self.out.exists())

    def test_changed_report_never_generates(self):
        sha = self.stage()
        decide(self.folder, "YES", sha, self.out)
        with (self.folder / "report.json").open("a") as w:
            w.write(" ")
        with self.assertRaises(ValueError):
            generate(self.folder, sha)
        with self.assertRaises(ValueError):
            generate(self.folder, file_hash(self.folder / "report.json"))

    def test_generated_project_mapping_and_validation(self):
        sha = self.stage()
        decide(self.folder, "YES", sha, self.out)
        self.assertEqual(generate(self.folder, sha)["elements"], 8)
        with self.assertRaises(FileExistsError):
            generate(self.folder, sha)
        view = (self.out / "app/src/main/res/layout/screen_1.xml").read_text()
        self.assertIn('android:textSize="28sp"', view)
        self.assertIn("20dp", view)
        self.assertNotIn("saveDraft", view)
        result = validate(self.out, self.root / "validation")
        self.assertEqual(result["checks"]["build"], "UNTESTED")
        self.assertEqual(result["xml_parsing"], "PASSED")
        (self.out / "app/build.gradle").write_text("changed")
        with self.assertRaises(ValueError):
            validate(self.out, self.root / "changed")
        self.assertFalse((self.root / "changed").exists())

    def test_explicit_bitmap_grant_and_changed_bytes(self):
        from PIL import Image

        src = self.root / "original"
        shutil.copytree(FIXTURE, src)
        image = src / "app/src/main/res/drawable/note.png"
        image.with_suffix(".xml").unlink()
        Image.new("RGB", (4, 4), "red").save(image)
        r = analyze(src)
        f = next(f for f in r["files"] if f["name"] == "note.png")
        sha = publish(r, self.folder)
        decide(self.folder, "YES", sha, self.out, {f["id"]: str(image)})
        Image.new("RGB", (4, 4), "blue").save(image)
        with self.assertRaises(ValueError):
            generate(self.folder, sha)
        Image.new("RGB", (4, 4), "red").save(image)
        generate(self.folder, sha)
        self.assertTrue(
            (
                self.out / ("app/src/main/res/drawable-nodpi/asset_" + f["id"] + ".png")
            ).exists()
        )
        self.assertIn(
            "asset_" + f["id"],
            (self.out / "app/src/main/res/layout/screen_1.xml").read_text(),
        )

    def test_runtime_and_pixel_difference(self):
        from PIL import Image

        hierarchy = self.root / "runtime.xml"
        hierarchy.write_text(
            '<hierarchy><node class="android.widget.Button" resource-id="demo:id/save" bounds="[2,3][5,6]" text="private text"/></hierarchy>'
        )
        a = self.root / "a.png"
        b = self.root / "b.png"
        img = Image.new("RGB", (5, 6), "white")
        img.save(a)
        img.putpixel((2, 4), (0, 0, 0))
        img.save(b)
        r = analyze(FIXTURE, runtime=hierarchy, screenshot=a, screen="notes")
        self.assertEqual(
            facts(r, "runtime-element")[0]["data"]["bounds_px"], [2, 3, 5, 6]
        )
        self.assertNotIn("private text", json.dumps(r))
        m = compare(a, b, self.out)["metrics"]
        self.assertEqual(m["changed_pixels"], 1)
        self.assertAlmostEqual(m["exact_pixel_fraction"], 29 / 30)
        Image.new("RGB", (1, 1)).save(b)
        self.assertIsNone(compare(a, b, self.root / "different-size")["metrics"])

    def test_cli_through_rea_dispatcher(self):
        proc = subprocess.run(
            [
                "node",
                str(ROOT / "scripts/rea.mjs"),
                "android-project",
                "analyze",
                str(FIXTURE),
                "--out",
                str(self.folder),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        overview = json.loads(proc.stdout)
        self.assertEqual(
            overview["report_sha256"], file_hash(self.folder / "report.json")
        )
        self.assertEqual(overview["actions"], ["YES", "NO", "REVIEW", "EXPORT"])
        self.assertFalse((self.folder / "decision.json").exists())

    @unittest.skipUnless(
        os.getenv("REA_TEST_PACKAGE_DIR"),
        "Set REA_TEST_PACKAGE_DIR to the Android SDK-built fixture directory",
    )
    def test_real_compiled_apk_aab_and_apks(self):
        for ext in ("apk", "aab", "apks"):
            with self.subTest(ext=ext):
                p = Path(os.environ["REA_TEST_PACKAGE_DIR"]) / ("sample." + ext)
                r = analyze(p)
                self.assertTrue(
                    any(
                        o["data"]["package"] == "demo.notes"
                        for o in facts(r, "package")
                    )
                )
                self.assertGreaterEqual(len(facts(r, "element")), 8)
                self.assertTrue(
                    any("saveDraft" in o["location"] for o in facts(r, "method"))
                )
                self.assertTrue(facts(r, "signature"))

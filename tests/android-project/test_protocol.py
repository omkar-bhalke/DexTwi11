import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "bridge/android"))
from project.engine import analyze
from project.reconstruct import decide

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    ClientSession = None


@unittest.skipUnless(ClientSession, "Install mcp to exercise stdio")
class ProtocolTests(unittest.IsolatedAsyncioTestCase):
    async def test_mcp_analysis_search_approval_and_containment(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            inputs = base / "inputs"
            outputs = base / "outputs"
            outputs.mkdir()
            inputs.mkdir()
            shutil.copytree(ROOT / "examples/android-project/source", inputs / "sample")
            params = StdioServerParameters(
                command="node",
                args=[
                    str(ROOT / "scripts/rea.mjs"),
                    "android-project",
                    "mcp",
                    "--input-root",
                    str(inputs),
                    "--output-root",
                    str(outputs),
                ],
                env=dict(os.environ, REA_PROJECT_PYTHON=sys.executable),
            )
            async with (
                stdio_client(params) as (read, write),
                ClientSession(read, write) as client,
            ):
                await client.initialize()
                tools = await client.list_tools()
                self.assertEqual(len(tools.tools), 3)
                self.assertFalse(any("decide" in t.name for t in tools.tools))
                invalid = await client.call_tool(
                    "analyze_android_project",
                    dict(relative_input="../outputs", report_name="escape"),
                )
                self.assertTrue(invalid.isError)
                result = await client.call_tool(
                    "analyze_android_project",
                    dict(relative_input="sample", report_name="report"),
                )
                self.assertFalse(result.isError)
                sha = json.loads(result.content[0].text)["report_sha256"]
                result = await client.call_tool(
                    "read_android_project",
                    dict(
                        report_name="report",
                        category="element",
                        query="EditText",
                        limit=1,
                    ),
                )
                self.assertEqual(json.loads(result.content[0].text)["total"], 2)
                args = dict(
                    report_name="report", report_sha256=sha, destination_name="approved"
                )
                self.assertTrue(
                    (
                        await client.call_tool(
                            "reconstruct_approved_android_project", args
                        )
                    ).isError
                )
                decide(outputs / "report", "YES", sha, outputs / "approved")
                self.assertFalse(
                    (
                        await client.call_tool(
                            "reconstruct_approved_android_project", args
                        )
                    ).isError
                )
                self.assertTrue((outputs / "approved/app/build.gradle").is_file())


@unittest.skipUnless(
    os.getenv("REA_TEST_PACKAGE_DIR"),
    "Set REA_TEST_PACKAGE_DIR to run provider integration",
)
class ProviderTests(unittest.TestCase):
    def test_authenticated_evidence_and_deterministic_nested_signing(self):
        p = Path(os.environ["REA_TEST_PACKAGE_DIR"])
        r = analyze(p / "sample.apks")
        self.assertEqual(r, analyze(p / "sample.apks"))
        with tempfile.TemporaryDirectory() as temp:
            e = Path(temp) / "evidence.json"
            result = subprocess.run(
                [
                    "node",
                    str(ROOT / "scripts/rea.mjs"),
                    "inspect-apk-signature",
                    str(p / "sample.apk"),
                    "--json",
                ],
                capture_output=True,
                check=True,
            )
            e.write_bytes(result.stdout)
            r = analyze(p / "sample.apk", rea_evidence=[e])
            self.assertTrue(
                any(o["category"] == "provider-evidence" for o in r["observations"])
            )
            with self.assertRaises(ValueError):
                analyze(p / "sample.aab", rea_evidence=[e])
            data = json.loads(result.stdout)
            data["normalized_result"]["artifact"]["bytes"] += 1
            e.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                analyze(p / "sample.apk", rea_evidence=[e])

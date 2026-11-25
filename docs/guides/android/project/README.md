# Android project analysis and authorized reconstruction

This extension to REA 6.9.0 inventories local application packages and source trees, writes three reports and stops for a decision. Its first reconstruction engine generates a buildable native Android Views project from supported XML layouts. Field Notes, the included example, has two layout variants, eight elements and an XML callback that can be traced to a candidate Java method.

## Install from this source tree

Use the Node version in `.nvmrc`, the npm version declared in `package.json` and Python 3.11 or later. From the repository root run the following commands.

```sh
npm ci
npm run build:cached
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r bridge/android/project/requirements.txt
node scripts/rea.mjs android-project --help
```

On Windows use `.venv\Scripts\activate` or set `REA_PROJECT_PYTHON` to the absolute path of the venv interpreter. In a linked installation, `rea android-project` and `node scripts/rea.mjs android-project` reach the same dispatcher. The source checkout also supports `python bridge/android/android_project.py` directly. The core text XML, package inventory, reports and generator use the Python standard library. Optional features and their requirements are listed below.

| Feature | Required tools |
| --- | --- |
| Compiled APK XML, resources.arsc and DEX | Androguard 4.1.3. The bridge imports its static parsers. |
| Bitmap metadata, authorized image reuse and screenshot comparison | Pillow |
| Project MCP server | Python MCP SDK 1.x with FastMCP |
| Signing and authenticated Evidence import | Built REA and its locked Node dependencies |
| Generate Android sources | Python 3.11+ |
| Build generated Android sources | JDK 17, Gradle 8.9, Android SDK platform 35 and Build Tools 34.0.0. The first build resolves Android Gradle Plugin 8.7.3 from Google Maven. |
| Inspect selected decompiled methods through REA | Full JDK 17+ and caller-supplied headless JADX MCP JAR 0.7.1. Consult REA's Android guide. |
| Device capture | An isolated emulator or authorized test device plus the existing REA ADB provider |

## Analyze and inspect

Give the CLI a local APK, APKS, XAPK, AAB, directory containing split APKs, extracted application, or owned source tree. Select a new report directory outside the input. This example uses the reviewed UI text from the included fixture.

```sh
node scripts/rea.mjs android-project analyze examples/android-project/source \
  --approved-ui-text examples/android-project/approved-ui-text.json --out notes-report
node scripts/rea.mjs android-project review notes-report --category element --find EditText
node scripts/rea.mjs android-project review notes-report --category limitations
node scripts/rea.mjs android-project export notes-report --out notes-export
```

Open `report.html` to browse 24 sections, filter by status, search a section or expand a record. `report.md` contains the review narrative and full evidence ledger. `report.json` contains the machine-readable snapshot. `SHA256SUMS` identifies all three files. The CLI summary includes the input digest, package declarations, ABI observations, certificate facts, counts, report paths and approval prompt. The example reports are in [examples/android-project/report](../../../../examples/android-project/report).

Files and observations have separate IDs. A file occurrence identifies its container chain, original path and duplicate ordinal; its SHA-256 identifies the bytes. Observation `evidence` points to the file ID, `input` for the package, or a capture identity. XML child paths start at zero. A usage edge may point to several qualifier variants. `null` and missing attributes mean unavailable or undeclared. An element's declared width or margin retains units. An imported runtime rectangle has four physical pixel edges.

Directory digests hash canonical, sorted path/length/content-hash triples. Unreadable in-scope files make that digest unknown. The scan records the omission of version-control directories. Archive digests cover the original file. Inner APKs have separate hashes. Split dependencies use manifest package, version and split declarations. APKS variant selection, install eligibility and signer compatibility require additional evidence.

The scanner retains inventory when parsers are missing, an entry is encrypted, a CRC fails or a budget is exceeded. The defaults are 100,000 file occurrences, 2 GiB cumulative decompressed data, 512 MiB per member, 12 MiB per semantic parser input and 150,000 observations. ZIP central directories are admitted up to 16 MiB and 250,000 declared entries. Use `--max-entries`, `--max-total-mib` and `--max-parse-mib` to change the configurable budgets. The CLI writes JSON progress to stderr every 250 entries. Ctrl-C cancels a foreground run. Use a stable local copy of a source checkout or archive for reproducibility.

## Combine existing REA evidence

The project bridge calls the existing APK signature application service and checks its result against the observed artifact hash. Nested signature rows retain provider identity, signer facts and member hashes. Temporary extraction paths are excluded from nested report identity.

The following example uses the existing CLI to obtain a complete record. The project bridge authenticates it using REA's `parseEvidence`, checks the subject against the root or a member, and retains its ID and selected structural facts. Method text, raw payloads, certificate subject names and string tables stay in their original Evidence files.

```sh
rea inspect-apk-signature owned.apk --json > signature-evidence.json
rea android-project analyze owned.apk --rea-evidence signature-evidence.json --out owned-report
```

Accepted complete Evidence operations include APK signing, Android package/class/method inspection, incoming references, Apktool resource decoding, and the Android application graph. A selected view with a parent ID needs the complete parent record. Use existing REA tools to inspect a particular method, JNI binding or R8 mapping. Their installation and provider-specific limitations are in the [Android analysis guide](../android-analysis.md) and [Apktool guide](../apktool-resource-analysis.md).

## Review and approve

The decision belongs to the person authorizing reconstruction. REVIEW reads the snapshot and EXPORT copies it. YES binds a specific report SHA-256 to an unused destination. NO revokes an earlier approval for the report. The CLI returns the full digest after analysis or review.

```sh
rea android-project decide notes-report YES --sha256 <reviewed-report-sha256> --destination notes-preview
rea android-project reconstruct notes-report --sha256 <reviewed-report-sha256>
rea android-project validate notes-preview --out notes-check
rea android-project validate notes-preview --gradle /absolute/path/to/gradle --out notes-build-check
```

The approval receipt is local, relies on the user's control of the output directory and is checked again by the generator. A changed report, different destination, absent approval or existing output refuses generation. The generator writes original Java and platform layouts, metadata for each substituted view or omitted attribute, a local validation checklist and source hashes. Each layout variant can be inspected in the generated selector. Unsupported views receive a platform substitute. A new placeholder vector stands in for unresolved images. Business logic, backend requests and payment operations require owner-supplied implementations.

For authorized bitmap reuse, pass `--asset-grants grants.json` to the YES decision. Provide a JSON object mapping a report file ID to an absolute local PNG, JPEG or WebP path. The grant applies to those bytes. The generator verifies their digest again and re-encodes still images without metadata. A uniquely granted candidate can populate a layout image or background. Nine-patch, animated and proprietary library reuse require manual handling. UI text is a separate decision: `--approved-ui-text` accepts exact, reviewed literal strings. Without that list the report shows resource references and withholds free-form labels.

## Runtime observations and visual comparison

Use REA's existing `capture-adb-screen` for an authorized isolated target, and supply a corresponding UI Automator hierarchy for the same state. Analysis reads those local artifacts. The runtime rows associate the supplied screen identifier, screenshot dimensions and SHA-256 with element bounds. The caller owns the capture-time and screen association.

```sh
rea android-project analyze owned.apk --runtime-xml hierarchy.xml --screenshot original.png --screen settings --out capture-report
rea android-project compare original.png reconstructed.png --out frame-comparison
```

Matching dimensions produce a side-by-side PNG, RGB difference PNG, changed-pixel count, exact-pixel fraction, mean absolute error, RMS error and the changed bounding rectangle. Different dimensions yield the original-size side-by-side frames and a recorded limitation. One frame cannot establish navigation, scrolling, animation or functional equivalence.

## MCP and AI clients

Create separate existing input and output directories. Register the following command as a second stdio server alongside the ordinary REA server. Use absolute paths. The Python interpreter selected by REA needs the MCP extra listed above.

```json
{
  "mcpServers": {
    "rea-project": {
      "command": "node",
      "args": ["/path/to/rea/scripts/rea.mjs", "android-project", "mcp",
               "--input-root", "/path/to/owned-inputs", "--output-root", "/path/to/reports"],
      "env": {"REA_PROJECT_PYTHON": "/path/to/rea/.venv/bin/python"}
    }
  }
}
```

| Client | Configure the stdio command |
| --- | --- |
| Claude Code | Use project `.mcp.json` or `claude mcp add rea-project -- node ...`. |
| Codex | Use a `[mcp_servers.rea-project]` table in `config.toml` with the same command and argument array. The repository AGENTS.md and packaged REA skill describe the review gate. |
| Gemini CLI | Add the `mcpServers` entry to the project's `.gemini/settings.json`. |
| Cursor | Add the entry to the project's `.cursor/mcp.json`. |
| Generic MCP | Start the same command over stdio and discover the tool schemas with `tools/list`. |
| Generic CLI | Use `analyze`, `review`, `export`, `decide`, `reconstruct`, `validate` and `compare`. |

`analyze_android_project` takes a relative input and simple report name. `read_android_project` pages observations, file records or limitations by category and query. `reconstruct_approved_android_project` requires both the reviewed digest and destination name from the local receipt. The MCP server exposes no capability for creating approval receipts. A human records consent using the local CLI. Protect the output root from writes by unrelated processes. The packaged agent instructions direct agents to present the report and wait for the user's decision.

## Verification and limitations

The [audit and roadmap](roadmap.md) maps each requested phase to its existing REA owner and release criterion. The [verification record](verification.md) identifies the exercised paths, open work and reproduction commands. The source scanners recognize declarations and selected patterns; comments, dynamic construction, reflection, native dispatch and obfuscation limit attribution. Source module and split references are scoped conservatively. Java/Kotlin/Compose symbols and Flutter/React Native/Cordova/Unity markers can be inventoried. Their runtime trees and application semantics require further work. Compiled AAB scalar XML is supported; full protobuf resource-table resolution is pending. Style inheritance, includes, constraints, adaptive navigation, animation timing, dynamic API contracts, database schemas and billing flows can remain unresolved.

## Contributing and licenses

Extend a parser at its format boundary, preserve the file digest and occurrence on partial results, and add a case that distinguishes the new observations from prior unknowns. Use a synthetic or redistributable fixture with an explicit provenance record. For report changes, verify JSON, Markdown, HTML search and the human approval gate. Follow the root [contribution guide](../../../../CONTRIBUTING.md) and [security policy](../../../../SECURITY.md).

REA's root MIT license covers the repository, including these additions. Retain the copyright and license text when redistributing. Node dependencies retain the notices in THIRD_PARTY_NOTICES.md and licenses/. The extension imports optional upstream packages at installation time. Androguard uses Apache-2.0, Pillow 13 declares MIT-CMU, and the MCP Python SDK uses MIT; their dependencies carry their own terms. Android SDK, Gradle, JDK, JADX and Apktool are separately installed tools. The deliverable includes no SDK, signing key, external APK, merchant configuration or third-party application assets. Field Notes is original fixture content under the repository license. Ownership of an APK and permission to redistribute its assets are separate decisions.

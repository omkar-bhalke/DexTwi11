# Android project audit and implementation roadmap

## Starting point

The supplied archive contains the 6.9.0 source distribution (9,215 ZIP entries including directories). It contains no Git history. The package declares Node 24.22.1 in .nvmrc. Its npm lockfile, TypeScript compiler, Turbo pipeline, Vitest configuration, Python bridges and platform-specific verification lanes are present. The submodule paths exist without the upstream source trees.

| Area | Existing owner | What the new workflow needs |
| --- | --- | --- |
| Artifact identity | src/artifacts, src/domain/android/androidApplication.ts, project_android_application_graph | The Android projection consumes authenticated APK inventory pages and classifies DEX, JVM, resource, native and bridge candidates. Project reporting also needs split/module occurrences, source trees, resource usage and per-file outcomes. |
| Resources | src/apktool, decode_android_resources | The temporary Apktool decode projects strings, locales, manifest and counts. Layouts and drawable attributes need persistent, element-level observations. |
| Manifest and code | src/android, src/application/android, bridge/android/ReaJadxBridge.java | JADX provides package, class, selected method and incoming-reference evidence. Manifest components preserve declaration locations. JNI and R8 tools have separate contracts. A consolidated report needs UI, source and DEX links with explicit unknowns. |
| Signing | src/apkSignature, inspect_apk_signature | Reuse REA's actual signing result with its subject SHA-256 and Evidence ID. Keep verification scope visible. |
| Frameworks and device | src/flutter, src/il2cpp, src/adb | Existing tools inspect selected artifacts and device state. Runtime family evidence alone cannot recover widgets, effective geometry or purchase behavior. |
| Evidence and delivery | src/domain/evidence.ts, src/domain/analysisView, src/server, src/cli | REA authenticates, retains and pages Evidence. Project item identifiers are report-local references. Imported provider results retain their own identities. |
| Reconstruction | docs/reconstruction-coverage.md | Existing verifier evaluates claims and provenance. It does not turn Android layouts into projects or capture a user's decision about one report. |
| Agents and tests | .agents/skills, .claude-plugin, .codex-plugin, .cursor-plugin, tests/{acceptance,boundary,conformance}, .github/workflows/real-* | Preserve existing catalogs and providers. Add a local project CLI and a separately selectable MCP surface with restricted filesystem roots. |

## Implementation order and release criteria

| Phase | Delivery criterion | Further work / release condition |
| --- | --- | --- |
| 1 · Audit | Inspect component owners, package scripts, fixtures, provider docs, setup, agent entry points and license notices. Run the upstream cached build. | A source ZIP cannot establish commit identity or upstream CI results. |
| 2 · Architecture | Keep orchestration alongside REA's Android bridge. Use one report model for all adapters. | Compare schema evolution and retained evidence with the native catalog before merging catalogs. |
| 3 · Inputs | Hash and inventory each accessible occurrence. Stream members, bound nested traversal, distinguish bad CRC, duplicates, links, incomplete inputs and missing manifests. | Verify large production bundles across delivery variants. |
| 4 · UI | Record XML declaration order, parents and attributes, qualifiers, resource dependencies and runtime unknowns. Test text and compiled layouts. | Constraint solving, Compose trees, framework-generated surfaces and style/theme inheritance need additional evidence. |
| 5 · Code and functionality | Index DEX definitions and source declarations, preserve overload identity, separate event declarations from executed behavior. | Add robust AST-based and cross-module control flow with representative ground truth. |
| 6 · APIs and dependencies | Report static endpoint declarations, framework markers, ABI and library evidence with references. | Extend contracts for each transport and verify runtime associations. |
| 7 · Permissions, security and billing | Extract manifest declarations and purchase-flow references. Keep credentials and arbitrary payloads out of reports. | Verify effective permissions, entitlement state and server validation only in owner-supplied environments. |
| 8 · Evidence | Give items deterministic identifiers and file-specific evidence. Report hashing and semantic coverage separately. | Extend interoperability to full project Evidence bundles. |
| 9 · Reports | Generate linked JSON, Markdown and searchable HTML from the same snapshot; surface missing information before approval. | Profile very large retained reports. |
| 10 · Approval | Review/export without generation. Bind explicit YES to the exact report digest and a new destination. | Exercise client-specific confirmation UX. |
| 11 · Reconstruction | Generate original Android project files from supported, allowlisted layout facts; list all substitutions. | Additional renderers, navigation, business logic, licensed assets and owner integrations need separate implementation. |
| 12 · Comparison | Provide matching-size pixel comparison, side-by-side and difference images. | Add time-aligned interaction traces and device-normalized text metrics. |
| 13 · Validation | Test package variants, failures, reporting, approval and example reconstruction. Record only checks actually run. | Test install, launch, densities, platform versions, backend and billing on controlled environments. |
| 14 · Delivery | Include run instructions, fixtures, example reports, limitations, license review and verification results. | Production certification requires the remaining real-device, compatibility and scale checks. |

## Delivery status

| Phase | Implemented and checked in this distribution | Open scope |
| --- | --- | --- |
| 1 | Audited the uploaded distribution and ran the locked upstream build. | The source archive has no commit history or populated submodules. |
| 2 | Shared report engine under the Android bridge, existing REA dispatcher and signing service, native Evidence authentication and a separate project MCP surface. | Integration into REA's default tool catalog remains a future API decision. |
| 3 | APK, AAB, APKS, XAPK, split directories and source trees. Tested digest stability, duplicate ordinals, encryption, CRC failure, malformed roots, symlinks and limits. | Large device-specific bundles and mixed variants need additional compatibility coverage. |
| 4 | Ordered layout/menu/navigation trees, qualifier variants, declared attributes, values and bitmap metadata. Checked binary XML and AAPT2 protobuf XML from SDK-built packages. | Framework-generated UI, complete style inheritance and constraint solving. |
| 5 | DEX classes, methods, descriptors, fields, hierarchy, class annotations and standard invoke operands. Source symbols and callback candidates. Verified actual DEX in ApiDemos and Field Notes. | Whole-program control flow, reflection targets, method annotations and automatic proof of interactions. |
| 6 | Resource and usage references, static source route candidates, Gradle declarations, native filenames, ABI paths and ELF machine IDs. Tested credential suppression. | General network contracts, dynamic hosts and complete library license identification. |
| 7 | Permission and component declarations, selected security settings, known billing source and DEX references. | Effective grants, purchase-state transitions and owner server verification. |
| 8 | Deterministic occurrence IDs, coverage by status, per-failure records and subject-bound import of authenticated REA Evidence. Verified tamper refusal. | Full behavioral coverage and evidence for runtime-only states. |
| 9 | Three deterministic report formats; 24 HTML sections, filters, paging and search. Exercised desktop and mobile views in Chromium. | Full-device accessibility and publishing workflows. |
| 10 | Local YES/NO receipt bound to report and destination. Verified rejection on missing, changed, revoked or mismatched approvals, including over MCP. | Host output permissions remain the trust boundary. |
| 11 | Original Java and XML Views project, substitution ledger, per-file bitmap grants and fresh source hashes. Built a two-variant fixture. | Implementing owner business logic, custom widgets, cross-platform renderers and service integrations. |
| 12 | Original-size comparisons, changed bounds and quantitative RGB metrics. Tested a known one-pixel change and unequal dimensions. | Multi-frame, per-element and scroll comparisons. |
| 13 | Reproducible Android fixture builder, unit tests, real stdio MCP checks, original and generated APK builds and upstream regression checks. | Device installation, launch, performance, densities, API, storage, and billing tests on an authorized test system. |
| 14 | Repository archive, guide, example fixture and reports, security and contribution notes, open-source review and verification record. | Wider compatibility testing precedes a production-readiness claim. |

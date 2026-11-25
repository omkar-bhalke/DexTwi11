# Android project verification

Verified on Linux on 24 November 2026. The test input for reconstruction was Field Notes, the original example included in this distribution. Appium ApiDemos was analyzed statically.

| Check | Result and scope |
| --- | --- |
| Existing REA build | The locked npm install and `npm run build:cached` completed on Node 24.22.3. The npm packing dry run included the project bridge, its launcher, template and requirements. |
| Existing Android regressions | All 88 selected tests passed across five upstream files covering Android application services, native inventory, mapping, Apktool decoding and signature reports. The full REA test suite was not run. |
| Extension suite | All 20 tests passed, with the optional parser dependencies installed, the stdio MCP client active and the compiled fixtures enabled. Tests covered package formats, stable evidence, CRC and size limits, privacy, approvals, authorized image reuse, output integrity, layout generation and screenshot metrics. |
| Protocol | A live MCP client discovered all three project tools, analyzed a fixture, paged results, and exercised refusals for an out-of-root input and a missing approval. Generation succeeded after a matching local decision. |
| HTML and JSON | Chromium exercised all 24 section choices, desktop search, evidence expansion, status filters, the narrow-screen selector and overflow checks. The example JSON validated against the shipped draft 2020-12 schema. |
| Native Android fixture | AAPT2 compiled and linked the original resources, javac built its Java sources, D8 produced DEX, and bundletool built and validated the AAB and produced an APKS set. The tests found the package, layouts, method and signing evidence in all three carriers. |
| Generated Android build | Gradle 8.9, AGP 8.7.3, JDK 17, platform 35 and Build Tools 34.0.0 built the two-variant native layout preview. Android apksigner verified the debug APK's v1 and v2 signatures. The test signing key was local to the verification workspace. |
| Device and backend | Installation, launch, runtime interaction, orientation, density and Android-version matrices, authenticated API calls and billing integration remain untested. The isolated build runner had no compatible emulator or attached test device. |
| Public APK | ApiDemos 6.0.18 matched the upstream fixture digest. All 869 file occurrences were hashed. The run recovered 2,015 UI elements, 5,700 DEX class definitions and 34,882 method definitions. The XML decoder flagged noncanonical encoding on 350 resources. Their recovered declarations are marked partial. |

The machine-readable [public APK observations](apidemos-verification.json) identify the input hash and bounded counts. The [generated fixture build result](fixture-validation.json) identifies the report and built debug APK by SHA-256. Of the application checks in that file, only the build was exercised. The [original fixture source](../../../../examples/android-project/source) and [example analysis](../../../../examples/android-project/report) are in the archive.

## Reproduce the tests

Run the commands below in the checkout after following the installation guide. The SDK fixture helper expects Linux tool names. It uses temporary source and signing workspaces and an unused output directory. Run the REA build to completion before running provider tests. Rebuilding concurrently replaces compiled provider modules used by those tests.

```sh
npm run build:cached
python tests/android-project/make_sdk_fixtures.py \
  --jdk /path/to/jdk17 --platform /path/to/sdk/platforms/android-35 \
  --build-tools /path/to/sdk/build-tools/34.0.0 \
  --bundletool /path/to/bundletool-all-1.18.2.jar --out /tmp/rea-sdk-fixtures
REA_TEST_PACKAGE_DIR=/tmp/rea-sdk-fixtures python -m unittest discover -s tests/android-project -v

npm run test:local -- src/android/AndroidNativeInventory.test.ts \
  src/domain/android/androidMapping.test.ts src/apktool/ApktoolDecodeOutput.test.ts \
  src/application/android/AndroidAnalysisService.test.ts src/domain/apkSignature/apkSignatureReport.test.ts
```

The public APK is identified in `scripts/fixtures/android/apidemos.json` and is excluded from this distribution. To reproduce its application label in the report, supply an approved UI-text list containing `API Demos`. To rebuild the generated fixture, follow the review, decision, reconstruction and validation commands in the [project guide](README.md). A new local debug signing key can change the resulting APK digest.

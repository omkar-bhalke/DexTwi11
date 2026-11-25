# Android application analysis

**source** · directory · 7 file occurrences

Input SHA-256: `df87cec8c7ec9b65f86d44dcdca5597f457edf81c7c1dbc77cf40321d35d2813`

## Application overview

Review observed package declarations and technology indicators.

package: 1, technology: 1. See the evidence ledger below.

## Package information

Each declaration retains its source manifest. Signature posture is reported by the existing REA provider.

package: 1, signature: 0. See the evidence ledger below.

## Original technology stack

Source extensions, annotations and runtime filenames provide different levels of evidence.

technology: 1. See the evidence ledger below.

## Screen inventory

A layout variant, component or function is a screen candidate. One-to-one correspondence requires corroboration.

layout: 2, component: 1, source-symbol: 3. See the evidence ledger below.

## Layout hierarchy

The parent and ordered children identify the declared hierarchy in each layout variant.

### app/src/main/res/layout/notes.xml

<pre>LinearLayout (match_parent × match_parent)
  ImageView @+id/icon (32dp × 32dp)
  TextView @+id/title @string/app_name (match_parent × wrap_content)
  EditText @+id/draft (match_parent × wrap_content)
  Button @+id/save @string/save (wrap_content × wrap_content)</pre>

### app/src/main/res/layout-land/notes.xml

<pre>LinearLayout (match_parent × match_parent)
  EditText @+id/draft (0dp × wrap_content)
  Button @string/save (wrap_content × wrap_content)</pre>

## UI element inventory

An element location is the zero-based child path from the layout root.

element: 8. See the evidence ledger below.

## UI dimensions and typography

Static units retain their declarations. Runtime captures use physical pixels.

element: 8, runtime-element: 0. See the evidence ledger below.

## Asset inventory

All file occurrences are listed. Resolved references identify candidate uses.

files: 7, visual: 1, value: 6, resource-id: 0. See the evidence ledger below.

## Source and DEX analysis

Method descriptors distinguish overloads. Recovered declarations describe compiled or supplied evidence.

class: 0, field: 0, method: 0, source-symbol: 3, provider-evidence: 0. See the evidence ledger below.

## Functionality mapping

Source patterns and callback declarations need execution or additional code to establish effects.

interaction: 3. See the evidence ledger below.

## API inventory

Routes describe source declarations. Authentication, payloads and responses are unknown unless independently observed.

endpoint: 0. See the evidence ledger below.

## Library inventory

A packaged library or Gradle declaration alone cannot establish its license or execution.

dependency: 0. See the evidence ledger below.

## Permission analysis

Declared permissions are distinct from runtime grants. Purpose annotations cover a subset of Android permissions.

permission: 0. See the evidence ledger below.

## Security findings

Credential findings disclose a location and type with a redacted value.

security: 1, sensitive: 0, signature: 0. See the evidence ledger below.

## Billing analysis

Purchase references are declarations. Merchant configuration, verification and entitlement require owner evidence.

billing: 0. See the evidence ledger below.

## Navigation architecture

Navigation XML and intent-filter declarations identify possible transitions.

navigation: 0, component: 1, layout-binding: 1. See the evidence ledger below.

## Database and local storage

Storage API references and database headers do not disclose stored records.

storage: 0. See the evidence ledger below.

## Runtime observations

Each capture represents one caller-supplied state. Matched screenshot hashes identify observed pixels.

runtime: 0, runtime-element: 0. See the evidence ledger below.

## Missing information

Unresolved references also appear on individual file records. Dynamic behavior requires further evidence.

No processing limitations recorded.

## Reconstruction dependencies

Review variants, referenced resources, unsupported views and service contracts.

dependency: 0, value: 6, resource-id: 0. See the evidence ledger below.

## Compatibility risks

Validate platform, theme, language, density and configuration selection on target devices.

No processing limitations recorded.

## Reuse authorization

Every file starts with REQUIRES_USER_INPUT. This report grants no asset or library rights.

Original asset and library reuse requires a separate rights decision.

## Reconstruction plan

Explicit approval binds the generator to a particular report.

- Review layout variants, resource references, substitutions and unresolved observations.
- Confirm scope and rights for the UI specifications. Select YES for this report digest.
- Generate a native Android layout project. Review the generated mapping for every element.
- Supply authorized navigation, backend, storage and billing contracts for unresolved behavior.
- Build and exercise on a controlled emulator. Compare matched screenshots and record results.

## Coverage statistics

Hash coverage counts bytes read. Observation categories count evidence, independently of behavioral coverage.

{"file_occurrences": 7, "hashed": 7, "file_statuses": {"ANALYZED": 6, "PARTIALLY_ANALYZED": 1}, "observation_categories": {"component": 1, "element": 8, "interaction": 3, "layout": 2, "layout-binding": 1, "package": 1, "security": 1, "source-symbol": 3, "technology": 1, "value": 6, "visual": 1}, "inventory_scope": "Enumerated files, nested APK members and explicit omissions", "runtime_behavior": "REQUIRES_RUNTIME"}

## Evidence ledger

### File inventory

| Category | Location | Status | Evidence and details |
| --- | --- | --- | --- |
| manifest | app/src/main/AndroidManifest.xml | ANALYZED | {&quot;id&quot;: &quot;d75927907aafcfe95990719ebe5a5c43&quot;, &quot;container&quot;: [], &quot;occurrence&quot;: 1, &quot;name&quot;: &quot;AndroidManifest.xml&quot;, &quot;type&quot;: &quot;xml&quot;, &quot;bytes&quot;: 588, &quot;sha256&quot;: &quot;19ac61e35e2e9129c2be05a8c7e1b9a7a21e1600fa9e13b7256717c620983c1e&quot;, &quot;qualifier&quot;: null, &quot;resource&quot;: null, &quot;decoding&quot;: &quot;text-xml&quot;, &quot;evidence&quot;: &quot;d75927907aafcfe95990719ebe5a5c43&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [{&quot;reference&quot;: &quot;@string/app_name&quot;, &quot;symbols&quot;: [&quot;@string/app_name&quot;], &quot;candidates&quot;: [&quot;0d072dbee43d692b7124de938b3cde5e&quot;, &quot;4dc4e4197790f54a92241623fa1c579e&quot;], &quot;status&quot;: &quot;DISCOVERED&quot;}], &quot;used_by&quot;: [], &quot;reuse&quot;: &quot;REQUIRES_USER_INPUT&quot;, &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;} |
| code | app/src/main/java/demo/notes/NotesActivity.java | PARTIALLY_ANALYZED | {&quot;id&quot;: &quot;1ceb36ea425921acef865f2ad01fc750&quot;, &quot;container&quot;: [], &quot;occurrence&quot;: 1, &quot;name&quot;: &quot;NotesActivity.java&quot;, &quot;type&quot;: &quot;java&quot;, &quot;bytes&quot;: 532, &quot;sha256&quot;: &quot;07755589fa2d6e8ca2aae2efcfe50e4aabbb8999ff5dcc4631d0735af9154a6f&quot;, &quot;qualifier&quot;: null, &quot;resource&quot;: null, &quot;decoding&quot;: &quot;source pattern scan&quot;, &quot;evidence&quot;: &quot;1ceb36ea425921acef865f2ad01fc750&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [{&quot;reference&quot;: &quot;@id/draft&quot;, &quot;symbols&quot;: [&quot;@id/draft&quot;], &quot;candidates&quot;: [], &quot;status&quot;: &quot;UNKNOWN&quot;}, {&quot;reference&quot;: &quot;@layout/notes&quot;, &quot;symbols&quot;: [&quot;@layout/notes&quot;], &quot;candidates&quot;: [&quot;3c7ac8a547975c39daf38838bea450a8&quot;, &quot;8e469605be586e1b5b30259293a2be06&quot;], &quot;status&quot;: &quot;DISCOVERED&quot;}], &quot;used_by&quot;: [], &quot;reuse&quot;: &quot;REQUIRES_USER_INPUT&quot;, &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;} |
| drawable | app/src/main/res/drawable/note.xml | ANALYZED | {&quot;id&quot;: &quot;f663a0cf8a5aa438c2b7055751955440&quot;, &quot;container&quot;: [], &quot;occurrence&quot;: 1, &quot;name&quot;: &quot;note.xml&quot;, &quot;type&quot;: &quot;xml&quot;, &quot;bytes&quot;: 247, &quot;sha256&quot;: &quot;d29e8611ffb5693581f373862c0ca69abf179cfd643bd052dd49e03ac7967be8&quot;, &quot;qualifier&quot;: &quot;default&quot;, &quot;resource&quot;: &quot;@drawable/note&quot;, &quot;decoding&quot;: &quot;text-xml&quot;, &quot;evidence&quot;: &quot;f663a0cf8a5aa438c2b7055751955440&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [], &quot;used_by&quot;: [&quot;3c7ac8a547975c39daf38838bea450a8&quot;], &quot;reuse&quot;: &quot;REQUIRES_USER_INPUT&quot;, &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;} |
| layout | app/src/main/res/layout/notes.xml | ANALYZED | {&quot;id&quot;: &quot;3c7ac8a547975c39daf38838bea450a8&quot;, &quot;container&quot;: [], &quot;occurrence&quot;: 1, &quot;name&quot;: &quot;notes.xml&quot;, &quot;type&quot;: &quot;xml&quot;, &quot;bytes&quot;: 1009, &quot;sha256&quot;: &quot;31c5fef805b07270e369761d4b07c506030ca08c155e110d1c7bfabc0255f0cd&quot;, &quot;qualifier&quot;: &quot;default&quot;, &quot;resource&quot;: &quot;@layout/notes&quot;, &quot;decoding&quot;: &quot;text-xml&quot;, &quot;evidence&quot;: &quot;3c7ac8a547975c39daf38838bea450a8&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [{&quot;reference&quot;: &quot;@+id/draft&quot;, &quot;symbols&quot;: [&quot;@id/draft&quot;], &quot;candidates&quot;: [], &quot;status&quot;: &quot;UNKNOWN&quot;}, {&quot;reference&quot;: &quot;@+id/icon&quot;, &quot;symbols&quot;: [&quot;@id/icon&quot;], &quot;candidates&quot;: [], &quot;status&quot;: &quot;UNKNOWN&quot;}, {&quot;reference&quot;: &quot;@+id/save&quot;, &quot;symbols&quot;: [&quot;@id/save&quot;], &quot;candidates&quot;: [], &quot;status&quot;: &quot;UNKNOWN&quot;}, {&quot;reference&quot;: &quot;@+id/title&quot;, &quot;symbols&quot;: [&quot;@id/title&quot;], &quot;candidates&quot;: [], &quot;status&quot;: &quot;UNKNOWN&quot;}, {&quot;reference&quot;: &quot;@color/paper&quot;, &quot;symbols&quot;: [&quot;@color/paper&quot;], &quot;candidates&quot;: [&quot;0d072dbee43d692b7124de938b3cde5e&quot;], &quot;status&quot;: &quot;DISCOVERED&quot;}, {&quot;reference&quot;: &quot;@dimen/gutter&quot;, &quot;symbols&quot;: [&quot;@dimen/gutter&quot;], &quot;candidates&quot;: [&quot;0d072dbee43d692b7124de938b3cde5e&quot;], &quot;status&quot;: &quot;DISCOVERED&quot;}, {&quot;reference&quot;: &quot;@drawable/note&quot;, &quot;symbols&quot;: [&quot;@drawable/note&quot;], &quot;candidates&quot;: [&quot;f663a0cf8a5aa438c2b7055751955440&quot;], &quot;status&quot;: &quot;DISCOVERED&quot;}, {&quot;reference&quot;: &quot;@string/app_name&quot;, &quot;symbols&quot;: [&quot;@string/app_name&quot;], &quot;candidates&quot;: [&quot;0d072dbee43d692b7124de938b3cde5e&quot;, &quot;4dc4e4197790f54a92241623fa1c579e&quot;], &quot;status&quot;: &quot;DISCOVERED&quot;}, {&quot;reference&quot;: &quot;@string/prompt&quot;, &quot;symbols&quot;: [&quot;@string/prompt&quot;], &quot;candidates&quot;: [&quot;0d072dbee43d692b7124de938b3cde5e&quot;], &quot;status&quot;: &quot;DISCOVERED&quot;}, {&quot;reference&quot;: &quot;@string/save&quot;, &quot;symbols&quot;: [&quot;@string/save&quot;], &quot;candidates&quot;: [&quot;0d072dbee43d692b7124de938b3cde5e&quot;], &quot;status&quot;: &quot;DISCOVERED&quot;}], &quot;used_by&quot;: [&quot;1ceb36ea425921acef865f2ad01fc750&quot;], &quot;reuse&quot;: &quot;REQUIRES_USER_INPUT&quot;, &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;} |
| layout | app/src/main/res/layout-land/notes.xml | ANALYZED | {&quot;id&quot;: &quot;8e469605be586e1b5b30259293a2be06&quot;, &quot;container&quot;: [], &quot;occurrence&quot;: 1, &quot;name&quot;: &quot;notes.xml&quot;, &quot;type&quot;: &quot;xml&quot;, &quot;bytes&quot;: 526, &quot;sha256&quot;: &quot;4cb4d0fcfaf1a6bb9e7883b5458cf7fb3c4e625eb869ad5efac66eeba4eec855&quot;, &quot;qualifier&quot;: &quot;land&quot;, &quot;resource&quot;: &quot;@layout/notes&quot;, &quot;decoding&quot;: &quot;text-xml&quot;, &quot;evidence&quot;: &quot;8e469605be586e1b5b30259293a2be06&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [{&quot;reference&quot;: &quot;@+id/draft&quot;, &quot;symbols&quot;: [&quot;@id/draft&quot;], &quot;candidates&quot;: [], &quot;status&quot;: &quot;UNKNOWN&quot;}, {&quot;reference&quot;: &quot;@string/prompt&quot;, &quot;symbols&quot;: [&quot;@string/prompt&quot;], &quot;candidates&quot;: [&quot;0d072dbee43d692b7124de938b3cde5e&quot;], &quot;status&quot;: &quot;DISCOVERED&quot;}, {&quot;reference&quot;: &quot;@string/save&quot;, &quot;symbols&quot;: [&quot;@string/save&quot;], &quot;candidates&quot;: [&quot;0d072dbee43d692b7124de938b3cde5e&quot;], &quot;status&quot;: &quot;DISCOVERED&quot;}], &quot;used_by&quot;: [&quot;1ceb36ea425921acef865f2ad01fc750&quot;], &quot;reuse&quot;: &quot;REQUIRES_USER_INPUT&quot;, &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;} |
| values | app/src/main/res/values/values.xml | ANALYZED | {&quot;id&quot;: &quot;0d072dbee43d692b7124de938b3cde5e&quot;, &quot;container&quot;: [], &quot;occurrence&quot;: 1, &quot;name&quot;: &quot;values.xml&quot;, &quot;type&quot;: &quot;xml&quot;, &quot;bytes&quot;: 225, &quot;sha256&quot;: &quot;8edc66b118fdab5953d2348d7c11649c60c6a01a2eaff155cfc1cdb0553c8fa7&quot;, &quot;qualifier&quot;: &quot;default&quot;, &quot;resource&quot;: &quot;@values/values&quot;, &quot;decoding&quot;: &quot;text-xml&quot;, &quot;evidence&quot;: &quot;0d072dbee43d692b7124de938b3cde5e&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [], &quot;used_by&quot;: [&quot;d75927907aafcfe95990719ebe5a5c43&quot;, &quot;3c7ac8a547975c39daf38838bea450a8&quot;, &quot;3c7ac8a547975c39daf38838bea450a8&quot;, &quot;3c7ac8a547975c39daf38838bea450a8&quot;, &quot;3c7ac8a547975c39daf38838bea450a8&quot;, &quot;3c7ac8a547975c39daf38838bea450a8&quot;, &quot;8e469605be586e1b5b30259293a2be06&quot;, &quot;8e469605be586e1b5b30259293a2be06&quot;], &quot;reuse&quot;: &quot;REQUIRES_USER_INPUT&quot;, &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;} |
| values | app/src/main/res/values-fr/strings.xml | ANALYZED | {&quot;id&quot;: &quot;4dc4e4197790f54a92241623fa1c579e&quot;, &quot;container&quot;: [], &quot;occurrence&quot;: 1, &quot;name&quot;: &quot;strings.xml&quot;, &quot;type&quot;: &quot;xml&quot;, &quot;bytes&quot;: 63, &quot;sha256&quot;: &quot;7f6c3499e50c540d6a9ce63fcb5bfe615d0cc29f91fa3f2a3166675cefb3b672&quot;, &quot;qualifier&quot;: &quot;fr&quot;, &quot;resource&quot;: &quot;@values/strings&quot;, &quot;decoding&quot;: &quot;text-xml&quot;, &quot;evidence&quot;: &quot;4dc4e4197790f54a92241623fa1c579e&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [], &quot;used_by&quot;: [&quot;d75927907aafcfe95990719ebe5a5c43&quot;, &quot;3c7ac8a547975c39daf38838bea450a8&quot;], &quot;reuse&quot;: &quot;REQUIRES_USER_INPUT&quot;, &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;} |

### Observations

| Category | Location | Status | Evidence and details |
| --- | --- | --- | --- |
| package | manifest | ANALYZED | {&quot;id&quot;: &quot;4410146ff0b1ec8748a84f40b5a689ea&quot;, &quot;evidence&quot;: &quot;d75927907aafcfe95990719ebe5a5c43&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [], &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;, &quot;data&quot;: {&quot;package&quot;: &quot;demo.notes&quot;, &quot;split&quot;: null, &quot;config_for_split&quot;: null, &quot;uses_splits&quot;: [], &quot;label&quot;: &quot;@string/app_name&quot;, &quot;version_name&quot;: &quot;1.0&quot;, &quot;version_code&quot;: &quot;1&quot;, &quot;min_sdk&quot;: &quot;23&quot;, &quot;target_sdk&quot;: &quot;35&quot;, &quot;default_label&quot;: &quot;Field Notes&quot;}} |
| security | application[2] | ANALYZED | {&quot;id&quot;: &quot;e599595e0b4dad5ebe57024e9f7ec130&quot;, &quot;evidence&quot;: &quot;d75927907aafcfe95990719ebe5a5c43&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [], &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;, &quot;data&quot;: {&quot;allowBackup&quot;: &quot;false&quot;, &quot;debuggable&quot;: null, &quot;usesCleartextTraffic&quot;: &quot;false&quot;, &quot;networkSecurityConfig&quot;: null, &quot;fullBackupContent&quot;: null, &quot;dataExtractionRules&quot;: null}} |
| component | activity[3] | ANALYZED | {&quot;id&quot;: &quot;7dff123048fd373b6d1d83aea8b3f97e&quot;, &quot;evidence&quot;: &quot;d75927907aafcfe95990719ebe5a5c43&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [], &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;, &quot;data&quot;: {&quot;kind&quot;: &quot;activity&quot;, &quot;name&quot;: &quot;.NotesActivity&quot;, &quot;filters&quot;: [{&quot;actions&quot;: [&quot;android.intent.action.MAIN&quot;], &quot;categories&quot;: [&quot;android.intent.category.LAUNCHER&quot;], &quot;data&quot;: []}], &quot;declarations&quot;: {&quot;exported&quot;: &quot;true&quot;, &quot;enabled&quot;: null, &quot;permission&quot;: null, &quot;authorities&quot;: null, &quot;grantUriPermissions&quot;: null, &quot;readPermission&quot;: null, &quot;writePermission&quot;: null, &quot;targetActivity&quot;: null}}} |
| technology | source extension | ANALYZED | {&quot;id&quot;: &quot;f5728604c3ae80bf43ae9fa75eadf7cf&quot;, &quot;evidence&quot;: &quot;1ceb36ea425921acef865f2ad01fc750&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [], &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;, &quot;data&quot;: {&quot;name&quot;: &quot;Java&quot;}} |
| source-symbol | line 8:14 | PARTIALLY_ANALYZED | {&quot;id&quot;: &quot;ed85f5304017b61d0768561199c78d93&quot;, &quot;evidence&quot;: &quot;1ceb36ea425921acef865f2ad01fc750&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [], &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;, &quot;data&quot;: {&quot;kind&quot;: &quot;class&quot;, &quot;name&quot;: &quot;NotesActivity&quot;, &quot;compose_declaration&quot;: false, &quot;language&quot;: &quot;Java&quot;}} |
| source-symbol | line 9:30 | PARTIALLY_ANALYZED | {&quot;id&quot;: &quot;f7c5c314d7d18be34bd19581792ef8db&quot;, &quot;evidence&quot;: &quot;1ceb36ea425921acef865f2ad01fc750&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [], &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;, &quot;data&quot;: {&quot;kind&quot;: &quot;method&quot;, &quot;name&quot;: &quot;onCreate&quot;, &quot;language&quot;: &quot;Java&quot;}} |
| layout-binding | line 11:9 | PARTIALLY_ANALYZED | {&quot;id&quot;: &quot;1c721f8854d0b4bb4f606efcc03740bc&quot;, &quot;evidence&quot;: &quot;1ceb36ea425921acef865f2ad01fc750&quot;, &quot;confidence&quot;: &quot;inferred&quot;, &quot;dependencies&quot;: [], &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;, &quot;data&quot;: {&quot;symbol&quot;: &quot;@layout/notes&quot;, &quot;kind&quot;: &quot;setContentView source expression&quot;}} |
| interaction | line 11:9 | PARTIALLY_ANALYZED | {&quot;id&quot;: &quot;b6277ee86298feec375068f1ed188717&quot;, &quot;evidence&quot;: &quot;1ceb36ea425921acef865f2ad01fc750&quot;, &quot;confidence&quot;: &quot;inferred&quot;, &quot;dependencies&quot;: [], &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;, &quot;data&quot;: {&quot;reference&quot;: &quot;setContentView&quot;, &quot;behavior&quot;: &quot;UNKNOWN&quot;}} |
| source-symbol | line 14:17 | PARTIALLY_ANALYZED | {&quot;id&quot;: &quot;424279a0764687769f1723231e7180ef&quot;, &quot;evidence&quot;: &quot;1ceb36ea425921acef865f2ad01fc750&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [], &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;, &quot;data&quot;: {&quot;kind&quot;: &quot;method&quot;, &quot;name&quot;: &quot;saveDraft&quot;, &quot;language&quot;: &quot;Java&quot;}} |
| visual | vector | ANALYZED | {&quot;id&quot;: &quot;63015fbcee74c265c69300dc89dd51d1&quot;, &quot;evidence&quot;: &quot;f663a0cf8a5aa438c2b7055751955440&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [], &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;, &quot;data&quot;: {&quot;format&quot;: &quot;Android vector&quot;, &quot;dimensions&quot;: [&quot;24dp&quot;, &quot;24dp&quot;], &quot;viewport&quot;: [&quot;24&quot;, &quot;24&quot;]}} |
| layout | root | ANALYZED | {&quot;id&quot;: &quot;87ad41f5bae061f1b1f57777638ae1db&quot;, &quot;evidence&quot;: &quot;3c7ac8a547975c39daf38838bea450a8&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [], &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;, &quot;data&quot;: {&quot;symbol&quot;: &quot;@layout/notes&quot;, &quot;qualifier&quot;: &quot;default&quot;, &quot;kind&quot;: &quot;layout&quot;}} |
| element | 0 | ANALYZED | {&quot;id&quot;: &quot;1b6eec6ec5e52bbe6731467de33cbfe9&quot;, &quot;evidence&quot;: &quot;3c7ac8a547975c39daf38838bea450a8&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [], &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;, &quot;data&quot;: {&quot;layout&quot;: &quot;87ad41f5bae061f1b1f57777638ae1db&quot;, &quot;parent&quot;: null, &quot;children&quot;: [&quot;28ee8210cd58c5082b84435d930e0ec7&quot;, &quot;8b3210233ee039cf329a62daa3056b09&quot;, &quot;52c3eb5e9086f550e2f5dc267edee844&quot;, &quot;6592ba98e2bd929a42fc93b5549053c1&quot;], &quot;element_type&quot;: &quot;LinearLayout&quot;, &quot;attributes&quot;: {&quot;orientation&quot;: &quot;vertical&quot;, &quot;padding&quot;: &quot;@dimen/gutter&quot;, &quot;layout_width&quot;: &quot;match_parent&quot;, &quot;layout_height&quot;: &quot;match_parent&quot;, &quot;background&quot;: &quot;@color/paper&quot;}, &quot;runtime_bounds_px&quot;: null, &quot;normalized_coordinates&quot;: null, &quot;source&quot;: &quot;app/src/main/res/layout/notes.xml#0&quot;}} |
| element | 0.0 | ANALYZED | {&quot;id&quot;: &quot;28ee8210cd58c5082b84435d930e0ec7&quot;, &quot;evidence&quot;: &quot;3c7ac8a547975c39daf38838bea450a8&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [], &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;, &quot;data&quot;: {&quot;layout&quot;: &quot;87ad41f5bae061f1b1f57777638ae1db&quot;, &quot;parent&quot;: &quot;1b6eec6ec5e52bbe6731467de33cbfe9&quot;, &quot;children&quot;: [], &quot;element_type&quot;: &quot;ImageView&quot;, &quot;attributes&quot;: {&quot;id&quot;: &quot;@+id/icon&quot;, &quot;src&quot;: &quot;@drawable/note&quot;, &quot;contentDescription&quot;: &quot;@string/app_name&quot;, &quot;layout_width&quot;: &quot;32dp&quot;, &quot;layout_height&quot;: &quot;32dp&quot;}, &quot;runtime_bounds_px&quot;: null, &quot;normalized_coordinates&quot;: null, &quot;source&quot;: &quot;app/src/main/res/layout/notes.xml#0.0&quot;}} |
| element | 0.1 | ANALYZED | {&quot;id&quot;: &quot;8b3210233ee039cf329a62daa3056b09&quot;, &quot;evidence&quot;: &quot;3c7ac8a547975c39daf38838bea450a8&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [], &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;, &quot;data&quot;: {&quot;layout&quot;: &quot;87ad41f5bae061f1b1f57777638ae1db&quot;, &quot;parent&quot;: &quot;1b6eec6ec5e52bbe6731467de33cbfe9&quot;, &quot;children&quot;: [], &quot;element_type&quot;: &quot;TextView&quot;, &quot;attributes&quot;: {&quot;id&quot;: &quot;@+id/title&quot;, &quot;text&quot;: &quot;@string/app_name&quot;, &quot;textSize&quot;: &quot;28sp&quot;, &quot;textStyle&quot;: &quot;bold&quot;, &quot;layout_width&quot;: &quot;match_parent&quot;, &quot;layout_height&quot;: &quot;wrap_content&quot;}, &quot;runtime_bounds_px&quot;: null, &quot;normalized_coordinates&quot;: null, &quot;source&quot;: &quot;app/src/main/res/layout/notes.xml#0.1&quot;}} |
| element | 0.2 | ANALYZED | {&quot;id&quot;: &quot;52c3eb5e9086f550e2f5dc267edee844&quot;, &quot;evidence&quot;: &quot;3c7ac8a547975c39daf38838bea450a8&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [], &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;, &quot;data&quot;: {&quot;layout&quot;: &quot;87ad41f5bae061f1b1f57777638ae1db&quot;, &quot;parent&quot;: &quot;1b6eec6ec5e52bbe6731467de33cbfe9&quot;, &quot;children&quot;: [], &quot;element_type&quot;: &quot;EditText&quot;, &quot;attributes&quot;: {&quot;id&quot;: &quot;@+id/draft&quot;, &quot;hint&quot;: &quot;@string/prompt&quot;, &quot;inputType&quot;: &quot;textMultiLine&quot;, &quot;layout_width&quot;: &quot;match_parent&quot;, &quot;layout_height&quot;: &quot;wrap_content&quot;}, &quot;runtime_bounds_px&quot;: null, &quot;normalized_coordinates&quot;: null, &quot;source&quot;: &quot;app/src/main/res/layout/notes.xml#0.2&quot;}} |
| element | 0.3 | ANALYZED | {&quot;id&quot;: &quot;6592ba98e2bd929a42fc93b5549053c1&quot;, &quot;evidence&quot;: &quot;3c7ac8a547975c39daf38838bea450a8&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [], &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;, &quot;data&quot;: {&quot;layout&quot;: &quot;87ad41f5bae061f1b1f57777638ae1db&quot;, &quot;parent&quot;: &quot;1b6eec6ec5e52bbe6731467de33cbfe9&quot;, &quot;children&quot;: [], &quot;element_type&quot;: &quot;Button&quot;, &quot;attributes&quot;: {&quot;id&quot;: &quot;@+id/save&quot;, &quot;text&quot;: &quot;@string/save&quot;, &quot;onClick&quot;: &quot;saveDraft&quot;, &quot;layout_width&quot;: &quot;wrap_content&quot;, &quot;layout_height&quot;: &quot;wrap_content&quot;}, &quot;runtime_bounds_px&quot;: null, &quot;normalized_coordinates&quot;: null, &quot;source&quot;: &quot;app/src/main/res/layout/notes.xml#0.3&quot;}} |
| interaction | 0.3 | PARTIALLY_ANALYZED | {&quot;id&quot;: &quot;7a858134711bdc7e10779c3d77c51aa1&quot;, &quot;evidence&quot;: &quot;3c7ac8a547975c39daf38838bea450a8&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [], &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;, &quot;data&quot;: {&quot;element&quot;: &quot;6592ba98e2bd929a42fc93b5549053c1&quot;, &quot;callback&quot;: &quot;saveDraft&quot;, &quot;kind&quot;: &quot;android:onClick declaration&quot;, &quot;effect&quot;: &quot;UNKNOWN&quot;, &quot;name_matched_method_candidates&quot;: [&quot;424279a0764687769f1723231e7180ef&quot;]}} |
| layout | root | ANALYZED | {&quot;id&quot;: &quot;ecf474c754c8d8625038ebbdf2d118e6&quot;, &quot;evidence&quot;: &quot;8e469605be586e1b5b30259293a2be06&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [], &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;, &quot;data&quot;: {&quot;symbol&quot;: &quot;@layout/notes&quot;, &quot;qualifier&quot;: &quot;land&quot;, &quot;kind&quot;: &quot;layout&quot;}} |
| element | 0 | ANALYZED | {&quot;id&quot;: &quot;240d260724f61f1f3945c5a98940fe85&quot;, &quot;evidence&quot;: &quot;8e469605be586e1b5b30259293a2be06&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [], &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;, &quot;data&quot;: {&quot;layout&quot;: &quot;ecf474c754c8d8625038ebbdf2d118e6&quot;, &quot;parent&quot;: null, &quot;children&quot;: [&quot;0f919768ae80b9aecff6c140a453e644&quot;, &quot;4f8a7ab86275799c050078898e9c2677&quot;], &quot;element_type&quot;: &quot;LinearLayout&quot;, &quot;attributes&quot;: {&quot;orientation&quot;: &quot;horizontal&quot;, &quot;padding&quot;: &quot;16dp&quot;, &quot;layout_width&quot;: &quot;match_parent&quot;, &quot;layout_height&quot;: &quot;match_parent&quot;}, &quot;runtime_bounds_px&quot;: null, &quot;normalized_coordinates&quot;: null, &quot;source&quot;: &quot;app/src/main/res/layout-land/notes.xml#0&quot;}} |
| element | 0.0 | ANALYZED | {&quot;id&quot;: &quot;0f919768ae80b9aecff6c140a453e644&quot;, &quot;evidence&quot;: &quot;8e469605be586e1b5b30259293a2be06&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [], &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;, &quot;data&quot;: {&quot;layout&quot;: &quot;ecf474c754c8d8625038ebbdf2d118e6&quot;, &quot;parent&quot;: &quot;240d260724f61f1f3945c5a98940fe85&quot;, &quot;children&quot;: [], &quot;element_type&quot;: &quot;EditText&quot;, &quot;attributes&quot;: {&quot;id&quot;: &quot;@+id/draft&quot;, &quot;hint&quot;: &quot;@string/prompt&quot;, &quot;layout_width&quot;: &quot;0dp&quot;, &quot;layout_weight&quot;: &quot;1&quot;, &quot;layout_height&quot;: &quot;wrap_content&quot;}, &quot;runtime_bounds_px&quot;: null, &quot;normalized_coordinates&quot;: null, &quot;source&quot;: &quot;app/src/main/res/layout-land/notes.xml#0.0&quot;}} |
| element | 0.1 | ANALYZED | {&quot;id&quot;: &quot;4f8a7ab86275799c050078898e9c2677&quot;, &quot;evidence&quot;: &quot;8e469605be586e1b5b30259293a2be06&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [], &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;, &quot;data&quot;: {&quot;layout&quot;: &quot;ecf474c754c8d8625038ebbdf2d118e6&quot;, &quot;parent&quot;: &quot;240d260724f61f1f3945c5a98940fe85&quot;, &quot;children&quot;: [], &quot;element_type&quot;: &quot;Button&quot;, &quot;attributes&quot;: {&quot;text&quot;: &quot;@string/save&quot;, &quot;onClick&quot;: &quot;saveDraft&quot;, &quot;layout_width&quot;: &quot;wrap_content&quot;, &quot;layout_height&quot;: &quot;wrap_content&quot;}, &quot;runtime_bounds_px&quot;: null, &quot;normalized_coordinates&quot;: null, &quot;source&quot;: &quot;app/src/main/res/layout-land/notes.xml#0.1&quot;}} |
| interaction | 0.1 | PARTIALLY_ANALYZED | {&quot;id&quot;: &quot;a3fc215cd64fe4ee9e354379eca5a2f0&quot;, &quot;evidence&quot;: &quot;8e469605be586e1b5b30259293a2be06&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [], &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;, &quot;data&quot;: {&quot;element&quot;: &quot;4f8a7ab86275799c050078898e9c2677&quot;, &quot;callback&quot;: &quot;saveDraft&quot;, &quot;kind&quot;: &quot;android:onClick declaration&quot;, &quot;effect&quot;: &quot;UNKNOWN&quot;, &quot;name_matched_method_candidates&quot;: [&quot;424279a0764687769f1723231e7180ef&quot;]}} |
| value | child[0] | ANALYZED | {&quot;id&quot;: &quot;883a3f3febc7266053f7d141254290a7&quot;, &quot;evidence&quot;: &quot;0d072dbee43d692b7124de938b3cde5e&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [], &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;, &quot;data&quot;: {&quot;symbol&quot;: &quot;@string/app_name&quot;, &quot;kind&quot;: &quot;string&quot;, &quot;value&quot;: &quot;Field Notes&quot;, &quot;qualifier&quot;: &quot;default&quot;, &quot;parent&quot;: null}} |
| value | child[1] | ANALYZED | {&quot;id&quot;: &quot;f169295d5b0e05d91d13f0a34a664d09&quot;, &quot;evidence&quot;: &quot;0d072dbee43d692b7124de938b3cde5e&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [], &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;, &quot;data&quot;: {&quot;symbol&quot;: &quot;@string/save&quot;, &quot;kind&quot;: &quot;string&quot;, &quot;value&quot;: &quot;Save draft&quot;, &quot;qualifier&quot;: &quot;default&quot;, &quot;parent&quot;: null}} |
| value | child[2] | ANALYZED | {&quot;id&quot;: &quot;de1627e638d78177b11fa5a7a8921803&quot;, &quot;evidence&quot;: &quot;0d072dbee43d692b7124de938b3cde5e&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [], &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;, &quot;data&quot;: {&quot;symbol&quot;: &quot;@string/prompt&quot;, &quot;kind&quot;: &quot;string&quot;, &quot;value&quot;: &quot;Write a note&quot;, &quot;qualifier&quot;: &quot;default&quot;, &quot;parent&quot;: null}} |
| value | child[3] | ANALYZED | {&quot;id&quot;: &quot;589993787bd6bf9eb447285cc54d895b&quot;, &quot;evidence&quot;: &quot;0d072dbee43d692b7124de938b3cde5e&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [], &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;, &quot;data&quot;: {&quot;symbol&quot;: &quot;@dimen/gutter&quot;, &quot;kind&quot;: &quot;dimen&quot;, &quot;value&quot;: &quot;20dp&quot;, &quot;qualifier&quot;: &quot;default&quot;, &quot;parent&quot;: null}} |
| value | child[4] | ANALYZED | {&quot;id&quot;: &quot;d310c4c40959493bff771fd1082ac7d0&quot;, &quot;evidence&quot;: &quot;0d072dbee43d692b7124de938b3cde5e&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [], &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;, &quot;data&quot;: {&quot;symbol&quot;: &quot;@color/paper&quot;, &quot;kind&quot;: &quot;color&quot;, &quot;value&quot;: &quot;#FAFAF6&quot;, &quot;qualifier&quot;: &quot;default&quot;, &quot;parent&quot;: null}} |
| value | child[0] | ANALYZED | {&quot;id&quot;: &quot;c31569d42b38464b6b507f6542868a02&quot;, &quot;evidence&quot;: &quot;4dc4e4197790f54a92241623fa1c579e&quot;, &quot;confidence&quot;: &quot;observed&quot;, &quot;dependencies&quot;: [], &quot;reconstruction_status&quot;: &quot;PENDING_REVIEW&quot;, &quot;data&quot;: {&quot;symbol&quot;: &quot;@string/app_name&quot;, &quot;kind&quot;: &quot;string&quot;, &quot;value&quot;: &quot;Carnet&quot;, &quot;qualifier&quot;: &quot;fr&quot;, &quot;parent&quot;: null}} |

### Processing limitations

| Category | Location | Status | Evidence and details |
| --- | --- | --- | --- |

## Reconstruction decision

Application analysis is complete. I have prepared the screen inventory, layout specifications, UI element mapping, assets, functionality, API contracts, dependencies, permissions, billing analysis, and reconstruction plan.

Would you like to begin authorized application reconstruction?

YES · NO · REVIEW · EXPORT

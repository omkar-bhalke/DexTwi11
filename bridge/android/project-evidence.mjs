import { readFile } from "node:fs/promises";
import { parseEvidence } from "../../dist/domain/evidence.js";
import { ApkSignatureService } from "../../dist/application/apkSignature/ApkSignatureService.js";
import { ApkSignatureProvider } from "../../dist/apkSignature/ApkSignatureProvider.js";

const [mode, path] = process.argv.slice(2);
try {
  if (mode === "signature") {
    const service = new ApkSignatureService(new ApkSignatureProvider());
    try {
      const result = await service.inspect({ path, detail: "complete" });
      if (!result.ok) throw new Error("Signature operation failed");
      process.stdout.write(JSON.stringify(result.value));
    } finally {
      await service.close();
    }
  } else if (mode === "import") {
    const evidence = parseEvidence(JSON.parse(await readFile(path, "utf8")));
    const value = evidence.normalized_result;
    const facts = {};
    switch (evidence.operation) {
      case "inspect_android_package":
        facts.class_count = value.class_count;
        facts.resource_count = value.resource_count;
        break;
      case "inspect_android_class":
        facts.method_count = value.methods.length;
        facts.field_count = value.fields.length;
        break;
      case "inspect_android_method":
        facts.representation = value.representation;
        facts.body_status = value.body_status;
        facts.overload_count = value.overload_count;
        break;
      case "trace_android_references":
        facts.reference_count = value.total;
        break;
      case "decode_android_resources":
        facts.decoded_file_count = value.decoded_file_count;
        facts.coverage = value.coverage;
        break;
      case "inspect_apk_signature":
        facts.schemes_present = Object.entries(value.schemes)
          .filter(([, s]) => s.present)
          .map(([k]) => k);
        break;
      case "project_android_application_graph":
        facts.runtime_families = value.runtime_families;
        facts.coverage = value.coverage.status;
        break;
      default:
        throw new Error("Unsupported Android Evidence operation");
    }
    process.stdout.write(
      JSON.stringify({
        rea_evidence_id: evidence.evidence_id,
        artifact_sha256: evidence.subject?.digest.sha256 ?? value.root_sha256,
        operation: evidence.operation,
        facts,
      }),
    );
  } else {
    throw new Error("Unknown bridge operation");
  }
} catch {
  // Avoid propagating literal target values in validation errors.
  process.stderr.write(
    "REA could not authenticate or project the selected Android evidence.\n",
  );
  process.exitCode = 1;
}

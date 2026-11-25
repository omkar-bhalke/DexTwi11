import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import { constants } from "node:os";

/** Delegate the opt-in Android project workflow to its Python bridge. */
export async function runAndroidProject(args) {
  const script = fileURLToPath(
    new URL("../../bridge/android/android_project.py", import.meta.url),
  );
  const interpreter =
    process.env.REA_PROJECT_PYTHON ||
    (process.platform === "win32" ? "python" : "python3");
  const child = spawn(interpreter, [script, ...args], {
    stdio: "inherit",
    shell: false,
  });
  const interrupt = () => child.kill("SIGINT");
  const terminate = () => child.kill("SIGTERM");
  process.on("SIGINT", interrupt);
  process.on("SIGTERM", terminate);
  try {
    return await new Promise((resolve, reject) => {
      child.once("error", reject);
      child.once("exit", (code, signal) =>
        resolve(code ?? 128 + (constants.signals[signal] ?? 1)),
      );
    });
  } catch (error) {
    process.stderr.write(
      `Unable to start the Android project bridge. Set REA_PROJECT_PYTHON to a Python 3.11+ interpreter. ${error.code ?? "spawn failed"}\n`,
    );
    return 1;
  } finally {
    process.off("SIGINT", interrupt);
    process.off("SIGTERM", terminate);
  }
}

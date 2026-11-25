"""Build the original example into APK, AAB and APKS in a new test directory."""

import argparse
import os
from pathlib import Path
import subprocess
import tempfile
from zipfile import ZipFile

repo = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
for arg in ("jdk", "platform", "build-tools", "bundletool", "out"):
    parser.add_argument("--" + arg, required=True, type=Path)
opt = parser.parse_args()
out = opt.out.resolve()
out.mkdir()
env = dict(os.environ, JAVA_HOME=str(opt.jdk.resolve()))
src = repo / "examples/android-project/source/app/src/main"
android = opt.platform.resolve() / "android.jar"
tools = opt.build_tools.resolve()
jdk = opt.jdk.resolve() / "bin"
jar = opt.bundletool.resolve()


def run(*args):
    subprocess.run([str(x) for x in args], check=True, env=env)


with tempfile.TemporaryDirectory() as temp:
    tmp = Path(temp)
    for directory in ("java", "classes", "dex"):
        (tmp / directory).mkdir()
    run(tools / "aapt2", "compile", "--dir", src / "res", "-o", tmp / "res.zip")
    run(
        tools / "aapt2",
        "link",
        "-I",
        android,
        "--manifest",
        src / "AndroidManifest.xml",
        "--java",
        tmp / "java",
        "-o",
        out / "sample.apk",
        tmp / "res.zip",
    )
    run(
        jdk / "javac",
        "--release",
        "8",
        "-classpath",
        android,
        "-d",
        tmp / "classes",
        tmp / "java/demo/notes/R.java",
        src / "java/demo/notes/NotesActivity.java",
    )
    run(jdk / "jar", "cf", tmp / "classes.jar", "-C", tmp / "classes", ".")
    run(
        tools / "d8",
        "--lib",
        android,
        "--min-api",
        "23",
        "--output",
        tmp / "dex",
        tmp / "classes.jar",
    )
    with ZipFile(out / "sample.apk", "a") as z:
        z.write(tmp / "dex/classes.dex", "classes.dex")
    run(
        tools / "aapt2",
        "convert",
        "--output-format",
        "proto",
        "-o",
        tmp / "proto.apk",
        out / "sample.apk",
    )
    with (
        ZipFile(tmp / "proto.apk") as source,
        ZipFile(tmp / "module.zip", "w") as module,
    ):
        for name in source.namelist():
            prefix = (
                "manifest/"
                if name == "AndroidManifest.xml"
                else "dex/"
                if name.endswith(".dex")
                else ""
            )
            module.writestr(prefix + name, source.read(name))
    run(
        jdk / "java",
        "-jar",
        jar,
        "build-bundle",
        "--modules=" + str(tmp / "module.zip"),
        "--output=" + str(out / "sample.aab"),
    )
    run(jdk / "java", "-jar", jar, "validate", "--bundle=" + str(out / "sample.aab"))
    keystore = tmp / "fixture.jks"
    run(
        jdk / "keytool",
        "-genkeypair",
        "-keystore",
        keystore,
        "-storepass",
        "android",
        "-keypass",
        "android",
        "-alias",
        "fixture",
        "-keyalg",
        "RSA",
        "-keysize",
        "2048",
        "-validity",
        "7",
        "-dname",
        "CN=Local Android Fixture",
    )
    run(
        jdk / "java",
        "-jar",
        jar,
        "build-apks",
        "--bundle=" + str(out / "sample.aab"),
        "--output=" + str(out / "sample.apks"),
        "--ks=" + str(keystore),
        "--ks-key-alias=fixture",
        "--ks-pass=pass:android",
        "--key-pass=pass:android",
    )

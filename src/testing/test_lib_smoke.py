"""Smoke test for the vendored src/lib.

Verifies two things:
 1. Compiled extensions (.so files) in src/lib were built for the
    currently running interpreter - catches a lib vendored for the
    wrong Python version, which is what you get to debug on App Engine
    otherwise.
  2. The third-party libraries that main.py imports actually import.

Run from anywhere with the interpreter you intend to deploy:

    python3 src/testing/test_lib_smoke.py

Exits 0 on success, 1 with a summary on failure.
"""

import glob
import importlib
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LIB = os.path.join(REPO_ROOT, "src", "lib")

# Third-party imports used by main.py plus all binary-backed packages
# that would explode at runtime if their .so files are stale.
MODULES_TO_IMPORT = [
    "_cffi_backend",
    "cryptography",
    "device_detector",
    "feedgen.feed",
    "feedparser",
    "feedparser_sgmllib",
    "flask",
    "google.api_core.exceptions",
    "google.auth.exceptions",
    "google.cloud.logging",
    "google.cloud.storage",
    "grpc",
    "gunicorn",
    "jsondiff",
    "lxml.etree",
    "markupsafe",
    "regex",
    "requests",
    "yaml",
]


def check_so_versions():
    """Return a list of .so files not built for this interpreter"""
    current = f"cpython-{sys.version_info.major}{sys.version_info.minor}"
    bad = []
    for so_file in glob.glob(os.path.join(LIB, "**", "*.so"), recursive=True):
        match = re.search(r"cpython-(\d+)", os.path.basename(so_file))
        if match and f"cpython-{match.group(1)}" != current:
            bad.append(os.path.relpath(so_file, REPO_ROOT))
    return bad


def main():
    """The actual smoke test happens here"""
    failures = []

    print(f"Interpreter: {sys.version.split()[0]}")
    print(f"Lib under test: {LIB}")

    bad_sos = check_so_versions()
    if bad_sos:
        failures.append(
            "compiled extensions built for another python: " + ", ".join(bad_sos)
        )
    else:
        so_count = len(glob.glob(os.path.join(LIB, "**", "*.so"), recursive=True))
        print(f".so version check: OK ({so_count} extensions match this interpreter)")

    sys.path.insert(0, LIB)
    for module in MODULES_TO_IMPORT:
        try:
            importlib.import_module(module)
        except Exception as err:  # pylint: disable=broad-exception-caught
            failures.append(f"import {module}: {err}")

    if failures:
        print("\nFAILURES:")
        for failure in failures:
            print(f" - {failure}")
        sys.exit(1)

    print(f"import check: OK ({len(MODULES_TO_IMPORT)} modules)")
    print("SMOKE TEST OK")


if __name__ == "__main__":
    main()

# plugins/clang/tests/test_stubs.py
import os
import subprocess
import sys
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent
BUILD_DIR = TESTS / "build"   # same location conftest.py adds to sys.path
STUBS = TESTS / "typings" / "cxbind_tests"


@unittest.skipUnless(BUILD_DIR.exists(), "cxbind_tests not built")
class TestStubs(unittest.TestCase):
    def test_stubtest(self):
        modules = sorted(f"cxbind_tests.{p.stem}" for p in STUBS.glob("test_*.pyi"))
        self.assertTrue(modules, f"no stubs found in {STUBS}")

        # The subprocess doesn't inherit conftest's sys.path change;
        # PYTHONPATH carries it across so stubtest can import the runtime.
        pythonpath = [str(BUILD_DIR), os.environ.get("PYTHONPATH", "")]
        env = {**os.environ, "PYTHONPATH": os.pathsep.join(p for p in pythonpath if p)}

        result = subprocess.run(
            [
                sys.executable, "-m", "mypy.stubtest",
                *modules,
                "--mypy-config-file", str(TESTS / "mypy.ini"),
                "--allowlist", str(TESTS / "stubtest_allowlist.txt"),
                "--concise",
            ],
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
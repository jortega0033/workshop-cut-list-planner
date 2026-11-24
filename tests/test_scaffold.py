import contextlib
import importlib
import io
import subprocess
import sys
import unittest

from cut_planner import __version__
from cut_planner.cli import main

MODULES = ["project", "parts_csv", "layout", "verify", "store", "exports", "server"]


class ModuleSmokeTests(unittest.TestCase):
    def test_modules_import(self):
        for name in MODULES:
            with self.subTest(module=name):
                importlib.import_module(f"cut_planner.{name}")

    def test_manifests_package_imports(self):
        importlib.import_module("tests.manifests")


class CliSmokeTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "cut_planner", *args], capture_output=True, text=True
        )

    def test_help_and_version(self):
        self.assertEqual(self.run_cli("--help").returncode, 0)
        result = self.run_cli("--version")
        self.assertEqual(result.returncode, 0)
        self.assertIn(__version__, result.stdout)

    def test_serve_stub(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = main(["serve"])
        self.assertNotEqual(code, 0)
        self.assertIn("not implemented yet: see #2", err.getvalue())


if __name__ == "__main__":
    unittest.main()

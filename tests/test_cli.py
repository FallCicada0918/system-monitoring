import sys
import io
import unittest
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from cyber_pulse import __version__
from cyber_pulse.cli import main


class TestCLI(unittest.TestCase):
    def test_version_string(self):
        self.assertTrue(len(__version__) > 0)
        self.assertEqual(__version__, "2.0.0")

    def test_cli_version_flag(self):
        original_stdout = sys.stdout
        sys.stdout = io.StringIO()
        original_argv = sys.argv
        sys.argv = ["cpulse", "-v"]

        try:
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 0)
            output = sys.stdout.getvalue()
            self.assertIn("cpulse 2.0.0", output)
        finally:
            sys.stdout = original_stdout
            sys.argv = original_argv

    def test_cli_help_flag(self):
        original_stdout = sys.stdout
        sys.stdout = io.StringIO()
        original_argv = sys.argv
        sys.argv = ["cpulse", "--help"]

        try:
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 0)
            output = sys.stdout.getvalue()
            self.assertIn("CYBER_PULSE", output)
            self.assertIn("hud", output)
            self.assertIn("report", output)
        finally:
            sys.stdout = original_stdout
            sys.argv = original_argv


if __name__ == "__main__":
    unittest.main()

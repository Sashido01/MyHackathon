"""Tests for the repository checker, independent of the future product stack."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_repo import is_text, markdown_targets, validate_markdown_links, validate_text  # noqa: E402


class RepositoryCheckerTests(unittest.TestCase):
    def test_text_file_types(self):
        self.assertTrue(is_text(Path(".gitignore")))
        self.assertTrue(is_text(Path("docs/README.md")))
        self.assertFalse(is_text(Path("assets/logo.png")))

    def test_lf_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "valid.md"
            path.write_bytes(b"hello\n")
            self.assertEqual(validate_text(path), [])

    def test_crlf_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.md"
            path.write_bytes(b"hello\r\n")
            self.assertTrue(any("CR detected" in e for e in validate_text(path)))

    def test_missing_final_newline_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.md"
            path.write_bytes(b"hello")
            self.assertIn("missing final newline", validate_text(path))

    def test_markdown_links_ignore_code_fences_and_web_links(self):
        s = "[local](docs/guide.md)\n[web](https://github.com)\n```md\n[example](fake.md)\n```\n"
        self.assertEqual(markdown_targets(s), ["docs/guide.md"])

    def test_relative_links(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs").mkdir()
            readme = root / "README.md"
            guide = root / "docs" / "guide.md"
            guide.write_text("# Guide\n", encoding="utf-8")
            readme.write_text("[Guide](docs/guide.md)\n", encoding="utf-8")
            self.assertEqual(validate_markdown_links(readme, root), [])
            readme.write_text("[Missing](docs/missing.md)\n", encoding="utf-8")
            self.assertTrue(any("broken relative link" in e for e in validate_markdown_links(readme, root)))


if __name__ == "__main__":
    unittest.main()

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from assistant import config, tools


class ReadFileTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.workspace = Path(self.directory.name).resolve()
        for module in (config, tools):
            patcher = patch.object(module, "WORKSPACE", self.workspace)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.content = "я" * 30001
        (self.workspace / "notes.txt").write_text(self.content, encoding="utf-8")

    def test_rejects_character_limits_outside_declared_range(self):
        for max_chars in (-1, 0, 99, 30001):
            with self.subTest(max_chars=max_chars):
                with self.assertRaises(ValueError):
                    tools.execute("read_file", {"path": "notes.txt", "max_chars": max_chars})

    def test_accepts_character_limit_boundaries(self):
        for max_chars in (100, 30000):
            with self.subTest(max_chars=max_chars):
                result = tools.read_file("notes.txt", max_chars=max_chars)
                self.assertEqual(result["content"], self.content[:max_chars])
                self.assertTrue(result["truncated"])

    def test_default_character_limit(self):
        result = tools.read_file("notes.txt")
        self.assertEqual(result["content"], self.content[:12000])
        self.assertTrue(result["truncated"])

    def test_short_file_is_not_truncated(self):
        (self.workspace / "short.txt").write_text("Привет", encoding="utf-8")
        result = tools.read_file("short.txt", max_chars=100)
        self.assertEqual(result["content"], "Привет")
        self.assertFalse(result["truncated"])


if __name__ == "__main__":
    unittest.main()

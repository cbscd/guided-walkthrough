"""Tests for handover.py (stdlib unittest, no pytest needed).

Run: python3 scripts/tests/test_handover.py
"""
import os
import sys
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import handover  # noqa: E402


class TestSlugify(unittest.TestCase):
    def test_matches_claude_code_layout(self):
        self.assertEqual(
            handover.slugify_project_path("/Volumes/LexarSSD/Projects/AI_Influencer"),
            "-Volumes-LexarSSD-Projects-AI-Influencer",
        )

    def test_underscores_and_dots_become_dashes(self):
        self.assertEqual(
            handover.slugify_project_path("/a/b_c.d"), "-a-b-c-d"
        )


class TestFindCurrentSession(unittest.TestCase):
    def setUp(self):
        import tempfile

        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.project = "/proj/demo"
        self.slug_dir = self.root / handover.slugify_project_path(self.project)
        self.slug_dir.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_returns_newest_transcript_stem(self):
        old = self.slug_dir / "old-session.jsonl"
        new = self.slug_dir / "new-session.jsonl"
        old.write_text("{}")
        new.write_text("{}")
        # Make `new` definitively newer.
        os.utime(old, (time.time() - 100, time.time() - 100))
        os.utime(new, (time.time(), time.time()))
        self.assertEqual(
            handover.find_current_session_id(self.root, self.project), "new-session"
        )

    def test_missing_dir_raises(self):
        with self.assertRaises(FileNotFoundError):
            handover.find_current_session_id(self.root, "/proj/nonexistent")

    def test_empty_dir_raises(self):
        empty = "/proj/empty"
        (self.root / handover.slugify_project_path(empty)).mkdir(parents=True)
        with self.assertRaises(FileNotFoundError):
            handover.find_current_session_id(self.root, empty)


class TestBuildPrompt(unittest.TestCase):
    def test_embeds_both_resume_forms(self):
        p = handover.build_handover_prompt("abc-123", "Set up X", ["do a", "do b"])
        self.assertIn("/resume abc-123", p)
        self.assertIn("claude --resume abc-123", p)

    def test_numbers_steps(self):
        p = handover.build_handover_prompt("id", "T", ["first", "second"])
        self.assertIn("1. first", p)
        self.assertIn("2. second", p)

    def test_instructs_skill_load_and_branch_context(self):
        p = handover.build_handover_prompt("id", "T", ["s"])
        self.assertIn("guided-walkthrough", p)
        self.assertIn("already in the branch", p.lower())
        self.assertIn("Skill tool", p)


if __name__ == "__main__":
    unittest.main()

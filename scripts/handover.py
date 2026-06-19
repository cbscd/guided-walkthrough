# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Build the handover prompt for a guided manual-steps walkthrough and copy it to
the macOS clipboard.

The handover prompt is what you paste into a `/branch` so the branch runs the
walkthrough and knows how to return to the parent session. This script:

  1. Detects the current Claude Code session id (the parent), or takes it via
     --session-id.
  2. Composes the handover prompt from the task title + steps, embedding both
     resume forms (`/resume <id>` and `claude --resume <id>`).
  3. Copies the prompt to the clipboard with pbcopy (macOS only).

It deliberately does NOT touch the end-of-walkthrough summary: that summary is
copied separately and must exclude the resume lines.

stdlib-only, Python 3.9+.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

PROMPT_TEMPLATE = """\
You are in a guided-walkthrough branch. Use the Skill tool to invoke the \
`guided-walkthrough` skill now — it contains the full walkthrough instructions.

You are ALREADY in the branch: skip any step that says to branch or create a \
new session. Go straight to running the walkthrough for the task below.

Parent session (show these at the end, on screen only, never in the clipboard):
  /resume {session_id}
  claude --resume {session_id}

Task: {title}
Steps:
{numbered_steps}
"""


def slugify_project_path(path: str) -> str:
    """Replicate Claude Code's project-dir slug: every non-alphanumeric run-character
    becomes a dash. `/Volumes/LexarSSD/Projects/AI_Influencer` ->
    `-Volumes-LexarSSD-Projects-AI-Influencer`."""
    return re.sub(r"[^A-Za-z0-9]", "-", path)


def find_current_session_id(projects_root: Path, project_path: str) -> str:
    """Return the id of the most recently modified transcript in the project's
    slug directory. The active session's transcript is being appended to right now,
    so it carries the newest mtime."""
    slug_dir = projects_root / slugify_project_path(project_path)
    if not slug_dir.is_dir():
        raise FileNotFoundError(f"no transcript directory at {slug_dir}")
    transcripts = sorted(
        slug_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    if not transcripts:
        raise FileNotFoundError(f"no .jsonl transcripts in {slug_dir}")
    return transcripts[0].stem


def build_handover_prompt(
    session_id: str, title: str, steps: list[str]
) -> str:
    numbered = "\n".join(f"  {i}. {s}" for i, s in enumerate(steps, start=1))
    return PROMPT_TEMPLATE.format(
        session_id=session_id, title=title, numbered_steps=numbered
    )


def copy_to_clipboard(text: str) -> bool:
    """pbcopy the text. Returns True on success, False if pbcopy is unavailable
    (e.g. non-macOS)."""
    if sys.platform != "darwin":
        return False
    try:
        proc = subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True)
        return proc.returncode == 0
    except (OSError, subprocess.CalledProcessError):
        return False


def read_steps(steps_file: str | None) -> list[str]:
    raw = Path(steps_file).read_text() if steps_file else sys.stdin.read()
    return [line.strip() for line in raw.splitlines() if line.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True, help="walkthrough task title")
    parser.add_argument(
        "--steps-file",
        help="file with one step per line; if omitted, steps are read from stdin",
    )
    parser.add_argument(
        "--session-id",
        help="parent session id; auto-detected from the transcript dir if omitted",
    )
    parser.add_argument(
        "--projects-root",
        default=str(Path.home() / ".claude" / "projects"),
        help="root of Claude Code project transcripts",
    )
    parser.add_argument(
        "--project-path",
        default=os.getcwd(),
        help="absolute path of the current project (defaults to cwd)",
    )
    parser.add_argument(
        "--no-copy", action="store_true", help="print the prompt without copying"
    )
    args = parser.parse_args(argv)

    session_id = args.session_id or find_current_session_id(
        Path(args.projects_root), args.project_path
    )
    steps = read_steps(args.steps_file)
    if not steps:
        print("REJECTED: no steps provided.", file=sys.stderr)
        return 2

    prompt = build_handover_prompt(session_id, args.title, steps)

    copied = False
    if not args.no_copy:
        copied = copy_to_clipboard(prompt)

    print(f"parent session id: {session_id}")
    print("return-to-parent lines (embedded in the handover prompt for the branch;")
    print("at the END of the walkthrough they go on screen only, never in the summary clipboard):")
    print(f"  /resume {session_id}")
    print(f"  claude --resume {session_id}")
    if args.no_copy:
        print("clipboard: skipped (--no-copy)")
    elif copied:
        print("clipboard: handover prompt copied via pbcopy")
    else:
        print("clipboard: pbcopy unavailable; paste the prompt below manually")
    print("\n--- handover prompt ---")
    print(prompt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

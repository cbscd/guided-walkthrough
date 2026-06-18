[![skills.sh](https://skills.sh/b/cbscd/guided-walkthrough)](https://skills.sh/cbscd/guided-walkthrough)

# guided-walkthrough

A shareable Claude Code skill that walks a user step-by-step through **manual
setup done outside the session** (installs, logins, interactive CLIs, GUI
clicks). It runs the walkthrough in a dedicated `/branch`, pauses after each step
with `AskUserQuestion`, and hands a summary back to the parent session, with the
parent's resume command surfaced so the user can return.

## Install

Copy the `guided-walkthrough/` directory into either:

- `~/.claude/skills/guided-walkthrough/` — personal, available in all your
  projects, or
- `<repo>/.claude/skills/guided-walkthrough/` — checked into a project so a team
  shares it.

No other setup. The skill is self-contained (SKILL.md + one stdlib-only Python
script).

## Use

- Explicit (guaranteed): type `/guided-walkthrough`.
- Automatic: the description can trigger it, but trigger-eval shows that on its
  own it fires reliably only on near-verbatim phrasings ("run the guided
  walkthrough") and under-fires on plain requests like "install X step by step",
  because the model tends to guide inline instead of loading a behavioral skill.
  It is, however, safe: it does not fire on code work or code explanations.

For dependable automatic firing, add this line to your own `CLAUDE.md` (this is
the recommended path, not optional, if you want it to fire without asking):

```
- For tasks needing manual steps outside the session, use the guided-walkthrough skill.
```

## Requirements

macOS. Uses `pbcopy`, and the `/branch` and `/resume` commands from Claude Code.

## Test

```bash
python3 scripts/tests/test_handover.py
```

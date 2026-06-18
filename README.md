[![skills.sh](https://skills.sh/b/cbscd/guided-walkthrough)](https://skills.sh/cbscd/guided-walkthrough)
[![Install](https://img.shields.io/badge/skills.sh-guided--walkthrough-blue)](https://skills.sh/cbscd/guided-walkthrough)

# guided-walkthrough

```bash
npx skills add cbscd/guided-walkthrough
```

Claude Code skill that walks a user step-by-step through **manual
setup done outside the session** (installs, logins, interactive CLIs, GUI
clicks). It runs the walkthrough in a dedicated `/branch`, pauses after each step
with `AskUserQuestion`, and hands a summary back to the parent session, with the
parent's resume command surfaced so the user can return.

## Use

Type `/guided-walkthrough` to invoke it explicitly.

**For automatic triggering**, copy-paste the following to your `CLAUDE.md`:

```
- For tasks needing manual steps outside the session, use the guided-walkthrough skill.
```

Without it, the skill only fires on near-verbatim phrasings like "run the guided
walkthrough". With it, Claude picks it up reliably for any install, login, or
manual configuration request.

## Requirements

macOS. Uses `pbcopy`, and the `/branch` and `/resume` commands from Claude Code.

For a personal install available across all projects, run the command from your home directory:

```bash
cd ~ && npx skills add cbscd/guided-walkthrough
```

## Test

```bash
python3 scripts/tests/test_handover.py
```

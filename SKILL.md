---
name: guided-walkthrough
description: >-
  Use whenever the user must do hands-on setup OUTSIDE Claude Code that you
  cannot run for them: installing software (brew install, downloading an app),
  setting up or signing up for an account, configuring a service by hand,
  logging in through a browser/OAuth, running an interactive CLI, or clicking
  through a GUI. Triggers on "install X on my machine", "set up Y myself",
  "configure Z by hand", "I have to do this on their site", "guide me step by
  step", "walk me through installing/setting up", "set this up with me", or
  /guided-walkthrough. Instead of guiding inline, run it in a dedicated /branch
  that paces one step at a time and hands a summary back to the parent session.
  Does NOT apply to code you edit/run yourself or to explaining how code works.
  macOS only (uses pbcopy, /branch, /resume).
---

# Guided manual-steps walkthrough

When a task needs the user to do things by hand outside Claude Code, do not dump
the whole list and move on. Run a paced, branch-isolated walkthrough that pauses
after each step and returns a summary to the parent session.

## If you are already in a branch

If the prompt that loaded this skill says "you are already in a branch", skip
steps 1 and 2 below entirely. The parent session id and task steps are already
in the prompt — go straight to step 3 (run the walkthrough).

## When this applies

Any step the user performs away from the session: `brew install`, account
sign-up, OAuth/browser logins, interactive CLIs, copying files by hand, clicking
through a GUI. If the work is all tool calls you can make yourself, this skill
does not apply.

## Flow

1. **Capture the parent session and build the handover prompt.** Write the steps
   (one per line) to a file or pipe them on stdin, then run the bundled script:

   ```bash
   python3 ~/.claude/skills/guided-walkthrough/scripts/handover.py \
     --title "Set up the Foobar CLI" --steps-file /tmp/steps.txt
   ```

   It auto-detects the current (parent) session id from the transcript directory,
   composes the handover prompt with both resume forms baked in, and copies the
   prompt to the clipboard via `pbcopy`. Pass `--session-id <id>` to override the
   auto-detection if you already know the id (more reliable than letting it
   guess). The script prints the session id and the two resume lines; keep them.

2. **Tell the user to branch and paste.** Instruct them to type `/branch
   <name>` and paste the clipboard (the handover prompt) into the new branch.
   `/branch` is a command the user types; you cannot run it for them.

3. **Run the walkthrough (in the branch).** Present ONE step at a time. After
   each step, pause with the `AskUserQuestion` tool. Do NOT advance until the
   user confirms. Structure the options as follows:

   - **If the step involves a shell command:** offer three options: "Run in
     session shell (copies command to clipboard)", "Done, next step", and
     "Something went wrong / I have a question". When the user selects "Run in
     session shell": copy the command to the clipboard via `pbcopy` (without the
     `!` prefix — the user types `! ` then pastes), confirm the copy on screen,
     then immediately call `AskUserQuestion` again with ONLY "Done, next step"
     and "Something went wrong / I have a question". Selecting "Run in session
     shell" must NEVER itself advance to the next step — advancement only happens
     when the user explicitly selects "Done, next step".
   - **Always include:** "Done, next step" and "Something went wrong / I have a
     question". Let the tool's "Other" field carry free-form detail.

4. **Return to the parent.** On "close this session", "return to the main
   session", "exit the walkthrough", or similar: stop, then
   - write a short summary (steps completed, anything skipped or failed, any
     values or paths produced),
   - show the summary inline AND copy it to the clipboard with `pbcopy`,
   - the clipboard copy holds the summary ONLY,
   - then show the two resume lines as separate on-screen lines (NOT in the
     clipboard):

     ```
     /resume <parent-session-id>
     claude --resume <parent-session-id>
     ```

     `/resume` is the likely path (the user is usually still inside Claude Code);
     `claude --resume` is the terminal fallback.

5. **Back in the parent**, the user pastes the summary; continue the original
   work with that context.

## Constraints

- macOS only: relies on `pbcopy`, and on the `/branch` and `/resume` commands
  existing in the user's Claude Code build.
- Run the walkthrough inline in the branch; do not spawn a subagent for it
  (subagents cannot pause to ask the user mid-step).
- Resume lines never go in any clipboard copy; they are always separate
  on-screen lines.

## Verifying changes to the script

```bash
python3 ~/.claude/skills/guided-walkthrough/scripts/tests/test_handover.py
```

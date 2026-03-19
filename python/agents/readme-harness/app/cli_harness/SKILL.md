---
name: cli_harness
description: >
  Improve any GitHub repo's README using the ADK README harness running
  on localhost. Fetches code via GitHub MCP, generates against a quality
  checklist, and refines until a critic approves. Works with Claude Code
  and Gemini CLI.
---

# CLI Harness — README Improvement via ADK

## Prerequisites

The ADK README harness must be running as an api_server on port 8000.

To start it:
```bash
cd <path-to>/adk-readme-harness
source code/.venv/bin/activate
adk api_server . --port 8000
```

## How to Use

When the user asks to improve a README for a GitHub repo, run the helper script
bundled with this skill. The script path is relative to this skill's directory.

Find the `call_harness.py` script in this skill's `scripts/` folder and run:

```bash
python3 <skill-dir>/scripts/call_harness.py <owner/repo>
```

For example, if this skill is installed at `.claude/skills/cli_harness/`:
```bash
python3 .claude/skills/cli_harness/scripts/call_harness.py google/adk-samples
```

Or if installed globally for Gemini CLI:
```bash
python3 ~/.gemini/skills/cli_harness/scripts/call_harness.py google/adk-samples
```

### Save to file
```bash
python3 <skill-dir>/scripts/call_harness.py owner/repo --save improved-readme.md
```

### Custom host
```bash
python3 <skill-dir>/scripts/call_harness.py owner/repo --host http://localhost:9000
```

## Output

- **stderr**: Color-coded progress showing each harness stage (analyzer, writer, critic, feedback, approval)
- **stdout**: The final improved README in markdown

## What Happens Behind the Scenes

The script calls an ADK agent harness running as an api_server. The harness is a
SequentialAgent with two stages:

1. **Codebase Analyzer** — Fetches repo via GitHub MCP (file tree, source, deps, existing README)
2. **Refinement Loop** — A LoopAgent cycles between:
   - **Writer** — Generates README using a SkillToolset with conventions checklist
   - **Critic** — Validates against 9 required sections, calls `exit_loop` when approved

The loop runs up to 3 iterations. You will see the progress streamed in the terminal.

## Trigger Phrases

- "Improve the README for owner/repo"
- "Generate a better README for this GitHub repo: owner/repo"
- "Fix the README for owner/repo"
- "Analyze owner/repo and write a good README"

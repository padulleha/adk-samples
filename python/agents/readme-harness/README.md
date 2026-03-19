# README Improvement Harness with ADK

A harness that fetches a GitHub repo, analyzes the codebase, generates a README against a quality checklist, and refines until a critic approves. Built with ADK's SequentialAgent, LoopAgent, McpToolset, and SkillToolset.

## Architecture

```
readme_harness (SequentialAgent)
├── codebase_analyzer (Agent)          → Fetches repo via GitHub MCP
│   └── tools: [McpToolset]           → output_key: codebase_analysis
└── refinement_loop (LoopAgent, max_iterations: 3)
    ├── readme_writer (Agent)          → Generates README using SkillToolset
    │   └── tools: [SkillToolset]     → output_key: current_readme
    └── readme_critic (Agent)          → Validates against 9-section checklist
        └── tools: [exit_loop]        → output_key: criticism
```

**How it works:**

1. The **analyzer** fetches the repo's file tree, source files, and dependencies via GitHub MCP
2. The **writer** loads a README conventions skill and generates a draft
3. The **critic** checks 9 required sections (Title, Installation, Usage, Configuration, API, Contributing, License, Prerequisites, Project Structure)
4. If any section is missing, the critic provides feedback and the loop continues
5. When all sections pass, the critic calls `exit_loop` and the harness returns the final README

## Prerequisites

- Python 3.11+
- [Google ADK](https://google.github.io/adk-docs/) (`pip install google-adk`)
- A [Google API key](https://aistudio.google.com/apikey)
- A [GitHub Personal Access Token](https://github.com/settings/personal-access-tokens/new)
- Node.js/npx (for the GitHub MCP server)

## Quick Start

```bash
# Clone the repo
git clone https://github.com/GoogleCloudPlatform/adk-samples.git
cd adk-samples/python/agents/readme-harness

# Set up environment
python3 -m venv .venv && source .venv/bin/activate
pip install -e .

# Configure API keys
cp .env.example app/.env
# Edit app/.env with your GOOGLE_API_KEY and GITHUB_PERSONAL_ACCESS_TOKEN
```

## Three Ways to Run

### 1. ADK Web UI (Interactive)

Run the harness inside ADK's built-in web interface. Best for exploring and debugging.

```bash
adk web .
```

Open `http://localhost:8000`, select `app` from the agent dropdown, and type:

> Improve the README for google/adk-samples

You will see each stage execute in real time: analyzer fetching files, writer loading skills, critic providing feedback, and the loop iterating until approval.

### 2. API Server (Programmatic)

Run the harness as a REST API. Other agents, scripts, or services can call it over HTTP.

```bash
adk api_server . --port 8000
```

Test with the bundled helper script:

```bash
python3 app/scripts/call_harness.py google/adk-samples
```

The script streams color-coded progress to stderr and prints the final README to stdout:

```
[   STAGE 1] Analyzing codebase via GitHub MCP...
[     FETCH] google/adk-samples/
[     FETCH] google/adk-samples/README.md
[  ANALYSIS] A comprehensive collection of cross-language sample agents...
[   STAGE 2] Generating README (pass 1)...
[     SKILL] Loading: readme-conventions
[     DRAFT] 87 lines generated
[    REVIEW] Critic reviewing (pass 1)...
[  FEEDBACK] Configuration section needs additions...
[    REFINE] Improving README (pass 2)...
[     DRAFT] 95 lines generated
[    REVIEW] Critic reviewing (pass 2)...
[  APPROVED] Critic approved the README!
```

Save to a file:

```bash
python3 app/scripts/call_harness.py google/adk-samples --save improved-readme.md
```

### 3. CLI Tool Integration (Claude Code / Gemini CLI)

Use the harness from your daily coding CLI. Start the API server, copy the bundled skill, and ask naturally.

**Step 1: Start the harness server**

```bash
adk api_server . --port 8000
```

**Step 2: Install the CLI skill**

The `cli_harness/` folder is a self-contained skill compatible with both Claude Code and Gemini CLI.

For Claude Code:
```bash
cp -r app/cli_harness .claude/skills/cli_harness
```

For Gemini CLI:
```bash
cp -r app/cli_harness ~/.gemini/skills/cli_harness
```

**Step 3: Use it**

In Claude Code:
```
/cli_harness Improve the README for google/adk-samples
```

In Gemini CLI:
```
Use cli_harness to improve the README for google/adk-samples
```

The CLI tool runs the helper script, which calls the ADK harness over HTTP. The harness does the heavy lifting: fetching the repo via GitHub MCP, generating against conventions, validating against the checklist, and refining until the critic approves. The CLI tool is just the interface.

## Project Structure

```
readme-harness/
├── app/
│   ├── __init__.py
│   ├── agent.py              # Root agent: SequentialAgent + LoopAgent
│   ├── skills/
│   │   └── readme-conventions/
│   │       ├── SKILL.md              # L2: README writing instructions
│   │       └── references/
│   │           └── checklist.md      # L3: 9-section quality checklist
│   ├── scripts/
│   │   └── call_harness.py           # Helper script for API server mode
│   └── cli_harness/
│       ├── SKILL.md                  # Skill for Claude Code / Gemini CLI
│       └── scripts/
│           └── call_harness.py       # Bundled helper script
├── .env.example
├── pyproject.toml
└── README.md
```

## ADK Primitives Used

| Primitive | Role in Harness | Docs |
|-----------|----------------|------|
| `SequentialAgent` | Two-stage pipeline: analyze then refine | [Docs](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/) |
| `LoopAgent` | Iterative refinement: writer + critic cycle | [Docs](https://google.github.io/adk-docs/agents/workflow-agents/loop-agents/) |
| `McpToolset` | GitHub repo access via MCP | [Docs](https://google.github.io/adk-docs/tools-custom/mcp-tools/) |
| `SkillToolset` | README conventions loaded on demand | [Docs](https://google.github.io/adk-docs/skills/) |
| `exit_loop` | Critic signals approval to stop the loop | [Source](https://github.com/google/adk-python/tree/main/src/google/adk/tools/exit_loop_tool.py) |
| `output_key` | State passing between agents | [Docs](https://google.github.io/adk-docs/sessions/state/) |

## License

Apache 2.0

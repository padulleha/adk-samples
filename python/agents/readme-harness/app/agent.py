"""README improvement harness built with ADK.

A SequentialAgent pipeline that fetches a GitHub repo via MCP,
generates a README using skill-based conventions, and refines
it in a LoopAgent until a critic approves.
"""

import os
import pathlib

from google.adk.agents import Agent, LoopAgent, SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.skills import load_skill_from_dir
from google.adk.tools import exit_loop
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools.skill_toolset import SkillToolset
from mcp import StdioServerParameters

SKILLS_DIR = pathlib.Path(__file__).parent / "skills"

# --- Tool Group 1: GitHub MCP (fetch repo contents) ---

github_mcp = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-github"],
            env={
                "GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv(
                    "GITHUB_PERSONAL_ACCESS_TOKEN", ""
                ),
            },
        ),
        timeout=30,
    ),
    tool_filter=[
        "get_file_contents",
        "search_code",
        "search_repositories",
        "list_commits",
    ],
)

# --- Tool Group 2: README conventions skill ---

readme_skill = SkillToolset(
    skills=[load_skill_from_dir(SKILLS_DIR / "readme-conventions")],
)

# --- Stage 1: Codebase Analyzer ---

codebase_analyzer = Agent(
    model="gemini-3-flash-preview",
    name="codebase_analyzer",
    instruction="""\
You are a codebase analyst. The user will give you a GitHub repository
(owner/repo format or a full URL).

Your job:
1. Use the GitHub MCP tools to explore the repository.
2. Read the top-level file list and identify key files:
   - README.md (if it exists)
   - package.json, pyproject.toml, requirements.txt, or similar
   - Main source directories (src/, lib/, app/, etc.)
   - Configuration files (.env.example, Dockerfile, etc.)
3. Read the main source files (up to 5 key files) to understand
   what the project does.
4. Read any existing README.md to understand current coverage.

Output a structured analysis with these sections:
- **Project purpose**: One sentence on what this project does.
- **Tech stack**: Languages, frameworks, key dependencies.
- **Key modules**: Main directories and what they contain.
- **Setup requirements**: How to install and configure.
- **API surface**: Main exports, commands, or endpoints.
- **Existing README gaps**: What the current README misses or gets wrong.
  If no README exists, say "No README found."
""",
    tools=[github_mcp],
    output_key="codebase_analysis",
)

# --- Callback: Initialize loop state on first iteration ---


async def init_loop_state(callback_context: CallbackContext) -> None:
    """Set default criticism on first loop pass so {criticism} resolves."""
    if "criticism" not in callback_context.state:
        callback_context.state["criticism"] = (
            "No previous feedback. This is the first draft."
        )


# --- Stage 2a: README Writer ---

readme_writer = Agent(
    model="gemini-3-flash-preview",
    name="readme_writer",
    before_agent_callback=init_loop_state,
    instruction="""\
You are a README writer. Your job is to write or improve a README.md
for the repository described in the codebase analysis below.

**Codebase analysis:**
{codebase_analysis}

**Previous criticism (if any):**
{criticism}

Instructions:
1. Load the readme-conventions skill to learn the required structure.
2. Load the checklist reference for section-by-section quality criteria.
3. Write a complete README.md that covers every required section.
4. If criticism was provided, address every point specifically.
5. Write from a developer's perspective: assume the reader wants to
   clone, install, and use this project within 5 minutes.

Output the full README.md content in markdown format.
""",
    tools=[readme_skill],
    output_key="current_readme",
)

# --- Stage 2b: README Critic ---

readme_critic = Agent(
    model="gemini-3-flash-preview",
    name="readme_critic",
    instruction="""\
You are a README quality reviewer. Review the README below against
the required sections checklist.

**README to review:**
{current_readme}

**Codebase context (for accuracy check):**
{codebase_analysis}

Check each required section:
1. **Title and description**: Clear, one-sentence purpose statement?
2. **Installation**: Step-by-step setup commands that work?
3. **Usage**: At least one code example or CLI command?
4. **Configuration**: Environment variables, config files documented?
5. **API / Key features**: Main capabilities listed?
6. **Contributing**: How to contribute mentioned?
7. **License**: License referenced?

Scoring:
- If ALL sections are present and reasonably complete, call exit_loop.
- If ANY section is missing or clearly incomplete, list what needs
  fixing and do NOT call exit_loop.

Be practical, not pedantic. A section with 2-3 sentences is fine.
A missing section is not.
""",
    tools=[exit_loop],
    output_key="criticism",
)

# --- Stage 2: Refinement Loop ---

refinement_loop = LoopAgent(
    name="refinement_loop",
    sub_agents=[readme_writer, readme_critic],
    max_iterations=3,
)

# --- Root Agent: The Harness ---

root_agent = SequentialAgent(
    name="readme_harness",
    description=(
        "A README improvement harness. Give it a GitHub repo and it "
        "fetches the code, generates a README against a quality checklist, "
        "and refines until the critic approves."
    ),
    sub_agents=[codebase_analyzer, refinement_loop],
)

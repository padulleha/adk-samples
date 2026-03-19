#!/usr/bin/env python3
"""Call the README harness api_server and stream progress.

Usage:
    python scripts/call_harness.py owner/repo [--host localhost:8000] [--save output.md]

The script:
1. Creates a session on the running api_server
2. Sends the repo to the README harness
3. Streams progress (which agent is running, tool calls, feedback)
4. Prints the final README to stdout (or saves to file)
"""

import argparse
import json
import sys
import urllib.error
import urllib.request


def create_session(base_url: str) -> str:
    """Create a new session and return its ID."""
    url = f"{base_url}/apps/app/users/cli_user/sessions"
    req = urllib.request.Request(
        url,
        data=b"{}",
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
        return data["id"]


def run_harness(base_url: str, session_id: str, repo: str):
    """Send repo to the harness and stream progress. Returns final README."""
    url = f"{base_url}/run_sse"
    payload = json.dumps(
        {
            "app_name": "app",
            "user_id": "cli_user",
            "session_id": session_id,
            "new_message": {
                "role": "user",
                "parts": [{"text": f"Improve the README for {repo}"}],
            },
            "streaming": False,
        }
    ).encode()

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    final_readme = ""
    current_agent = ""
    iteration = 0

    with urllib.request.urlopen(req, timeout=300) as resp:
        for raw_line in resp:
            line = raw_line.decode("utf-8").strip()
            if not line or line.startswith(":"):
                continue
            if not line.startswith("data: "):
                continue

            data = line[6:]
            try:
                event = json.loads(data)
            except json.JSONDecodeError:
                continue

            content = event.get("content", {})
            author = content.get("author", event.get("author", ""))
            parts = content.get("parts", [])

            # Track agent transitions
            if author and author != current_agent:
                current_agent = author
                if author == "codebase_analyzer":
                    log("STAGE 1", "Analyzing codebase via GitHub MCP...")
                elif author == "readme_writer":
                    iteration += 1
                    if iteration == 1:
                        log("STAGE 2", "Generating README (pass 1)...")
                    else:
                        log("REFINE", f"Improving README (pass {iteration})...")
                elif author == "readme_critic":
                    log("REVIEW", f"Critic reviewing (pass {iteration})...")

            for part in parts:
                if "functionCall" in part:
                    fc = part["functionCall"]
                    name = fc["name"]
                    args = fc.get("args", {})

                    if name == "exit_loop":
                        log("APPROVED", "Critic approved the README!")
                    elif name == "get_file_contents":
                        path = args.get("path", "/")
                        log(
                            "  FETCH",
                            f"{args.get('owner', '')}/{args.get('repo', '')}/{path}",
                        )
                    elif name == "search_code":
                        log("  SEARCH", f"query: {args.get('query', '')[:60]}")
                    elif name == "load_skill":
                        log("  SKILL", f"Loading: {args.get('name', '')}")
                    elif name == "load_skill_resource":
                        log("  SKILL", f"Reading: {args.get('path', '')}")
                    else:
                        log("  TOOL", f"{name}")

                elif "text" in part:
                    text = part["text"]
                    if author == "codebase_analyzer":
                        # Show first line of analysis
                        first_line = text.strip().split("\n")[0][:120]
                        log("ANALYSIS", first_line)
                    elif author == "readme_writer":
                        # Capture the README output
                        final_readme = text
                        lines = text.strip().split("\n")
                        log("DRAFT", f"{len(lines)} lines generated")
                    elif author == "readme_critic":
                        if "exit_loop" not in text.lower() and len(text) > 30:
                            # Show first line of feedback
                            first_line = text.strip().split("\n")[0][:120]
                            log("FEEDBACK", first_line)

    return final_readme


def log(tag: str, message: str):
    """Print a formatted progress line to stderr."""
    # Color codes for terminal
    colors = {
        "STAGE 1": "\033[36m",  # cyan
        "STAGE 2": "\033[33m",  # yellow
        "REFINE": "\033[33m",  # yellow
        "REVIEW": "\033[35m",  # magenta
        "APPROVED": "\033[32m",  # green
        "ANALYSIS": "\033[36m",  # cyan
        "DRAFT": "\033[33m",  # yellow
        "FEEDBACK": "\033[31m",  # red
        "  FETCH": "\033[90m",  # gray
        "  SEARCH": "\033[90m",  # gray
        "  SKILL": "\033[90m",  # gray
        "  TOOL": "\033[90m",  # gray
    }
    reset = "\033[0m"
    color = colors.get(tag, "")
    print(f"{color}[{tag:>10}]{reset} {message}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Call the README harness")
    parser.add_argument("repo", help="GitHub repo in owner/repo format")
    parser.add_argument(
        "--host", default="http://localhost:8000", help="api_server URL"
    )
    parser.add_argument("--save", help="Save README to file instead of stdout")
    args = parser.parse_args()

    print(f"\033[1m{'=' * 60}\033[0m", file=sys.stderr)
    print(f"\033[1m README Harness — {args.repo}\033[0m", file=sys.stderr)
    print(f"\033[1m{'=' * 60}\033[0m", file=sys.stderr)

    try:
        session_id = create_session(args.host)
        log("SESSION", f"Created: {session_id[:8]}...")
    except urllib.error.URLError:
        print(
            "ERROR: Cannot connect to api_server. Is it running?",
            file=sys.stderr,
        )
        print("Start it with: adk api_server . --port 8000", file=sys.stderr)
        sys.exit(1)

    readme = run_harness(args.host, session_id, args.repo)

    print(f"\033[1m{'=' * 60}\033[0m", file=sys.stderr)

    if args.save:
        with open(args.save, "w") as f:
            f.write(readme)
        log("SAVED", f"README written to {args.save}")
    else:
        # Print README to stdout (progress went to stderr)
        print(readme)


if __name__ == "__main__":
    main()

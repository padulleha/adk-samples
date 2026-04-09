# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test the deployed Small Business Loan Agent on Agent Engine.

Usage:
    python deployment/test_deployed_agent.py --resource-name <RESOURCE_NAME> --pdf <PATH_TO_PDF>

If --resource-name is not provided, it will list available agents and prompt you to pick one.
"""

import argparse
import base64
import os
import random
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

import vertexai
from vertexai import agent_engines


def get_agent(resource_name: str | None = None):
    """Get a deployed agent by resource name, or list available agents."""
    if resource_name:
        return agent_engines.get(resource_name)

    print("No --resource-name provided. Listing deployed agents...\n")
    agents = agent_engines.list()
    agent_list = list(agents)

    if not agent_list:
        print("No agents found. Deploy one first with deploy_to_agent_engine.py")
        sys.exit(1)

    for i, agent in enumerate(agent_list):
        print(f"  [{i}] {agent.display_name} — {agent.resource_name}")

    print()
    choice = input("Select agent number: ").strip()
    try:
        return agent_list[int(choice)]
    except (ValueError, IndexError):
        print("Invalid selection.")
        sys.exit(1)


def test_loan_processing(remote_agent, pdf_path: str):
    """Test loan processing with PDF upload."""
    print("\n" + "=" * 60)
    print(f"Loan processing test with {pdf_path}")
    print("=" * 60)

    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        print(f"Error: PDF not found at {pdf_path}")
        return

    pdf_bytes = pdf_file.read_bytes()
    pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")
    print(f"PDF loaded: {len(pdf_bytes)} bytes")

    sbl_id = f"SBL-2025-{random.randint(10000, 99999)}"
    print(f"Generated loan ID: {sbl_id}")

    session = remote_agent.create_session(user_id="test_user")
    print(f"Session: {session['id']}")

    # Send message as a dict (Content schema) so it serializes over the wire
    content_dict = {
        "role": "user",
        "parts": [
            {"text": f"Process this loan application for {sbl_id}"},
            {
                "inline_data": {
                    "mime_type": "application/pdf",
                    "data": pdf_b64,
                }
            },
        ],
    }

    response = remote_agent.stream_query(
        user_id="test_user",
        session_id=session["id"],
        message=content_dict,
    )

    print("\nStreaming events (Turn 1 - Processing):")
    for event in response:
        if not isinstance(event, dict):
            continue
        author = event.get("author", "unknown")
        # Print text responses
        if "content" in event and "parts" in event["content"]:
            for part in event["content"]["parts"]:
                if "text" in part:
                    print(f"  [{author}] {part['text']}")
        # Print tool/state activity
        actions = event.get("actions", {})
        if actions.get("state_delta"):
            keys = list(actions["state_delta"].keys())
            print(f"  [{author}] State update: {keys}")

    # Turn 2: Approve the loan (human-in-the-loop)
    print("\n" + "-" * 40)
    print("Sending approval: 'yes'")
    print("-" * 40)

    approval_response = remote_agent.stream_query(
        user_id="test_user",
        session_id=session["id"],
        message="yes",
    )

    print("\nStreaming events (Turn 2 - Approval):")
    for event in approval_response:
        if not isinstance(event, dict):
            continue
        author = event.get("author", "unknown")
        if "content" in event and "parts" in event["content"]:
            for part in event["content"]["parts"]:
                if "text" in part:
                    print(f"  [{author}] {part['text']}")
        actions = event.get("actions", {})
        if actions.get("state_delta"):
            keys = list(actions["state_delta"].keys())
            print(f"  [{author}] State update: {keys}")

    print("\n✓ Loan processing completed")


def main():
    parser = argparse.ArgumentParser(description="Test deployed Small Business Loan Agent")
    parser.add_argument(
        "--resource-name",
        type=str,
        help="Agent Engine resource name (e.g., projects/123/locations/us-central1/reasoningEngines/456)",
    )
    parser.add_argument(
        "--pdf",
        type=str,
        default="data/sample_applications/sample_application_complete.pdf",
        help="Path to sample PDF for loan processing test",
    )
    args = parser.parse_args()

    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_AGENT_ENGINE_LOCATION", "us-central1")

    if not project_id:
        print("Error: GOOGLE_CLOUD_PROJECT environment variable must be set.")
        sys.exit(1)

    vertexai.init(project=project_id, location=location)

    remote_agent = get_agent(args.resource_name)
    print(f"\nUsing agent: {remote_agent.display_name}")
    print(f"Resource: {remote_agent.resource_name}")

    test_loan_processing(remote_agent, args.pdf)

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

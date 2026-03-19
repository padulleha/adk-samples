#!/usr/bin/env python
#
# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This module defines a programmatic workflow for code generation and review."""

import asyncio

from google.adk.agents.context import Context
from google.adk.agents.llm_agent import LlmAgent
from google.adk.events.event import Event
from google.adk.workflow._node import node

from .tools import (
    run_integration_tests,
    run_linter,
    run_unit_tests,
)

# --- Node Definitions ---
# Wrap the existing tool functions with the @node decorator to make them
# available to the programmatic workflow.
lint_node = node(run_linter)
unit_test_node = node(run_unit_tests)
integration_test_node = node(run_integration_tests)


# --- Agent Definitions ---
coder_agent = LlmAgent(
    name="coder_agent",
    instruction="You are an expert software engineer. Write Python code to satisfy the following user request: {request}",
)

fixer_agent = LlmAgent(
    name="fixer_agent",
    instruction="""You are an expert debugger. The following code has failed its quality checks.
    Please fix the code based on the findings.

    Code:
    {code}

    Findings:
    {findings}
    """,
)


# --- Workflow Definition ---
@node(rerun_on_resume=True)
async def code_review_workflow(ctx: Context, request: str):
    """A programmatic workflow to generate, test, and fix code."""

    # 1. Sequential Execution: Generate the initial code.
    code = await ctx.run_node(coder_agent, {"request": request})

    max_retries = 3
    for i in range(max_retries):
        yield Event(state={"code": code, "attempt": i + 1})

        # 2. Parallel Execution: Run linter and tests concurrently.
        lint_future = ctx.run_node(lint_node, code)
        unit_test_future = ctx.run_node(unit_test_node, code)
        integration_test_future = ctx.run_node(integration_test_node, code)

        (
            lint_result,
            unit_test_result,
            integration_test_result,
        ) = await asyncio.gather(
            lint_future, unit_test_future, integration_test_future
        )

        # 3. Loop & Conditional Execution: Check results and loop if necessary.
        if (
            lint_result.passed
            and unit_test_result.passed
            and integration_test_result.passed
        ):
            yield Event(state={"status": "All checks passed!"})
            return code  # type: ignore # Success, exit the loop and workflow

        # Collect findings and try to fix the code.
        findings = f"""{lint_result.findings}
            {unit_test_result.findings}
            {integration_test_result.findings}"""

        yield Event(
            state={
                "status": "Checks failed, attempting to fix...",
                "findings": findings,
            }
        )

        code = await ctx.run_node(
            fixer_agent, {"code": code, "findings": findings}
        )

    yield Event(
        state={"status": f"Failed to fix code after {max_retries} attempts."}
    )
    return code  # type: ignore


# To make this workflow deployable, we assign it to root_agent
root_agent = code_review_workflow

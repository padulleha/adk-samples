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

"""This module contains the tools used in the programmatic coder workflow."""

import random
from typing import NamedTuple


class LintResult(NamedTuple):
    passed: bool
    findings: str


class TestResult(NamedTuple):
    passed: bool
    findings: str


LINT_RATE = 0.5
TEST_RATE = 0.3
INTEGRATION_RATE = 0.7


def run_linter(code: str) -> LintResult:
    """Runs a linter on the given code and returns the findings."""
    # Simulate a linter that sometimes finds issues
    if random.random() > LINT_RATE:
        return LintResult(passed=True, findings="")
    else:
        return LintResult(
            passed=False, findings="Lint error on line 5: Unused variable."
        )


def run_unit_tests(code: str) -> TestResult:
    """Runs unit tests on the given code."""
    if random.random() > TEST_RATE:
        return TestResult(passed=True, findings="All unit tests passed.")
    else:
        return TestResult(
            passed=False, findings="Unit Test Failed: test_edge_case"
        )


def run_integration_tests(code: str) -> TestResult:
    """Runs integration tests on the given code."""
    if random.random() > INTEGRATION_RATE:
        return TestResult(passed=True, findings="All integration tests passed.")
    else:
        return TestResult(
            passed=False,
            findings="Integration Test Failed: database connection",
        )

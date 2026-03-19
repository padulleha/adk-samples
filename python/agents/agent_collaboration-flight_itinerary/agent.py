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

"""This module defines a multi-agent collaborative vacation planner."""

from google.adk import Agent
from google.adk.agents.llm_agent import LlmAgent
from pydantic import BaseModel, Field

from .tools import book_flight, convert_currency, get_weather


# --- Pydantic Schemas for typed I/O ---
class FlightInput(BaseModel):
    destination: str = Field(description="The city to fly to.")
    date: str = Field(description="The desired flight date.")


class FlightResult(BaseModel):
    confirmation: str = Field(
        description="The flight booking confirmation details."
    )


# --- Single-Turn Sub-Agents ---
# These agents perform a single, non-interactive task and return a result immediately.
# They can be run in parallel.

weather_checker_agent = Agent(
    name="weather_checker",
    mode="single_turn",
    instruction="Check the weather for a given city using the available tool.",
    tools=[get_weather],
)

currency_converter_agent = LlmAgent(
    name="currency_converter",
    mode="single_turn",
    instruction="Convert a given amount from one currency to another.",
    tools=[convert_currency],
)


# --- Task-Mode Sub-Agent ---
# This agent can ask clarifying questions to complete its assigned task.
# Once the task is complete, it automatically returns control to the parent.

flight_booker_agent = LlmAgent(
    name="flight_booker",
    mode="task",
    instruction="Book a flight for the user. Ask for the destination and date if they are not provided.",
    tools=[book_flight],
    input_schema=FlightInput,
    output_schema=FlightResult,
)


# --- Chat-Mode Sub-Agent ---
# This agent engages in an open-ended conversation. Control must be manually
# transferred away from this agent.

concierge_agent = LlmAgent(
    name="concierge",
    mode="chat",
    instruction="You are a helpful travel concierge. You can chat with the user about their travel preferences, offer suggestions, or discuss what to pack.",
)


# --- Coordinator Agent ---
# This is the main agent that delegates tasks to its sub-agents.

root_agent = LlmAgent(
    name="vacation_planner",
    instruction="""You are a master vacation planner.

You have a team of specialist agents to assist you:
- **weather_checker**: To get the current weather in any city.
- **currency_converter**: To perform currency conversions.
- **flight_booker**: To book flights. This agent may ask for more details.
- **concierge**: A helpful assistant for general travel chat.

Delegate tasks to your team. You can ask the `weather_checker` and `currency_converter` to work in parallel.
For example, you can say: `concurrently check the weather in Paris and convert 100 USD to EUR`.
""",
    sub_agents=[
        weather_checker_agent,
        currency_converter_agent,
        flight_booker_agent,
        concierge_agent,
    ],
)

# Collaborative Planner Workflow

This sample demonstrates a multi-agent workflow where a coordinator agent delegates tasks to a team of specialist sub-agents, each with a different collaboration `mode`.

## 1. Architecture

This workflow implements a vacation planning assistant. A central `root_agent` acts as a coordinator, delegating tasks to a team of sub-agents with specific roles and behaviors:

- **`root_agent` (Coordinator)**: The user interacts with this agent. It understands the user's request and delegates it to the appropriate sub-agent.
- **`weather_checker_agent` (`single_turn`)**: A non-interactive agent that takes a city, calls a tool to get the weather, and returns the result immediately.
- **`currency_converter_agent` (`single_turn`)**: Another non-interactive agent that performs a currency conversion and returns the result. Because they are `single_turn`, this and the weather agent can be run concurrently.
- **`flight_booker_agent` (`task`)**: A semi-autonomous agent that handles flight bookings. It can ask the user clarifying questions (e.g., for a date or destination) to complete its task, and automatically returns control to the coordinator when done.
- **`concierge_agent` (`chat`)**: A fully interactive agent for open-ended conversation about travel plans. Control is managed manually, allowing for a free-form chat session.

```mermaid
graph TD
    A[User] <=> B(root_agent: Coordinator);
    B --> C{Delegate Task};
    C -- "Check Weather" --> D(weather_checker: single_turn);
    C -- "Convert Currency" --> E(currency_converter: single_turn);
    C -- "Book Flight" --> F(flight_booker: task);
    C -- "General Chat" --> G(concierge: chat);
    D --> B;
    E --> B;
    F <=> A; F-->B;
    G <=> A;
```

## 2. Feature: Agent Collaboration Modes

This sample showcases the three different `mode` behaviors for sub-agents in a collaborative team:

- **`single_turn`**: For simple, non-interactive tasks that can be completed in one step. These agents are ideal for tool use and can be executed in parallel, as shown with the weather and currency agents.
- **`task`**: For multi-step tasks that require some interaction but have a clear end goal. The agent can ask for clarifying information but will automatically return control to the parent agent upon completion.
- **`chat`**: For open-ended, human-in-the-loop interactions. This mode allows for a continuous conversation until control is explicitly transferred to another agent.

## 3. Deployment Guide

To deploy this workflow agent, you can use the `adk deploy` command.

### Prerequisites

Ensure you have authenticated with Google Cloud:
```sh
gcloud auth application-default login
```

Your GCP `project` and `location` should be set in a `.env` file in the root of this project.

### Deployment Command

```sh
adk deploy workflow-collaborative-planner/agent.py:root_agent --display-name "Collaborative Vacation Planner"
```

### Example Use

After deploying, you can interact with the coordinator agent to plan a trip.

**Example 1 (Parallel Single-Turn):**
> "Concurrently check the weather in Tokyo and convert 500 USD to JPY."

The coordinator will delegate these tasks to the two `single_turn` agents, which will execute in parallel.

**Example 2 (Task Mode):**
> "Book a flight."

The coordinator will transfer control to the `flight_booker` agent, which will then ask you for the destination and date before completing the booking and returning control.

**Example 3 (Chat Mode):**
> "Let me chat with the concierge."

The coordinator will transfer you to the `concierge` agent for a free-form conversation.

# YouTube Analyst Agent

The YouTube Analyst Agent is a powerful Gemini-powered assistant designed to provide deep insights into YouTube content, channel performance, and audience engagement. It leverages the YouTube Data API to retrieve real-time data and uses Gemini's reasoning capabilities to analyze trends, sentiment, and metrics.

## Demo

[![YouTube Analyst Demo](https://img.youtube.com/vi/PEKMLi52OzM/0.jpg)](https://www.youtube.com/watch?v=PEKMLi52OzM)

*Click the image above to watch the agent in action.*

---

## Overview

This agent assists marketers, content creators, and researchers in understanding the YouTube landscape. It serves as a comprehensive demonstration of two key ADK capabilities:

1.  **Extensive YouTube API Integration:** Demonstrates how to orchestrate multiple complex API calls (search, video details, channel stats, comments) into a seamless conversational flow.
2.  **Interactive Visualizations with ADK:** Showcases the use of a specialized sub-agent to dynamically generate and execute Python code to produce interactive Plotly charts as artifacts within the ADK environment.

### Architecture

```mermaid
graph TD
    User[User] -->|Query| RootAgent[YouTube Analyst Agent]
    RootAgent -->|Calls| YouTubeTools[YouTube Data API Tools]
    YouTubeTools -->|Returns Data| RootAgent
    RootAgent -->|Delegates| VizAgent[Visualization Agent]
    VizAgent -->|Generates Code| PythonExec[Python Executor]
    PythonExec -->|Returns Artifact| VizAgent
    VizAgent -->|Returns Chart| RootAgent
    RootAgent -->|Final Response| User
```

## Agent Details

| Feature | Description |
| --- | --- |
| **Interaction Type:** | Conversational / Analytics |
| **Complexity:**  | Intermediate |
| **Agent Type:**  | Multi-Agent (Root + Visualization Sub-Agent) |
| **Components:**  | YouTube Data API, ADK Tools, Interactive Plotly Charts |
| **Vertical:**  | Marketing / Media Analytics |

### Component Details

*   **Agents:**
    *   `youtube_agent` (Root): The main orchestrator that handles user queries, YouTube data retrieval, and analysis tasks.
    *   `visualization_agent` (Sub-agent): Specialized in generating Python code to create interactive Plotly charts based on data provided by the root agent.

*   **Tools:**
    *   `search_youtube`: Finds videos matching specific queries and date filters.
    *   `get_video_details`: Retrieves comprehensive stats (views, likes, comments) for video IDs.
    *   `get_channel_details`: Fetches subscriber counts and total view metrics for channels.
    *   `get_video_comments`: Downloads top-level comments for sentiment analysis.
    *   `calculate_engagement_metrics`: Computes engagement and active rates.
    *   `analyze_sentiment_heuristic`: Performs keyword-based sentiment scoring on text.
    *   `render_html`: Renders HTML content (used for reports).
    *   `execute_visualization_code`: Executes generated plotting code to produce artifacts.

## Setup and Installation

### Folder Structure
```
youtube-analyst/
├── README.md                 # Documentation
├── pyproject.toml            # Dependencies and configuration
├── .env                      # Environment variables (credentials)
└── youtube_analyst/          # Main Package
    ├── __init__.py
    ├── agent.py              # Main Agent logic
    ├── config.py             # Configuration loader
    ├── tools.py              # YouTube API tools
    ├── visualization_agent.py # Sub-agent for charting
    ├── visualization_tools.py # Tools for code execution & plotting
    └── prompts/              # System instructions
```

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) for dependency management and packaging
  - See the official [uv website](https://docs.astral.sh/uv/) for installation.

  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

- Google Cloud project (with Vertex AI enabled)
- [YouTube Data API key](https://developers.google.com/youtube/v3/getting-started) with YouTube Data API v3 enabled
- A local `.env` file (copy from `.env.example`) with your runtime credentials

## Agent Starter Pack (recommended)

Use the [Agent Starter Pack](https://goo.gle/agent-starter-pack) to scaffold a production-ready project and choose your deployment target ([Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview) or [Cloud Run](https://cloud.google.com/run)), with CI/CD and other production features. The easiest way is with [uv](https://docs.astral.sh/uv/) (one command, no venv or pip install needed):

```bash
uvx agent-starter-pack create my-youtube-analyst -a adk@youtube-analyst
```

If you don't have uv yet: `curl -LsSf https://astral.sh/uv/install.sh | sh`

The starter pack will prompt you to select deployment options and set up your Google Cloud project.

<details>
<summary>Alternative: Using pip + virtual environment</summary>

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade agent-starter-pack
agent-starter-pack create my-youtube-analyst -a adk@youtube-analyst
```

</details>

From your newly created project directory (e.g. `my-youtube-analyst`), copy the env template and configure credentials:

```bash
cp .env.example .env
```

Set `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION=global`, `GOOGLE_GENAI_USE_VERTEXAI=1`, and `YOUTUBE_API_KEY`, then run:

```bash
cd my-youtube-analyst
uv sync --dev
uv run adk run youtube_analyst
```

For the Web UI (recommended for interactive charts):

```bash
uv run adk web
```

Then select `youtube_analyst` from the dropdown menu.

---

<details>
<summary>Alternative: Local development (run from this sample repo)</summary>

### Clone and install

```bash
git clone https://github.com/google/adk-samples.git
cd adk-samples/python/agents/youtube-analyst
```

Stay in `python/agents/youtube-analyst` for the steps below.

```bash
uv sync
```

### Configuration

Copy the environment template and edit values:

```bash
cp .env.example .env
```

Set `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION=global`, `GOOGLE_GENAI_USE_VERTEXAI=1`, and `YOUTUBE_API_KEY`.

### Running the agent locally

**CLI:**

```bash
adk run .
```

**ADK web UI:**

```bash
adk web
```

Then select `youtube_analyst` from the dropdown.

</details>

## Example Interactions

- **Trend Analysis:** "Find the top 5 videos about 'Generative AI' from the last month and plot their view counts."
- **Competitor Research:** "Compare the engagement rates of MKBHD and Linus Tech Tips."
- **Audience Feedback:** "What is the sentiment of the comments on the latest OpenAI video? Summarize the top concerns."
- **Visual Reporting:** "Create a bar chart comparing the subscriber counts of the top 3 tech reviewers."

### Sample Trace (Under the Hood)

Here is what happens when you ask: *"Compare the engagement on the latest video from Running HK."*

```text
[User]: Compare the engagement on the latest video from Running HK.

[youtube_agent]: Calling tool `search_youtube`...
Arguments: {"query": "Running HK", "max_results": 1}

[Tool Output]: [{"title": "HK100 2024 Highlights", "videoId": "AbCdEfGhIjK", "channelTitle": "Running HK"}]

[youtube_agent]: Calling tool `get_video_details`...
Arguments: {"video_ids": ["AbCdEfGhIjK"]}

[Tool Output]: [{"videoId": "AbCdEfGhIjK", "viewCount": "50000", "likeCount": "2500", "commentCount": "150", ...}]

[youtube_agent]: Calling tool `calculate_engagement_metrics`...
Arguments: {"view_count": 50000, "like_count": 2500, "comment_count": 150}

[Tool Output]: {"engagement_rate": 5.3, "active_rate": 0}

[youtube_agent]: The latest video from Running HK has an engagement rate of 5.3%. Would you like me to visualize this against other running KOLs?
```

## Troubleshooting

- **API Errors:** If you see "Quota Exceeded" or 403 errors, ensure your `YOUTUBE_API_KEY` is valid and has the YouTube Data API v3 enabled in the Google Cloud Console.
- **Visualization Failures:** If a chart fails to render, ask the agent to "try again" or "check the data format." The visualization agent writes code dynamically, and sometimes a retry fixes syntax issues.
- **Empty Results:** If searches return nothing, try broadening your query or removing date filters.

## Customization

- **Add New Metrics:** Extend `tools.py` to calculate custom metrics like "views per subscriber" or "comment-to-like ratio."
- **Enhance Sentiment:** Replace the heuristic sentiment tool in `tools.py` with a call to the Gemini API for more nuanced analysis of comments.
- **Database Integration:** Modify `tools.py` to save analysis results to BigQuery or a local SQL database for long-term tracking.

## Authors

- Pili Hu
- Jasmine Tong
- Kun Wang
- Jeff Yang

## Disclaimer

This agent sample is provided for illustrative purposes only and is not intended for production use. It serves as a basic example of an agent and a foundational starting point for individuals or teams to develop their own agents.

This sample has not been rigorously tested, may contain bugs or limitations, and does not include features or optimizations typically required for a production environment.

Users are solely responsible for any further development, testing, security hardening, and deployment of agents based on this sample. We recommend thorough review, testing, and the implementation of appropriate safeguards before using any derived agent in a live or critical system.
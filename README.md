# ADK Samples

A collection of sample agents and applications built with [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/).

> This is a community fork of [google/adk-samples](https://github.com/google/adk-samples).

## Overview

This repository contains ready-to-use sample agents demonstrating various capabilities of the Agent Development Kit (ADK), including:

- Multi-agent orchestration
- Tool use and function calling
- Retrieval-augmented generation (RAG)
- Streaming and async agents
- Integration with Google Cloud services

## Prerequisites

- Python 3.11+
- [Google ADK](https://pypi.org/project/google-adk/) (`pip install google-adk`)
- A Google Cloud project with the Vertex AI API enabled
- [gcloud CLI](https://cloud.google.com/sdk/docs/install) configured

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-org/adk-samples.git
cd adk-samples
```

### 2. Set up a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies

Each sample has its own `requirements.txt`. Navigate to the sample directory and install:

```bash
cd agents/<sample-name>
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
# Edit .env with your Google Cloud project details
```

### 5. Run a sample

```bash
adk run agents/<sample-name>
```

Or launch the ADK web UI:

```bash
adk web
```

> **Personal note:** I've found `adk web` the easiest way to explore samples interactively — it hot-reloads on file changes, which is handy during development.
>
> **Tip:** If you're on macOS and `adk web` opens a blank page, try visiting `http://127.0.0.1:8000` instead of `http://localhost:8000` — fixed a confusing issue for me.
>
> **Tip:** If you get an `Application Default Credentials` error on first run, execute `gcloud auth application-default login` and try again — easy to miss in the setup docs.
>
> **Tip:** If you have multiple Google Cloud projects and want to quickly switch between them without editing `.env`, you can override the project inline: `GOOGLE_CLOUD_PROJECT=my-other-project adk run agents/<sample-name>` — saves time when testing across projects.
>
> **Tip:** To avoid accidentally committing your `.env` file, double-check that `.env` is listed in `.gitignore` before your first commit — `grep '.env' .gitignore` should confirm it.

## Repository Structure

```
adk-samples/
├── agents/                  # Individual agent samples
│   ├── customer-service/    # Customer service agent example
│   ├── data-analysis/       # Data analysis agent example
│   └── ...                  # More samples
├── .github/                 # GitHub Actions workflows and templates
└── README.md
```

## Contributing

Contributions are welcome! Please read our [contribution guidelines](CONTRIBUTING.md) before submitting a pull request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/my-new-sample`)
3. Commit your changes (`git commit -m 'feat: add new sample agent'`)
4. Push to the branch (`
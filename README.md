# Setup
- Install Python version 3.11 (pyenv recommended)
- Run the `install_dependencies.sh` script to install requirements and setup a virtual environment (`.venv`)
- Activate the virtual environment `source .venv/bin/activate`
- Create `.env` file and populate it with API keys:
    - `OPENAI_API_KEY`

# Running Locally
Standup the Milvus Vector Database container by running:
```shell
docker compose up
```

Then run the `run_app.sh` script to start a local instance of the application:
```shell
./run_app.sh
```

Once the application starts, open your browser and navigate to:
```
http://localhost:5000
```

# Application Architecture

The application follows a modular architecture to ensure flexibility and maintainability. Here's an overview of the main components:

- **`app/services/llm_interaction.py`**: This module provides an abstraction layer for interacting with language models (LLMs) and embeddings. It allows the application to dynamically switch between different LLMs based on configuration, without modifying the codebase.

- **`app/utils/util.py`**: This module contains utility functions for car diagnostics, such as generating diagnostic context using the selected LLM and embeddings.

- **`app/routes/`**: This directory contains the route definitions for the application, including routes for handling ChatGPT interactions and form submissions.

- **`app/__init__.py`**: This module initializes the Flask application and sets up the necessary configurations, such as loading environment variables and registering blueprints.




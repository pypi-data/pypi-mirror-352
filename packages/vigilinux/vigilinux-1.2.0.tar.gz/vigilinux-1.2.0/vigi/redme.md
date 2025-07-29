# Vigi - Your Versatile AI-Powered CLI Assistant

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
<!-- Add other badges as appropriate, e.g., license, build status -->

Vigi is a comprehensive command-line interface (CLI) application designed to assist with a wide range of programming, system administration, and development tasks. It leverages generative AI to understand natural language queries and provide code, shell commands, Docker assistance, and complete software project generation.

**Core Capabilities:**

*   **Natural Language Understanding:** Interact with Vigi using plain English.
*   **Shell Command Generation:** Get tailored shell commands for your OS and shell (Linux, macOS, Windows).
*   **Shell Command Execution & Explanation:** Execute generated commands, get explanations, and safety ratings.
*   **AI-Powered Interactive Shell (`.shell`, `.memshell`):** An intelligent shell environment that understands context, helps with complex tasks, and manages dependencies.
*   **Code Generation (`.c`):** Generate Python code snippets or entire project structures.
*   **Docker Assistance (`--docker`):** Get help with Docker commands, create Dockerfiles, search/pull images, and run containers interactively.
*   **Developer Agent (DeveloperCH - invoked via `.c`):** An AI agent that can plan, generate, and modify entire software projects based on your prompts.
*   **Persona System:** Interact with Vigi using different AI personas (default, shell-focused, code-focused, or custom-created).
*   **Interactive Chat Mode (`.talk`, `.prs`):** Engage in conversations with Vigi for general assistance or specific tasks.
*   **Extensible Functions/Procedures:** Add custom Python functions that Vigi can call.
*   **Configuration & Caching:** Customize Vigi's behavior and cache responses for speed.

---

## Table of Contents

1.  [Features](#features)
2.  [Core Modules](#core-modules)
3.  [Installation](#installation)
4.  [Configuration](#configuration)
5.  [Usage](#usage)
    *   [General CLI Options](#general-cli-options)
    *   [Shell Assistance](#shell-assistance)
    *   [Code Generation (DeveloperCH)](#code-generation-developerch)
    *   [Docker Module](#docker-module)
    *   [Interactive Chat & Personas](#interactive-chat--personas)
    *   [Custom Procedures/Functions](#custom-proceduresfunctions)
6.  [Module Deep Dives](#module-deep-dives)
    *   [Shell Smart Module (`.shell`, `.memshell`)](#shell-smart-module-shell-memshell)
    *   [Docker Module (`--docker`)](#docker-module---docker)
    *   [DeveloperCH Module (`.c`)](#developerch-module-c)
7.  [Troubleshooting](#troubleshooting)

---

## Features

*   **Shell Command Generation:**
    *   OS-specific commands (Linux, macOS, Windows).
    *   Shell-specific syntax (Bash, Zsh, PowerShell, CMD).
    *   Handles complex multi-step tasks by chaining commands.
    *   Infers commands from vague requests.
*   **Shell Command Description:**
    *   Provides concise explanations of shell commands and their arguments.
*   **Python Code Generation:**
    *   Generates Python code snippets directly.
    *   Can generate entire project structures via the DeveloperCH module.
*   **Interactive REPL/Chat:**
    *   Persistent chat sessions with history.
    *   Markdown rendering for AI responses.
    *   Execute generated Python code within the REPL.
*   **Persona Management:**
    *   Pre-defined personas for different tasks (General, Shell, Code, Describe Shell).
    *   Interactive persona creation and selection.
    *   Load personas from JSON files.
*   **Extensible Tooling:**
    *   Define custom Python "Procedures" (functions) that the AI can invoke to perform specific actions.
*   **Docker Assistance:**
    *   Interactive Dockerfile and `.dockerignore` generation for various project types (Python, Node.js, Static HTML/CSS/JS, Generic).
    *   Search Docker Hub for images.
    *   Inspect image compatibility with your system.
    *   Pull Docker images.
    *   Run existing local Docker images with custom options.
    *   List local images and containers.
*   **DeveloperCH - AI Software Developer:**
    *   Generates complete project structures from a high-level prompt.
    *   Plans development steps and file paths.
    *   Generates code for multiple files.
    *   Engages in conversational interaction to modify code, answer questions about the codebase, or add features.
    *   Stores project context (plan, files, history) in a `.vigi_dev_meta` folder within the project.
*   **Shell Smart - Intelligent Shell Environment:**
    *   Interactive AI-powered shell session.
    *   Context-aware command generation.
    *   Command explanation and safety validation.
    *   Optional command execution with output summarization.
    *   Error handling and retry suggestions.
    *   Automatic dependency checking and (with approval) installation.
    *   Session memory for conversation history.
*   **Configuration & Caching:**
    *   Global configuration via `~/Desktop/VIGI/.vigirc`.
    *   Caching for chat history and AI model responses to improve speed and reduce API calls.
*   **User-Friendly CLI:**
    *   Rich formatting for better readability.
    *   Interactive prompts and selections using `questionary` and `typer`.
    *   Helpful epilog with usage examples.

---

## Core Modules

Vigi is composed of several key modules:

*   **`vigi.start`**: The main entry point for the CLI, handling argument parsing and dispatching to various handlers and sub-modules.
*   **`vigi.config`**: Manages application configuration, loading settings from `~/Desktop/VIGI/.vigirc` and environment variables.
*   **`vigi.tools_and_personas`**: Handles the loading and management of AI "Personas" and custom "Procedures" (functions).
*   **`vigi.handler`, `vigi.default_handler`, `vigi.chat_handler`, `vigi.repl_handler`**: Core logic for interacting with the AI model, managing conversation history, and processing user prompts in different modes.
*   **`vigi.shell_smart`**: Implements the AI-powered interactive shell (`.shell`, `.memshell`). It uses LangGraph for its agentic behavior.
*   **`vigi.docker_part`**: Provides Docker-related assistance, including interactive project setup and command generation. It also uses LangGraph.
*   **`vigi.developerch`**: The AI software development agent capable of creating and modifying projects.
*   **`vigi.consoleUI`**: Manages the Rich-based rendering of markdown and text in the console.
*   **`vigi.corefunctions`**: Contains utility functions like opening an editor for prompts and running shell commands.
*   **`vigi.hold_data`**: Implements a generic caching decorator.

---

## Installation

1.  **Prerequisites:**
    *   Python 3.9 or higher.
    *   `pip` (Python package installer).
    *   Git (optional, for cloning if you're not installing via pip from a package).
    *   Docker Desktop (or Docker Engine on Linux) installed and running if you plan to use the Docker module or have Vigi Shell Smart manage Docker-related dependencies.

2.  **Clone the Repository (if applicable):**
    ```bash
    git clone <repository_url>
    cd vigi-project-directory
    ```

3.  **Install Dependencies:**
    It's highly recommended to use a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    ```
    If you are installing Vigi as a package (e.g., via `pip install vigi`), dependencies should be handled automatically.

4.  **API Keys:**
    Vigi requires API keys for the AI models it uses. Set these as environment variables:
    *   **Google Gemini:** Set the `GOOGLE_API_KEY` environment variable. This is the primary key used by most Vigi features.
        ```bash
        export GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
        ```
    *   **Tavily Search (for Shell Smart web search):** Set `TAVILY_API_KEY`.
        ```bash
        export TAVILY_API_KEY="YOUR_TAVILY_API_KEY"
        ```
    *   **Groq (for Docker module LLM, optional):** Set `GROQ_API_KEY` if you intend to use Groq via the Docker module's configuration.
        ```bash
        export GROQ_API_KEY="YOUR_GROQ_API_KEY"
        ```
    *Note: The `config.py` file contains a placeholder API key. This is **NOT** recommended for use and is likely non-functional. Always use your own API keys set via environment variables.*

5.  **Project Directory:**
    Vigi creates a directory structure at `~/Desktop/VIGI/` to store:
    *   `roles/`: Custom personas.
    *   `functions/`: Custom procedures.
    *   `chat_cache/`: Chat history.
    *   `cache/`: General API response cache.
    *   `.vigirc`: Configuration file.
    This directory will be created automatically on the first run if it doesn't exist.

6.  **Make Vigi Executable (if installed from source):**
    You might want to create a symlink or add the Vigi script to your PATH for easier access. If Vigi is installed as a package, the `vg` command should be available.
    Example for symlink (after `pip install .` or similar):
    ```bash
    # Find where vg is installed, e.g., .venv/bin/vg
    # sudo ln -s /path/to/your/vigi-project-directory/.venv/bin/vg /usr/local/bin/vg
    ```

---

## Configuration

Vigi's behavior can be customized through a configuration file and environment variables.

*   **Configuration File:** `~/Desktop/VIGI/.vigirc`
    This file is created automatically. It stores key-value pairs.
*   **Environment Variables:** Many settings in `.vigirc` can be overridden by environment variables (e.g., `DEFAULT_MODEL`, `CHAT_CACHE_LENGTH`).

**Key Configuration Options (from `config.py`):**

| Setting                      | Environment Variable         | Default (`.vigirc`)                      | Description                                                                |
| ---------------------------- | ---------------------------- | ---------------------------------------- | -------------------------------------------------------------------------- |
| Chat Cache Path              | `CHAT_CACHE_PATH`            | `~/Desktop/VIGI/chat_cache`            | Path to store chat session histories.                                      |
| General Cache Path           | `CACHE_PATH`                 | `~/Desktop/VIGI/cache`                 | Path for general API response caching.                                     |
| Chat Cache Length            | `CHAT_CACHE_LENGTH`          | `100`                                    | Max number of message turns (user + assistant) to keep in chat history.    |
| Request Timeout              | `REQUEST_TIMEOUT`            | `350`                                    | Timeout in seconds for API requests.                                       |
| Default AI Model             | `DEFAULT_MODEL`              | `gemini-1.5-flash`                       | Default model for AI interactions.                                         |
| Default User Color (Rich)    | `DEFAULT_COLOR`              | `cyan`                                   | Default color for user input in Rich console displays.                     |
| Persona Storage Path         | `ROLE_STORAGE_PATH`          | `~/Desktop/VIGI/roles`                 | Directory to store custom persona JSON files.                              |
| Default Execute Shell Cmd    | `DEFAULT_EXECUTE_SHELL_CMD`  | `false`                                  | Default action in shell assistance mode ('e'xecute or 'a'bort).          |
| Disable Streaming            | `DISABLE_STREAMING`          | `false`                                  | Set to `true` to disable streaming AI responses.                         |
| Code Theme (Rich)            | `CODE_THEME`                 | `vigi-dark`                              | Theme for code blocks in Markdown rendering.                               |
| Custom Functions Path        | `VIGI_FUNCTIONS_PATH`        | `~/Desktop/VIGI/functions`             | Path to load custom Python procedures from.                                |
| Use Custom Functions         | `VIGI_USE_FUNCTIONS`         | `true`                                   | Whether to allow Vigi to use custom functions/tools.                       |
| Show Functions Output        | `SHOW_FUNCTIONS_OUTPUT`      | `false`                                  | If `true`, displays the output of called functions in the chat.            |
| API Base URL                 | `API_BASE_URL`               | `https://generativelanguage.googleapis.com/v1beta` | Base URL for the generative AI API.                                        |
| Prettify Markdown            | `PRETTIFY_MARKDOWN`          | `true`                                   | Enable Rich library's Markdown rendering.                                  |
| Use Vigi Core (LiteLLM)      | `USE_VIGI_CORE`              | `false`                                  | Set to `true` to use LiteLLM as the API gateway (experimental).            |
| Shell Interaction (Prompt)   | `SHELL_INTERACTION`          | `true`                                   | Whether to prompt for execute/abort after shell command generation.        |
| OS Name Override             | `OS_NAME`                    | `auto`                                   | Manually set OS name (e.g., "Linux/Ubuntu 22.04"). `auto` for detection. |
| Shell Name Override          | `SHELL_NAME`                 | `auto`                                   | Manually set shell name (e.g., "bash"). `auto` for detection.              |
| Vigi API Key (Internal)      | `VIGI_API_KEY`               | (Hardcoded placeholder, **use ENV VARS**) | AI API Key. **Strongly recommend using `GOOGLE_API_KEY` environment variable.** |

---

## Usage

Vigi is invoked using the `vg` command (or `python -m vigi.start` if not installed on PATH).

```bash
vg [OPTIONS] [PROMPT_TEXT...]
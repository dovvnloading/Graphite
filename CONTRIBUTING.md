# Contributing to Graphite

First off, thank you for considering contributing to Graphite! It's people like you that make the open-source community such a fantastic place to learn, inspire, and create. All contributions are welcome and greatly appreciated.

This document provides guidelines for contributing to the project. Please read it to ensure a smooth and effective contribution process for everyone involved.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Pull Requests](#pull-requests)
- [Understanding the Architecture](#understanding-the-architecture)
- [Development Setup](#development-setup)
- [Style Guides](#style-guides)
  - [Git Commit Messages](#git-commit-messages)
  - [Python Styleguide](#python-styleguide)

## Code of Conduct

This project and everyone participating in it is governed by a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report any unacceptable behavior.

## How Can I Contribute?

There are many ways to contribute to Graphite, from writing code and documentation to submitting bug reports and feature requests.

### Reporting Bugs

If you encounter a bug, please open an issue on GitHub. When filing a bug report, please include the following:

*   **A clear and descriptive title** for the issue.
*   **A detailed description of the problem**, including the steps to reproduce the bug.
*   **The expected behavior** and what is happening instead.
*   **Your operating system and Graphite version**.
*   **Any relevant screenshots or logs**.

### Suggesting Enhancements

If you have an idea for a new feature or an improvement to an existing one, we'd love to hear it! To ensure your effort is not wasted, please **open an issue on GitHub to discuss the idea first**. This allows for a discussion with the maintainers and community before you begin implementation.

When suggesting an enhancement, please include:

*   **A clear and descriptive title** for the issue.
*   **A detailed description of the proposed enhancement** and the problem it solves.
*   **Any mockups or examples** that might help to illustrate your idea.

### Pull Requests

Ready to contribute code? Please follow these steps to ensure your contribution can be smoothly integrated.

**Important: Before You Start Coding**

1.  **Sync with the `main` branch.** The project is under active development. To avoid building on an outdated version, please pull the latest changes from the official `main` branch before creating your own branch.
2.  **Open an Issue First.** For any new feature or significant change, please open an issue to discuss your plan. This helps prevent duplicated effort and ensures your proposed changes align with the project's direction.

**The Pull Request Process**

1.  **Fork the repository** on GitHub.
2.  **Create a new branch** from the up-to-date `main` branch (`git checkout -b feature/your-feature-name`).
3.  **Make your changes** in your branch. Please see the architecture guide below to understand where your changes should go.
4.  **Commit your changes** with clear, descriptive messages.
5.  **Push your branch** to your forked repository.
6.  **Create a pull request** to the `main` branch of the official Graphite repository.
7.  In your pull request, **provide a clear description of the changes** you have made and reference the issue number it resolves (e.g., "Closes #42").

## Understanding the Architecture

Graphite has been refactored from a single file into a modular structure. Understanding this structure is key to contributing effectively. All development should be done within these files, not by creating a new monolithic script.

*   `graphite_app.py`: **Main Application Entry Point.** Contains the `ChatWindow` class, toolbar setup, and event handling. This is the primary file for launching the app and managing the main UI.
*   `graphite_ui.py`: **The UI Layer.** Contains all custom Qt widgets, dialogs, and `QGraphicsItem` subclasses (`ChatNode`, `ConnectionItem`, `Frame`, `Note`, `ChatView`, `ChatScene`, etc.). All visual components belong here.
*   `graphite_core.py`: **Core Logic and Data.** Manages data persistence (`ChatDatabase`) and session management (`ChatSessionManager`), including serialization/deserialization of scene elements.
*   `graphite_agents.py`: **AI and Backend Logic.** Contains all classes related to LLM interaction, including the `ChatAgent`, specialized tool agents, and the `QThread` workers for running AI tasks in the background.
*   `graphite_config.py`: **Global Configuration.** A simple file for storing global settings, such as default model names.

## Development Setup

To get started with developing on Graphite, follow these steps:

1.  **Prerequisites**:
    *   Python 3.8 or newer.
    *   Ollama installed and running.

2.  **Install an LLM Model**:
    Before running Graphite, you need a model for Ollama. The current default is `qwen2.5:7b-instruct`. Open your terminal and run:
    ```bash
    ollama pull qwen2.5:7b-instruct
    ```
    Ensure the Ollama application is running in the background.

3.  **Clone and Install Dependencies**:
    *   Clone the repository:
        ```bash
        git clone https://github.com/dovvnloading/Graphite.git
        cd Graphite
        ```
    *   Create and activate a virtual environment (recommended):
        ```bash
        # For Windows
        python -m venv venv
        .\venv\Scripts\activate

        # For macOS/Linux
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   Install the required Python packages:
        ```bash
        pip install -r requirements.txt
        ```

4.  **Run the Application**:
    The main entry point is now `graphite_app.py`.
    ```bash
    python graphite_app.py
    ```

## Style Guides

### Git Commit Messages

*   Use the present tense ("Add feature" not "Added feature").
*   Use the imperative mood ("Move file to..." not "Moves file to...").
*   Limit the first line to 72 characters or less.
*   Reference issues and pull requests liberally in the body of the commit message.

### Python Styleguide

This project adheres to the [PEP 8 style guide for Python code](https://www.python.org/dev/peps/pep-0008/). Please ensure your contributions follow these guidelines. Using a linter like `flake8` can help you identify and fix style issues.

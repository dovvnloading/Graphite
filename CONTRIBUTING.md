# Contributing to Graphite

First off, thank you for considering contributing to Graphite! It's people like you that make the open-source community such a fantastic place to learn, inspire, and create. All contributions are welcome and greatly appreciated.

This document provides guidelines for contributing to the project. Please read it to ensure a smooth and effective contribution process for everyone involved.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Pull Requests](#pull-requests)
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

If you have an idea for a new feature or an improvement to an existing one, please open an issue on GitHub to discuss it. This allows for a discussion with the community and maintainers before you put in the effort to implement it.

When suggesting an enhancement, please include:

*   **A clear and descriptive title** for the issue.
*   **A detailed description of the proposed enhancement** and the problem it solves.
*   **Any mockups or examples** that might help to illustrate your idea.

### Pull Requests

If you would like to contribute code to fix a bug or implement a new feature, please follow these steps:

1.  **Fork the repository** on GitHub.
2.  **Create a new branch** for your feature or bug fix (`git checkout -b feature/your-feature-name`).
3.  **Make your changes** and commit them with clear, descriptive messages.
4.  **Push your changes** to your forked repository.
5.  **Create a pull request** to the `main` branch of the official Graphite repository.
6.  In your pull request, **provide a clear description of the changes** you have made and reference any related issues.

## Development Setup

To get started with developing on Graphite, follow these steps:

1.  **Prerequisites**:
    *   Python 3.8 or newer.
    *   Ollama installed and running.

2.  **Install an LLM Model**:
    Before running Graphite, you need a model for Ollama. Open your terminal and run:
    ```bash
    ollama pull qwen2.5:7b
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
    ```bash
    python Graphite.py
    ```

## Style Guides

### Git Commit Messages

*   Use the present tense ("Add feature" not "Added feature").
*   Use the imperative mood ("Move file to..." not "Moves file to...").
*   Limit the first line to 72 characters or less.
*   Reference issues and pull requests liberally in the body of the commit message.

### Python Styleguide

This project adheres to the [PEP 8 style guide for Python code](https://www.python.org/dev/peps/pep-0008/). Please ensure your contributions follow these guidelines. Using a linter like `flake8` can help you identify and fix style issues.

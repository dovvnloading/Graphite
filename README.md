
# Graphite: A Visual Node-Based LLM Interface

![License](https://img.shields.io/badge/License-MIT-green.svg) ![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg) ![Framework](https://img.shields.io/badge/Framework-PySide6-blue.svg) ![GitHub stars](https://img.shields.io/github/stars/dovvnloading/Graphite?style=social) ![GitHub forks](https://img.shields.io/github/forks/dovvnloading/Graphite?style=social)

<p align="center">
  <img width="1920" height="1032" alt="Screenshot 2025-10-26 101411" src="https://github.com/user-attachments/assets/9aaad762-a03e-40c7-b2be-4e962c97d6e6" />
</p>

Graphite is an advanced desktop environment for human–AI collaboration. It transforms traditional chat into a visual reasoning workspace where ideas branch, connect, and evolve.

Built with Python and PySide6, Graphite integrates Ollama, OpenAI, Gemini, Anthropic, and Groq models to provide a secure, local-first environment designed for research, creative exploration, and structured reasoning.

---

Big news at bottom of repo

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Gallery](#gallery)
- [Technical Architecture](#technical-architecture)
- [Technology Stack](#technology-stack)
- [Installation and Setup](#installation-and-setup)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Overview

Traditional chatbot interfaces confine conversations to a single chronological timeline. While convenient, this format makes it difficult to revisit ideas, branch alternative reasoning paths, or organize complex lines of thought.

Graphite addresses this limitation by transforming conversation into a visual graph structure on an infinite canvas. Each prompt and response becomes a distinct node, visually connected to represent the evolving structure of the dialogue.

This approach allows users to trace how ideas develop, branch conversations from any point, explore alternative reasoning paths, and build an interconnected knowledge workspace while keeping all data fully private on the local machine.

## Key Features

- **Node-Based Visual Interface:** Move beyond linear text logs. Every interaction appears as a draggable, selectable node on an infinite canvas.
- **Non-Linear Conversation Flow:** Branch conversations from any existing node to explore alternate ideas without disrupting the original thread.
- **Local and Private LLM Integration:** Powered by **Ollama**, AI processing can occur entirely locally. Conversations never leave your machine, ensuring complete privacy.
- **Flexible Model Selection:** Choose from preset models or specify any model compatible with Ollama. The application verifies model availability locally before use.
- **Rich Organizational Tools:**
  - **Frames:** Group nodes into labeled clusters with customizable titles and colors.
  - **Notes:** Add persistent sticky notes to annotate ideas or capture reminders.
  - **Navigation Pins:** Mark important nodes and access them instantly through a navigation overlay.
- **AI-Powered Content Generation:**
  - **Chart Generation:** Ask the AI to summarize data and generate `matplotlib` charts (Bar, Line, Pie, Histogram, and Sankey) directly on the canvas.
  - **Key Takeaways & Explainers:** Right-click any node to generate summaries or simplified explanations that appear as formatted notes.
- **Advanced Canvas Controls:**
  - **Infinite Canvas:** Pan and zoom across a virtually unlimited workspace.
  - **Custom UI Controls:** Adjust grid snapping, panning speed, zoom levels, and other interaction parameters.
- **Comprehensive Session Management:**
  - **Chat Library:** Save, load, rename, and manage multiple conversation canvases.
  - **Secure Local Database:** All sessions—including nodes, frames, notes, and pins—are stored locally in a SQLite database.

## Gallery

<table>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/6615f973-85ea-4be3-a222-b4d458604946" alt="Frames and Notes"></td>
    <td><img src="https://github.com/user-attachments/assets/a6bdf518-a704-4b3d-8a84-ac1ed79a2587" alt="Chart Generation"></td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/267ffc5e-8bc0-4bdc-b236-f84ca591ad33" alt="Navigation Pins"></td>
    <td><img src="https://github.com/user-attachments/assets/ec6b1cdf-3740-41d4-b879-ed9e5df9e383" alt="Conversation Branches"></td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/83e79a1c-879e-4f8f-9a61-10b4f2572127" alt="Chat Library"></td>
    <td><img width="1918" height="1029" alt="Screenshot 2025-10-26 122645" src="https://github.com/user-attachments/assets/f6be870b-3557-4562-84ac-04fe6f1c61f9" /></td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/30290b4f-7fa1-4ecc-8441-af2fc2d50b73" alt="New UI screenshot 1" /></td>
    <td><img src="https://github.com/user-attachments/assets/3ed24b56-f03c-4ebb-b066-7363e1e3a23a" alt="New UI screenshot 2" /></td>
  </tr>
</table>

---

## Technical Architecture

Graphite is built on a modular architecture designed for maintainability and scalability. The application is written in Python 3 and leverages the PySide6 framework to provide a cross-platform graphical interface. The architecture emphasizes a clear separation of concerns between UI components, core application logic, and AI services.

The project is organized into several primary modules:

- **`graphite_app.py`**: The main application entry point. It contains the primary `ChatWindow` class responsible for assembling the UI, initializing backend services, and managing the main event loop.

- **`graphite_ui.py`**: The full user interface layer. This module defines all Qt-based components, including dialogs (`APISettingsDialog`, `ChatLibraryDialog`) and custom-rendered `QGraphicsItem` objects that power the interactive canvas, such as `ChatNode`, `ConnectionItem`, `Frame`, `Note`, and `ChartItem`.

- **`graphite_core.py`**: The application's central state management and persistence layer.
  - `ChatSessionManager` serializes the canvas scene graph (nodes, connections, frames, etc.) into JSON and reconstructs sessions from stored data.
  - `ChatDatabase` manages the local SQLite database used to store and retrieve saved chat sessions.

- **`graphite_agents.py`**: Contains the logic for AI-driven tasks. Agents include the base `ChatAgent` along with specialized agents such as `KeyTakeawayAgent`, `ExplainerAgent`, and `ChartDataAgent`. Each agent performs network operations within a dedicated `QThread` worker to ensure the interface remains responsive.

- **`api_provider.py`**: An abstraction layer responsible for routing requests to the appropriate model provider. It supports both local Ollama instances and OpenAI-compatible remote APIs, allowing the application to remain independent of specific providers.

- **`graphite_config.py`**: Centralized configuration file containing global constants, task identifiers (`TASK_CHAT`, `TASK_CHART`), and default model names.

## Technology Stack

- **Language:** Python 3.8+
- **UI Framework:** PySide6
- **Local LLM Interface:** Ollama
- **Charting Library:** Matplotlib
- **Database:** SQLite
- **Icons:** QtAwesome (FontAwesome)

## Installation and Setup

Follow these steps to run Graphite locally.

### 1. Prerequisites

- **Python:** Python 3.8 or newer
- **Ollama:** Installed and running — https://ollama.com

### 2. Install an LLM Model

Pull the default model used by the application:

```bash
ollama pull qwen2.5:7b-instruct
````

Additional models can be configured inside the application using the model selection dialog.

### 3. Clone and Install Dependencies

Clone the repository:

```bash
git clone https://github.com/dovvnloading/Graphite.git
cd Graphite
```

Create a virtual environment (recommended):

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

If no `requirements.txt` is available:

```bash
pip install PySide6 ollama matplotlib qtawesome
```

### 4. Run the Application

```bash
python graphite_app.py
```

## Usage

* **Sending Messages:** Enter a prompt in the input box and press Enter to create a new node followed by the AI response.
* **Branching Conversations:** Select any existing node to use it as the context for a new branch.
* **Node Interaction**

  * **Move:** Drag nodes to reposition them.
  * **Select:** Click to select or drag to select multiple nodes.
  * **Context Menu:** Right-click nodes for actions such as copying text, generating summaries, creating charts, or deleting nodes.

### Keyboard Shortcuts

* `Ctrl + F` — Create a Frame around selected nodes
* `Ctrl + N` — Create a Note at the cursor position
* `Delete` — Delete selected items
* `Ctrl + S` — Save the current chat session
* `Ctrl + L` — Open the Chat Library

---

Known issue: Graph generation can sometimes be unstable. Larger models generally produce better chart data but require significantly greater system resources. Using coding-oriented models may improve chart accuracy.

---

## Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a branch for your feature or bug fix (`git checkout -b feature/your-feature-name`).
3. Commit your changes with clear and descriptive messages.
4. Push your branch to your forked repository.
5. Open a pull request describing the changes and rationale.

For major changes, please open an issue first to discuss the proposed modification.

## License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.

---

---

---
Updated - 3 / 28 / 2026

# Graphlink — formerly Graphite

**Graphite 2 has arrived under a new name: Graphlink.**

The name *Graphite* has become saturated across multiple unrelated projects, creating confusion and potential legal complications. To ensure the project remains clearly identifiable moving forward, **Graphite is now considered a legacy name**, and development will continue under the new name **Graphlink**.

Graphlink represents the next stage of the original system, expanding the tooling, architecture, and capabilities introduced in Graphite v1.

Repository:
[https://github.com/dovvnloading/Graphlink](https://github.com/dovvnloading/Graphlink)

![Graphlink Preview](https://github.com/user-attachments/assets/8eb57222-e9ca-4f2c-8b51-50e84ae99fa0)



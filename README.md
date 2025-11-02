# Graphite: A Visual Node-Based LLM Interface

![License](https://img.shields.io/badge/License-MIT-green.svg) ![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg) ![Framework](https://img.shields.io/badge/Framework-PySide6-blue.svg) ![GitHub stars](https://img.shields.io/github/stars/dovvnloading/Graphite?style=social) ![GitHub forks](https://img.shields.io/github/forks/dovvnloading/Graphite?style=social)

<p align="center">
  <img width="1920" height="1032" alt="Screenshot 2025-10-26 101411" src="https://github.com/user-attachments/assets/9aaad762-a03e-40c7-b2be-4e962c97d6e6" />

</p>

Graphite is an advanced desktop environment for human–AI collaboration. It transforms ordinary chat into a visual reasoning space, where ideas branch, connect, and evolve. Built with Python and PySide6, it seamlessly integrates Ollama, OpenAI, Gemini, Anthropic, and Groq models—offering a secure, local-first, and deeply intuitive workspace for research, creation, and thought.

---

Exciting news at the bottom! 

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

Traditional chatbot interfaces confine conversations to a single, chronological timeline. This linear format stifles creativity and makes it difficult to revisit, branch, or organize complex lines of thought.

Graphite solves this by treating every conversation as an interactive mind-map on an infinite canvas. Each prompt and response becomes a distinct node, visually connected to form a branching graph of your entire dialogue. This unique approach allows you to trace the evolution of ideas, explore multiple paths from any point in the conversation, and build a rich, interconnected knowledge base—all while ensuring your data remains completely private on your local machine.

## Key Features

- **Node-Based Visual Interface:** Move beyond linear text logs. Every interaction is a movable, selectable node on an infinite canvas.
- **Non-Linear Conversation Flow:** Branch your conversation from any previous node to explore alternative ideas without losing context.
- **Local and Private LLM Integration:** Powered by **Ollama**, all AI processing happens locally. Your conversations are never sent to the cloud, ensuring 100% privacy.
- **Flexible Model Selection:** Choose from a list of popular preset models or specify any custom model compatible with Ollama. The application validates and ensures the model is available locally before use.
- **Rich Organizational Tools:**
    - **Frames:** Group related nodes into logical clusters with customizable titles and colors.
    - **Notes:** Add persistent, editable sticky notes to the canvas for annotations and reminders.
    - **Navigation Pins:** Drop pins on important nodes and access them instantly from a dedicated overlay, creating a table of contents for your canvas.
- **AI-Powered Content Generation:**
    - **Chart Generation:** Ask the AI to summarize data and generate `matplotlib` charts (Bar, Line, Pie, Histogram, and Sankey) directly on the canvas.
    - **Key Takeaways & Explainers:** Right-click any node to generate a concise summary or a simplified explanation, which appear as new, formatted notes.
- **Advanced View and Canvas Controls:**
    - **Infinite Canvas:** Pan and zoom freely across a vast workspace.
    - **Custom UI Controls:** Fine-tune grid snapping, panning speed, and zoom levels.
- **Comprehensive Session Management:**
    - **Chat Library:** Save, load, rename, and manage all your conversation canvases.
    - **Secure Local Database:** All sessions, including nodes, frames, notes, and pins, are stored securely in a local SQLite database.

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
    <td><img width="1918" height="1029" alt="Screenshot 2025-10-26 122645" src="https://github.com/user-attachments/assets/f6be870b-3557-4562-84ac-04fe6f1c61f9" />
</td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/30290b4f-7fa1-4ecc-8441-af2fc2d50b73" alt="New UI screenshot 1" /></td>
    <td><img src="https://github.com/user-attachments/assets/3ed24b56-f03c-4ebb-b066-7363e1e3a23a" alt="New UI screenshot 2" /></td>
  </tr>
</table>



---

## Technical Architecture

Graphite is built on a modern, modular architecture designed for maintainability and scalability. The application is written in Python 3 and leverages the PySide6 framework for its cross-platform graphical user interface. The core principle is a clear separation of concerns, decoupling the UI, core logic, and AI services.

The project is organized into the following key modules:

-   **`graphite_app.py`**: The main application entry point. It contains the primary `ChatWindow` class, which orchestrates the entire application, assembling the UI, initializing backend services, and handling main event loops.

-   **`graphite_ui.py`**: The complete User Interface layer. This module contains all Qt-based components, from the main window's structure to custom dialogs (`APISettingsDialog`, `ChatLibraryDialog`). It also defines all custom-rendered `QGraphicsItem` subclasses that make up the interactive canvas, including `ChatNode`, `ConnectionItem`, `Frame`, `Note`, and `ChartItem`.

-   **`graphite_core.py`**: The application's central nervous system, managing state and data persistence.
    *   The `ChatSessionManager` handles the complex logic of serializing the entire scene graph (nodes, connections, frames, etc.) into a JSON format and deserializing it back into a live session.
    *   The `ChatDatabase` class provides an interface to the local SQLite database, managing the storage and retrieval of saved chat sessions.

-   **`graphite_agents.py`**: This module isolates all logic related to AI-powered tasks. It contains the base `ChatAgent` for conversations and specialized "tool" agents like `KeyTakeawayAgent`, `ExplainerAgent`, and `ChartDataAgent`. Each agent runs its network requests within a dedicated `QThread` worker to ensure the UI remains responsive.

-   **`api_provider.py`**: A crucial abstraction layer that unifies communication with different AI model providers. It acts as a router, directing requests to either a local Ollama instance or any OpenAI-compatible remote API based on the user's configuration. This module makes the core application agnostic to the underlying LLM service.

-   **`graphite_config.py`**: A centralized file for storing global configuration constants. It defines abstract task identifiers (e.g., `TASK_CHAT`, `TASK_CHART`) and default model names, providing a single source of truth for application-wide settings.

  
## Technology Stack

-   **Language:** Python 3.8+
-   **UI Framework:** PySide6
-   **Local LLM Interface:** Ollama
-   **Charting Library:** Matplotlib
-   **Database:** SQLite
-   **Icons:** QtAwesome (FontAwesome)

## Installation and Setup

Follow these steps to get Graphite running on your local machine.

### 1. Prerequisites

-   **Python:** Ensure you have Python 3.8 or newer installed.
-   **Ollama:** You must have **[Ollama](https://ollama.com/)** installed and running.

### 2. Install an LLM Model

Before running Graphite, you need to pull a model for Ollama to use. The default is `qwen2.5:7b-instruct`. Open your terminal and run:

```bash
ollama pull qwen2.5:7b-instruct
```

You can use the in-app Model Selection dialog to choose and validate other models. Ensure the Ollama application is running in the background.

### 3. Clone and Install Dependencies

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/dovvnloading/Graphite.git
    cd Graphite
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```
    *(If a `requirements.txt` is not available, install manually: `pip install PySide6 ollama matplotlib qtawesome`)*

### 4. Run the Application

Once the setup is complete, launch the application by running:

```bash
python graphite_app.py
```

## Usage

-   **Sending Messages:** Type your message in the input box at the bottom and press Enter or click the send button. A new user node will appear, followed by a connected AI response node.
-   **Setting Context:** To branch the conversation, simply click on any previous node. The input box will indicate it's your new context. Your next message will create a new branch from that selected node.
-   **Interacting with Nodes:**
    -   **Move:** Click and drag any node to reposition it.
    -   **Select:** Click a node to select it, or drag a selection box to select multiple nodes.
    -   **Context Menu:** Right-click a node to access options like copying text, generating takeaways, creating charts, or deleting the node.
-   **Keyboard Shortcuts:**
    -   `Ctrl + F`: Create a Frame around selected nodes.
    -   `Ctrl + N`: Create a new Note at the cursor's position.
    -   `Delete`: Delete any selected item (node, frame, note, etc.).
    -   `Ctrl + S`: Save the current chat session.
    -   `Ctrl + L`: Open the Chat Library.

---
(resolved) Known issues: The graph generation is often brittle and not very stable. Note: Larger models do handle chart data far better than smaller models however the system requirements to use the larger models is significantly more demanding. Using coding models does improve the chart accuracy.  
---

## Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix (`git checkout -b feature/your-feature-name`).
3.  Make your changes and commit them with clear, descriptive messages.
4.  Push your changes to your forked repository.
5.  Create a pull request, detailing the changes you made and why.

Please open an issue first to discuss any major changes or new features.

## License

This project is licensed under the **MIT License**. See the `LICENSE` file for more details.

---
---
---

# News: 

I’ve been quiet building. A lot has landed over the past few weeks — deep architectural work, new interaction models, UI refinement, and the groundwork for a stable v1.0.0 release.

The goal hasn’t changed:  
Graphite isn’t “a chat app with a twist.”  
It’s a thinking canvas — a place to work through ideas, branch, compare, refine, and build intelligent workflows visually.

Instead of rushing features and pretending it’s done, I took the opposite route:  
strengthen the core, polish the fundamentals, and make sure the interface *feels* right before opening the doors wider.

Here’s a look at the current state of the workspace:

<table>
<tr>
<td><img width="100%" src="https://github.com/user-attachments/assets/2b4c806d-ff61-4a90-b0de-b669d9abdde3" /></td>
<td><img width="100%" src="https://github.com/user-attachments/assets/fab6ebe6-8bb2-4d43-8844-59691eadc31a" /></td>
</tr>
<tr>
<td><img width="100%" src="https://github.com/user-attachments/assets/71cac9a0-6c23-4d67-ac38-30d8cd8028de" /></td>
<td><img width="100%" src="https://github.com/user-attachments/assets/1265bcf4-c8bd-41ff-95aa-dc8cac415281" /></td>
</tr>
</table>




[Visit the prototype site](https://dovvnloading.github.io/Graphite-Site/)

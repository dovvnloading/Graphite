# Graphite: A Visual Node-Based LLM Interface

![License](https://img.shields.io/badge/License-MIT-green.svg)![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)![Framework](https://img.shields.io/badge/Framework-PyQt5-orange.svg)![GitHub stars](https://img.shields.io/github/stars/dovvnloading/Graphite?style=social)![GitHub forks](https://img.shields.io/github/forks/dovvnloading/Graphite?style=social)

<p align="center">
  <img width="1920" height="1032" alt="Graphite Main Interface" src="https://github.com/user-attachments/assets/1c86682f-b62f-418c-ac1d-db385e432b16">
</p>

Graphite is a sophisticated desktop application that revolutionizes interaction with Large Language Models (LLMs). It transforms standard linear chat conversations into a dynamic, non-linear visual workspace. Built with Python and PyQt5, Graphite leverages local LLMs via Ollama to provide a secure, private, and powerful tool for brainstorming, research, and complex problem-solving.

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
    <td align="center"><b>Organize with Frames and Notes</b></td>
    <td align="center"><b>Generate Charts from Data</b></td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/6615f973-85ea-4be3-a222-b4d458604946" alt="Frames and Notes"></td>
    <td><img src="https://github.com/user-attachments/assets/a6bdf518-a704-4b3d-8a84-ac1ed79a2587" alt="Chart Generation"></td>
  </tr>
  <tr>
    <td align="center"><b>Navigate with Pins</b></td>
    <td align="center"><b>Explore Conversation Branches</b></td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/267ffc5e-8bc0-4bdc-b236-f84ca591ad33" alt="Navigation Pins"></td>
    <td><img src="https://github.com/user-attachments/assets/ec6b1cdf-3740-41d4-b879-ed9e5df9e383" alt="Conversation Branches"></td>
  </tr>
    <tr>
    <td align="center"><b>Chat Library for Session Management</b></td>
    <td align="center"><b>Detailed Node Interaction</b></td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/83e79a1c-879e-4f8f-9a61-10b4f2572127" alt="Chat Library"></td>
    <td><img src="https://github.com/user-attachments/assets/7ee493d8-95db-40b0-bffd-2183fc27e8ea" alt="Node Interaction"></td>
  </tr>
</table>

## Technical Architecture

Graphite is designed with a clear separation of concerns, loosely following a Model-View-Controller (MVC) pattern.

-   **View Layer (UI):** Built with PyQt5. The `ChatWindow` serves as the main application container. The core visual component is the `ChatView` (`QGraphicsView`), which displays the `ChatScene` (`QGraphicsScene`). All interactive elements—`ChatNode`, `Frame`, `Note`, `ConnectionItem`, `ChartItem`, and `NavigationPin`—are custom subclasses of `QGraphicsItem`, allowing for highly tailored rendering and event handling.
-   **Controller Layer (Logic):** The `ChatWindow` class acts as the central controller, managing user input, orchestrating UI updates, and handling communication with the AI backend. Long-running AI operations are delegated to `QThread` workers (`ChatWorkerThread`, `ChartWorkerThread`, etc.) to ensure the UI remains responsive.
-   **Model Layer (Data):** Data persistence is handled by the `ChatSessionManager` and the `ChatDatabase`. The `ChatDatabase` uses SQLite to store all session data. The `ChatSessionManager` is responsible for serializing the entire state of the `ChatScene` into a JSON format for storage and deserializing it to load sessions.

## Technology Stack

-   **Language:** Python 3.8+
-   **UI Framework:** PyQt5
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

Before running Graphite, you need to pull a model for Ollama to use. Open your terminal and run:

```bash
ollama pull qwen2.5:7b
```

You can use other models like qwen3, Gemma, or Phi, but this one is recommended for a good balance of performance and capability. Ensure the Ollama application is running in the background.

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
    *(If a `requirements.txt` is not available, install manually: `pip install PyQt5 ollama matplotlib qtawesome`)*

### 4. Run the Application

Once the setup is complete, launch the application by running:

```bash
python main.py
```
*(Note: The main executable script might have a different name, such as `app.py` or similar.)*

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

---
Known issues: The graph generation is very brittle and not very stable. Note: Larger models do handle chart data far better than smaller models, however the system requirements to use the larger models is significantly larger. 
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

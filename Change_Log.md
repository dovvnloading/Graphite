# Changelog

All notable changes to this project will be documented in this file.

---

### `[Beta v.0.2.2]` - 2024-05-25

This release introduces support for any OpenAI-compatible API endpoint as an alternative to a local Ollama instance. It also includes a significant user experience overhaul for model and provider selection, resolving critical design flaws and improving usability.

#### Added

*   **Added support for OpenAI-Compatible API Endpoints.**
    *   **Feature:** Users can now switch from using a local Ollama instance to any remote API service that is compatible with the OpenAI API specification (e.g., OpenAI, Groq, OpenRouter, or self-hosted solutions like LiteLLM).
    *   **Implementation:** A new `api_provider.py` module was created to act as a router, abstracting all LLM calls and directing them to either Ollama or the configured API endpoint based on the user's selection. All agent classes (`ChatAgent`, `KeyTakeawayAgent`, etc.) were refactored to use this new provider instead of calling `ollama` directly.
*   **Added Per-Task Model Configuration for API Mode.**
    *   **Feature:** When using an API provider, users can configure different models for different tasks (Title Generation, Chat/Analysis, and Chart Data Extraction) to optimize for cost, speed, and capability.
    *   **Implementation:** An `APISettingsDialog` was created, allowing users to enter their API credentials, load a list of available models from the endpoint, and assign a specific model to each task category.

#### Changed

*   **Overhauled the Model and Provider Selection UX.**
    *   **Problem:** The previous UI design for model selection was confusing, with separate and sometimes hidden buttons for different providers. This created a frustrating and non-discoverable user experience.
    *   **Solution:** The toolbar has been redesigned with a clear, two-part system:
        1.  A "Mode" dropdown to explicitly select the provider (`Ollama (Local)` or `API Endpoint`).
        2.  A single, consistently visible "Settings" button. This button is now context-aware and will open the appropriate configuration dialog (`ModelSelectionDialog` for Ollama or `APISettingsDialog` for an API) based on the currently selected mode. This resolves all ambiguity and makes the feature intuitive to use.

#### Fixed

*   **Fixed a critical UI bug where the API settings button was permanently invisible.**
    *   **Problem:** A logic error in the toolbar setup (`self.api_settings_btn.setVisible(False)`) caused the button to configure the API to be hidden, making the entire feature inaccessible.
    *   **Solution:** The erroneous line was removed, and the toolbar was refactored to use the new unified "Settings" button, ensuring the correct dialog is always accessible.
*   **Fixed an architectural violation where UI components were defined outside of `graphite_ui.py`.**
    *   **Problem:** The `APISettingsDialog` was incorrectly defined within the main application file (`graphite_app.py`), breaking the project's modular structure.
    *   **Solution:** The `APISettingsDialog` class has been moved to its proper location within `graphite_ui.py`, restoring the architectural integrity and separation of concerns.

---

### `[Beta v.0.2.1]` - 2024-05-25

This release focuses on critical stability and functionality fixes, primarily addressing issues within the API provider integration and the core UI rendering system.

#### Fixed

*   **Fixed a critical application crash when loading models from the Google Gemini API.**
    *   **Problem:** The application would crash with a `TypeError` when fetching the model list from Gemini. A deep-dive analysis revealed this was due to a fundamental incompatibility between the installed `google-generativeai` library and the current data structure of the API's response. The previous design, which relied on dynamic model discovery, proved to be too brittle for this provider.
    *   **Solution:** The architecture for the Gemini provider has been completely refactored. The brittle dynamic discovery process has been removed and replaced with a static, hard-coded list of known-stable Gemini models. The API Settings UI now intelligently adapts, hiding non-functional controls (e.g., "Load Models") for the Gemini provider and populating the model list instantly and reliably.

*   **Fixed a critical logic error preventing chat messages from being sent to Gemini models.**
    *   **Problem:** After successfully configuring a Gemini model, all chat attempts would fail with an "Error: message cannot be blank."
    *   **Solution:** The root cause was identified in the `api_provider.chat()` function, where a `pop()` operation was incorrectly removing the user's current message from the conversation history before the payload was sent to the API. This line has been removed, ensuring the complete and correct conversation context is now sent with every request.

*   **Fixed a fatal application crash on startup due to incorrect UI class definition order.**
    *   **Problem:** A regression from a previous refactor caused the application to crash on launch with an `ImportError` and underlying `NameError` exceptions. Classes within `graphite_ui.py` (e.g., `ColorPickerDialog`, `ConnectionItem`) were being referenced before they were defined, halting the module loading process.
    *   **Solution:** The class definitions within `graphite_ui.py` have been meticulously reordered to ensure a correct, top-to-bottom dependency resolution. All classes are now defined before they are instantiated or referenced, resolving the startup crash.

*   **Fixed a fatal UI rendering crash related to the `ChartItem` class.**
    *   **Problem:** The application would enter a crash loop during the UI paint event, raising an `AttributeError` for a non-existent `QPainter.RenderHint` (`HighQualityAntialiasing`).
    *   **Solution:** The erroneous line has been removed from the `ChartItem.paint()` method. Rendering quality is preserved by other existing and correct render hints (`SmoothPixmapTransform`), and the crash is fully resolved.

#### Changed

*   **Updated the static model list for the Google Gemini provider.**
    *   The hard-coded list of Gemini models was updated to include the latest stable releases available through the public API, including the `gemini-2.5-pro` and `gemini-2.5-flash` series, ensuring users have access to current and powerful models.

---

### `[Beta v.0.2.0]` - 2024-05-23

#### Architectural Refactor

*   This update introduces a major architectural refactoring to improve the project's structure, maintainability, and scalability. The application has been transitioned from a single, monolithic script into a modular, multi-file structure with a clear separation of concerns. The primary goal of this refactor was to decouple the User Interface, Core Logic, and AI Agent services from one another.

*   The new project structure is as follows:
    *   `graphite_app.py`: Serves as the main application entry point. It contains the primary `ChatWindow` class and is responsible for initializing and launching the application.
    *   `graphite_ui.py`: Consolidates all classes related to the User Interface layer. This includes all Qt widgets, dialogs, custom graphics items for the scene (`ChatNode`, `ConnectionItem`, `Frame`, etc.), and view components (`ChatView`, `ChatScene`).
    *   `graphite_core.py`: Manages the application's core logic and data persistence. It contains the `ChatDatabase` class for all SQLite operations and the `ChatSessionManager` for handling the serialization and deserialization of chat sessions.
    *   `graphite_agents.py`: Isolates all logic related to AI model interaction. This module contains the base `ChatAgent` as well as specialized tool agents (`KeyTakeawayAgent`, `ExplainerAgent`, `ChartDataAgent`) and their corresponding `QThread` workers for asynchronous processing.
    *   `graphite_config.py`: A centralized location for application-wide configuration constants, such as task identifiers and default model names.
    *   `api_provider.py`: A dedicated module to abstract away the differences between various AI providers (Ollama, OpenAI-compatible, Google Gemini), presenting a unified interface to the rest of the application.


# Changelog

All notable changes to this project will be documented in this file.

---
---


## [Beta v.0.1.2] - 2025-05-23

### Architectural Refactor

This update introduces a major architectural refactoring to improve the project's structure, maintainability, and scalability. The application has been transitioned from a single, monolithic `Graphite.py` file into a modular, multi-file structure with a clear separation of concerns.

The primary goal of this refactor was to decouple the User Interface, Core Logic (data persistence and session management), and AI Agent services from one another.

The new project structure is as follows:

*   **`graphite_app.py`**: Serves as the main application entry point. It contains the primary `ChatWindow` class and is responsible for initializing and launching the application.

*   **`graphite_ui.py`**: Consolidates all classes related to the User Interface layer. This includes all Qt widgets, dialogs, custom graphics items for the scene (`ChatNode`, `ConnectionItem`, `Frame`, etc.), and view components (`ChatView`, `ChatScene`). It also contains the application's stylesheet constants.

*   **`graphite_core.py`**: Manages the application's core logic and data persistence. It contains the `ChatDatabase` class for all SQLite operations and the `ChatSessionManager` for handling the serialization and deserialization of chat sessions.

*   **`graphite_agents.py`**: Isolates all logic related to AI model interaction. This module contains the base `ChatAgent` as well as specialized tool agents (`KeyTakeawayAgent`, `ExplainerAgent`, `ChartDataAgent`) and their corresponding `QThread` workers for asynchronous processing.

### Fixed

*   **Fixed a fatal crash on startup.** An `AttributeError` would occur because the `toggle_maximize` method was not correctly migrated to the `CustomTitleBar` class during the refactor. This method has been restored, allowing the application to launch successfully.

*   **Fixed an issue where the application icon would not display in the title bar.**
    *   The primary cause was the omission of the `self.parent.setWindowIcon()` method call within the `CustomTitleBar` class during the refactoring process. This critical line has been reinstated, ensuring the main window's icon is set correctly.
    *   This also resolves the persistent `QPixmap::scaled: Pixmap is a null pixmap` warning that appeared in the console, as the icon resource is now properly loaded and assigned.

---

When to expect updated code: 

```
10/24/2025
```

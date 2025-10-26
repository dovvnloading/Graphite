import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QToolBar,
    QToolButton, QLineEdit, QPushButton, QMessageBox, QSizePolicy, QLabel, QComboBox
)
from PySide6.QtCore import Qt, QSize, QPointF
from PySide6.QtGui import QKeySequence, QGuiApplication, QCursor, QShortcut
import qtawesome as qta
import json
import os

# Imports from new modules
from graphite_ui import (
    StyleSheet, CustomTitleBar, PinOverlay, ChatView, LoadingOverlay,
    ChatLibraryDialog, HelpDialog, Note, ModelSelectionDialog, APISettingsDialog
)
from graphite_core import ChatSessionManager
from graphite_agents import (
    ChatAgent, ExplainerAgent, KeyTakeawayAgent, ChartDataAgent,
    ChatWorkerThread, KeyTakeawayWorkerThread, ExplainerWorkerThread, ChartWorkerThread
)
import graphite_config as config
import api_provider

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(StyleSheet.DARK_THEME)
        self.library_dialog = None

        # Initialize AI agent
        self.agent = ChatAgent("Graphite Assistant", 
            """
            * You are a helpful AI assistant integrated within a program called Graphite.
            * Your purpose is to assist the user and provide high-quality, professional responses.
            * You have been provided with detailed knowledge about the Graphite application's features. When a user asks for help, use this knowledge to guide them clearly and concisely.

            --- Key Features of the Graphite Application ---
            
            **Core Concept: Node-Based Chat**
            * Conversations are visualized as a graph of connected nodes. Each message from the user or you is a new node. This allows for branching discussions and exploring multiple ideas in parallel.

            **Navigation & View Controls**
            * Panning the View: Hold the Middle Mouse Button and drag.
            * Zooming: Use Ctrl + Mouse Wheel, or the "Zoom In" / "Zoom Out" buttons in the toolbar.
            * Reset & Fit View: The toolbar has a "Reset" button to return to default zoom and a "Fit All" button to frame all existing nodes in the view.

            **Chat & Node Interaction**
            * Contextual Replies: When a user clicks on any node, it becomes the active context. Your next response will be created as a child of that selected node.
            * Node Tools (Right-Click Menu): Users can right-click any node to access powerful tools:
                - `Generate Key Takeaway`: Creates a concise summary of the node's text in a new green-headed note.
                - `Generate Explainer`: Simplifies the node's content into easy-to-understand terms in a new purple-headed note.
                - `Generate Chart`: Can visualize data from the node's text as a bar, line, pie chart, and more.
                - `Regenerate Response`: Allows the user to request a new version of one of your previous AI-generated messages.

            **Organization Tools**
            * Frames: Users can group related nodes by selecting them and pressing `Ctrl+F`. This creates a colored frame around them. The frame's title can be edited, and its color can be changed.
            * Notes: Users can create floating sticky notes anywhere on the canvas by pressing `Ctrl+N`.
            * Connections: The lines between nodes can be reshaped by adding 'pins' to them (Ctrl + Left-Click on a line). Pins can then be dragged to change the curve of the line.

            **Session Management**
            * The user can save (`Ctrl+S` or the "Save" button) and load (`Ctrl+L` or the "Library" button) entire chat graphs. The Library allows them to manage all their past conversations.

            --- Your Behavior ---
            * Always be professional, thoughtful, and think your responses through.
            * If you are unsure or unaware of a topic outside of the Graphite application, say so. Do not give blind advice.
            * Your primary role is to be an expert on the Graphite application itself, and a general-purpose assistant for all other topics.
            """)

        # Create main container
        self.container = QWidget()
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # Add title bar
        self.title_bar = CustomTitleBar(self)
        container_layout.addWidget(self.title_bar)

        # Create content widget to hold chat view and pin overlay
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)

        # Create and add pin overlay
        self.pin_overlay = PinOverlay(self)  # Pass self as parent
        content_layout.addWidget(self.pin_overlay)

        # Create and add chat view - BEFORE toolbar setup
        self.chat_view = ChatView(self)
        content_layout.addWidget(self.chat_view)

        # Initialize session manager
        self.session_manager = ChatSessionManager(self)

        # Create and add toolbar - AFTER chat view creation
        self.toolbar = QToolBar()
        container_layout.addWidget(self.toolbar)

        # Add Library and Save buttons to toolbar
        library_btn = QToolButton()
        library_btn.setIcon(qta.icon('fa5s.book', color='#2ecc71'))
        library_btn.setText("Library")
        library_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        library_btn.setObjectName("actionButton")
        library_btn.clicked.connect(self.show_library)
        self.toolbar.addWidget(library_btn)
        
        save_btn = QToolButton()
        save_btn.setIcon(qta.icon('fa5s.save', color='#2ecc71'))
        save_btn.setText("Save")
        save_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        save_btn.setObjectName("actionButton")
        save_btn.clicked.connect(self.save_chat)
        self.toolbar.addWidget(save_btn)
        
        self.toolbar.addSeparator()

        # Setup remaining toolbar items - NOW chat_view exists
        self.setup_toolbar(self.toolbar)

        # Add content widget to main container
        container_layout.addWidget(content_widget)

        # Create input area
        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(8, 8, 8, 8)
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message...")
        self.message_input.returnPressed.connect(self.send_message)
        
        self.send_button = QPushButton()
        self.send_button.setIcon(qta.icon('fa5s.paper-plane', color='white'))
        self.send_button.setToolTip("Send message")
        self.send_button.setFixedSize(40, 40)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                border: none;
                border-radius: 20px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219652;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        container_layout.addWidget(input_widget)

        # Set central widget
        self.setCentralWidget(self.container)

        # Initialize current node
        self.current_node = None

        # Add loading overlay
        self.loading_overlay = LoadingOverlay(self.container)
        self.loading_overlay.hide()

        # Add keyboard shortcuts
        self.library_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        self.library_shortcut.activated.connect(self.show_library)

        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_shortcut.activated.connect(self.save_chat)

        # Center the window on the screen
        screen = QGuiApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2),
                 int((screen.height() - size.height()) / 2))
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Keep loading overlay centered
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.setGeometry(
                (self.width() - 200) // 2,
                (self.height() - 100) // 2,
                200, 
                100
            )
        
    def show_library(self):
        """Show the chat library dialog"""
        # Create new dialog and store reference
        self.library_dialog = ChatLibraryDialog(self.session_manager, self)
        self.library_dialog.setWindowTitle("Chat Library")
        self.library_dialog.resize(500, 600)
        # Use exec_() for modal dialog or show() for non-modal
        self.library_dialog.show()
        
    def keyPressEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_N:
                # Get cursor position in scene coordinates
                view_pos = self.chat_view.mapFromGlobal(QCursor.pos())
                scene_pos = self.chat_view.mapToScene(view_pos)
                self.chat_view.scene().add_note(scene_pos)
        elif event.key() == Qt.Key.Key_Delete:
            # Forward delete key to scene for handling
            self.chat_view.scene().deleteSelectedNotes()
        else:
            super().keyPressEvent(event)
        
    def save_chat(self):
        """Save the current chat session"""
        self.session_manager.save_current_chat()
        QMessageBox.information(self, "Success", "Chat saved successfully!")

    def setup_toolbar(self, toolbar):
        """Setup toolbar with modern QToolButtons"""
        toolbar.setIconSize(QSize(20, 20))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        toolbar.setStyleSheet("""
            QToolBar {
                spacing: 4px;
                padding: 4px;
            }
            
            QToolButton {
                color: white;
                background: transparent;
                border: none;
                border-radius: 4px;
                padding: 6px;
                margin: 2px;
                font-size: 12px;
            }
            
            QToolButton:hover {
                background: rgba(255, 255, 255, 0.1);
            }
            
            QToolButton:pressed {
                background: rgba(0, 0, 0, 0.2);
            }
            
            QToolButton#actionButton {
                color: #3498db;
            }
            
            QToolButton#helpButton {
                color: #9b59b6;
            }
        """)

        # Organize Button
        organize_btn = QToolButton()
        organize_btn.setIcon(qta.icon('fa5s.project-diagram', color='#3498db'))
        organize_btn.setText("Organize")
        organize_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        organize_btn.setObjectName("actionButton")
        organize_btn.clicked.connect(lambda: self.chat_view.scene().organize_nodes())
        toolbar.addWidget(organize_btn)

        toolbar.addSeparator()

        # Zoom Controls
        zoom_in_btn = QToolButton()
        zoom_in_btn.setIcon(qta.icon('fa5s.search-plus', color='#3498db'))
        zoom_in_btn.setText("Zoom In")
        zoom_in_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        zoom_in_btn.setObjectName("actionButton")
        zoom_in_btn.clicked.connect(lambda: self.chat_view.scale(1.1, 1.1))
        toolbar.addWidget(zoom_in_btn)

        zoom_out_btn = QToolButton()
        zoom_out_btn.setIcon(qta.icon('fa5s.search-minus', color='#3498db'))
        zoom_out_btn.setText("Zoom Out")
        zoom_out_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        zoom_out_btn.setObjectName("actionButton")
        zoom_out_btn.clicked.connect(lambda: self.chat_view.scale(0.9, 0.9))
        toolbar.addWidget(zoom_out_btn)

        toolbar.addSeparator()

        # View Controls
        reset_btn = QToolButton()
        reset_btn.setIcon(qta.icon('fa5s.undo', color='#3498db'))
        reset_btn.setText("Reset")
        reset_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        reset_btn.setObjectName("actionButton")
        reset_btn.clicked.connect(self.chat_view.reset_zoom)
        toolbar.addWidget(reset_btn)

        fit_btn = QToolButton()
        fit_btn.setIcon(qta.icon('fa5s.expand', color='#3498db'))
        fit_btn.setText("Fit All")
        fit_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        fit_btn.setObjectName("actionButton")
        fit_btn.clicked.connect(self.chat_view.fit_all)
        toolbar.addWidget(fit_btn)

        # Add expanding spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        # Mode Toggle: Ollama vs API
        mode_label = QLabel("Mode:")
        mode_label.setStyleSheet("color: #ffffff; padding: 0 8px; font-size: 12px;")
        toolbar.addWidget(mode_label)

        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Ollama (Local)", False)
        self.mode_combo.addItem("API Endpoint", True)
        self.mode_combo.setMinimumWidth(150)
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        toolbar.addWidget(self.mode_combo)

        # Unified Settings Button
        settings_btn = QToolButton()
        settings_btn.setIcon(qta.icon('fa5s.cog', color='#3498db'))
        settings_btn.setText("Settings")
        settings_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        settings_btn.setObjectName("actionButton")
        settings_btn.clicked.connect(self.show_settings)
        toolbar.addWidget(settings_btn)

        # Help Button
        help_btn = QToolButton()
        help_btn.setIcon(qta.icon('fa5s.question-circle', color='#9b59b6'))
        help_btn.setText("Help")
        help_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        help_btn.setObjectName("helpButton")
        help_btn.clicked.connect(self.show_help)
        toolbar.addWidget(help_btn)

        # Set initial visibility based on mode
        self.on_mode_changed(self.mode_combo.currentIndex())


    def show_help(self):
        """Show the help dialog"""
        help_dialog = HelpDialog(self)
        # Center the dialog relative to the main window
        center = self.geometry().center()
        help_dialog.move(center.x() - help_dialog.width() // 2,
                        center.y() - help_dialog.height() // 2)
        help_dialog.show()

    def show_settings(self):
        """Show the appropriate settings dialog based on the current mode."""
        use_api = self.mode_combo.currentData()
        if use_api:
            dialog = APISettingsDialog(self)
        else:
            dialog = ModelSelectionDialog(self)
        
        center = self.geometry().center()
        dialog.move(center.x() - dialog.width() // 2,
                    center.y() - dialog.height() // 2)
        dialog.exec()
    
    def on_mode_changed(self, index):
        """Handle mode toggle between Ollama and API"""
        use_api = self.mode_combo.itemData(index)
        api_provider.set_mode(use_api)

    def setCurrentNode(self, node):
        self.current_node = node
        self.message_input.setPlaceholderText(f"Responding to: {node.text[:30]}...")
        
    def send_message(self):
        message = self.message_input.text().strip()
        if not message:
            return
            
        # Disable input during processing
        self.message_input.setEnabled(False)
        self.send_button.setEnabled(False)
        
        # Show loading overlay
        self.loading_overlay.show()
        
        # Get conversation history up to current node
        history = []
        if self.current_node:
            temp_node = self.current_node
            while temp_node:
                if hasattr(temp_node, 'conversation_history'):
                    history = temp_node.conversation_history + history
                temp_node = temp_node.parent_node
        
        # Add user message node
        user_node = self.chat_view.scene().add_chat_node(
            message, 
            is_user=True, 
            parent_node=self.current_node,
            conversation_history=history
        )
        
        # Update conversation history
        user_node.conversation_history = history + [
            {'role': 'user', 'content': message}
        ]
        
        # Create and start worker thread
        self.chat_thread = ChatWorkerThread(
            self.agent,
            message,
            user_node.conversation_history
        )
        
        self.chat_thread.finished.connect(lambda response: self.handle_response(response, user_node))
        self.chat_thread.error.connect(self.handle_error)
        self.chat_thread.start()
        
    def handle_response(self, response, user_node):
        # Add AI response node
        ai_node = self.chat_view.scene().add_chat_node(
            response,
            is_user=False,
            parent_node=user_node,
            conversation_history=self.agent.conversation_history + [
                {'role': 'assistant', 'content': response}
            ]
        )
        
        # Update current node and view
        self.current_node = ai_node
        self.message_input.clear()
        self.chat_view.centerOn(ai_node)
        
        # Re-enable input
        self.message_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.loading_overlay.hide()
        
        # Auto-save after response
        self.session_manager.save_current_chat()
        
    def handle_error(self, error_message):
        QMessageBox.critical(self, "Error", f"An error occurred: {error_message}")
        # Re-enable input
        self.message_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.loading_overlay.hide()
        
    
    def cleanup_takeaway_thread(self):
        """Clean up the takeaway thread properly"""
        if hasattr(self, 'takeaway_thread') and self.takeaway_thread is not None:
            self.takeaway_thread.finished.disconnect()
            self.takeaway_thread.error.disconnect()
            self.takeaway_thread.quit()
            self.takeaway_thread.wait()
            self.takeaway_thread = None
            
    def generate_takeaway(self, node):
        """Generate takeaway for the given node"""
        try:
            # Cleanup any existing thread
            self.cleanup_takeaway_thread()
                
            # Get node position for note placement
            node_pos = node.scenePos()
            
            # Show loading overlay
            self.loading_overlay.show()
            
            # Create and start worker thread
            self.takeaway_thread = KeyTakeawayWorkerThread(
                KeyTakeawayAgent(),
                node.text,
                node_pos
            )
            
            self.takeaway_thread.finished.connect(self.handle_takeaway_response)
            self.takeaway_thread.error.connect(self.handle_takeaway_error)
            self.takeaway_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating takeaway: {str(e)}")
            self.loading_overlay.hide()
            
    def handle_takeaway_response(self, response, node_pos):
        """Handle the key takeaway response"""
        try:
            # Calculate note position - offset from node
            note_pos = QPointF(node_pos.x() + 400, node_pos.y())
            
            # Create new note
            note = self.chat_view.scene().add_note(note_pos)
            note.content = response
            note.color = "#2d2d2d"
            note.header_color = "#2ecc71"
            
            self.loading_overlay.hide()
            self.cleanup_takeaway_thread()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creating takeaway note: {str(e)}")
            self.loading_overlay.hide()
            
    def handle_takeaway_error(self, error_message):
        """Handle any errors during takeaway generation"""
        QMessageBox.critical(self, "Error", f"Error generating takeaway: {error_message}")
        self.loading_overlay.hide()
        self.cleanup_takeaway_thread()
        
    def cleanup_explainer_thread(self):
        """Clean up the explainer thread properly"""
        if hasattr(self, 'explainer_thread') and self.explainer_thread is not None:
            self.explainer_thread.finished.disconnect()
            self.explainer_thread.error.disconnect()
            self.explainer_thread.quit()
            self.explainer_thread.wait()
            self.explainer_thread = None
            
    def generate_explainer(self, node):
        """Generate simple explanation for the given node"""
        try:
            # Cleanup any existing thread
            self.cleanup_explainer_thread()
                
            # Get node position for note placement
            node_pos = node.scenePos()
            
            # Show loading overlay
            self.loading_overlay.show()
            
            # Create and start worker thread
            self.explainer_thread = ExplainerWorkerThread(
                ExplainerAgent(),
                node.text,
                node_pos
            )
            
            self.explainer_thread.finished.connect(self.handle_explainer_response)
            self.explainer_thread.error.connect(self.handle_explainer_error)
            self.explainer_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating explanation: {str(e)}")
            self.loading_overlay.hide()
            
    def handle_explainer_response(self, response, node_pos):
        """Handle the explainer response"""
        try:
            # Calculate note position - offset from node
            note_pos = QPointF(node_pos.x() + 400, node_pos.y() + 100)  # Offset from takeaway note
            
            # Create new note
            note = self.chat_view.scene().add_note(note_pos)
            note.content = response
            note.color = "#2d2d2d"
            note.header_color = "#9b59b6"  # Purple to distinguish from takeaway
            
            self.loading_overlay.hide()
            self.cleanup_explainer_thread()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creating explainer note: {str(e)}")
            self.loading_overlay.hide()
            
    def handle_explainer_error(self, error_message):
        """Handle any errors during explanation generation"""
        QMessageBox.critical(self, "Error", f"Error generating explanation: {error_message}")
        self.loading_overlay.hide()
        self.cleanup_explainer_thread()
        

    def generate_chart(self, node, chart_type):
        """Generate chart for the given node"""
        try:
            # Show loading overlay
            self.loading_overlay.show()
        
            # Create and start worker thread with just text and chart type
            self.chart_thread = ChartWorkerThread(
                node.text,
                chart_type
            )
        
            self.chart_thread.finished.connect(self.handle_chart_data)
            self.chart_thread.error.connect(self.handle_error)
            self.chart_thread.start()
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating chart: {str(e)}")
            self.loading_overlay.hide()
        
    def handle_chart_data(self, data, chart_type):
        """Handle the chart data and create visualization"""
        try:
            chart_data = json.loads(data)
            if "error" in chart_data:
                QMessageBox.warning(self, "Warning", chart_data["error"])
                self.loading_overlay.hide()
                return
            
            # Calculate position
            if self.current_node:
                pos = self.current_node.scenePos()
                chart_pos = QPointF(pos.x() + 450, pos.y())
            else:
                chart_pos = QPointF(0, 0)
            
            # Create chart item
            self.chat_view.scene().add_chart(chart_data, chart_pos)
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creating chart: {str(e)}")
        
        finally:
            self.loading_overlay.hide()

    def stop_all_workers(self):
        """Safely stops all running worker threads before closing."""
        if hasattr(self, 'chat_thread') and self.chat_thread and self.chat_thread.isRunning():
            self.chat_thread.quit()
            self.chat_thread.wait()

        if hasattr(self, 'takeaway_thread') and self.takeaway_thread and self.takeaway_thread.isRunning():
            self.takeaway_thread.stop()
            self.takeaway_thread.quit()
            self.takeaway_thread.wait()

        if hasattr(self, 'explainer_thread') and self.explainer_thread and self.explainer_thread.isRunning():
            self.explainer_thread.stop()
            self.explainer_thread.quit()
            self.explainer_thread.wait()

        if hasattr(self, 'chart_thread') and self.chart_thread and self.chart_thread.isRunning():
            self.chart_thread.quit()
            self.chart_thread.wait()

    def closeEvent(self, event):
        """
        Overrides the default close event to ensure all background threads
        are properly terminated before the application exits.
        """
        self.stop_all_workers()
        super().closeEvent(event)

def main():
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

from datetime import datetime
from pathlib import Path
import json
import sys
import qtawesome as qta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import os

# Import the new worker thread
from graphite_agents import ModelPullWorkerThread
import graphite_config as config
import api_provider

FRAME_COLORS = {
    # Full frame colors
    "Green": {"color": "#2ecc71", "type": "full"},
    "Blue": {"color": "#3498db", "type": "full"},
    "Purple": {"color": "#9b59b6", "type": "full"},
    "Orange": {"color": "#e67e22", "type": "full"},
    "Red": {"color": "#e74c3c", "type": "full"},
    "Yellow": {"color": "#f1c40f", "type": "full"},
    # Header-only colors
    "Green Header": {"color": "#2ecc71", "type": "header"},
    "Blue Header": {"color": "#3498db", "type": "header"},
    "Purple Header": {"color": "#9b59b6", "type": "header"},
    "Orange Header": {"color": "#e67e22", "type": "header"},
    "Red Header": {"color": "#e74c3c", "type": "header"},
    "Yellow Header": {"color": "#f1c40f", "type": "header"}
}

class StyleSheet:
    DARK_THEME = """
        QMainWindow, QWidget {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        
        /* Custom Title Bar Styling */
        #titleBar {
            background-color: #2d2d2d;
            border-bottom: 1px solid #3f3f3f;
            padding: 4px;
            min-height: 32px;
        }
        
        #titleBar QLabel {
            color: #ffffff;
            font-size: 12px;
            font-weight: bold;
            font-family: 'Segoe UI', sans-serif;
        }
        
        #titleBarButtons QPushButton {
            background-color: transparent;
            border: none;
            width: 34px;
            height: 26px;
            padding: 4px;
            border-radius: 4px;
        }
        
        #titleBarButtons QPushButton:hover {
            background-color: #3f3f3f;
        }
        
        #closeButton:hover {
            background-color: #c42b1c !important;
        }
        
        /* Custom Scrollbar Styling */
        QScrollBar:vertical {
            background: #252526;
            width: 10px;
            margin: 0px;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical {
            background-color: #555555;
            min-height: 25px;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #6a6a6a;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
            background: none;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }

        QScrollBar:horizontal {
            background: #252526;
            height: 10px;
            margin: 0px;
            border-radius: 5px;
        }
        QScrollBar::handle:horizontal {
            background-color: #555555;
            min-width: 25px;
            border-radius: 5px;
        }
        QScrollBar::handle:horizontal:hover {
            background-color: #6a6a6a;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
            background: none;
        }
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
            background: none;
        }

        /* Toolbar styling */
        QToolBar {
            background-color: #252526;
            border-bottom: 1px solid #3f3f3f;
            spacing: 8px;
            padding: 8px;
        }
        
        /* Toolbar buttons only */
        QToolBar > QPushButton {
            background-color: #1a8447;  /* Darker shade of green */
            color: #ffffff;
            border: none;
            padding: 6px 16px;
            border-radius: 6px;
            font-size: 12px;
            font-family: 'Segoe UI', sans-serif;
            min-width: 80px;
            min-height: 28px;
        }
        
        QToolBar > QPushButton:hover {
            background-color: #219452;  /* Slightly lighter green on hover */
        }
        
        QToolBar > QPushButton:pressed {
            background-color: #157a3e;  /* Darker green when pressed */
        }
        
        QToolBar > QPushButton#actionButton {
            background-color: #2573b3;  /* Darker shade of blue */
        }
        
        QToolBar > QPushButton#actionButton:hover {
            background-color: #2e82c8;  /* Slightly lighter blue on hover */
        }
        
        QToolBar > QPushButton#helpButton {
            background-color: #9b59b6;  /* Keep the existing purple */
        }
        
        QToolBar > QPushButton#helpButton:hover {
            background-color: #a66bbe;  /* Slightly lighter purple on hover */
        }
        
        /* Regular button styling (for Send button etc) */
        QPushButton {
            background-color: #2ecc71;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 12px;
            font-family: 'Segoe UI', sans-serif;
        }
        
        QPushButton:hover {
            background-color: #27ae60;
        }
        
        /* Rest of the existing styles */
        QComboBox {
            background-color: #2d2d2d;
            border: 1px solid #3f3f3f;
            color: white;
            padding: 5px;
            border-radius: 4px;
            font-family: 'Segoe UI', sans-serif;
            font-size: 12px;
        }

        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left-width: 1px;
            border-left-color: #3f3f3f;
            border-left-style: solid;
            border-top-right-radius: 3px;
            border-bottom-right-radius: 3px;
        }

        QComboBox::down-arrow {
            image: url(C:/Users/Admin/source/repos/graphite_app/assets/down_arrow.png);
            width: 10px;
            height: 10px;
        }

        QComboBox QAbstractItemView {
            background-color: #2d2d2d;
            border: 1px solid #3f3f3f;
            selection-background-color: #2ecc71;
        }
        
        QLineEdit {
            background-color: #252526;
            color: #d4d4d4;
            border: 1px solid #3f3f3f;
            border-radius: 4px;
            padding: 8px;
            selection-background-color: #264f78;
            font-family: 'Segoe UI', sans-serif;
        }
        
        QLineEdit:focus {
            border-color: #2ecc71;
        }
    """


class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("titleBar")
        
        icon_path = r"C:\Users\Admin\source\repos\graphite_app\assets\graphite.ico"
        
        # THIS IS THE CRITICAL LINE THAT WAS MISSING.
        # It sets the icon for the main window itself.
        self.parent.setWindowIcon(QIcon(str(icon_path)))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 0, 0)

        # This QLabel shows the icon inside the title bar widget.
        icon_label = QLabel()
        icon_pixmap = QPixmap(str(icon_path)).scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        icon_label.setPixmap(icon_pixmap)
        layout.addWidget(icon_label)
        
        # Title
        self.title = QLabel("Graphite")
        layout.addWidget(self.title)
        layout.addStretch()
        
        # Window controls
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(0)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        
        self.minimize_btn = QPushButton("🗕")
        self.maximize_btn = QPushButton("🗖")
        self.close_btn = QPushButton("✕")
        
        for btn in (self.minimize_btn, self.maximize_btn, self.close_btn):
            btn.setFixedSize(34, 26)
            btn.setObjectName("titleBarButton")
            btn_layout.addWidget(btn)
        
        self.close_btn.setObjectName("closeButton")
        
        # Connect buttons
        self.minimize_btn.clicked.connect(self.parent.showMinimized)
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        self.close_btn.clicked.connect(self.parent.close)
        
        button_widget = QWidget()
        button_widget.setObjectName("titleBarButtons")
        button_widget.setLayout(btn_layout)
        layout.addWidget(button_widget)
        
        self.pressing = False
        self.start_pos = None
        
    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.maximize_btn.setText("🗖")
        else:
            self.parent.showMaximized()
            self.maximize_btn.setText("🗗")
            
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.pressing = True
            self.start_pos = event.globalPosition().toPoint()
            
    def mouseMoveEvent(self, event):
        if self.pressing:
            if self.parent.isMaximized():
                self.parent.showNormal()
            delta = event.globalPosition().toPoint() - self.start_pos
            self.parent.move(self.parent.x() + delta.x(), self.parent.y() + delta.y())
            self.start_pos = event.globalPosition().toPoint()
            
    def mouseReleaseEvent(self, event):
        self.pressing = False

class ChatLibraryDialog(QDialog):
    def __init__(self, session_manager, parent=None):
        super().__init__(parent)
        self.session_manager = session_manager
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # Enable transparent background
        self.setModal(False)
        self.resize(500, 600)
        
        # Main container layout - ZERO margins to remove the black frame
        self.container = QWidget(self)
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.setSpacing(0)
        dialog_layout.addWidget(self.container)
        
        # Container layout
        main_layout = QVBoxLayout(self.container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Add custom title bar
        self.title_bar = CustomTitleBar(self)
        self.title_bar.title.setText("Chat Library")
        main_layout.addWidget(self.title_bar)
        
        # Content layout
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(10)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search chats...")
        self.search_input.textChanged.connect(self.filter_chats)
        content_layout.addWidget(self.search_input)
        
        # Toolbar with actions
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        
        # New chat button
        new_chat_btn = QPushButton(qta.icon('fa5s.plus', color='white'), "New Chat")
        new_chat_btn.clicked.connect(self.new_chat)
        toolbar.addWidget(new_chat_btn)
        
        # Delete button
        delete_btn = QPushButton(qta.icon('fa5s.trash', color='white'), "Delete")
        delete_btn.clicked.connect(self.delete_selected)
        toolbar.addWidget(delete_btn)
        
        # Rename button
        rename_btn = QPushButton(qta.icon('fa5s.edit', color='white'), "Rename")
        rename_btn.clicked.connect(self.rename_selected)
        toolbar.addWidget(rename_btn)
        
        # Add toolbar to content layout
        toolbar_widget = QWidget()
        toolbar_widget.setLayout(toolbar)
        content_layout.addWidget(toolbar_widget)
        
        # Chat list
        self.chat_list = QListWidget()
        self.chat_list.setAlternatingRowColors(True)
        self.chat_list.itemDoubleClicked.connect(self.load_chat)
        self.chat_list.setStyleSheet("""
            QListWidget {
                background-color: #2d2d2d;
                border: 1px solid #3f3f3f;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3f3f3f;
            }
            QListWidget::item:alternate {
                background-color: #333333;
            }
            QListWidget::item:selected {
                background-color: #2ecc71;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #3f3f3f;
            }
        """)
        content_layout.addWidget(self.chat_list)
        
        # Status bar
        self.status_label = QLabel()
        content_layout.addWidget(self.status_label)
        
        # Add content widget to main layout
        main_layout.addWidget(content_widget)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 0)
        self.container.setGraphicsEffect(shadow)
        
        # Set proper styling for transparent background
        self.setStyleSheet("""
            ChatLibraryDialog {
                background: transparent;
            }
            QWidget {
                background-color: #1e1e1e;
                border-radius: 8px;
            }
            QWidget#toolbar_widget, QLineEdit, QPushButton {
                border-radius: 4px;
            }
        """)
        
        self.refresh_chat_list()
        
        # Center the dialog relative to the parent window
        if parent:
            parent_center = parent.geometry().center()
            self.move(parent_center.x() - self.width() // 2,
                     parent_center.y() - self.height() // 2)

    def closeEvent(self, event):
        # Handle proper cleanup when closing
        event.accept()
        
    def moveEvent(self, event):
        # Ensure the window stays within screen bounds
        screen = QGuiApplication.primaryScreen().geometry()
        window = self.geometry()
        
        if window.left() < screen.left():
            self.move(screen.left(), window.top())
        elif window.right() > screen.right():
            self.move(screen.right() - window.width(), window.top())
            
        if window.top() < screen.top():
            self.move(window.left(), screen.top())
        elif window.bottom() > screen.bottom():
            self.move(window.left(), screen.bottom() - window.height())
            
        super().moveEvent(event)

    def refresh_chat_list(self):
        self.chat_list.clear()
        chats = self.session_manager.db.get_all_chats()
        
        for chat_id, title, created_at, updated_at in chats:
            item = QListWidgetItem()
            
            created_dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
            updated_dt = datetime.strptime(updated_at, '%Y-%m-%d %H:%M:%S')
            
            display_text = f"{title}\n"
            display_text += f"Created: {created_dt.strftime('%Y-%m-%d %H:%M')}\n"
            display_text += f"Updated: {updated_dt.strftime('%Y-%m-%d %H:%M')}"
            
            item.setText(display_text)
            item.setData(Qt.ItemDataRole.UserRole, chat_id)
            
            self.chat_list.addItem(item)
            
        self.update_status()
            
    def update_status(self):
        count = self.chat_list.count()
        self.status_label.setText(f"Total chats: {count}")
        
    def filter_chats(self, text):
        text = text.lower()
        for i in range(self.chat_list.count()):
            item = self.chat_list.item(i)
            if text in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)
                
    def new_chat(self):
        reply = QMessageBox.question(
            self, 'New Chat',
            'Start a new chat? This will clear the current session.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.session_manager.current_chat_id = None
            scene = self.session_manager.window.chat_view.scene()
            scene.clear()
            scene.nodes.clear()
            scene.connections.clear()
            scene.frames.clear()
            # <<< FIX: Reset stale reference and UI placeholder
            self.session_manager.window.current_node = None
            self.session_manager.window.message_input.setPlaceholderText("Type your message...")
            self.close()
                
    def delete_selected(self):
        current_item = self.chat_list.currentItem()
        if current_item:
            chat_id = current_item.data(Qt.ItemDataRole.UserRole)
            reply = QMessageBox.question(
                self, 'Delete Chat',
                'Are you sure you want to delete this chat?\nThis action cannot be undone.',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.session_manager.db.delete_chat(chat_id)
                self.refresh_chat_list()
                
    def rename_selected(self):
        current_item = self.chat_list.currentItem()
        if current_item:
            chat_id = current_item.data(Qt.ItemDataRole.UserRole)
            current_title = current_item.text().split('\n')[0]
            
            new_title, ok = QInputDialog.getText(
                self, 'Rename Chat',
                'Enter new title:',
                text=current_title
            )
            
            if ok and new_title:
                self.session_manager.db.rename_chat(chat_id, new_title)
                self.refresh_chat_list()
                
    def load_chat(self, item):
        chat_id = item.data(Qt.ItemDataRole.UserRole)
        try:
            self.session_manager.load_chat(chat_id)
            self.close()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load chat: {str(e)}"
            )

class CustomScrollBar(QWidget):
    valueChanged = Signal(float)
    
    def __init__(self, orientation=Qt.Orientation.Vertical, parent=None):
        super().__init__(parent)
        self.orientation = orientation
        self.value = 0
        self.handle_position = 0
        self.handle_pressed = False
        self.hover = False
        
        self.min_val = 0
        self.max_val = 99
        self.page_step = 10
        
        if orientation == Qt.Orientation.Vertical:
            self.setFixedWidth(8)
        else:
            self.setFixedHeight(8)
            
        self.setMouseTracking(True)
        
    def setRange(self, min_val, max_val):
        self.min_val = min_val
        self.max_val = max(min_val + 0.1, max_val)
        self.value = max(min_val, min(self.value, max_val))
        self.update()
        
    def setValue(self, value):
        old_value = self.value
        self.value = max(self.min_val, min(self.max_val, value))
        if self.value != old_value:
            self.valueChanged.emit(self.value)
            self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        track_color = QColor("#2A2A2A")
        track_color.setAlpha(100)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(track_color)
        
        if self.orientation == Qt.Orientation.Vertical:
            painter.drawRoundedRect(1, 0, self.width() - 2, self.height(), 4, 4)
        else:
            painter.drawRoundedRect(0, 1, self.width(), self.height() - 2, 4, 4)
            
        range_size = self.max_val - self.min_val
        if range_size <= 0:
            return
            
        visible_ratio = min(1.0, self.page_step / (range_size + self.page_step))
        
        if self.orientation == Qt.Orientation.Vertical:
            handle_size = max(20, int(self.height() * visible_ratio))
            available_space = max(0, self.height() - handle_size)
            if range_size > 0:
                handle_position = int(available_space * 
                    ((self.value - self.min_val) / range_size))
            else:
                handle_position = 0
        else:
            handle_size = max(20, int(self.width() * visible_ratio))
            available_space = max(0, self.width() - handle_size)
            if range_size > 0:
                handle_position = int(available_space * 
                    ((self.value - self.min_val) / range_size))
            else:
                handle_position = 0
            
        if self.hover:
            handle_color = QColor("#6C8EBF")
        else:
            handle_color = QColor("#5075B3")
            
        painter.setBrush(handle_color)
        
        if self.orientation == Qt.Orientation.Vertical:
            painter.drawRoundedRect(1, handle_position, self.width() - 2, handle_size, 3, 3)
        else:
            painter.drawRoundedRect(handle_position, 1, handle_size, self.height() - 2, 3, 3)
            
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.handle_pressed = True
            self.mouse_start_pos = event.position().toPoint()
            self.start_value = self.value
            
    def mouseMoveEvent(self, event):
        self.hover = True
        self.update()
        
        if self.handle_pressed:
            if self.orientation == Qt.Orientation.Vertical:
                delta = event.position().toPoint().y() - self.mouse_start_pos.y()
                available_space = max(1, self.height() - 20)
                delta_ratio = delta / available_space
            else:
                delta = event.position().toPoint().x() - self.mouse_start_pos.x()
                available_space = max(1, self.width() - 20)
                delta_ratio = delta / available_space
                
            range_size = self.max_val - self.min_val
            new_value = self.start_value + delta_ratio * range_size
            self.setValue(new_value)
            
    def mouseReleaseEvent(self, event):
        self.handle_pressed = False
        
    def enterEvent(self, event):
        self.hover = True
        self.update()
        
    def leaveEvent(self, event):
        self.hover = False
        self.update()

class CustomScrollArea(QWidget):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.viewport = QWidget()
        self.viewport.setLayout(QVBoxLayout())
        self.viewport.layout().setContentsMargins(0, 0, 0, 0)
        self.viewport.layout().addWidget(widget)
        
        self.v_scrollbar = CustomScrollBar(Qt.Orientation.Vertical)
        self.h_scrollbar = CustomScrollBar(Qt.Orientation.Horizontal)
        
        layout.addWidget(self.viewport, 0, 0)
        layout.addWidget(self.v_scrollbar, 0, 1)
        layout.addWidget(self.h_scrollbar, 1, 0)
        
        self.v_scrollbar.valueChanged.connect(self.updateVerticalScroll)
        self.h_scrollbar.valueChanged.connect(self.updateHorizontalScroll)
        
    def updateScrollbars(self):
        content_height = self.widget.height()
        viewport_height = self.viewport.height()
        
        if content_height > viewport_height:
            self.v_scrollbar.setRange(0, content_height - viewport_height)
            self.v_scrollbar.page_step = viewport_height
            self.v_scrollbar.show()
        else:
            self.v_scrollbar.hide()
            
        content_width = self.widget.width()
        viewport_width = self.viewport.width()
        
        if content_width > viewport_width:
            self.h_scrollbar.setRange(0, content_width - viewport_width)
            self.h_scrollbar.page_step = viewport_width
            self.h_scrollbar.show()
        else:
            self.h_scrollbar.hide()
            
    def updateVerticalScroll(self, value):
        self.viewport.move(self.viewport.x(), -int(value))
        
    def updateHorizontalScroll(self, value):
        self.viewport.move(-int(value), self.viewport.y())
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateScrollbars()

class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(parent.rect())
        
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 180);
            }
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
                background-color: transparent;
            }
        """)
        
        self.container = QFrame(self)
        self.container.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                border: 1px solid #3f3f3f;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        
        self.spinner_frames = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
        self.current_frame = 0
        
        self.loading_label = QLabel("Processing...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.loading_label)
        
        layout.addStretch()
        layout.addWidget(self.container, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_spinner)
        self.timer.start(100)
        
        self.hide()
    
    def update_spinner(self):
        self.current_frame = (self.current_frame + 1) % len(self.spinner_frames)
        self.loading_label.setText(f"{self.spinner_frames[self.current_frame]} Processing...")
    
    def resizeEvent(self, event):
        self.setGeometry(self.parent().rect())
        container_width = 200
        container_height = 100
        self.container.setFixedSize(container_width, container_height)
        super().resizeEvent(event)
    
    def showEvent(self, event):
        super().showEvent(event)
        self.raise_()
        self.timer.start()
    
    def hideEvent(self, event):
        super().hideEvent(event)
        self.timer.stop()

class ScrollHandle(QGraphicsItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.width = 6
        self.min_height = 20
        self.height = self.min_height
        self.hover = False
        self.dragging = False
        self.start_drag_pos = None
        self.start_drag_value = 0
        self.setAcceptHoverEvents(True)
        
    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)
        
    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
        if self.hover:
            color = QColor("#6C8EBF")
        else:
            color = QColor("#5075B3")
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(color))
    
        painter.drawRoundedRect(0, 0, int(self.width), int(self.height), 3.0, 3.0)
        
    def hoverEnterEvent(self, event):
        self.hover = True
        self.update()
        super().hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        self.hover = False
        self.update()
        super().hoverLeaveEvent(event)

class ScrollBar(QGraphicsItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.width = 8
        self.height = 0
        self.value = 0
        self.handle = ScrollHandle(self)
        self.update_handle_position()
        
    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)
        
    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        track_color = QColor("#2A2A2A")
        track_color.setAlpha(100)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(track_color))
        painter.drawRoundedRect(1, 0, self.width - 2, self.height, 4, 4)
        
    def set_range(self, visible_ratio):
        self.handle.height = max(self.handle.min_height, 
                               self.height * visible_ratio)
        self.update_handle_position()
        
    def set_value(self, value):
        self.value = max(0, min(1, value))
        self.update_handle_position()
        
    def update_handle_position(self):
        max_y = self.height - self.handle.height
        self.handle.setPos(1, self.value * max_y)
        
    def mousePressEvent(self, event):
        handle_pos = self.handle.pos().y()
        click_pos = event.pos().y()
        
        if handle_pos <= click_pos <= handle_pos + self.handle.height:
            self.handle.dragging = True
            self.handle.start_drag_pos = click_pos
            self.handle.start_drag_value = self.value
        else:
            click_ratio = click_pos / self.height
            self.set_value(click_ratio)
            if isinstance(self.parentItem(), ChatNode):
                self.parentItem().update_scroll_position(self.value)
                
    def mouseMoveEvent(self, event):
        if self.handle.dragging:
            delta = event.pos().y() - self.handle.start_drag_pos
            delta_ratio = delta / (self.height - self.handle.height)
            new_value = self.handle.start_drag_value + delta_ratio
            self.set_value(new_value)
            if isinstance(self.parentItem(), ChatNode):
                self.parentItem().update_scroll_position(self.value)
                
    def mouseReleaseEvent(self, event):
        self.handle.dragging = False
        self.handle.start_drag_pos = None

class TextBlock:
    def __init__(self, content, block_type='text', font=None):
        self.content = content
        self.type = block_type
        self.font = font or QFont('Segoe UI', 10)
        self.y = 0
        self.height = 0
        self.layout = None

#
# --- REORDERED GRAPHICS ITEM CLASSES ---
# The following classes have been reordered to solve import-time NameErrors.
#

class ColorPickerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Popup
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setModal(False)
        self.resize(200, 180)
        
        self.container = QWidget(self)
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.setSpacing(0)
        dialog_layout.addWidget(self.container)
        
        main_layout = QVBoxLayout(self.container)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)

        full_label = QLabel("Frame Colors")
        full_label.setStyleSheet("color: #ffffff; font-size: 10px;")
        main_layout.addWidget(full_label)
        
        full_color_layout = QGridLayout()
        full_color_layout.setSpacing(8)
        
        col = 0
        full_colors = [c for c in FRAME_COLORS.items() if c[1]["type"] == "full"]
        for color_name, color_data in full_colors:
            btn = QPushButton()
            btn.setFixedSize(40, 40)
            btn.setToolTip(color_name)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color_data["color"]};
                    border: 2px solid #555555;
                    border-radius: 20px;
                }}
                QPushButton:hover {{
                    border: 2px solid #ffffff;
                }}
            """)
            
            btn.clicked.connect(
                lambda checked, c=color_data: self.color_selected(c["color"], "full")
            )
            full_color_layout.addWidget(btn, 0, col)
            col += 1
            
        main_layout.addLayout(full_color_layout)
        
        header_label = QLabel("Header Colors Only")
        header_label.setStyleSheet("color: #ffffff; font-size: 10px;")
        main_layout.addWidget(header_label)
        
        header_color_layout = QGridLayout()
        header_color_layout.setSpacing(8)
        
        col = 0
        header_colors = [c for c in FRAME_COLORS.items() if c[1]["type"] == "header"]
        for color_name, color_data in header_colors:
            btn = QPushButton()
            btn.setFixedSize(40, 40)
            btn.setToolTip(color_name)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            gradient = QLinearGradient(0, 0, 0, 40)
            gradient.setColorAt(0, QColor(color_data["color"]))
            gradient.setColorAt(1, QColor("#2d2d2d"))
            
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {color_data["color"]},
                        stop:0.3 {color_data["color"]},
                        stop:0.31 #2d2d2d,
                        stop:1 #2d2d2d);
                    border: 2px solid #555555;
                    border-radius: 20px;
                }}
                QPushButton:hover {{
                    border: 2px solid #ffffff;
                }}
            """)
            
            btn.clicked.connect(
                lambda checked, c=color_data: self.color_selected(c["color"], "header")
            )
            header_color_layout.addWidget(btn, 0, col)
            col += 1
            
        main_layout.addLayout(header_color_layout)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 0)
        self.container.setGraphicsEffect(shadow)
        
        self.setStyleSheet("""
            QDialog {
                background: transparent;
            }
            QWidget#container {
                background-color: #1e1e1e;
                border-radius: 8px;
            }
        """)
        
        self.selected_color = None
        self.selected_type = None
        
    def color_selected(self, color, color_type):
        self.selected_color = color
        self.selected_type = color_type
        self.accept()
        
    def get_selected_color(self):
        return self.selected_color, self.selected_type
    
    def focusOutEvent(self, event):
        self.close()
        super().focusOutEvent(event)

class PinEditDialog(QDialog):
    def __init__(self, title="", note="", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.resize(300, 200)
        
        self.container = QWidget(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.container)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setSpacing(10)
        container_layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel("Pin Title")
        container_layout.addWidget(title_label)
        
        self.title_input = QLineEdit(title)
        self.title_input.setPlaceholderText("Enter pin title...")
        container_layout.addWidget(self.title_input)
        
        note_label = QLabel("Note")
        container_layout.addWidget(note_label)
        
        self.note_input = QTextEdit()
        self.note_input.setPlaceholderText("Add a note...")
        self.note_input.setText(note)
        self.note_input.setMaximumHeight(80)
        container_layout.addWidget(self.note_input)
        
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        container_layout.addLayout(button_layout)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 0)
        self.container.setGraphicsEffect(shadow)
        
        self.container.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-radius: 10px;
            }
            QLabel {
                color: white;
                font-size: 12px;
            }
            QLineEdit, QTextEdit {
                background-color: #3f3f3f;
                border: none;
                border-radius: 5px;
                padding: 5px;
                color: white;
            }
            QPushButton {
                background-color: #2ecc71;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                color: white;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)

class Pin(QGraphicsItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        self.hover = False
        self.radius = 5
        self._dragging = False
        
    def boundingRect(self):
        return QRectF(-self.radius, -self.radius, 
                     self.radius * 2, self.radius * 2)
        
    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self.isSelected():
            color = QColor("#2ecc71")
        elif self.hover:
            color = QColor("#3498db")
        else:
            color = QColor("#ffffff")
            
        painter.setPen(QPen(color.darker(120), 1))
        painter.setBrush(QBrush(color))
        painter.drawEllipse(self.boundingRect())
        
    def hoverEnterEvent(self, event):
        self.hover = True
        self.update()
        super().hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        self.hover = False
        self.update()
        super().hoverLeaveEvent(event)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            parent_connection = self.parentItem()
            # This check is modified to use the class name as a string to break
            # the circular dependency between Pin and ConnectionItem at import time.
            if parent_connection and parent_connection.__class__.__name__ == 'ConnectionItem':
                parent_connection.remove_pin(self)
                if self.scene():
                    self.scene().removeItem(self)
                event.accept()
                return
        else:
            self._dragging = True
            super().mousePressEvent(event)
            
    def mouseReleaseEvent(self, event):
        self._dragging = False
        super().mouseReleaseEvent(event)
            
    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and self._dragging:
            grid_size = 5
            new_pos = QPointF(
                round(value.x() / grid_size) * grid_size,
                round(value.y() / grid_size) * grid_size
            )
            if self.parentItem().__class__.__name__ == 'ConnectionItem':
                self.parentItem().prepareGeometryChange()
                self.parentItem().update_path()
            return new_pos
        return super().itemChange(change, value)

class ChatNode(QGraphicsItem):
    MAX_HEIGHT = 300
    PADDING = 20
    
    def __init__(self, text, is_user=True, parent=None):
        super().__init__(parent)
        self.text = text
        self.raw_text = text
        self.is_user = is_user
        self.children = []
        self.parent_node = None
        self.conversation_history = []
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.hovered = False
        
        self.width = 400
        self.height = 100
        self.content_height = 0
        
        self._text_layout = None
        self._cached_text = None
        self._cached_width = None
        
        self.scroll_value = 0
        self.scrollbar = ScrollBar(self)
        self.scrollbar.width = 8
        
        self.blocks = []
        self.process_text(self.raw_text)
        self._create_layouts()

    def boundingRect(self):
        return QRectF(-5, -5, self.width + 10, self.height + 10)

    def _create_layouts(self):
        available_width = self.width - (self.PADDING * 3) - self.scrollbar.width
        y_offset = 0
        
        for block in self.blocks:
            layout = QTextLayout(block.content)
            layout.setFont(block.font)
            
            options = QTextOption()
            options.setWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
            layout.setTextOption(options)
            
            layout.beginLayout()
            line_height = 0
            while True:
                line = layout.createLine()
                if not line.isValid():
                    break
                    
                line.setLineWidth(available_width)
                line.setPosition(QPointF(0, line_height))
                line_height += line.height() + 2
                
            layout.endLayout()
            
            block.layout = layout
            block.y = y_offset
            block.height = line_height
            
            y_offset += line_height + 10
            
        self.content_height = y_offset + (self.PADDING * 2)
        self.height = min(self.MAX_HEIGHT, self.content_height)
        
        self.scrollbar.height = self.height
        self.scrollbar.setPos(self.width - self.scrollbar.width - self.PADDING, 0)
        
        visible_ratio = self.height / self.content_height if self.content_height > self.height else 1
        self.scrollbar.set_range(visible_ratio)
        self.scrollbar.setVisible(self.content_height > self.height)
        
        self.prepareGeometryChange()
        
    def contextMenuEvent(self, event):
        menu = ChatNodeContextMenu(self)
        menu.exec(event.screenPos())

    def clean_text(self, text):
        if not text:
            return ""

        lines = text.splitlines()
        cleaned_lines = []
        in_code_block = False
        list_indent = 0
    
        for line in lines:
            if not line.strip():
                cleaned_lines.append('')
                continue
            
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            
            if in_code_block:
                cleaned_lines.append(line)
                continue
            
            cleaned_line = line
        
            if cleaned_line.lstrip().startswith('#'):
                header_level = len(cleaned_line) - len(cleaned_line.lstrip('#'))
                cleaned_line = f"[h{header_level}]{cleaned_line.lstrip('#').strip()}"
            
            elif cleaned_line.lstrip().startswith(('- ', '* ', '+ ')):
                indent = len(cleaned_line) - len(cleaned_line.lstrip())
                content = cleaned_line.lstrip('- *+').strip()
                cleaned_line = f"[bullet]{' ' * indent}{content}"
            
            elif cleaned_line.lstrip()[0:1].isdigit() and '. ' in cleaned_line.lstrip():
                indent = len(cleaned_line) - len(cleaned_line.lstrip())
                number, content = cleaned_line.lstrip().split('. ', 1)
                cleaned_line = f"[num{number}]{' ' * indent}{content}"
            
            replacements = [
                ('`', ''),
                ('**', ''),
                ('__', ''),
                ('*', ''),
                ('_', ''),
                ('~~', ''),
            ]
        
            for old, new in replacements:
                while old in cleaned_line:
                    start = cleaned_line.find(old)
                    if start != -1:
                        end = cleaned_line.find(old, start + len(old))
                        if end != -1:
                            cleaned_line = (
                                cleaned_line[:start] +
                                cleaned_line[start + len(old):end] +
                                cleaned_line[end + len(old):]
                            )
                        else:
                            break
                        
            import re
            cleaned_line = re.sub(r'<[^>]+>', '', cleaned_line)
        
            cleaned_lines.append(cleaned_line)
    
        return '\n'.join(cleaned_lines)

    def process_text(self, text):
        self.blocks = []
        cleaned_text = self.clean_text(text)
        current_text = ""
    
        for line in cleaned_text.split('\n'):
            if not line.strip():
                if current_text:
                    self.blocks.append(TextBlock(current_text.strip()))
                    current_text = ""
                continue
            
            if line.startswith('[h'):
                if current_text:
                    self.blocks.append(TextBlock(current_text.strip()))
                    current_text = ""
            
                level = int(line[2])
                content = line[4:].strip()
            
                font_size = max(10, 14 - level)
                font = QFont('Segoe UI', font_size, QFont.Weight.Bold)
                self.blocks.append(TextBlock(content, 'header', font))
                continue
            
            elif line.startswith('[bullet]'):
                if current_text:
                    self.blocks.append(TextBlock(current_text.strip()))
                    current_text = ""
                
                content = line[8:].strip()
                font = QFont('Segoe UI', 10)
                self.blocks.append(TextBlock('• ' + content, 'bullet', font))
                continue
            
            elif line.startswith('[num'):
                if current_text:
                    self.blocks.append(TextBlock(current_text.strip()))
                    current_text = ""
                
                num_end = line.find(']')
                number = line[4:num_end]
                content = line[num_end + 1:].strip()
                font = QFont('Segoe UI', 10)
                self.blocks.append(TextBlock(f"{number}. {content}", 'numbered', font))
                continue
            
            else:
                if current_text:
                    current_text += " " + line.strip()
                else:
                    current_text = line.strip()
    
        if current_text:
            self.blocks.append(TextBlock(current_text.strip()))

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
    
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, 30))
        shadow_path = QPainterPath()
        shadow_path.addRoundedRect(3, 3, self.width, self.height, 10, 10)
        painter.drawPath(shadow_path)
    
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width, self.height, 10, 10)
    
        if self.isSelected():
            painter.setPen(QPen(QColor("#00ff00"), 2))
        elif self.hovered:
            painter.setPen(QPen(QColor("#ffffff"), 2))
        else:
            painter.setPen(QPen(QColor("#555555")))
        
        base_color = QColor("#2ecc71") if self.is_user else QColor("#3498db")
        base_color.setAlpha(230)
        painter.setBrush(QBrush(base_color))
        painter.drawPath(path)
    
        content_rect = QRectF(
            self.PADDING, 
            self.PADDING, 
            self.width - (self.PADDING * 3) - self.scrollbar.width, 
            self.height - (self.PADDING * 2)
        )
        painter.setClipRect(content_rect)
    
        scroll_offset = (self.content_height - self.height) * self.scroll_value if self.content_height > self.height else 0
    
        painter.save()
        painter.translate(self.PADDING, self.PADDING - scroll_offset)
    
        for block in self.blocks:
            if block.type == 'header':
                if self.is_user:
                    painter.setPen(QPen(QColor("#ffffff")))
                else:
                    painter.setPen(QPen(QColor("#2ecc71")))
            else:
                painter.setPen(QPen(QColor("#ffffff")))
            
            painter.setFont(block.font)
            block.layout.draw(painter, QPointF(0, block.y))
    
        painter.restore()

    def wheelEvent(self, event):
        if self.content_height <= self.height:
            return
            
        delta = event.angleDelta().y() / 120
        scroll_delta = -delta * 0.1
        
        new_value = max(0, min(1, self.scroll_value + scroll_delta))
        self.scroll_value = new_value
        self.scrollbar.set_value(new_value)
        self.update()
        
        event.accept()

    def update_scroll_position(self, value):
        self.scroll_value = value
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            scene = self.scene()
            if scene and hasattr(scene, 'window'):
                scene.window.setCurrentNode(self)
        super().mousePressEvent(event)

    def hoverEnterEvent(self, event):
        self.hovered = True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.hovered = False
        self.update()
        super().hoverLeaveEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and self.scene():
            self.scene().update_connections()
        return super().itemChange(change, value)

class ConnectionItem(QGraphicsItem):
    def __init__(self, start_node, end_node):
        super().__init__()
        self.start_node = start_node
        self.end_node = end_node
        self.setZValue(-1)
        self.setAcceptHoverEvents(True)
        self.path = QPainterPath()
        self.pins = []
        self.hover = False
        self.click_tolerance = 20.0
        self.hover_path = None
        self.is_selected = False
        
        self.hover_start_timer = QTimer()
        self.hover_start_timer.setSingleShot(True)
        self.hover_start_timer.timeout.connect(self.startArrowAnimation)
        
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.updateArrows)
        
        self.arrows = []
        self.arrow_spacing = 30
        self.arrow_size = 10
        self.animation_speed = 2
        self.is_animating = False
        
        self.setAcceptHoverEvents(True)
        
        start_pos = self.start_node.scenePos()
        end_pos = self.end_node.scenePos()
        
        start_x = start_pos.x() + self.start_node.width
        start_y = start_pos.y() + (self.start_node.height / 2)
        end_x = end_pos.x()
        end_y = end_pos.y() + (self.end_node.height / 2)
        
        self.path = QPainterPath()
        self.path.moveTo(start_x, start_y)
        
        distance = min((end_x - start_x) / 2, 200)
        ctrl1_x = start_x + distance
        ctrl1_y = start_y
        ctrl2_x = end_x - distance
        ctrl2_y = end_y
        
        self.path.cubicTo(ctrl1_x, ctrl1_y, ctrl2_x, ctrl2_y, end_x, end_y)
        self.update()
        
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)

    def boundingRect(self):
        if not self.path:
            return QRectF()
            
        padding = self.click_tolerance * 2
        return self.path.boundingRect().adjusted(-padding, -padding,
                                               padding, padding)

    def create_hover_path(self):
        if not self.path:
            return None
            
        stroke = QPainterPathStroker()
        stroke.setWidth(self.click_tolerance * 2)
        stroke.setCapStyle(Qt.PenCapStyle.RoundCap)
        stroke.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        return stroke.createStroke(self.path)

    def contains_point(self, point):
        if not self.hover_path:
            self.hover_path = self.create_hover_path()
            
        if not self.hover_path:
            return False
            
        point_rect = QRectF(
            point.x() - self.click_tolerance/2,
            point.y() - self.click_tolerance/2,
            self.click_tolerance,
            self.click_tolerance
        )
        
        return self.hover_path.intersects(point_rect)

    def get_node_scene_pos(self, node):
        return node.scenePos()
        
    def add_pin(self, scene_pos):
        pin = Pin(self)
        local_pos = self.mapFromScene(scene_pos)
        pin.setPos(local_pos)
        self.pins.append(pin)
        self.update_path()
        return pin
        
    def remove_pin(self, pin):
        if pin in self.pins:
            self.pins.remove(pin)
            if pin.scene():
                pin.scene().removeItem(pin)
            self.update_path()
                
    def clear(self):
        if self.window and hasattr(self.window, 'pin_overlay'):
            self.window.pin_overlay.clear_pins()
        
        self.pins.clear()
        
        self.nodes.clear()
        self.connections.clear()
        self.frames.clear()
        
        super().clear()

    def update_path(self):
        if not (self.start_node and self.end_node):
            return
            
        old_path = self.path
        
        start_scene_pos = self.start_node.mapToScene(QPointF(self.start_node.width, self.start_node.height/2))
        end_scene_pos = self.end_node.mapToScene(QPointF(0, self.end_node.height/2))
        
        start_pos = self.mapFromScene(start_scene_pos)
        end_pos = self.mapFromScene(end_scene_pos)
        
        new_path = QPainterPath()
        new_path.moveTo(start_pos)
        
        if self.pins:
            sorted_pins = sorted(self.pins, key=lambda p: p.scenePos().x())
            points = [start_pos]
            
            for pin in sorted_pins:
                points.append(pin.pos())
            points.append(end_pos)
            
            for i in range(len(points) - 1):
                current_point = points[i]
                next_point = points[i + 1]
                
                dx = next_point.x() - current_point.x()
                distance = min(abs(dx) / 2, 200)
                
                ctrl1_x = current_point.x() + distance
                ctrl1_y = current_point.y()
                ctrl2_x = next_point.x() - distance
                ctrl2_y = next_point.y()
                
                new_path.cubicTo(
                    ctrl1_x, ctrl1_y,
                    ctrl2_x, ctrl2_y,
                    next_point.x(), next_point.y()
                )
        else:
            dx = end_pos.x() - start_pos.x()
            distance = min(abs(dx) / 2, 200)
            
            ctrl1_x = start_pos.x() + distance
            ctrl1_y = start_pos.y()
            ctrl2_x = end_pos.x() - distance
            ctrl2_y = end_pos.y()
            
            new_path.cubicTo(
                ctrl1_x, ctrl1_y,
                ctrl2_x, ctrl2_y,
                end_pos.x(), end_pos.y()
            )
        
        if new_path != old_path:
            self.path = new_path
            self.hover_path = None
            self.prepareGeometryChange()
            self.update()

    def startArrowAnimation(self):
        if not self.is_animating:
            self.is_animating = True
            self.arrows = []
            path_length = self.path.length()
            
            current_distance = 0
            while current_distance < path_length:
                self.arrows.append({
                    'pos': current_distance / path_length,
                    'opacity': 1.0,
                    'distance': current_distance
                })
                current_distance += self.arrow_spacing
            
            self.animation_timer.start(16)
            self.update()

    def stopArrowAnimation(self):
        self.is_animating = False
        self.animation_timer.stop()
        self.arrows.clear()
        self.update()

    def updateArrows(self):
        if not self.is_animating:
            return
            
        path_length = self.path.length()
        arrows_to_remove = []
        
        for arrow in self.arrows:
            arrow['distance'] += self.animation_speed
            arrow['pos'] = arrow['distance'] / path_length
            
            if arrow['pos'] >= 1:
                arrows_to_remove.append(arrow)
                
        for arrow in arrows_to_remove:
            self.arrows.remove(arrow)
            
        if not self.arrows or self.arrows[0]['distance'] >= self.arrow_spacing:
            self.arrows.insert(0, {
                'pos': 0,
                'opacity': 1.0,
                'distance': 0
            })
        
        self.update()

    def drawArrow(self, painter, pos, opacity):
        if pos < 0 or pos > 1:
            return
            
        point = self.path.pointAtPercent(pos)
        angle = self.path.angleAtPercent(pos)
        
        arrow = QPainterPath()
        arrow.moveTo(-self.arrow_size, -self.arrow_size/2)
        arrow.lineTo(0, 0)
        arrow.lineTo(-self.arrow_size, self.arrow_size/2)
        
        painter.save()
        
        painter.translate(point)
        painter.rotate(-angle)
        
        start_color = QColor("#3498db")
        end_color = QColor("#2ecc71")
        
        r = int(start_color.red() * (1 - pos) + end_color.red() * pos)
        g = int(start_color.green() * (1 - pos) + end_color.green() * pos)
        b = int(start_color.blue() * (1 - pos) + end_color.blue() * pos)
        
        color = QColor(r, g, b)
        color.setAlphaF(opacity)
        
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(color, 1))
        
        painter.drawPath(arrow)
        painter.restore()

    def shape(self):
        if not self.hover_path:
            self.hover_path = self.create_hover_path()
        return self.hover_path if self.hover_path else self.path

    def paint(self, painter, option, widget=None):
        if not (self.start_node and self.end_node):
            return
            
        view = self.scene().views()[0]
        view_rect = view.mapToScene(view.viewport().rect()).boundingRect()
        if not self.boundingRect().intersects(view_rect):
            return
            
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        gradient = QLinearGradient(
            self.path.pointAtPercent(0),
            self.path.pointAtPercent(1)
        )
        
        start_color = QColor("#2ecc71") if self.start_node.is_user else QColor("#3498db")
        end_color = QColor("#2ecc71") if self.end_node.is_user else QColor("#3498db")
        
        if self.hover or self.is_selected:
            start_color = start_color.lighter(120)
            end_color = end_color.lighter(120)
        
        gradient.setColorAt(0, start_color)
        gradient.setColorAt(1, end_color)
        
        width = 3 if (self.hover or self.is_selected) else 2
        pen = QPen(QBrush(gradient), width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawPath(self.path)
        
        if self.is_animating:
            for arrow in self.arrows:
                self.drawArrow(painter, arrow['pos'], arrow['opacity'])

    def hoverEnterEvent(self, event):
        point = event.pos()
        hover_rect = QRectF(
            point.x() - self.click_tolerance,
            point.y() - self.click_tolerance,
            self.click_tolerance * 2,
            self.click_tolerance * 2
        )
        
        if self.path.intersects(hover_rect) or self.contains_point(point):
            if not self.hover:
                self.hover = True
                self.hover_start_timer.start(1000)
                self.update()
        super().hoverEnterEvent(event)

    def hoverMoveEvent(self, event):
        if self.contains_point(event.pos()):
            if not self.hover:
                self.hover = True
                self.hover_start_timer.start(1000)
                self.update()
        else:
            if self.hover:
                self.hover = False
                self.hover_start_timer.stop()
                self.stopArrowAnimation()
                self.update()
        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event):
        self.hover = False
        self.hover_start_timer.stop()
        if self.is_animating:
            self.stopArrowAnimation()
        self.update()
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if self.contains_point(event.pos()):
            if event.button() == Qt.MouseButton.LeftButton and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                scene_pos = self.mapToScene(event.pos())
                self.add_pin(scene_pos)
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()

    def focusOutEvent(self, event):
        self.is_selected = False
        self.update()
        super().focusOutEvent(event)

class ChatNodeContextMenu(QMenu):
    def __init__(self, node, parent=None):
        super().__init__(parent)
        self.node = node
        self.takeaway_thread = None
        
        self.setStyleSheet("""
            QMenu {
                background-color: #2d2d2d;
                border: 1px solid #3f3f3f;
                border-radius: 4px;
                padding: 4px;
            }
            QMenu::item {
                background-color: transparent;
                padding: 8px 20px;
                border-radius: 4px;
                color: white;
            }
            QMenu::item:selected {
                background-color: #3498db;
            }
            QMenu::separator {
                height: 1px;
                background-color: #3f3f3f;
                margin: 4px 0px;
            }
        """)
        
        copy_action = QAction("Copy Text", self)
        copy_action.setIcon(qta.icon('fa5s.copy', color='white'))
        copy_action.triggered.connect(self.copy_text)
        self.addAction(copy_action)
        
        takeaway_action = QAction("Generate Key Takeaway", self)
        takeaway_action.setIcon(qta.icon('fa5s.lightbulb', color='white'))
        takeaway_action.triggered.connect(self.generate_takeaway)
        self.addAction(takeaway_action)
        
        self.addSeparator()
        
        explainer_action = QAction("Generate Explainer Note", self)
        explainer_action.setIcon(qta.icon('fa5s.question', color='white'))
        explainer_action.triggered.connect(self.generate_explainer)
        self.addAction(explainer_action)
        
        chart_menu = QMenu("Generate Chart", self)
        chart_menu.setIcon(qta.icon('fa5s.chart-bar', color='white'))
        chart_menu.setStyleSheet(self.styleSheet())
        
        chart_types = [
            ("Bar Chart", "bar", 'fa5s.chart-bar'),
            ("Line Graph", "line", 'fa5s.chart-line'),
            ("Histogram", "histogram", 'fa5s.chart-area'),
            ("Pie Chart", "pie", 'fa5s.chart-pie'),
            ("Sankey Diagram", "sankey", 'fa5s.project-diagram')
        ]
        
        for title, chart_type, icon in chart_types:
            action = QAction(title, chart_menu)
            action.setIcon(qta.icon(icon, color='white'))
            action.triggered.connect(lambda checked, t=chart_type: self.generate_chart(t))
            chart_menu.addAction(action)
            
        self.addMenu(chart_menu)
        
        self.addSeparator()
        
        delete_action = QAction("Delete Node", self)
        delete_action.setIcon(qta.icon('fa5s.trash', color='white'))
        delete_action.triggered.connect(self.delete_node)
        self.addAction(delete_action)
        
        if not node.is_user:
            self.addSeparator()
            
            regenerate_action = QAction("Regenerate Response", self)
            regenerate_action.setIcon(qta.icon('fa5s.sync', color='white'))
            regenerate_action.triggered.connect(self.regenerate_response)
            self.addAction(regenerate_action)
            
        self.destroyed.connect(self.cleanup_thread)
    
    def copy_text(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.node.text)
    
    def delete_node(self):
        try:
            scene = self.node.scene()
            if not scene:
                return
            
            children = self.node.children[:]
            parent_node = self.node.parent_node
            
            for frame in scene.frames[:]:
                if self.node in frame.nodes:
                    if len(frame.nodes) == 1:
                        scene.removeItem(frame)
                        scene.frames.remove(frame)
                    else:
                        frame.nodes.remove(self.node)
                        frame.updateGeometry()
            
            if parent_node:
                if self.node in parent_node.children:
                    parent_node.children.remove(self.node)
                
                for child in children:
                    child.parent_node = parent_node
                    if child not in parent_node.children:
                        parent_node.children.append(child)
                    
                    new_conn = ConnectionItem(parent_node, child)
                    scene.addItem(new_conn)
                    scene.connections.append(new_conn)
            else:
                for child in children:
                    child.parent_node = None
            
            for conn in scene.connections[:]:
                if self.node in (conn.start_node, conn.end_node):
                    for pin in conn.pins[:]:
                        conn.remove_pin(pin)
                    scene.removeItem(conn)
                    if conn in scene.connections:
                        scene.connections.remove(conn)
            
            self.node.children.clear()
            self.node.parent_node = None
            
            if self.node in scene.nodes:
                scene.nodes.remove(self.node)
            scene.removeItem(self.node)
            
            scene.update_connections()
            
            if scene.window and scene.window.current_node == self.node:
                scene.window.current_node = None
                scene.window.message_input.setPlaceholderText("Type your message...")
            
        except Exception as e:
            QMessageBox.critical(None, "Error", f"An error occurred while deleting the node: {str(e)}")
    
    def regenerate_response(self):
        from graphite_agents import ChatWorkerThread
        if not self.node.parent_node:
            return
            
        user_message = self.node.parent_node.text
        
        history = []
        temp_node = self.node.parent_node
        while temp_node:
            if hasattr(temp_node, 'conversation_history'):
                parent_history = [msg for msg in temp_node.conversation_history 
                                if msg['role'] != 'assistant' or 
                                temp_node.parent_node is not None]
                history = parent_history + history
            temp_node = temp_node.parent_node
        
        main_window = self.node.scene().window
        if not main_window:
            return
            
        main_window.message_input.setEnabled(False)
        main_window.send_button.setEnabled(False)
        main_window.loading_overlay.show()
        
        main_window.chat_thread = ChatWorkerThread(
            main_window.agent,
            user_message,
            history
        )
        
        main_window.chat_thread.finished.connect(
            lambda response: self.handle_regenerated_response(response)
        )
        main_window.chat_thread.error.connect(main_window.handle_error)
        main_window.chat_thread.start()
    
    def handle_regenerated_response(self, new_response):
        try:
            self.node.text = new_response
            self.node.raw_text = new_response
            self.node.process_text(new_response)
            self.node._create_layouts()
            
            if self.node.parent_node:
                parent_history = self.node.parent_node.conversation_history[:] if self.node.parent_node.conversation_history else []
                
                self.node.conversation_history = parent_history + [
                    {'role': 'assistant', 'content': new_response}
                ]
                
                for child in self.node.children:
                    if child.conversation_history:
                        divergence_point = len(parent_history)
                        child.conversation_history = (
                            self.node.conversation_history + 
                            child.conversation_history[divergence_point:]
                        )
            
            main_window = self.node.scene().window
            if main_window:
                main_window.message_input.setEnabled(True)
                main_window.send_button.setEnabled(True)
                main_window.loading_overlay.hide()
                
                main_window.session_manager.save_current_chat()
            
            self.node.update()
            
        except Exception as e:
            QMessageBox.critical(None, "Error", f"An error occurred while regenerating: {str(e)}")
            
            main_window = self.node.scene().window
            if main_window:
                main_window.message_input.setEnabled(True)
                main_window.send_button.setEnabled(True)
                main_window.loading_overlay.hide()
                
    def cleanup_thread(self):
        if self.takeaway_thread is not None:
            self.takeaway_thread.finished.disconnect()
            self.takeaway_thread.error.disconnect()
            self.takeaway_thread.quit()
            self.takeaway_thread.wait()
            self.takeaway_thread = None
            
    def generate_takeaway(self):
            scene = self.node.scene()
            if scene and scene.window:
                scene.window.generate_takeaway(self.node)
                
    def handle_takeaway_response(self, response, node_pos):
        try:
            scene = self.node.scene()
            if not scene:
                return
                
            note_pos = QPointF(node_pos.x() + self.node.width + 50, node_pos.y())
            
            note = scene.add_note(note_pos)
            note.content = response
            note.color = "#2d2d2d"
            note.header_color = "#2ecc71"
            
            if scene.window:
                scene.window.loading_overlay.hide()
                
            self.cleanup_thread()
                
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error creating takeaway note: {str(e)}")
            if scene and scene.window:
                scene.window.loading_overlay.hide()
                
    def handle_takeaway_error(self, error_message):
        QMessageBox.critical(None, "Error", f"Error generating takeaway: {error_message}")
        scene = self.node.scene()
        if scene and scene.window:
            scene.window.loading_overlay.hide()
            
        self.cleanup_thread()
        
    def generate_explainer(self):
        scene = self.node.scene()
        if scene and scene.window:
            scene.window.generate_explainer(self.node)
            
    def generate_chart(self, chart_type):
        scene = self.node.scene()
        if scene and scene.window:
            scene.window.generate_chart(self.node, chart_type)

class Frame(QGraphicsItem):
    PADDING = 30
    HEADER_HEIGHT = 40
    HANDLE_SIZE = 8
    
    def __init__(self, nodes, parent=None):
        super().__init__(parent)
        self.nodes = nodes
        self.note = "Add note..."
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        
        self.lock_icon = qta.icon('fa.lock', color='#ffffff')
        self.unlock_icon = qta.icon('fa.unlock-alt', color='#ffffff')
        self.lock_icon_hover = qta.icon('fa.lock', color='#3498db')
        self.unlock_icon_hover = qta.icon('fa.unlock-alt', color='#2DBB6A')
        
        self.is_locked = True
        self.rect = QRectF()
        self.color = "#2d2d2d"
        self.header_color = None 
        
        self.lock_button_rect = QRectF(0, 0, 24, 24)
        self.lock_button_hovered = False
        self.color_button_rect = QRectF(0, 0, 24, 24)
        self.color_button_hovered = False
        
        self.hovered = False
        self.editing = False
        self.edit_text = ""
        self.cursor_pos = 0
        self.cursor_visible = True
        
        self.handles = ['nw', 'n', 'ne', 'e', 'se', 's', 'sw', 'w']
        self.handle_cursors = {
            'nw': Qt.CursorShape.SizeFDiagCursor,
            'se': Qt.CursorShape.SizeFDiagCursor,
            'ne': Qt.CursorShape.SizeBDiagCursor,
            'sw': Qt.CursorShape.SizeBDiagCursor,
            'n': Qt.CursorShape.SizeVerCursor,
            's': Qt.CursorShape.SizeVerCursor,
            'e': Qt.CursorShape.SizeHorCursor,
            'w': Qt.CursorShape.SizeHorCursor
        }
        self.handle_rects = {}
        self.resize_handle = None
        self.resizing = False
        self.resize_start_rect = None
        self.resize_start_pos = None
        
        self.original_positions = {node: node.scenePos() for node in nodes}
        
        self.outline_animation = QVariantAnimation()
        self.outline_animation.setDuration(2000)
        self.outline_animation.setStartValue(0.0)
        self.outline_animation.setEndValue(1.0)
        self.outline_animation.setLoopCount(-1)
        self.outline_animation.valueChanged.connect(self.update)
        
        self.updateGeometry()
        
        self.cursor_timer = QTimer()
        self.cursor_timer.timeout.connect(self.toggle_cursor)
        self.cursor_timer.setInterval(500)
        
        self._update_nodes_movable()
        
    def calculate_minimum_size(self):
        if not self.nodes:
            return QRectF()
            
        min_x = float('inf')
        min_y = float('inf')
        max_x = float('-inf')
        max_y = float('-inf')
        
        for node in self.nodes:
            node_rect = node.boundingRect()
            node_pos = node.pos()
            scene_pos = node.scenePos() if not node.parentItem() else self.mapToScene(node_pos)
            
            min_x = min(min_x, scene_pos.x())
            min_y = min(min_y, scene_pos.y())
            max_x = max(max_x, scene_pos.x() + node_rect.width())
            max_y = max(max_y, scene_pos.y() + node_rect.height())
        
        return QRectF(
            min_x - self.PADDING,
            min_y - self.PADDING - self.HEADER_HEIGHT,
            (max_x - min_x) + (self.PADDING * 2),
            (max_y - min_y) + (self.PADDING * 2) + self.HEADER_HEIGHT
        )

    def get_handle_rects(self):
        rects = {}
        rect = self.rect
    
        visual_handle_size = self.HANDLE_SIZE
        hit_handle_size = 16
    
        half_visual = visual_handle_size / 2
        half_hit = hit_handle_size / 2
    
        rects['nw'] = {
            'visual': QRectF(rect.left() - half_visual, rect.top() - half_visual, 
                            visual_handle_size, visual_handle_size),
            'hit': QRectF(rect.left() - half_hit, rect.top() - half_hit,
                         hit_handle_size, hit_handle_size)
        }
    
        rects['ne'] = {
            'visual': QRectF(rect.right() - half_visual, rect.top() - half_visual,
                            visual_handle_size, visual_handle_size),
            'hit': QRectF(rect.right() - half_hit, rect.top() - half_hit,
                         hit_handle_size, hit_handle_size)
        }
    
        rects['se'] = {
            'visual': QRectF(rect.right() - half_visual, rect.bottom() - half_visual,
                            visual_handle_size, visual_handle_size),
            'hit': QRectF(rect.right() - half_hit, rect.bottom() - half_hit,
                         hit_handle_size, hit_handle_size)
        }
    
        rects['sw'] = {
            'visual': QRectF(rect.left() - half_visual, rect.bottom() - half_visual,
                            visual_handle_size, visual_handle_size),
            'hit': QRectF(rect.left() - half_hit, rect.bottom() - half_hit,
                         hit_handle_size, hit_handle_size)
        }
    
        rects['n'] = {
            'visual': QRectF(rect.center().x() - half_visual, rect.top() - half_visual,
                            visual_handle_size, visual_handle_size),
            'hit': QRectF(rect.center().x() - half_hit, rect.top() - half_hit,
                         hit_handle_size, hit_handle_size)
        }
    
        rects['s'] = {
            'visual': QRectF(rect.center().x() - half_visual, rect.bottom() - half_visual,
                            visual_handle_size, visual_handle_size),
            'hit': QRectF(rect.center().x() - half_hit, rect.bottom() - half_hit,
                         hit_handle_size, hit_handle_size)
        }
    
        rects['e'] = {
            'visual': QRectF(rect.right() - half_visual, rect.center().y() - half_visual,
                            visual_handle_size, visual_handle_size),
            'hit': QRectF(rect.right() - half_hit, rect.center().y() - half_hit,
                         hit_handle_size, hit_handle_size)
        }
    
        rects['w'] = {
            'visual': QRectF(rect.left() - half_visual, rect.center().y() - half_visual,
                            visual_handle_size, visual_handle_size),
            'hit': QRectF(rect.left() - half_hit, rect.center().y() - half_hit,
                         hit_handle_size, hit_handle_size)
        }
    
        return rects

    def handle_at(self, pos):
        for handle, rects in self.get_handle_rects().items():
            if rects['hit'].contains(pos):
                return handle
        return None

    def updateGeometry(self):
        if not self.nodes:
            return
            
        old_rect = self.rect
        
        min_x = float('inf')
        min_y = float('inf')
        max_x = float('-inf')
        max_y = float('-inf')
        
        for node in self.nodes:
            node_rect = node.boundingRect()
            node_pos = node.pos()
            
            min_x = min(min_x, node_pos.x())
            min_y = min(min_y, node_pos.y())
            max_x = max(max_x, node_pos.x() + node_rect.width())
            max_y = max(max_y, node_pos.y() + node_rect.height())
        
        new_rect = QRectF(
            min_x - self.PADDING,
            min_y - self.PADDING - self.HEADER_HEIGHT,
            (max_x - min_x) + (self.PADDING * 2),
            (max_y - min_y) + (self.PADDING * 2) + self.HEADER_HEIGHT
        )
        
        if old_rect.isValid():
            self.rect = QRectF(
                min(old_rect.left(), new_rect.left()),
                min(old_rect.top(), new_rect.top()),
                max(old_rect.width(), new_rect.width()),
                max(old_rect.height(), new_rect.height())
            )
        else:
            self.rect = new_rect
            
        self.prepareGeometryChange()

    def _update_nodes_movable(self):
        for node in self.nodes:
            scene_pos = node.scenePos()
            node.setParentItem(self)
            
            if not self.is_locked:
                node.setPos(self.mapFromScene(scene_pos))
            
            node.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, not self.is_locked)
            node.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, not self.is_locked)

    def boundingRect(self):
        return self.rect

    def toggle_lock(self):
        self.is_locked = not self.is_locked
    
        if not self.is_locked:
            self.outline_animation.start()
        else:
            self.outline_animation.stop()
    
        for node in self.nodes:
            node.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, not self.is_locked)
            node.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, not self.is_locked)

    def toggle_cursor(self):
        self.cursor_visible = not self.cursor_visible
        self.update()

    def mouseDoubleClickEvent(self, event):
        if self.rect.top() <= event.pos().y() <= self.rect.top() + self.HEADER_HEIGHT:
            self.editing = True
            self.edit_text = self.note
            self.cursor_pos = len(self.edit_text)
            self.cursor_timer.start()
            self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
            self.setFocus()
            self.update()
        else:
            super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        if self.isSelected():
            handle = self.handle_at(event.pos())
            if handle:
                self.resizing = True
                self.resize_handle = handle
                self.resize_start_rect = self.rect
                self.resize_start_pos = event.pos()
                event.accept()
                return
                
        if self.color_button_rect.contains(event.pos()):
            self.show_color_picker()
            event.accept()
        elif self.lock_button_rect.contains(event.pos()):
            self.toggle_lock()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.resizing and self.resize_handle:
            delta = event.pos() - self.resize_start_pos
            new_rect = QRectF(self.resize_start_rect)
        
            min_x = float('inf')
            max_x = float('-inf')
            min_y = float('inf')
            max_y = float('-inf')
        
            for node in self.nodes:
                node_rect = node.boundingRect()
                node_pos = node.pos()
                min_x = min(min_x, node_pos.x())
                max_x = max(max_x, node_pos.x() + node_rect.width())
                min_y = min(min_y, node_pos.y())
                max_y = max(max_y, node_pos.y() + node_rect.height())
    
            min_width = (max_x - min_x) + (self.PADDING * 2)
            min_height = (max_y - min_y) + (self.PADDING * 2) + self.HEADER_HEIGHT
    
            grid_size = 10
            delta.setX(round(delta.x() / grid_size) * grid_size)
            delta.setY(round(delta.y() / grid_size) * grid_size)
    
            if 'n' in self.resize_handle:
                max_top = self.resize_start_rect.bottom() - min_height
                new_top = min(self.resize_start_rect.top() + delta.y(), max_top)
                new_rect.setTop(max(new_top, min_y - self.PADDING - self.HEADER_HEIGHT))
        
            if 's' in self.resize_handle:
                min_bottom = self.resize_start_rect.top() + min_height
                new_bottom = max(self.resize_start_rect.bottom() + delta.y(), min_bottom)
                new_rect.setBottom(max(new_bottom, max_y + self.PADDING))
        
            if 'w' in self.resize_handle:
                max_left = self.resize_start_rect.right() - min_width
                new_left = min(self.resize_start_rect.left() + delta.x(), max_left)
                new_rect.setLeft(max(new_left, min_x - self.PADDING))
        
            if 'e' in self.resize_handle:
                min_right = self.resize_start_rect.left() + min_width
                new_right = max(self.resize_start_rect.right() + delta.x(), min_right)
                new_rect.setRight(max(new_right, max_x + self.PADDING))
    
            if new_rect != self.rect:
                self.prepareGeometryChange()
                self.rect = new_rect
            
                if self.scene():
                    scene_nodes = set()
                    for node in self.nodes:
                        if node not in scene_nodes:
                            scene_nodes.add(node)
                            for conn in self.scene().connections:
                                if conn.start_node == node or conn.end_node == node:
                                    conn.update_path()
                                    for pin in conn.pins:
                                        scene_pos = pin.mapToScene(QPointF(0, 0))
                                        pin.setPos(conn.mapFromScene(scene_pos))
    
            event.accept()
    
        elif self.is_locked:
            old_positions = {}
            pin_positions = {}
            for node in self.nodes:
                old_positions[node] = node.scenePos()
                for conn in self.scene().connections:
                    if conn.start_node == node or conn.end_node == node:
                        for pin in conn.pins:
                            pin_positions[pin] = pin.mapToScene(QPointF(0, 0))
    
            super().mouseMoveEvent(event)
        
            delta = event.pos() - self.resize_start_pos if self.resize_start_pos else QPointF(0, 0)
        
            if self.scene():
                for node in self.nodes:
                    new_scene_pos = node.mapToScene(QPointF(0, 0))
                    if new_scene_pos != old_positions[node]:
                        for conn in self.scene().connections:
                            if conn.start_node == node or conn.end_node == node:
                                conn.update_path()
                            
                                for pin in conn.pins:
                                    if pin in pin_positions:
                                        old_scene_pos = pin_positions[pin]
                                        new_scene_pos = old_scene_pos + delta
                                        pin.setPos(conn.mapFromScene(new_scene_pos))

        else:
            super().mouseMoveEvent(event)
            if self.scene():
                moving_node = None
                for node in self.nodes:
                    if node.isUnderMouse():
                        moving_node = node
                        break
            
                if moving_node:
                    for conn in self.scene().connections:
                        if conn.start_node == moving_node or conn.end_node == moving_node:
                            conn.update_path()
            
    def update_all_connections(self):
        if not self.scene():
            return
            
        for node in self.nodes:
            for conn in self.scene().connections:
                if conn.start_node == node or conn.end_node == node:
                    conn.update_path()
                    for pin in conn.pins:
                        scene_pos = pin.mapToScene(QPointF(0, 0))
                        pin.setPos(conn.mapFromScene(scene_pos))

    def mouseReleaseEvent(self, event):
        if self.resizing:
            self.resizing = False
            self.resize_handle = None
            self.resize_start_rect = None
            self.resize_start_pos = None
            event.accept()
        else:
            super().mouseReleaseEvent(event)
            if self.is_locked:
                self.updateGeometry()

    def hoverMoveEvent(self, event):
        if self.isSelected():
            handle = self.handle_at(event.pos())
            if handle:
                self.setCursor(self.handle_cursors[handle])
                return
                
        old_lock_hover = self.lock_button_hovered
        old_color_hover = self.color_button_hovered
        
        self.lock_button_hovered = self.lock_button_rect.contains(event.pos())
        self.color_button_hovered = self.color_button_rect.contains(event.pos())
        
        if (old_lock_hover != self.lock_button_hovered or 
            old_color_hover != self.color_button_hovered):
            self.update()
            
        self.unsetCursor()
        super().hoverMoveEvent(event)

    def hoverEnterEvent(self, event):
        self.hovered = True
        self.update()
        super().hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        self.hovered = False
        self.lock_button_hovered = False
        self.color_button_hovered = False
        self.unsetCursor()
        self.update()
        super().hoverLeaveEvent(event)

    def show_color_picker(self):
        dialog = ColorPickerDialog(self.scene().views()[0])
        
        frame_pos = self.mapToScene(self.color_button_rect.topRight())
        view_pos = self.scene().views()[0].mapFromScene(frame_pos)
        global_pos = self.scene().views()[0].mapToGlobal(view_pos)
        
        dialog.move(global_pos.x() + 10, global_pos.y())
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            color, color_type = dialog.get_selected_color()
            if color_type == "full":
                self.color = color
                self.header_color = None
            else:
                self.header_color = color
            self.update()

    def finishEditing(self):
        if self.editing:
            self.note = self.edit_text
            self.editing = False
            self.cursor_timer.stop()
            self.clearFocus()
            self.update()
            
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.finishEditing()

    def keyPressEvent(self, event):
        if not self.editing:
            return super().keyPressEvent(event)
            
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.finishEditing()
        elif event.key() == Qt.Key.Key_Escape:
            self.editing = False
            self.cursor_timer.stop()
            self.update()
        elif event.key() == Qt.Key.Key_Backspace:
            if self.cursor_pos > 0:
                self.edit_text = self.edit_text[:self.cursor_pos-1] + self.edit_text[self.cursor_pos:]
                self.cursor_pos -= 1
                self.update()
        elif event.key() == Qt.Key.Key_Delete:
            if self.cursor_pos < len(self.edit_text):
                self.edit_text = self.edit_text[:self.cursor_pos] + self.edit_text[self.cursor_pos+1:]
                self.update()
        elif event.key() == Qt.Key.Key_Left:
            self.cursor_pos = max(0, self.cursor_pos - 1)
            self.update()
        elif event.key() == Qt.Key.Key_Right:
            self.cursor_pos = min(len(self.edit_text), self.cursor_pos + 1)
            self.update()
        elif event.key() == Qt.Key.Key_Home:
            self.cursor_pos = 0
            self.update()
        elif event.key() == Qt.Key.Key_End:
            self.cursor_pos = len(self.edit_text)
            self.update()
        elif len(event.text()) and event.text().isprintable():
            self.edit_text = (
                self.edit_text[:self.cursor_pos] + 
                event.text() + 
                self.edit_text[self.cursor_pos:]
            )
            self.cursor_pos += 1
            self.update()

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
        gradient = QLinearGradient(
            self.rect.topLeft(),
            self.rect.bottomLeft()
        )
        base_color = QColor(self.color)
        gradient.setColorAt(0, base_color)
        gradient.setColorAt(1, base_color.darker(120))
    
        if self.isSelected():
            outline_color = QColor("#2ecc71")
        elif self.hovered:
            outline_color = QColor("#3498db")
        else:
            outline_color = QColor("#555555")
        
        path = QPainterPath()
        path.addRoundedRect(self.rect, 10, 10)
    
        painter.setPen(QPen(outline_color, 2))
        painter.setBrush(QBrush(gradient))
        painter.drawPath(path)
    
        if not self.is_locked:
            outline_path = QPainterPath()
            outline_path.addRoundedRect(self.rect.adjusted(-2, -2, 2, 2), 10, 10)
            
            gradient = QConicalGradient(self.rect.center(), 
                                      360 * self.outline_animation.currentValue())
            
            blue = QColor("#3498db")
            green = QColor("#2ecc71")
            
            gradient.setColorAt(0.0, blue)
            gradient.setColorAt(0.5, green)
            gradient.setColorAt(1.0, blue)
            
            painter.setPen(QPen(QBrush(gradient), 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(outline_path)
    
        header_rect = QRectF(
            self.rect.left(),
            self.rect.top(),
            self.rect.width(),
            self.HEADER_HEIGHT
        )
    
        header_gradient = QLinearGradient(
            header_rect.topLeft(),
            header_rect.bottomLeft()
        )
    
        if self.header_color:
            header_color = QColor(self.header_color)
            header_gradient.setColorAt(0, header_color)
            header_gradient.setColorAt(1, header_color.darker(110))
        else:
            header_color = QColor(self.color).lighter(120)
            header_gradient.setColorAt(0, header_color)
            header_gradient.setColorAt(1, header_color.darker(110))
    
        header_path = QPainterPath()
        header_path.addRoundedRect(header_rect, 10, 10)
        painter.setBrush(QBrush(header_gradient))
        painter.drawPath(header_path)
    
        self.lock_button_rect = QRectF(
            self.rect.right() - 68,
            self.rect.top() + 8,
            24,
            24
        )
    
        painter.setPen(QPen(QColor("#555555")))
        if self.lock_button_hovered:
            painter.setPen(QPen(QColor("#2DBB6A")))
    
        painter.setBrush(QBrush(QColor("#3f3f3f")))
        painter.drawEllipse(self.lock_button_rect)
    
        if self.lock_button_hovered:
            icon = self.lock_icon_hover if self.is_locked else self.unlock_icon_hover
        else:
            icon = self.lock_icon if self.is_locked else self.unlock_icon
            
        icon_size = 18
        icon_pixmap = icon.pixmap(icon_size, icon_size)
        
        icon_x = self.lock_button_rect.center().x() - icon_size / 2
        icon_y = self.lock_button_rect.center().y() - icon_size / 2
        
        painter.drawPixmap(int(icon_x), int(icon_y), icon_pixmap)
    
        self.color_button_rect = QRectF(
            self.rect.right() - 34,
            self.rect.top() + 8,
            24,
            24
        )
    
        painter.setPen(QPen(QColor("#555555")))
        if self.color_button_hovered:
            painter.setPen(QPen(QColor("#ffffff")))
    
        painter.setBrush(QBrush(QColor(self.header_color if self.header_color else self.color)))
        painter.drawEllipse(self.color_button_rect)
    
        icon_color = QColor("#ffffff")
        icon_color.setAlpha(180)
        painter.setPen(QPen(icon_color))
        circle_size = 4
        spacing = 3
        total_width = (circle_size * 3) + (spacing * 2)
        x_start = self.color_button_rect.center().x() - (total_width / 2)
        y_pos = self.color_button_rect.center().y() - (circle_size / 2)
        
        for i in range(3):
            x_pos = x_start + (i * (circle_size + spacing))
            painter.drawEllipse(QRectF(x_pos, y_pos, circle_size, circle_size))
    
        painter.setPen(QPen(QColor("#ffffff")))
        font = QFont("Segoe UI", 10)
        painter.setFont(font)
        text_rect = header_rect.adjusted(10, 0, -78, 0)
    
        if self.editing:
            text = self.edit_text
            cursor_x = painter.fontMetrics().horizontalAdvance(text[:self.cursor_pos])
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter, text)
        
            if self.cursor_visible:
                cursor_height = painter.fontMetrics().height()
                cursor_y = text_rect.center().y() - cursor_height/2
                painter.drawLine(
                    int(text_rect.left() + cursor_x),
                    int(cursor_y),
                    int(text_rect.left() + cursor_x),
                    int(cursor_y + cursor_height)
                )
        else:
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter, self.note)
            
        if self.isSelected():
            painter.setPen(QPen(QColor("#2ecc71"), 1))
            painter.setBrush(QBrush(QColor("#2ecc71")))
            
            for handle_rects in self.get_handle_rects().values():
                painter.drawRect(handle_rects['visual'])
                            
class Note(QGraphicsItem):
    PADDING = 20
    HEADER_HEIGHT = 40
    DEFAULT_WIDTH = 200
    DEFAULT_HEIGHT = 150
    
    def __init__(self, pos, parent=None):
        super().__init__(parent)
        self.setPos(pos)
        self.content = "Add note..."
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        
        self.width = self.DEFAULT_WIDTH
        self.height = self.DEFAULT_HEIGHT
        self.color = "#2d2d2d"
        self.header_color = None
        
        self.editing = False
        self.edit_text = ""
        self.cursor_pos = 0
        self.cursor_visible = True
        
        self.selection_start = 0
        self.selection_end = 0
        self.selecting = False
        self.mouse_drag_start_pos = None
        
        self.hovered = False
        self.resize_handle_hovered = False
        self.resizing = False
        self.color_button_hovered = False
        
        self.cursor_timer = QTimer()
        self.cursor_timer.timeout.connect(self.toggle_cursor)
        self.cursor_timer.setInterval(500)
        
        self.color_button_rect = QRectF(0, 0, 24, 24)

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)
        
    def toggle_cursor(self):
        self.cursor_visible = not self.cursor_visible
        self.update()

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        shadow_path = QPainterPath()
        shadow_path.addRoundedRect(3, 3, self.width, self.height, 10, 10)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, 30))
        painter.drawPath(shadow_path)
        
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width, self.height, 10, 10)
        
        if self.isSelected():
            painter.setPen(QPen(QColor("#2ecc71"), 2))
        elif self.hovered:
            painter.setPen(QPen(QColor("#ffffff"), 2))
        else:
            painter.setPen(QPen(QColor("#555555")))
            
        base_color = QColor(self.color)
        painter.setBrush(QBrush(base_color))
        painter.drawPath(path)
        
        header_rect = QRectF(0, 0, self.width, self.HEADER_HEIGHT)
        header_path = QPainterPath()
        header_path.addRoundedRect(header_rect, 10, 10)
        
        if self.header_color:
            header_gradient = QLinearGradient(header_rect.topLeft(), header_rect.bottomLeft())
            header_color = QColor(self.header_color)
            header_gradient.setColorAt(0, header_color)
            header_gradient.setColorAt(1, header_color.darker(110))
        else:
            header_gradient = QLinearGradient(header_rect.topLeft(), header_rect.bottomLeft())
            header_color = QColor(self.color).lighter(120)
            header_gradient.setColorAt(0, header_color)
            header_gradient.setColorAt(1, header_color.darker(110))
            
        painter.setBrush(QBrush(header_gradient))
        painter.drawPath(header_path)
        
        self.color_button_rect = QRectF(
            self.width - 34,
            8,
            24,
            24
        )
        
        painter.setPen(QPen(QColor("#555555")))
        if self.color_button_hovered:
            painter.setPen(QPen(QColor("#ffffff")))
            
        painter.setBrush(QBrush(QColor(self.header_color if self.header_color else self.color)))
        painter.drawEllipse(self.color_button_rect)
        
        icon_color = QColor("#ffffff")
        icon_color.setAlpha(180)
        painter.setPen(QPen(icon_color))
        circle_size = 4
        spacing = 3
        total_width = (circle_size * 3) + (spacing * 2)
        x_start = self.color_button_rect.center().x() - (total_width / 2)
        y_pos = self.color_button_rect.center().y() - (circle_size / 2)
        
        for i in range(3):
            x_pos = x_start + (i * (circle_size + spacing))
            painter.drawEllipse(QRectF(x_pos, y_pos, circle_size, circle_size))
            
        painter.setPen(QPen(QColor("#ffffff")))
        font = QFont("Segoe UI", 10)
        painter.setFont(font)
        
        content_rect = QRectF(
            self.PADDING,
            self.HEADER_HEIGHT + 10,
            self.width - (self.PADDING * 2),
            self.height - self.HEADER_HEIGHT - (self.PADDING * 2)
        )
        
        if self.editing:
            text = self.edit_text
            metrics = painter.fontMetrics()
            
            layout = QTextLayout(text, font)
            text_option = QTextOption()
            text_option.setAlignment(Qt.AlignmentFlag.AlignLeft)
            text_option.setWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
            layout.setTextOption(text_option)
            
            layout.beginLayout()
            height = 0
            cursor_x = 0
            cursor_y = 0
            cursor_found = False
            text_lines = []
            
            while True:
                line = layout.createLine()
                if not line.isValid():
                    break
                    
                line.setLineWidth(content_rect.width())
                line_height = metrics.height()
                
                text_lines.append({
                    'line': line,
                    'y': height,
                    'text': text[line.textStart():line.textStart() + line.textLength()]
                })
                
                if not cursor_found and line.textStart() <= self.cursor_pos <= (line.textStart() + line.textLength()):
                    cursor_text = text[line.textStart():self.cursor_pos]
                    cursor_x = metrics.horizontalAdvance(cursor_text)
                    cursor_y = height
                    cursor_found = True
                    
                height += line_height
                
            layout.endLayout()
            
            if self.selection_start != self.selection_end:
                sel_start = min(self.selection_start, self.selection_end)
                sel_end = max(self.selection_start, self.selection_end)
                
                for line_info in text_lines:
                    line = line_info['line']
                    line_start = line.textStart()
                    line_length = line.textLength()
                    line_end = line_start + line_length
                    
                    if sel_start < line_end and sel_end > line_start:
                        start_x = 0
                        width = 0
                        
                        if sel_start > line_start:
                            start_text = text[line_start:sel_start]
                            start_x = metrics.horizontalAdvance(start_text)
                        
                        sel_text = text[
                            max(line_start, sel_start):
                            min(line_end, sel_end)
                        ]
                        width = metrics.horizontalAdvance(sel_text)
                        
                        sel_rect = QRectF(
                            content_rect.left() + start_x,
                            content_rect.top() + line_info['y'],
                            width,
                            metrics.height()
                        )
                        painter.fillRect(sel_rect, QColor("#2ecc71"))
            
            for line_info in text_lines:
                line = line_info['line']
                painter.drawText(
                    QPointF(content_rect.left(), content_rect.top() + line_info['y'] + metrics.ascent()),
                    line_info['text']
                )
            
            if self.cursor_visible and (not self.selecting or self.selection_start == self.selection_end):
                if cursor_found:
                    cursor_height = metrics.height()
                    painter.drawLine(
                        int(content_rect.left() + cursor_x),
                        int(content_rect.top() + cursor_y),
                        int(content_rect.left() + cursor_x),
                        int(content_rect.top() + cursor_y + cursor_height)
                    )
        else:
            text_option = QTextOption()
            text_option.setWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
            painter.drawText(content_rect, self.content, text_option)
            
        if self.hovered or self.isSelected():
            handle_size = 10
            handle_rect = QRectF(
                self.width - handle_size,
                self.height - handle_size,
                handle_size,
                handle_size
            )
            painter.setPen(QPen(QColor("#ffffff")))
            painter.drawLine(handle_rect.topLeft(), handle_rect.bottomRight())
            painter.drawLine(
                handle_rect.topLeft() + QPointF(0, handle_size/2),
                handle_rect.topRight() + QPointF(-handle_size/2, handle_size)
            )

    def get_char_pos_at_x(self, x, y):
        metrics = QFontMetrics(QFont("Segoe UI", 10))
        content_rect = QRectF(
            self.PADDING,
            self.HEADER_HEIGHT + 10,
            self.width - (self.PADDING * 2),
            self.height - self.HEADER_HEIGHT - (self.PADDING * 2)
        )
    
        layout = QTextLayout(self.edit_text, QFont("Segoe UI", 10))
        text_option = QTextOption()
        text_option.setAlignment(Qt.AlignmentFlag.AlignLeft)
        text_option.setWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        layout.setTextOption(text_option)
    
        layout.beginLayout()
        height = 0
        clicked_line = None
        relative_x = x - self.PADDING
        relative_y = y - (self.HEADER_HEIGHT + 10)
    
        while True:
            line = layout.createLine()
            if not line.isValid():
                break
            
            line.setLineWidth(content_rect.width())
            line_height = metrics.height()
        
            if height <= relative_y < (height + line_height):
                clicked_line = line
                break
            
            height += line_height
        
        layout.endLayout()
    
        if clicked_line:
            line_text = self.edit_text[clicked_line.textStart():clicked_line.textStart() + clicked_line.textLength()]
        
            text_width = 0
            for i, char in enumerate(line_text):
                char_width = metrics.horizontalAdvance(char)
                if text_width + (char_width / 2) > relative_x:
                    return clicked_line.textStart() + i
                text_width += char_width
            return clicked_line.textStart() + len(line_text)
    
        return len(self.edit_text)

    def mousePressEvent(self, event):
        if self.editing and event.pos().y() > self.HEADER_HEIGHT:
            self.selecting = True
            self.mouse_drag_start_pos = event.pos()
            char_pos = self.get_char_pos_at_x(event.pos().x(), event.pos().y())
            self.cursor_pos = char_pos
            self.selection_start = char_pos
            self.selection_end = char_pos
            self.update()
            event.accept()
        elif self.color_button_rect.contains(event.pos()):
            self.show_color_picker()
            event.accept()
        elif self._is_resize_handle(event.pos()):
            self.resizing = True
            self.resize_start_pos = event.pos()
            self.resize_start_size = QSizeF(self.width, self.height)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.selecting:
            self.selecting = False
            self.mouse_drag_start_pos = None
            event.accept()
        elif self.resizing:
            self.resizing = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self.selecting and self.editing:
            char_pos = self.get_char_pos_at_x(event.pos().x(), event.pos().y())
            self.selection_end = char_pos
            self.cursor_pos = char_pos
            self.update()
            event.accept()
        elif self.resizing:
            delta = event.pos() - self.resize_start_pos
            new_width = max(150, self.resize_start_size.width() + delta.x())
            new_height = max(100, self.resize_start_size.height() + delta.y())
            self.width = new_width
            self.height = new_height
            self.prepareGeometryChange()
            self.update()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.pos().y() > self.HEADER_HEIGHT:
            if not self.editing:
                self.editing = True
                self.edit_text = self.content
                char_pos = self.get_char_pos_at_x(event.pos().x(), event.pos().y())
                
                text = self.edit_text
                start = end = char_pos
                
                while start > 0 and text[start-1].isalnum():
                    start -= 1
                    
                while end < len(text) and text[end].isalnum():
                    end += 1
                
                self.selection_start = start
                self.selection_end = end
                self.cursor_pos = end
                
            self.cursor_timer.start()
            self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
            self.setFocus()
            self.update()
        else:
            super().mouseDoubleClickEvent(event)

    def keyPressEvent(self, event):
        if not self.editing:
            return super().keyPressEvent(event)
            
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_C:
                self.copy_selection()
                return
            elif event.key() == Qt.Key.Key_V:
                self.paste_text()
                return
            elif event.key() == Qt.Key.Key_X:
                self.cut_selection()
                return
            elif event.key() == Qt.Key.Key_A:
                self.select_all()
                return
        
        if event.key() == Qt.Key.Key_Return and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.finishEditing()
        elif event.key() == Qt.Key.Key_Escape:
            self.editing = False
            self.cursor_timer.stop()
            self.update()
        elif event.key() in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete):
            if self.selection_start != self.selection_end:
                self.delete_selection()
            elif event.key() == Qt.Key.Key_Backspace and self.cursor_pos > 0:
                self.edit_text = (
                    self.edit_text[:self.cursor_pos-1] + 
                    self.edit_text[self.cursor_pos:]
                )
                self.cursor_pos -= 1
            elif event.key() == Qt.Key.Key_Delete and self.cursor_pos < len(self.edit_text):
                self.edit_text = (
                    self.edit_text[:self.cursor_pos] + 
                    self.edit_text[self.cursor_pos+1:]
                )
            self.selection_start = self.selection_end = self.cursor_pos
            self.update()
        elif event.key() in (Qt.Key.Key_Left, Qt.Key.Key_Right):
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                if self.selection_start == self.selection_end:
                    self.selection_start = self.cursor_pos
                if event.key() == Qt.Key.Key_Left:
                    self.cursor_pos = max(0, self.cursor_pos - 1)
                else:
                    self.cursor_pos = min(len(self.edit_text), self.cursor_pos + 1)
                self.selection_end = self.cursor_pos
            else:
                if self.selection_start != self.selection_end and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    self.cursor_pos = min(self.selection_start, self.selection_end) if event.key() == Qt.Key.Key_Left else max(self.selection_start, self.selection_end)
                else:
                    if event.key() == Qt.Key.Key_Left:
                        self.cursor_pos = max(0, self.cursor_pos - 1)
                    else:
                        self.cursor_pos = min(len(self.edit_text), self.cursor_pos + 1)
                self.selection_start = self.selection_end = self.cursor_pos
            self.update()
        elif event.key() == Qt.Key.Key_Home:
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                if self.selection_start == self.selection_end:
                    self.selection_start = self.cursor_pos
                self.cursor_pos = 0
                self.selection_end = self.cursor_pos
            else:
                self.cursor_pos = 0
                self.selection_start = self.selection_end = self.cursor_pos
            self.update()
        elif event.key() == Qt.Key.Key_End:
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                if self.selection_start == self.selection_end:
                    self.selection_start = self.cursor_pos
                self.cursor_pos = len(self.edit_text)
                self.selection_end = self.cursor_pos
            else:
                self.cursor_pos = len(self.edit_text)
                self.selection_start = self.selection_end = self.cursor_pos
            self.update()
        elif event.key() == Qt.Key.Key_Return:
            if self.selection_start != self.selection_end:
                self.delete_selection()
            self.edit_text = (
                self.edit_text[:self.cursor_pos] + 
                '\n' + 
                self.edit_text[self.cursor_pos:]
            )
            self.cursor_pos += 1
            self.selection_start = self.selection_end = self.cursor_pos
            self.update()
        elif len(event.text()) and event.text().isprintable():
            if self.selection_start != self.selection_end:
                self.delete_selection()
            self.edit_text = (
                self.edit_text[:self.cursor_pos] + 
                event.text() + 
                self.edit_text[self.cursor_pos:]
            )
            self.cursor_pos += 1
            self.selection_start = self.selection_end = self.cursor_pos
            self.update()

    def copy_selection(self):
        if self.selection_start != self.selection_end:
            start = min(self.selection_start, self.selection_end)
            end = max(self.selection_start, self.selection_end)
            selected_text = self.edit_text[start:end]
            QApplication.clipboard().setText(selected_text)

    def cut_selection(self):
        if self.selection_start != self.selection_end:
            self.copy_selection()
            self.delete_selection()

    def paste_text(self):
        text = QApplication.clipboard().text()
        if text:
            if self.selection_start != self.selection_end:
                self.delete_selection()
            self.edit_text = (
                self.edit_text[:self.cursor_pos] + 
                text + 
                self.edit_text[self.cursor_pos:]
            )
            self.cursor_pos += len(text)
            self.selection_start = self.selection_end = self.cursor_pos
            self.update()

    def delete_selection(self):
        if self.selection_start != self.selection_end:
            start = min(self.selection_start, self.selection_end)
            end = max(self.selection_start, self.selection_end)
            self.edit_text = self.edit_text[:start] + self.edit_text[end:]
            self.cursor_pos = start
            self.selection_start = self.selection_end = start
            self.update()

    def select_all(self):
        self.selection_start = 0
        self.selection_end = len(self.edit_text)
        self.cursor_pos = self.selection_end
        self.update()

    def _is_resize_handle(self, pos):
        handle_rect = QRectF(
            self.width - 10,
            self.height - 10,
            10,
            10
        )
        return handle_rect.contains(pos)
        
    def hoverMoveEvent(self, event):
        old_resize_hover = self.resize_handle_hovered
        old_color_hover = self.color_button_hovered
        
        self.resize_handle_hovered = self._is_resize_handle(event.pos())
        self.color_button_hovered = self.color_button_rect.contains(event.pos())
        
        if (old_resize_hover != self.resize_handle_hovered or 
            old_color_hover != self.color_button_hovered):
            self.update()
            
        if self.resize_handle_hovered:
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            
    def hoverEnterEvent(self, event):
        self.hovered = True
        self.update()
        super().hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        self.hovered = False
        self.resize_handle_hovered = False
        self.color_button_hovered = False
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()
        super().hoverLeaveEvent(event)
        
    def show_color_picker(self):
        dialog = ColorPickerDialog(self.scene().views()[0])
        
        note_pos = self.mapToScene(self.color_button_rect.topRight())
        view_pos = self.scene().views()[0].mapFromScene(note_pos)
        global_pos = self.scene().views()[0].mapToGlobal(view_pos)
        
        dialog.move(global_pos.x() + 10, global_pos.y())
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            color, color_type = dialog.get_selected_color()
            if color_type == "full":
                self.color = color
                self.header_color = None
            else:
                self.header_color = color
            self.update()
            
    def finishEditing(self):
        if self.editing:
            self.content = self.edit_text
            self.editing = False
            self.cursor_timer.stop()
            self.clearFocus()
            self.update()
            
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.finishEditing()
        
    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            grid_size = 10
            new_pos = QPointF(
                round(value.x() / grid_size) * grid_size,
                round(value.y() / grid_size) * grid_size
            )
            return new_pos
        return super().itemChange(change, value)
    
class NavigationPin(QGraphicsItem):
    def __init__(self, title="New Pin", note="", parent=None):
        super().__init__(parent)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        
        self.title = title
        self.note = note
        self.hovered = False
        self.size = 32
        
    def boundingRect(self):
        return QRectF(-self.size/2, -self.size/2, self.size, self.size)
        
    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self.isSelected():
            pin_color = QColor("#2ecc71")
        elif self.hovered:
            pin_color = QColor("#3498db")
        else:
            pin_color = QColor("#e74c3c")
            
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(pin_color)
        head_rect = QRectF(-10, -10, 20, 20)
        painter.drawEllipse(head_rect)
        
        path = QPainterPath()
        path.moveTo(0, 10)
        path.lineTo(-8, 25)
        path.lineTo(8, 25)
        path.closeSubpath()
        
        painter.setBrush(pin_color)
        painter.drawPath(path)
        
        if self.hovered or self.isSelected():
            painter.setPen(QPen(QColor("#ffffff")))
            font = QFont("Segoe UI", 8)
            painter.setFont(font)
            text_rect = QRectF(-50, -35, 100, 20)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.title)
            
    def hoverEnterEvent(self, event):
        self.hovered = True
        self.update()
        super().hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        self.hovered = False
        self.update()
        super().hoverLeaveEvent(event)
        
    def mouseDoubleClickEvent(self, event):
        dialog = PinEditDialog(self.title, self.note, self.scene().views()[0])
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.title = dialog.title_input.text()
            self.note = dialog.note_input.toPlainText()
            if self.scene() and hasattr(self.scene().window, 'pin_overlay'):
                self.scene().window.pin_overlay.update_pin(self)
        super().mouseDoubleClickEvent(event)

class PinOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.window = parent
        self.setFixedWidth(200)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        
        # Initialize pins list
        self.pins = []
        
        # Main container layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header with icon
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(5)
        
        icon_label = QLabel("⚲")
        icon_label.setStyleSheet("font-size: 16px;")
        header_layout.addWidget(icon_label)
        
        header_text = QLabel("Navigation Pins")
        header_text.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        header_layout.addWidget(header_text)
        header_layout.addStretch()
        
        main_layout.addWidget(header_widget)
        
        # Pin list container with scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #2d2d2d;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #3f3f3f;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Pin list widget
        self.pin_list = QWidget()
        self.pin_layout = QVBoxLayout(self.pin_list)
        self.pin_layout.setSpacing(5)
        self.pin_layout.setContentsMargins(5, 5, 5, 5)
        self.pin_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll.setWidget(self.pin_list)
        main_layout.addWidget(scroll)
        
        
        
        # Add pin button
        self.add_btn = QPushButton("Drop New Pin")
        self.add_btn.setIcon(qta.icon('fa5s.map-pin', color='white'))
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.clicked.connect(self.create_pin)
        main_layout.addWidget(self.add_btn)
        
        # Set overall styling (keeping your original style)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-radius: 10px;
            }
            QPushButton {
                background-color: #2ecc71;
                border: none;
                border-radius: 5px;
                padding: 10px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:disabled {
                background-color: #555555;
            }
        """)

    def refresh_pins(self):
        """Refresh pin display with validation"""
        # Keep only valid pins
        self.pins = [pin for pin in self.pins if pin.scene() is not None]

        # Clear existing widgets
        while self.pin_layout.count():
            item = self.pin_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Rebuild pin buttons for valid pins
        for pin in self.pins:
            if pin.scene():  # Double check pin is still valid
                self._create_pin_button(pin)

        # Update add button state
        self.add_btn.setEnabled(len(self.pins) < 10)

    def _create_pin_button(self, pin):
        """Create a single pin button widget"""
        pin_widget = QWidget()
        pin_widget.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-radius: 5px;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 3px;
                padding: 8px;
                color: white;
                text-align: left;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        
        layout = QHBoxLayout(pin_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        btn = QPushButton(pin.title)
        btn.setIcon(qta.icon('fa5s.map-pin', color='#e74c3c'))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda: self.navigate_to_pin(pin))
        layout.addWidget(btn, stretch=1)
        
        del_btn = QPushButton()
        del_btn.setIcon(qta.icon('fa5s.times', color='#666666'))
        del_btn.setFixedSize(24, 24)
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.clicked.connect(lambda: self.remove_pin(pin))
        layout.addWidget(del_btn)
        
        self.pin_layout.addWidget(pin_widget)

    def create_pin(self):
        """Create a new pin"""
        if len(self.pins) >= 10:
            return
            
        scene = self.window.chat_view.scene()
        view = self.window.chat_view
        center = view.mapToScene(view.viewport().rect().center())
        
        pin = scene.add_navigation_pin(center)
        self.pins.append(pin)
        self.refresh_pins()

    def remove_pin(self, pin):
        """Remove a pin safely from the overlay and the scene."""
        if pin in self.pins:
            scene = self.window.chat_view.scene()

            # Remove from the scene's tracking list if it exists there
            if pin in scene.pins:
                scene.pins.remove(pin)

            # Remove the graphical item from the scene itself
            if pin.scene() == scene:
                scene.removeItem(pin)

            # Now, remove from this overlay's list and refresh the UI
            self.pins.remove(pin)
            self.refresh_pins()

    def navigate_to_pin(self, pin):
        """Navigate to a pin's location"""
        if pin.scene():  # Check pin is still valid
            view = self.window.chat_view
            view.centerOn(pin)
            pin.setSelected(True)

    def clear_pins(self):
        """Clear all pins safely"""
        # Clear internal pin list first
        self.pins.clear()
        
        # Clear all widgets from layout
        while self.pin_layout.count():
            item = self.pin_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Update add button state
        self.add_btn.setEnabled(True)

    def update_pin(self, pin):
        """Update pin display after editing"""
        if pin in self.pins and pin.scene():  # Check pin is still valid
            self.refresh_pins()
            
    def add_pin_button(self, pin):
        """Add a new pin button with validation"""
        if len(self.pins) >= 10 or pin in self.pins:
            return

        if pin.scene():  # Only add if pin is in a scene
            self.pins.append(pin)
            self.refresh_pins()

class ChartItem(QGraphicsItem):
    PADDING = 20
    HEADER_HEIGHT = 40
    
    def __init__(self, data, pos, parent=None):
        super().__init__(parent)
        self.setPos(pos)
        self.data = data
        self.title = data.get('title', 'Chart')
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        
        self.width = 650
        self.height = 500
        
        self.hovered = False
        self.resize_handle_hovered = False
        self.resizing = False
        
        self.figure = Figure(figsize=(6, 4), dpi=300)
        self.figure.patch.set_facecolor('#2d2d2d')
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setStyleSheet("background-color: transparent;")
        
        self.generate_chart()

    def generate_chart(self):
        def abbreviate_text(text):
            if not isinstance(text, str):
                return str(text)
            
            words = text.split()
            abbreviated = []
        
            for word in words:
                if len(word) > 8:
                    abbreviated.append(word[:3].lower())
                else:
                    abbreviated.append(word)
                
            return ' '.join(abbreviated)

        self.figure.clear()
    
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#2d2d2d')
    
        plt.style.use('dark_background')
    
        plt.rcParams['axes.labelsize'] = 8
        plt.rcParams['axes.titlesize'] = 8
        plt.rcParams['xtick.labelsize'] = 7
        plt.rcParams['ytick.labelsize'] = 7
        plt.rcParams['legend.fontsize'] = 8
    
        chart_type = self.data.get('type', '')
    
        if chart_type == 'sankey':
            flows = self.data.get('flows', [])
            if not flows:
                ax.text(0.5, 0.5, 'No flow data provided', 
                       ha='center', va='center')
                return
            
            labels = []
            sources = []
            targets = []
            values = []
        
            label_to_index = {}
            for flow in flows:
                source = abbreviate_text(flow.get('source', ''))
                target = abbreviate_text(flow.get('target', ''))
            
                if source not in label_to_index:
                    label_to_index[source] = len(label_to_index)
                    labels.append(source)
                if target not in label_to_index:
                    label_to_index[target] = len(label_to_index)
                    labels.append(target)
                
                sources.append(label_to_index[source])
                targets.append(label_to_index[target])
                values.append(flow.get('value', 0))
            
            from matplotlib.sankey import Sankey
        
            figsize = max(6, len(labels) * 0.5)
            self.figure.set_size_inches(figsize, figsize * 0.75)
        
            sankey = Sankey(ax=ax, unit='', scale=0.01)
            sankey.add(flows=values,
                      labels=labels,
                      orientations=[0] * len(values),
                      pathlengths=[0.25] * len(values),
                      patchlabel=None,
                      alpha=0.7,
                      facecolor='#3498db')
                  
            ax.axis('off')
        
        else:
            labels = [abbreviate_text(str(label)) for label in self.data.get('labels', [])]
            values = self.data.get('values', [])
            xaxis = abbreviate_text(self.data.get('xAxis', ''))
            yaxis = abbreviate_text(self.data.get('yAxis', ''))
        
            if chart_type == 'bar':
                bars = ax.bar(labels, values, color='#2ecc71')
                ax.set_xlabel(xaxis)
                ax.set_ylabel(yaxis)
            
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:,.1f}',
                           ha='center', va='bottom',
                           fontsize=7)
            
            elif chart_type == 'line':
                line = ax.plot(labels, values, color='#3498db', marker='o',
                              linewidth=2, markersize=6,
                              markerfacecolor='white')[0]
                ax.set_xlabel(xaxis)
                ax.set_ylabel(yaxis)
            
            elif chart_type == 'pie':
                colors = ['#2ecc71', '#3498db', '#9b59b6', '#e67e22', 
                         '#e74c3c', '#f1c40f']
                wedges, texts, autotexts = ax.pie(
                    values, labels=labels,
                    autopct='%1.1f%%',
                    colors=colors,
                    textprops={'fontsize': 7, 'color': 'white'},
                    wedgeprops={'linewidth': 1, 'edgecolor': '#2d2d2d'}
                )
            
                plt.setp(autotexts, weight="bold", size=7)
                plt.setp(texts, weight="bold", size=7)
            
            elif chart_type == 'histogram':
                ax.hist(values, bins=self.data.get('bins', 10),
                       color='#9b59b6', edgecolor='white', linewidth=1)
                ax.set_xlabel(xaxis)
                ax.set_ylabel(yaxis)
        
                ax.grid(True, linestyle='--', alpha=0.3, linewidth=0.5)
            
                if chart_type in ['bar', 'line']:
                    plt.xticks(rotation=45, ha='right')
    
        self.figure.tight_layout(pad=1.8)
    
        self.canvas.draw()
    
        width, height = self.canvas.get_width_height()
        self.chart_image = QImage(self.canvas.buffer_rgba(),
                                width, height,
                                QImage.Format.Format_RGBA8888)
    
        if hasattr(self.chart_image, 'setDevicePixelRatio'):
            self.chart_image.setDevicePixelRatio(2.0)
        
    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)
        
    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        shadow_path = QPainterPath()
        shadow_path.addRoundedRect(3, 3, self.width, self.height, 10, 10)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, 30))
        painter.drawPath(shadow_path)
        
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width, self.height, 10, 10)
        
        if self.isSelected():
            painter.setPen(QPen(QColor("#2ecc71"), 2))
        elif self.hovered:
            painter.setPen(QPen(QColor("#ffffff"), 2))
        else:
            painter.setPen(QPen(QColor("#555555")))
            
        painter.setBrush(QBrush(QColor("#2d2d2d")))
        painter.drawPath(path)
        
        header_rect = QRectF(0, 0, self.width, self.HEADER_HEIGHT)
        header_path = QPainterPath()
        header_path.addRoundedRect(header_rect, 10, 10)
        
        header_gradient = QLinearGradient(header_rect.topLeft(), header_rect.bottomLeft())
        header_color = QColor("#3498db")
        header_gradient.setColorAt(0, header_color)
        header_gradient.setColorAt(1, header_color.darker(110))
        
        painter.setBrush(QBrush(header_gradient))
        painter.drawPath(header_path)
        
        painter.setPen(QPen(QColor("#ffffff")))
        font = QFont("Segoe UI", 10, QFont.Weight.Bold)
        painter.setFont(font)
        title_rect = header_rect.adjusted(10, 0, -10, 0)
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignVCenter, self.title)
        
        if hasattr(self, 'chart_image'):
            chart_rect = QRectF(
                self.PADDING,
                self.HEADER_HEIGHT + 10,
                self.width - (self.PADDING * 2),
                self.height - self.HEADER_HEIGHT - (self.PADDING * 2)
            )
            painter.drawImage(chart_rect, self.chart_image)
            
        if self.hovered or self.isSelected():
            handle_size = 10
            handle_rect = QRectF(
                self.width - handle_size,
                self.height - handle_size,
                handle_size,
                handle_size
            )
            painter.setPen(QPen(QColor("#ffffff")))
            painter.drawLine(handle_rect.topLeft(), handle_rect.bottomRight())
            painter.drawLine(
                handle_rect.topLeft() + QPointF(0, handle_size/2),
                handle_rect.topRight() + QPointF(-handle_size/2, handle_size)
            )
            
    def hoverEnterEvent(self, event):
        self.hovered = True
        self.update()
        super().hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        self.hovered = False
        self.resize_handle_hovered = False
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()
        super().hoverLeaveEvent(event)
        
    def mousePressEvent(self, event):
        if self._is_resize_handle(event.pos()):
            self.resizing = True
            self.resize_start_pos = event.pos()
            self.resize_start_size = QSizeF(self.width, self.height)
            event.accept()
        else:
            super().mousePressEvent(event)
            
    def mouseReleaseEvent(self, event):
        if self.resizing:
            self.resizing = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)
            
    def mouseMoveEvent(self, event):
        if self.resizing:
            delta = event.pos() - self.resize_start_pos
            new_width = max(400, self.resize_start_size.width() + delta.x())
            new_height = max(300, self.resize_start_size.height() + delta.y())
            self.width = new_width
            self.height = new_height
            self.generate_chart()
            self.prepareGeometryChange()
            self.update()
            event.accept()
        else:
            super().mouseMoveEvent(event)
            
    def _is_resize_handle(self, pos):
        handle_rect = QRectF(
            self.width - 10,
            self.height - 10,
            10,
            10
        )
        return handle_rect.contains(pos)
        
    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            grid_size = 10
            new_pos = QPointF(
                round(value.x() / grid_size) * grid_size,
                round(value.y() / grid_size) * grid_size
            )
            return new_pos
        return super().itemChange(change, value)

class ChatScene(QGraphicsScene):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.nodes = []
        self.connections = []
        self.frames = []
        self.pins = []
        self.setBackgroundBrush(QColor("#252526"))
        self.horizontal_spacing = 300
        self.vertical_spacing = 100
        
    def add_chat_node(self, text, is_user=True, parent_node=None, conversation_history=None):
        try:
            if parent_node is not None:
                if parent_node not in self.nodes:
                    print("Warning: Parent node not found in scene")
                    parent_node = None
                elif not parent_node.scene():
                    print("Warning: Parent node no longer in scene")
                    parent_node = None
            
            node = ChatNode(text, is_user)
            if conversation_history:
                node.conversation_history = conversation_history.copy()
            
            if parent_node:
                try:
                    parent_pos = parent_node.pos()
                    
                    parent_node.children.append(node)
                    node.parent_node = parent_node
                    
                    base_pos = QPointF(
                        parent_pos.x() + self.horizontal_spacing,
                        parent_pos.y()
                    )
                    
                    node.setPos(self.find_free_position(base_pos, node))
                    
                    connection = ConnectionItem(parent_node, node)
                    self.addItem(connection)
                    self.connections.append(connection)
                except RuntimeError as e:
                    print(f"Error setting up parent relationship: {str(e)}")
                    node.parent_node = None
                    if parent_node and hasattr(parent_node, 'children'):
                        if node in parent_node.children:
                            parent_node.children.remove(node)
                    node.setPos(50, 150)
            else:
                node.setPos(50, 150)
            
            self.addItem(node)
            self.nodes.append(node)
            
            if node not in self.nodes or not node.scene():
                raise RuntimeError("Node failed to add to scene")
                
            return node
            
        except Exception as e:
            print(f"Error adding chat node: {str(e)}")
            if 'node' in locals():
                if node in self.nodes:
                    self.nodes.remove(node)
                if node.scene() == self:
                    self.removeItem(node)
            return None

    def nodeMoved(self, node):
        if node not in self.nodes or not node.scene():
            return
            
        for conn in self.connections[:]:
            if node in (conn.start_node, conn.end_node):
                if (conn.start_node in self.nodes and 
                    conn.end_node in self.nodes and
                    conn.start_node.scene() and 
                    conn.end_node.scene()):
                    conn.update_path()
                else:
                    if conn in self.connections:
                        self.connections.remove(conn)
                    if conn.scene() == self:
                        self.removeItem(conn)
                        
    def add_navigation_pin(self, pos):
        pin = NavigationPin()
        pin.setPos(pos)
        self.addItem(pin)
        self.pins.append(pin)
        return pin
    
    def add_chart(self, data, pos):
        chart = ChartItem(data, pos)
        self.addItem(chart)
        return chart

    def createFrame(self):
        selected_nodes = [item for item in self.selectedItems() 
                         if isinstance(item, ChatNode)]
        
        if len(selected_nodes) < 1:
            return
            
        for node in selected_nodes:
            if node.parentItem() and isinstance(node.parentItem(), Frame):
                old_frame = node.parentItem()
                
                scene_pos = node.scenePos()
                
                node.setParentItem(None)
                node.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
                
                node.setPos(scene_pos)
                
                old_frame.nodes.remove(node)
                
                if not old_frame.nodes:
                    self.removeItem(old_frame)
                    self.frames.remove(old_frame)
                else:
                    old_frame.updateGeometry()
        
        frame = Frame(selected_nodes)
        self.addItem(frame)
        self.frames.append(frame)
        
        frame.setZValue(-2)
        
        for node in selected_nodes:
            self.nodeMoved(node)
            
    def add_note(self, pos):
        note = Note(pos)
        self.addItem(note)
        return note
    
    def deleteSelectedNotes(self):
        for item in list(self.selectedItems()):
            if isinstance(item, Note):
                self.removeItem(item)
    
    def deleteFrame(self, frame):
        for node in frame.nodes:
            scene_pos = node.scenePos()
            
            node.setParentItem(None)
            node.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
            
            node.setPos(scene_pos)
            
            self.nodeMoved(node)
        
        self.removeItem(frame)
        if frame in self.frames:
            self.frames.remove(frame)

    def keyPressEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_F:
                self.createFrame()
            elif event.key() == Qt.Key.Key_A:
                self.selectAllNodes()
        elif event.key() == Qt.Key.Key_Delete:
            for item in list(self.selectedItems()):
                if isinstance(item, Frame):
                    self.deleteFrame(item)
                elif isinstance(item, Note):
                    self.removeItem(item)
                
        super().keyPressEvent(event)
        
    def selectAllNodes(self):
        for node in self.nodes:
            node.setSelected(True)

    def calculate_node_rect(self, node, pos):
        PADDING = 30
        return QRectF(
            pos.x() - PADDING,
            pos.y() - PADDING,
            node.width + (PADDING * 2),
            node.height + (PADDING * 2)
        )

    def check_collision(self, test_rect, ignore_node=None):
        for node in self.nodes:
            if node == ignore_node:
                continue
            node_rect = self.calculate_node_rect(node, node.pos())
            if test_rect.intersects(node_rect):
                return True
        return False

    def find_free_position(self, base_pos, node, max_attempts=50):
        def spiral_positions():
            x, y = base_pos.x(), base_pos.y()
            layer = 1
            while True:
                for i in range(layer):
                    yield QPointF(x, y)
                    x += self.horizontal_spacing // 2
                for i in range(layer):
                    yield QPointF(x, y)
                    y += self.vertical_spacing
                for i in range(layer):
                    yield QPointF(x, y)
                    x -= self.horizontal_spacing // 2
                for i in range(layer):
                    yield QPointF(x, y)
                    y -= self.vertical_spacing
                layer += 1

        attempts = max_attempts
        for pos in spiral_positions():
            if attempts <= 0:
                break
            test_rect = self.calculate_node_rect(node, pos)
            if not self.check_collision(test_rect, node):
                return pos
            attempts -= 1

        return QPointF(base_pos.x(), base_pos.y() + len(self.nodes) * self.vertical_spacing)

    def mousePressEvent(self, event):
        clicked_item = self.itemAt(event.scenePos(), QTransform())
        if not clicked_item:
            for item in self.items():
                if isinstance(item, ConnectionItem):
                    item.is_selected = False
                    item.stopArrowAnimation()
                    item.update()
                
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            item = self.itemAt(event.scenePos(), self.views()[0].transform())
            if isinstance(item, ConnectionItem):
                if event.button() == Qt.MouseButton.LeftButton:
                    item.add_pin(event.scenePos())
                    event.accept()
                    return
                
        super().mousePressEvent(event)
    
        if not event.modifiers() and not self.itemAt(event.scenePos(), self.views()[0].transform()):
            self.clearSelection()
            
    def update_connections(self):
        valid_connections = []
        for conn in self.connections[:]:
            try:
                if (conn.start_node in self.nodes and 
                    conn.end_node in self.nodes and 
                    conn.start_node.scene() == self and
                    conn.end_node.scene() == self and
                    hasattr(conn.start_node, 'children') and
                    conn.end_node in conn.start_node.children):
                    valid_connections.append(conn)
                    conn.setZValue(-1)
                    conn.update_path()
                    conn.show()
                else:
                    for pin in conn.pins[:]:
                        conn.remove_pin(pin)
                    if conn.scene() == self:
                        self.removeItem(conn)
            except RuntimeError:
                if conn.scene() == self:
                    self.removeItem(conn)
                    
        self.connections = valid_connections

    def organize_nodes(self):
        if not self.nodes:
            return
        
        START_X = 50
        START_Y = 150
        NODE_GAP_X = 500
        MIN_NODE_GAP_Y = 150
        FRAME_CLEARANCE = 50
    
        def get_node_size(node):
            PADDING = 40
            return node.width + PADDING * 2, node.height + PADDING * 2
    
        def get_frame_rect(frame):
            return frame.mapRectToScene(frame.boundingRect())
    
        def is_node_in_frame(node):
            return isinstance(node.parentItem(), Frame)
    
        def get_rightmost_frame_x():
            if not self.frames:
                return START_X
        
            max_x = START_X
            for frame in self.frames:
                frame_rect = get_frame_rect(frame)
                max_x = max(max_x, frame_rect.right())
            return max_x + FRAME_CLEARANCE
    
        def check_collision(node, pos_x, pos_y):
            node_width, node_height = get_node_size(node)
            test_rect = QRectF(pos_x, pos_y, node_width, node_height)
        
            for other in self.nodes:
                if other == node or is_node_in_frame(other):
                    continue
                other_width, other_height = get_node_size(other)
                other_rect = QRectF(other.pos().x(), other.pos().y(), 
                                  other_width, other_height)
                if test_rect.intersects(other_rect):
                    return True
        
            for frame in self.frames:
                frame_rect = get_frame_rect(frame)
                if test_rect.intersects(frame_rect):
                    return True
                
            return False
    
        def find_free_position(node, base_x, base_y):
            if is_node_in_frame(node):
                return node.pos().x(), node.pos().y()
            
            rightmost_x = max(base_x, get_rightmost_frame_x())
        
            y_offset = 0
            y_step = MIN_NODE_GAP_Y
            max_attempts = 100
        
            if not check_collision(node, rightmost_x, base_y):
                return rightmost_x, base_y
            
            while max_attempts > 0:
                if not check_collision(node, rightmost_x, base_y + y_offset):
                    return rightmost_x, base_y + y_offset
                
                if not check_collision(node, rightmost_x, base_y - y_offset):
                    return rightmost_x, base_y - y_offset
            
                y_offset += y_step
                max_attempts -= 1
            
            return rightmost_x, base_y + (len(self.nodes) * MIN_NODE_GAP_Y)
    
        def position_node_and_children(node, level_x, level_y):
            if not is_node_in_frame(node):
                free_x, free_y = find_free_position(node, level_x, level_y)
                node.setPos(free_x, free_y)
                current_x = free_x
            else:
                current_x = node.scenePos().x()
        
            if node.children:
                sorted_children = sorted(node.children, 
                                      key=lambda n: self.nodes.index(n))
            
                next_level_x = current_x + NODE_GAP_X
            
                child_y = level_y
                for child in sorted_children:
                    position_node_and_children(child, next_level_x, child_y)
                    if not is_node_in_frame(child):
                        _, child_height = get_node_size(child)
                        child_y += child_height + MIN_NODE_GAP_Y

        root_nodes = [node for node in self.nodes if not node.parent_node]
        current_y = START_Y
    
        for root in root_nodes:
            position_node_and_children(root, START_X, current_y)
            if not is_node_in_frame(root):
                _, root_height = get_node_size(root)
                current_y += root_height + MIN_NODE_GAP_Y * 2

        self.update_connections()

    def deleteSelectedItems(self):
        for item in list(self.selectedItems()):
            if isinstance(item, Frame):
                self.deleteFrame(item)
            elif isinstance(item, Note):
                self.removeItem(item)
            elif isinstance(item, ChartItem):
                self.removeItem(item)
            elif isinstance(item, NavigationPin):
                if hasattr(self.window, 'pin_overlay') and self.window.pin_overlay:
                    self.window.pin_overlay.remove_pin(item)
                if item in self.pins:
                    self.pins.remove(item)
                self.removeItem(item)
            
class GridControl(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_size = 20
        self.grid_opacity = 0.1
        
        self.canvas = QWidget(self)
        main_layout = QVBoxLayout(self.canvas)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(6)

        self.canvas.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 10px;
            }
        """)

        icon_slider_layout = QHBoxLayout()
        icon_slider_layout.setContentsMargins(0, 0, 0, 0)
        icon_slider_layout.setSpacing(10)
        
        label = QLabel("⊞", self.canvas)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFixedWidth(30)
        label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 0);
                border-radius: 5px;
            }
        """)
        icon_slider_layout.addWidget(label)
        
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal, self.canvas)
        self.opacity_slider.setFixedWidth(130)
        self.opacity_slider.setMinimum(0)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(int(self.grid_opacity * 100))
        self.opacity_slider.valueChanged.connect(self._update_opacity)
        self.opacity_slider.setToolTip(f"{self.opacity_slider.value()}%")
        self.opacity_slider.valueChanged.connect(
            lambda: self.opacity_slider.setToolTip(f"{self.opacity_slider.value()}%")
        )

        self.opacity_slider.setStyleSheet("""
            QSlider::handle:horizontal {
                background-color: #2ecc71;
                border-radius: 6px;
                width: 16px;
                margin: -6px 0;
            }
            QSlider::groove:horizontal {
                background-color: rgba(0, 0, 0, 0.2);
                height: 4px;
                border-radius: 2px;
            }
        """)
        
        icon_slider_layout.addWidget(self.opacity_slider)
        main_layout.addLayout(icon_slider_layout)
        
        grid_presets_layout = QHBoxLayout()
        grid_presets_layout.setContentsMargins(0, 0, 0, 0)
        grid_presets_layout.setSpacing(12)
        
        preset_sizes = [(10, "10px"), (20, "20px"), (50, "50px"), (100, "100px")]
        for size, label in preset_sizes:
            button = QPushButton(label, self.canvas)
            button.setFixedSize(40, 25)
            button.setStyleSheet("""
                QPushButton {
                    color: white;
                    background-color: rgba(63, 63, 63, 0.1);
                    border: none;
                    border-radius: 5px;
                    font-size: 10px;
                    padding: 2px;
                }
                QPushButton:hover {
                    background-color: rgba(85, 85, 85, 0);
                }
                QPushButton:pressed {
                    background-color: rgba(46, 204, 113, 0.3);
                    color: black;
                }
            """)
            button.clicked.connect(lambda checked, s=size: self._set_grid_size(s))
            grid_presets_layout.addWidget(button)
            
        main_layout.addLayout(grid_presets_layout)
        
        self.setFixedSize(200, 90)
        self.canvas.setFixedSize(200, 90)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 0)
        self.canvas.setGraphicsEffect(shadow)
        
    def _update_opacity(self, value):
        self.grid_opacity = value / 100.0
        if self.parent():
            self.parent().update()
            
    def _set_grid_size(self, size):
        self.grid_size = size
        if self.parent():
            self.parent().update()
        
class ChatView(QGraphicsView):
    def __init__(self, window):
        super().__init__()
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.v_scrollbar = CustomScrollBar(Qt.Orientation.Vertical, self)
        self.h_scrollbar = CustomScrollBar(Qt.Orientation.Horizontal, self)
        
        self.v_scrollbar.valueChanged.connect(lambda v: self.verticalScrollBar().setValue(int(v)))
        self.h_scrollbar.valueChanged.connect(lambda h: self.horizontalScrollBar().setValue(int(h)))
        
        self.setScene(ChatScene(window))
        
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        
        self._panning = False
        self._last_mouse_pos = None
        self._zoom_factor = 1.0
        self._drag_factor = 1.0
        
        self._expanding = False
        self._expand_start = None
        self._expand_rect = None
        self._original_transform = None
        
        self._setup_drag_control()
        
        self.setMouseTracking(True)
        
        self.grid_control = GridControl(self)
        self._update_grid_control_position()
        
        self._current_mouse_pos = None
        
        self.setSceneRect(-100000, -100000, 200000, 200000)
        
    def _setup_drag_control(self):
        self.control_widget = QWidget(self)
        main_layout = QVBoxLayout(self.control_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(6)

        self.control_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 10px;
            }
        """)

        icon_slider_layout = QHBoxLayout()
        icon_slider_layout.setContentsMargins(0, 0, 0, 0)
        icon_slider_layout.setSpacing(10)

        label = QLabel("⚡", self.control_widget)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFixedWidth(30)
        label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 0);
                border-radius: 5px;
            }
        """)
        icon_slider_layout.addWidget(label)

        self.drag_slider = QSlider(Qt.Orientation.Horizontal, self.control_widget)
        self.drag_slider.setFixedWidth(130)
        self.drag_slider.setMinimum(10)
        self.drag_slider.setMaximum(100)
        self.drag_slider.setValue(100)
        self.drag_slider.valueChanged.connect(self._update_drag)
        self.drag_slider.setToolTip(f"{self.drag_slider.value()}%")
        self.drag_slider.valueChanged.connect(
            lambda: self.drag_slider.setToolTip(f"{self.drag_slider.value()}%")
        )

        self.drag_slider.setStyleSheet("""
            QSlider::handle:horizontal {
                background-color: #2ecc71;
                border-radius: 6px;
                width: 16px;
                margin: -6px 0;
            }
            QSlider::groove:horizontal {
                background-color: rgba(0, 0, 0, 0.2);
                height: 4px;
                border-radius: 2px;
            }
        """)

        icon_slider_layout.addWidget(self.drag_slider)
        main_layout.addLayout(icon_slider_layout)

        notches_layout = QHBoxLayout()
        notches_layout.setContentsMargins(0, 0, 0, 0)
        notches_layout.setSpacing(12)

        button_labels = [(25, "25%"), (50, "50%"), (75, "75%"), (100, "100%")]
        for value, label in button_labels:
            button = QPushButton(label, self.control_widget)
            button.setFixedSize(40, 25)
            button.setStyleSheet("""
                QPushButton {
                    color: white;
                    background-color: rgba(63, 63, 63, 0.1);
                    border: none;
                    border-radius: 5px;
                    font-size: 10px;
                    padding: 2px;
                }
                QPushButton:hover {
                    background-color: rgba(85, 85, 85, 0);
                }
                QPushButton:pressed {
                    background-color: rgba(46, 204, 113, 0.3);
                    color: black;
                }
            """)
            button.clicked.connect(lambda _, v=value: self._set_slider_value(v))
            notches_layout.addWidget(button)

        main_layout.addLayout(notches_layout)

        self.control_widget.setFixedSize(200, 90)
        self._update_control_position()

    def _set_slider_value(self, value):
        self.drag_slider.setValue(value)
        self._update_drag()

    def _update_control_position(self):
        padding = 10
        self.control_widget.move(
            self.width() - self.control_widget.width() - padding,
            padding
        )

    def _update_drag(self):
        self._drag_factor = self.drag_slider.value() / 100.0

    def _update_grid_control_position(self):
        padding = 10
        self.grid_control.move(
            self.width() - self.grid_control.width() - padding,
            120
        )

    def updateScrollbars(self):
        v_bar = self.verticalScrollBar()
        self.v_scrollbar.setRange(v_bar.minimum(), v_bar.maximum())
        self.v_scrollbar.page_step = v_bar.pageStep()
        self.v_scrollbar.setValue(v_bar.value())
        
        h_bar = self.horizontalScrollBar()
        self.h_scrollbar.setRange(h_bar.minimum(), h_bar.maximum())
        self.h_scrollbar.page_step = h_bar.pageStep()
        self.h_scrollbar.setValue(h_bar.value())

    def mousePressEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            self._expanding = True
            self._expand_start = event.position().toPoint()
            self._expand_rect = None
            self._original_transform = self.transform()
            event.accept()
        elif event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._last_mouse_pos = event.position().toPoint()
            self.viewport().setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._expanding and self._expand_start:
            self._current_mouse_pos = event.position().toPoint()
            self._expand_rect = QRectF(
                self.mapToScene(self._expand_start),
                self.mapToScene(self._current_mouse_pos)
            ).normalized()
            
            self.viewport().update()
            event.accept()
        elif self._panning and self._last_mouse_pos is not None:
            delta = event.position().toPoint() - self._last_mouse_pos
            delta *= self._drag_factor
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            self.updateScrollbars()
            self._last_mouse_pos = event.position().toPoint()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._expanding and self._expand_rect:
            self.fitInView(self._expand_rect, Qt.AspectRatioMode.KeepAspectRatio)
            self._zoom_factor = self.transform().m11()
            self._expanding = False
            self._expand_rect = None
            event.accept()
        elif self._panning:
            self._panning = False
            self._last_mouse_pos = None
            self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Shift:
            if self._expanding and self._original_transform:
                self.setTransform(self._original_transform)
                self._zoom_factor = self._original_transform.m11()
                self._expanding = False
                self._expand_rect = None
                self.viewport().update()
        elif event.key() == Qt.Key.Key_Escape:
            if self._original_transform:
                self.setTransform(self._original_transform)
                self._zoom_factor = self._original_transform.m11()
                self._expanding = False
                self._expand_rect = None
                self.viewport().update()
        super().keyReleaseEvent(event)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            zoom_in = event.angleDelta().y() > 0
            
            if zoom_in:
                factor = 1.1
                self._zoom_factor *= factor
            else:
                factor = 0.9
                self._zoom_factor *= factor
                
            if 0.1 <= self._zoom_factor <= 4.0:
                self.scale(factor, factor)
            else:
                self._zoom_factor /= factor
        else:
            v_bar = self.verticalScrollBar()
            h_bar = self.horizontalScrollBar()
            
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                delta = event.angleDelta().y() if event.angleDelta().y() != 0 else event.angleDelta().x()
                h_bar.setValue(h_bar.value() - delta)
            else:
                delta = event.angleDelta().y()
                v_bar.setValue(v_bar.value() - delta)
                
            self.updateScrollbars()

    def paintEvent(self, event):
        super().paintEvent(event)
        
        if self._expanding and self._expand_start and self._current_mouse_pos:
            painter = QPainter(self.viewport())
            painter.setPen(QPen(QColor("#2ecc71"), 2, Qt.PenStyle.DashLine))
            painter.setBrush(QBrush(QColor(46, 204, 113, 30)))
            
            rect = QRectF(
                self._expand_start,
                self._current_mouse_pos
            ).normalized()
            
            painter.drawRect(rect)

    def resizeEvent(self, event):
        super().resizeEvent(event)
    
        self._update_control_position()
        self._update_grid_control_position()
    
        scrollbar_width = self.v_scrollbar.width()
        scrollbar_height = self.h_scrollbar.height()
    
        self.v_scrollbar.setGeometry(
            self.width() - scrollbar_width,
            0,
            scrollbar_width,
            self.height() - scrollbar_height
        )
    
        self.h_scrollbar.setGeometry(
            0,
            self.height() - scrollbar_height,
            self.width() - scrollbar_width,
            scrollbar_height
        )
    
        self.updateScrollbars()

    def scrollContentsBy(self, dx, dy):
        super().scrollContentsBy(dx, dy)
        self.updateScrollbars()
            
    def reset_zoom(self):
        self.resetTransform()
        self._zoom_factor = 1.0
        
    def fit_all(self):
        if self.scene() and not self.scene().nodes:
            return
        self.fitInView(self.scene().itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self._zoom_factor = self.transform().m11()

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
    
        painter.fillRect(rect, QColor("#252526"))
    
        grid_size = self.grid_control.grid_size
        opacity = self.grid_control.grid_opacity
    
        if opacity <= 0:
            return
        
        grid_color = QColor(255, 255, 255, int(255 * opacity))
        painter.setPen(QPen(grid_color, 1, Qt.PenStyle.DotLine))
    
        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)
        right = int(rect.right())
        bottom = int(rect.bottom())
    
        for x in range(left, right, grid_size):
            painter.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))
        
        for y in range(top, bottom, grid_size):
            painter.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))
        
class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(False)
        self.resize(800, 600)

        self.container = QWidget(self)
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.setSpacing(0)
        dialog_layout.addWidget(self.container)

        main_layout = QVBoxLayout(self.container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self)
        self.title_bar.title.setText("Graphite Help")
        main_layout.addWidget(self.title_bar)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(20, 20, 20, 20)

        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3f3f3f;
                background: #2d2d2d;
                border-radius: 4px;
            }
            QTabBar::tab {
                background: #252526;
                color: #ffffff;
                padding: 8px 16px;
                border: 1px solid #3f3f3f;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 100px;
            }
            QTabBar::tab:selected {
                background: #2d2d2d;
                border-bottom: 2px solid #2ecc71;
            }
            QTabBar::tab:hover {
                background: #333333;
            }
        """)

        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.addWidget(self._create_section("Basic Navigation", [
            ("Pan View", "Hold Middle Mouse Button and drag", "fa5s.hand-paper"),
            ("Zoom", "Ctrl + Mouse Wheel or use Zoom buttons", "fa5s.search-plus"),
            ("Select Nodes", "Click or drag selection box", "fa5s.mouse-pointer"),
            ("Move Nodes", "Click and drag nodes", "fa5s.arrows-alt"),
            ("Reset View", "Click 'Reset' button to restore default zoom", "fa5s.undo"),
            ("Fit All", "Click 'Fit All' to show all nodes", "fa5s.expand")
        ]))
        tab_widget.addTab(nav_widget, "Navigation")

        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)
        chat_layout.addWidget(self._create_section("Chat Interaction", [
            ("Send Message", "Type message and press Enter or click Send", "fa5s.paper-plane"),
            ("Select Context", "Click a node to set it as current context", "fa5s.comment"),
            ("View History", "Follow node connections to see conversation flow", "fa5s.history"),
            ("Save Chat", "Click 'Save' button to store conversation", "fa5s.save"),
            ("Load Chat", "Use Library to access previous conversations", "fa5s.folder-open")
        ]))
        tab_widget.addTab(chat_widget, "Chat Features")

        org_widget = QWidget()
        org_layout = QVBoxLayout(org_widget)
        org_layout.addWidget(self._create_section("Organization Tools", [
            ("Create Frame", "Ctrl + F with nodes selected", "fa5s.object-group"),
            ("Edit Frame", "Double-click frame title to edit", "fa5s.edit"),
            ("Color Frame", "Click color button in frame header", "fa5s.palette"),
            ("Delete Frame", "Select frame and press Delete", "fa5s.trash-alt"),
            ("Auto-Organize", "Click 'Organize' to arrange nodes", "fa5s.sitemap")
        ]))
        tab_widget.addTab(org_widget, "Organization")

        conn_widget = QWidget()
        conn_layout = QVBoxLayout(conn_widget)
        conn_layout.addWidget(self._create_section("Connection Management", [
            ("Add Pin", "Ctrl + Left Click on connection", "fa5s.dot-circle"),
            ("Remove Pin", "Ctrl + Right Click on pin", "fa5s.times-circle"),
            ("Move Pin", "Click and drag pin", "fa5s.arrows-alt"),
            ("Auto-Route", "Connections auto-adjust to avoid crossings", "fa5s.route")
        ]))
        tab_widget.addTab(conn_widget, "Connections")

        content_layout.addWidget(tab_widget)
        main_layout.addWidget(content_widget)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 0)
        self.container.setGraphicsEffect(shadow)

        self.setStyleSheet("""
            HelpDialog {
                background: transparent;
            }
            QWidget#container {
                background-color: #1e1e1e;
                border-radius: 8px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
        """)

    def _create_section(self, title, items):
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setSpacing(15)

        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #2ecc71;
                font-size: 16px;
                font-weight: bold;
                padding-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)

        for action, description, icon_name in items:
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setSpacing(15)

            icon_label = QLabel()
            icon = qta.icon(icon_name, color='#2ecc71')
            icon_label.setPixmap(icon.pixmap(24, 24))
            item_layout.addWidget(icon_label)

            text_widget = QWidget()
            text_layout = QVBoxLayout(text_widget)
            text_layout.setSpacing(4)

            action_label = QLabel(action)
            action_label.setStyleSheet("color: white; font-weight: bold;")
            text_layout.addWidget(action_label)

            desc_label = QLabel(description)
            desc_label.setStyleSheet("color: #aaaaaa;")
            text_layout.addWidget(desc_label)

            item_layout.addWidget(text_widget)
            item_layout.addStretch()
            layout.addWidget(item_widget)

        layout.addStretch()
        return section

    def moveEvent(self, event):
        screen = QGuiApplication.primaryScreen().geometry()
        window = self.geometry()
        
        if window.left() < screen.left():
            self.move(screen.left(), window.top())
        elif window.right() > screen.right():
            self.move(screen.right() - window.width(), window.top())
            
        if window.top() < screen.top():
            self.move(window.left(), screen.top())
        elif window.bottom() > screen.bottom():
            self.move(window.left(), screen.bottom() - window.height())
            
        super().moveEvent(event)

class ModelSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ollama Model Settings")
        self.setMinimumWidth(500)
        self.setStyleSheet(StyleSheet.DARK_THEME)
        self.worker_thread = None

        layout = QVBoxLayout(self)

        info_label = QLabel(
            "Configure the default model for chat tasks when using the local Ollama provider."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #d4d4d4; margin-bottom: 15px;")
        layout.addWidget(info_label)
        
        form_layout = QFormLayout()
        form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.models = [
            'qwen2.5:7b-instruct', 'llama3:8b', 'phi3:latest', 'mistral:7b',
            'gemma:7b', 'codegemma:7b', 'deepseek-coder:6.7b'
        ]

        self.current_model_label = QLabel(f"<b>{config.CURRENT_MODEL}</b>")
        self.current_model_label.setStyleSheet("color: #2ecc71;")
        form_layout.addRow("Current Active Chat Model:", self.current_model_label)

        self.model_combo = QComboBox()
        self.model_combo.addItems([""] + self.models)
        self.model_combo.currentTextChanged.connect(self.on_combo_change)
        form_layout.addRow("Preset Model:", self.model_combo)

        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("e.g., llama3:latest")
        self.model_input.textChanged.connect(self.on_text_change)
        form_layout.addRow("Custom Model Name:", self.model_input)
        
        layout.addLayout(form_layout)

        self.model_input.setText(config.CURRENT_MODEL)

        self.status_label = QLabel("Enter a model name and click Save to validate and set the model.")
        self.status_label.setWordWrap(True)
        self.status_label.setObjectName("statusLabel")
        self.status_label.setStyleSheet("color: #e67e22; min-height: 40px;")
        layout.addWidget(self.status_label)
        layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def closeEvent(self, event):
        if self.worker_thread and self.worker_thread.isRunning():
            try:
                self.worker_thread.status_update.disconnect(self.handle_status_update)
                self.worker_thread.finished.disconnect(self.handle_worker_finished)
                self.worker_thread.error.disconnect(self.handle_worker_error)
            except RuntimeError:
                pass
        super().closeEvent(event)

    def on_combo_change(self, text):
        if not text:
            return
        self.model_input.textChanged.disconnect(self.on_text_change)
        self.model_input.setText(text)
        self.model_input.textChanged.connect(self.on_text_change)

    def on_text_change(self, text):
        self.model_combo.currentTextChanged.disconnect(self.on_combo_change)
        if text in self.models:
            self.model_combo.setCurrentText(text)
        else:
            self.model_combo.setCurrentIndex(0)
        self.model_combo.currentTextChanged.connect(self.on_combo_change)

    def save_settings(self):
        model_name = self.model_input.text().strip()
        if not model_name:
            self.status_label.setText("Model name cannot be empty.")
            return

        self.save_button.setEnabled(False)
        self.save_button.setText("Validating...")
        
        self.worker_thread = ModelPullWorkerThread(model_name)
        self.worker_thread.status_update.connect(self.handle_status_update)
        self.worker_thread.finished.connect(self.handle_worker_finished)
        self.worker_thread.error.connect(self.handle_worker_error)
        self.worker_thread.start()

    def handle_status_update(self, message):
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #3498db;")

    def handle_worker_finished(self, message, model_name):
        config.set_current_model(model_name)
        self.reset_button()
        QMessageBox.information(self, "Success", message)
        self.accept()

    def handle_worker_error(self, error_message):
        self.status_label.setText(f"Error: {error_message}")
        self.status_label.setStyleSheet("color: #e74c3c;")
        self.reset_button()
        QMessageBox.warning(self, "Model Error", error_message)

    def reset_button(self):
        self.save_button.setEnabled(True)
        self.save_button.setText("Save")

class APISettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("API Endpoint Configuration")
        self.setMinimumWidth(700)
        self.setStyleSheet(StyleSheet.DARK_THEME)

        layout = QVBoxLayout(self)
        
        provider_label = QLabel("API Provider:")
        provider_label.setStyleSheet("color: #ffffff; font-weight: bold;")
        layout.addWidget(provider_label)
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItem(config.API_PROVIDER_OPENAI)
        self.provider_combo.addItem(config.API_PROVIDER_GEMINI)
        self.provider_combo.currentTextChanged.connect(self._on_provider_changed)
        layout.addWidget(self.provider_combo)

        info = QLabel(
            "Configure your API endpoint.\n"
            "OpenAI-Compatible works with: OpenAI, LiteLLM, Anthropic, OpenRouter, etc.\n\n"
            "Choose different models for different tasks."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #d4d4d4; margin-bottom: 15px; margin-top: 10px;")
        layout.addWidget(info)

        self.base_url_label = QLabel("Base URL:")
        self.base_url_label.setStyleSheet("color: #ffffff; font-weight: bold;")
        layout.addWidget(self.base_url_label)

        self.base_url_input = QLineEdit()
        self.base_url_input.setPlaceholderText("https://api.openai.com/v1")
        self.base_url_input.setText(os.getenv('GRAPHITE_API_BASE', 'https://api.openai.com/v1'))
        layout.addWidget(self.base_url_input)

        api_key_label = QLabel("API Key:")
        api_key_label.setStyleSheet("color: #ffffff; font-weight: bold; margin-top: 10px;")
        layout.addWidget(api_key_label)

        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("Enter your API key...")
        self.api_key_input.setText(os.getenv('GRAPHITE_API_KEY', ''))
        layout.addWidget(self.api_key_input)

        self.load_btn = QPushButton("Load Models from Endpoint")
        self.load_btn.clicked.connect(self.load_models_from_endpoint)
        layout.addWidget(self.load_btn)

        models_label = QLabel("Model Selection (per task):")
        models_label.setStyleSheet("color: #ffffff; font-weight: bold; margin-top: 15px;")
        layout.addWidget(models_label)

        self.model_combos = {}

        title_label = QLabel("Title Generation (fast, cheap model):")
        title_label.setStyleSheet("color: #d4d4d4; margin-top: 8px;")
        layout.addWidget(title_label)
        self.title_combo = QComboBox()
        self.title_combo.setPlaceholderText("Select model...")
        self.model_combos[config.TASK_TITLE] = self.title_combo
        layout.addWidget(self.title_combo)

        chat_label = QLabel("Chat, Explain, Takeaways (main model):")
        chat_label.setStyleSheet("color: #d4d4d4; margin-top: 8px;")
        layout.addWidget(chat_label)
        self.chat_combo = QComboBox()
        self.chat_combo.setPlaceholderText("Select model...")
        self.model_combos[config.TASK_CHAT] = self.chat_combo
        layout.addWidget(self.chat_combo)

        chart_label = QLabel("Chart Generation (code-capable model):")
        chart_label.setStyleSheet("color: #d4d4d4; margin-top: 8px;")
        layout.addWidget(chart_label)
        self.chart_combo = QComboBox()
        self.chart_combo.setPlaceholderText("Select model...")
        self.model_combos[config.TASK_CHART] = self.chart_combo
        layout.addWidget(self.chart_combo)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_btn = QPushButton("Save Configuration")
        save_btn.clicked.connect(self.save_configuration)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        
        saved_provider = os.getenv('GRAPHITE_API_PROVIDER', config.API_PROVIDER_OPENAI)
        self.provider_combo.setCurrentText(saved_provider)
        self._on_provider_changed(saved_provider)

    def _populate_models(self, models):
        """Helper function to populate all model dropdowns with a given list."""
        for combo in self.model_combos.values():
            combo.clear()
            combo.addItems(models)
    
    def _on_provider_changed(self, provider_name):
        is_openai = (provider_name == config.API_PROVIDER_OPENAI)
        
        # Show/hide UI elements based on provider
        self.base_url_label.setVisible(is_openai)
        self.base_url_input.setVisible(is_openai)
        self.load_btn.setVisible(is_openai)
        
        if is_openai:
            self.api_key_input.setPlaceholderText("Enter your OpenAI-compatible API key...")
            key = os.getenv('GRAPHITE_OPENAI_API_KEY', '')
            self.api_key_input.setText(key)
            self._populate_models([]) # Clear models, require user to load
        else: # Gemini
            self.api_key_input.setPlaceholderText("Enter your Google Gemini API key...")
            key = os.getenv('GRAPHITE_GEMINI_API_KEY', '')
            self.api_key_input.setText(key)
            # Immediately populate with the static list, no API call needed.
            self._populate_models(api_provider.GEMINI_MODELS_STATIC)

    def load_models_from_endpoint(self):
        provider = self.provider_combo.currentText()
        base_url = self.base_url_input.text().strip()
        api_key = self.api_key_input.text().strip()

        if not base_url:
            QMessageBox.warning(self, "Missing Information", "Please enter the Base URL for the OpenAI-compatible provider.")
            return
        if not api_key:
            QMessageBox.warning(self, "Missing Information", "Please enter the API Key.")
            return

        try:
            api_provider.initialize_api(provider, api_key, base_url)
            models = api_provider.get_available_models()
            self._populate_models(models)

            QMessageBox.information(
                self,
                "Models Loaded",
                f"Successfully loaded {len(models)} models!\n\nNow select a model for each task."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Failed to Load Models",
                f"Could not fetch models from API:\n\n{str(e)}"
            )
            # Graceful fallback for Gemini on API call failure
            if provider == config.API_PROVIDER_GEMINI:
                QMessageBox.warning(
                    self, 
                    "Using Fallback List",
                    "Could not reach the API. Populating with a standard list of Gemini models."
                )
                self._populate_models(api_provider.GEMINI_MODELS_STATIC)


    def save_configuration(self):
        provider = self.provider_combo.currentText()
        base_url = self.base_url_input.text().strip()
        api_key = self.api_key_input.text().strip()

        if not api_key:
            QMessageBox.warning(self, "Missing API Key", "Please enter your API Key.")
            return

        for task_key, combo in self.model_combos.items():
            if not combo.currentText():
                QMessageBox.warning(
                    self,
                    "Missing Model Selection",
                    f"Please select a model for all tasks.\n\nMissing: {task_key}"
                )
                return

        try:
            os.environ['GRAPHITE_API_PROVIDER'] = provider
            if provider == config.API_PROVIDER_OPENAI:
                os.environ['GRAPHITE_OPENAI_API_KEY'] = api_key
                os.environ['GRAPHITE_API_BASE'] = base_url
            else:
                 os.environ['GRAPHITE_GEMINI_API_KEY'] = api_key


            api_provider.initialize_api(provider, api_key, base_url)

            for task_key, combo in self.model_combos.items():
                api_provider.set_task_model(task_key, combo.currentText())

            task_models = api_provider.get_task_models()
            
            QMessageBox.information(
                self,
                "Configuration Saved",
                (f"API configured successfully for {provider}!\n\n"
                 f"Title Model: {task_models[config.TASK_TITLE]}\n"
                 f"Chat Model: {task_models[config.TASK_CHAT]}\n"
                 f"Chart Model: {task_models[config.TASK_CHART]}")
            )
            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Configuration Failed",
                f"Failed to save configuration:\n\n{str(e)}"
            )

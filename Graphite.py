from datetime import datetime
from pathlib import Path
import json
import sys
import os
import api_provider
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qtawesome as qta
import sqlite3
import matplotlib
matplotlib.use('Agg')  # Use Agg backend for off-screen rendering
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

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
            background-color: #2ecc71;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px;
            min-width: 120px;
            font-family: 'Segoe UI', sans-serif;
            font-size: 12px;
            font-weight: bold;
        }
        
        QComboBox:hover {
            background-color: #27ae60;
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
        
        icon_path = Path(__file__).parent / "graphite.png"
        self.setWindowIcon(QIcon(str(icon_path)))

        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 0, 0)

        # Add icon
        icon_label = QLabel()
        icon_pixmap = QPixmap(str(icon_path)).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
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
        if event.button() == Qt.LeftButton:
            self.pressing = True
            self.start_pos = event.globalPos()
            
    def mouseMoveEvent(self, event):
        if self.pressing:
            if self.parent.isMaximized():
                self.parent.showNormal()
            delta = event.globalPos() - self.start_pos
            self.parent.move(self.parent.x() + delta.x(), self.parent.y() + delta.y())
            self.start_pos = event.globalPos()
            
    def mouseReleaseEvent(self, event):
        self.pressing = False
        
class TitleGenerator:
    def __init__(self):
        self.system_prompt = """You are a title generation assistant. Your only job is to create short, 
        2-3 word titles based on conversation content. Rules:
        - ONLY output the title, nothing else
        - Keep it between 2-3 words
        - Use title case
        - Make it descriptive but concise
        - NO punctuation
        - NO explanations
        - NO additional text"""
        
    def generate_title(self, message):
        try:
            messages = [
                {'role': 'system', 'content': self.system_prompt},
                {'role': 'user', 'content': f"Create a 2-3 word title for this message: {message}"}
            ]
            response = api_provider.chat(model='qwen2.5:3b', messages=messages)
            title = response['message']['content'].strip()
            # Clean up title if needed
            title = ' '.join(title.split()[:3])  # Ensure max 3 words
            return title
        except Exception as e:
            return f"Chat {datetime.now().strftime('%Y%m%d_%H%M')}"

class ChatDatabase:
    def __init__(self):
        self.db_path = Path.home() / '.graphite' / 'chats.db'
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
        
    def init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            # Existing chats table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data TEXT NOT NULL
                )
            """)
            
            # Notes table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    position_x REAL NOT NULL,
                    position_y REAL NOT NULL,
                    width REAL NOT NULL,
                    height REAL NOT NULL,
                    color TEXT NOT NULL,
                    header_color TEXT,
                    FOREIGN KEY (chat_id) REFERENCES chats (id) ON DELETE CASCADE
                )
            """)
            
            # Add pins table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    note TEXT,
                    position_x REAL NOT NULL,
                    position_y REAL NOT NULL,
                    FOREIGN KEY (chat_id) REFERENCES chats (id) ON DELETE CASCADE
                )
            """)
            
    def save_pins(self, chat_id, pins_data):
        """Save pins for a chat session"""
        with sqlite3.connect(self.db_path) as conn:
            # First delete existing pins for this chat
            conn.execute("DELETE FROM pins WHERE chat_id = ?", (chat_id,))
            
            # Insert new pins
            for pin_data in pins_data:
                conn.execute("""
                    INSERT INTO pins (
                        chat_id, title, note, position_x, position_y
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    chat_id,
                    pin_data['title'],
                    pin_data['note'],
                    pin_data['position']['x'],
                    pin_data['position']['y']
                ))
                
    def load_pins(self, chat_id):
        """Load pins for a chat session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT title, note, position_x, position_y
                FROM pins WHERE chat_id = ?
            """, (chat_id,))
            
            pins = []
            for row in cursor.fetchall():
                pins.append({
                    'title': row[0],
                    'note': row[1],
                    'position': {'x': row[2], 'y': row[3]}
                })
            return pins
            
    def save_notes(self, chat_id, notes_data):
        with sqlite3.connect(self.db_path) as conn:
            # First delete existing notes for this chat
            conn.execute("DELETE FROM notes WHERE chat_id = ?", (chat_id,))
            
            # Insert new notes
            for note_data in notes_data:
                conn.execute("""
                    INSERT INTO notes (
                        chat_id, content, position_x, position_y,
                        width, height, color, header_color
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    chat_id,
                    note_data['content'],
                    note_data['position']['x'],
                    note_data['position']['y'],
                    note_data['size']['width'],
                    note_data['size']['height'],
                    note_data['color'],
                    note_data.get('header_color')
                ))
                
    def load_notes(self, chat_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT content, position_x, position_y, width, height,
                       color, header_color
                FROM notes WHERE chat_id = ?
            """, (chat_id,))
            
            notes = []
            for row in cursor.fetchall():
                notes.append({
                    'content': row[0],
                    'position': {'x': row[1], 'y': row[2]},
                    'size': {'width': row[3], 'height': row[4]},
                    'color': row[5],
                    'header_color': row[6]
                })
            return notes
            
    def save_chat(self, title, chat_data):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO chats (title, data, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (title, json.dumps(chat_data)))
            return cursor.lastrowid  # Return the ID of the newly inserted chat
            
    def get_latest_chat_id(self):
        """Get the ID of the most recently created chat"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id FROM chats 
                ORDER BY created_at DESC 
                LIMIT 1
            """)
            result = cursor.fetchone()
            return result[0] if result else None
            
    def update_chat(self, chat_id, title, chat_data):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE chats 
                SET title = ?, data = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (title, json.dumps(chat_data), chat_id))
            
    def load_chat(self, chat_id):
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute("""
                SELECT title, data FROM chats WHERE id = ?
            """, (chat_id,)).fetchone()
            if result:
                return {
                    'title': result[0],
                    'data': json.loads(result[1])
                }
            return None
            
    def get_all_chats(self):
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute("""
                SELECT id, title, created_at, updated_at 
                FROM chats 
                ORDER BY updated_at DESC
            """).fetchall()
            
    def delete_chat(self, chat_id):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
            
    def rename_chat(self, chat_id, new_title):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE chats 
                SET title = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (new_title, chat_id))

class ChatSessionManager:
    def __init__(self, window):
        self.window = window
        self.db = ChatDatabase()
        self.title_generator = TitleGenerator()
        self.current_chat_id = None
        
    def serialize_pin(self, pin):
        """Convert a navigation pin to a serializable dictionary"""
        return {
            'title': pin.title,
            'note': pin.note,
            'position': {'x': pin.pos().x(), 'y': pin.pos().y()}
        }
        
    def serialize_pin_layout(self, pin):
        """Convert a pin to a serializable dictionary"""
        return {
            'position': {'x': pin.pos().x(), 'y': pin.pos().y()}
        }
        
    def serialize_connection(self, connection):
        """Convert a connection to a serializable dictionary"""
        return {
            'start_node_index': self.window.chat_view.scene().nodes.index(connection.start_node),
            'end_node_index': self.window.chat_view.scene().nodes.index(connection.end_node),
            'pins': [self.serialize_pin_layout(pin) for pin in connection.pins]
        }
        
    def serialize_node(self, node):
        """Convert a ChatNode to a serializable dictionary"""
        return {
            'text': node.text,
            'is_user': node.is_user,
            'position': {'x': node.pos().x(), 'y': node.pos().y()},
            'conversation_history': node.conversation_history,
            'children_indices': [self.window.chat_view.scene().nodes.index(child) for child in node.children],
            'scroll_value': node.scroll_value
        }
        
    def serialize_frame(self, frame):
        """Convert a Frame to a serializable dictionary"""
        return {
            'nodes': [self.window.chat_view.scene().nodes.index(node) for node in frame.nodes],
            'position': {'x': frame.pos().x(), 'y': frame.pos().y()},
            'note': frame.note,
            'size': {
                'width': frame.rect.width(),
                'height': frame.rect.height()
            },
            'color': frame.color,
            'header_color': frame.header_color
        }
        
    def serialize_note(self, note):
        """Convert a Note to a serializable dictionary"""
        return {
            'content': note.content,
            'position': {'x': note.pos().x(), 'y': note.pos().y()},
            'size': {'width': note.width, 'height': note.height},
            'color': note.color,
            'header_color': note.header_color
        }
        
    def serialize_chart(self, chart):
        """Convert a ChartItem to a serializable dictionary"""
        return {
            'data': chart.data,
            'position': {'x': chart.pos().x(), 'y': chart.pos().y()},
            'size': {'width': chart.width, 'height': chart.height}
        }

    def serialize_current_chat(self):
        """Serialize the current chat session with all elements"""
        scene = self.window.chat_view.scene()
    
        # Get all notes, pins, and charts in the scene
        notes = [item for item in scene.items() if isinstance(item, Note)]
        pins = [item for item in scene.items() if isinstance(item, NavigationPin)]
        charts = [item for item in scene.items() if isinstance(item, ChartItem)]
    
        chat_data = {
            'nodes': [self.serialize_node(node) for node in scene.nodes],
            'connections': [self.serialize_connection(conn) for conn in scene.connections],
            'frames': [self.serialize_frame(frame) for frame in scene.frames],
            'charts': [self.serialize_chart(chart) for chart in charts],  # Add charts
            'view_state': {
                'zoom_factor': self.window.chat_view._zoom_factor,
                'scroll_position': {
                    'x': self.window.chat_view.horizontalScrollBar().value(),
                    'y': self.window.chat_view.verticalScrollBar().value()
                }
            }
        }
    
        # Save chat data first
        if not self.current_chat_id:
            last_message = scene.nodes[-1].text if scene.nodes else "New Chat"
            title = self.title_generator.generate_title(last_message)
            self.current_chat_id = self.db.save_chat(title, chat_data)
        else:
            chat = self.db.load_chat(self.current_chat_id)
            if chat:
                title = chat['title']
                self.db.update_chat(self.current_chat_id, title, chat_data)
            
        # Now save notes and pins separately
        if self.current_chat_id:
            notes_data = [self.serialize_note(note) for note in notes]
            self.db.save_notes(self.current_chat_id, notes_data)
            
            pins_data = [self.serialize_pin(pin) for pin in pins]
            self.db.save_pins(self.current_chat_id, pins_data)
        
        return chat_data

    def deserialize_chart(self, data, scene):
        """Recreate a chart from serialized data"""
        chart = scene.add_chart(data['data'], QPointF(
            data['position']['x'],
            data['position']['y']
        ))
        
        if 'size' in data:
            chart.width = data['size']['width']
            chart.height = data['size']['height']
            chart.generate_chart()  # Regenerate chart with new size
            
        return chart
        
    def deserialize_pin(self, data, connection):
        """Recreate a pin from serialized data"""
        pin = connection.add_pin(QPointF(0, 0))  # Create pin
        pin.setPos(data['position']['x'], data['position']['y'])
        return pin
        
    def deserialize_connection(self, data, scene):
        """Recreate a connection from serialized data"""
        start_node = scene.nodes[data['start_node_index']]
        end_node = scene.nodes[data['end_node_index']]
        
        # Find existing connection or create new one
        connection = None
        for conn in scene.connections:
            if conn.start_node == start_node and conn.end_node == end_node:
                connection = conn
                break
                
        if connection is None:
            connection = ConnectionItem(start_node, end_node)
            scene.addItem(connection)
            scene.connections.append(connection)
        
        # Recreate pins
        for pin_data in data['pins']:
            self.deserialize_pin(pin_data, connection)
            
        return connection
        
    def deserialize_node(self, data, nodes_map=None):
        """Convert serialized data back to ChatNode"""
        scene = self.window.chat_view.scene()
        
        # Create node without parent initially
        node = scene.add_chat_node(
            data['text'],
            is_user=data['is_user'],
            parent_node=None,  # Important: No parent node initially
            conversation_history=data.get('conversation_history', [])
        )
        
        # Remove the automatically created connection since we'll restore them later
        if scene.connections and node.parent_node:
            for conn in scene.connections[:]:  # Create a copy of the list to modify it
                if conn.end_node == node:
                    scene.removeItem(conn)
                    scene.connections.remove(conn)
            node.parent_node = None  # Clear the parent reference
        
        # Restore position and scroll state
        node.setPos(data['position']['x'], data['position']['y'])
        node.scroll_value = data.get('scroll_value', 0)
        node.scrollbar.set_value(node.scroll_value)
        
        # Store in nodes map if provided
        if nodes_map is not None:
            nodes_map[len(scene.nodes) - 1] = node
            
        return node
        
    def deserialize_frame(self, data, scene):
        """Recreate a frame from serialized data"""
        nodes = [scene.nodes[i] for i in data['nodes']]
        frame = Frame(nodes)
        frame.setPos(data['position']['x'], data['position']['y'])
        frame.note = data['note']
        
        if 'color' in data:
            frame.color = data['color']
        if 'header_color' in data:
            frame.header_color = data['header_color']
            
        if 'size' in data:
            frame.rect.setWidth(data['size']['width'])
            frame.rect.setHeight(data['size']['height'])
            
        scene.addItem(frame)
        scene.frames.append(frame)
        frame.setZValue(-2)
        return frame

    def load_chat(self, chat_id):
        """Load a chat session with all elements including pins, charts, and notes"""
        chat = self.db.load_chat(chat_id)
        if not chat:
            return

        # Clear current scene
        scene = self.window.chat_view.scene()
        scene.clear()
        scene.nodes.clear()
        scene.connections.clear()
        scene.frames.clear()
        scene.pins.clear()  # Ensure pins are cleared

        try:
            # First pass: Create all nodes
            nodes_map = {}  # Map to store node indices
            for node_data in chat['data']['nodes']:
                node = self.deserialize_node(node_data, nodes_map)
    
            # Second pass: Set up parent-child relationships
            for i, node_data in enumerate(chat['data']['nodes']):
                if 'children_indices' in node_data:
                    node = nodes_map[i]
                    for child_index in node_data['children_indices']:
                        child_node = nodes_map[child_index]
                        node.children.append(child_node)
                        child_node.parent_node = node

            # Third pass: Create connections WITHOUT pins first
            connections_map = {}  # Store connections for later pin addition
            if 'connections' in chat['data']:
                for i, conn_data in enumerate(chat['data']['connections']):
                    start_node = scene.nodes[conn_data['start_node_index']]
                    end_node = scene.nodes[conn_data['end_node_index']]
        
                    # Check if connection already exists
                    existing_conn = None
                    for conn in scene.connections:
                        if (conn.start_node == start_node and 
                            conn.end_node == end_node):
                            existing_conn = conn
                            break
        
                    if not existing_conn:
                        connection = ConnectionItem(start_node, end_node)
                        scene.addItem(connection)
                        scene.connections.append(connection)
                        connections_map[i] = connection
                    else:
                        connections_map[i] = existing_conn

            # Fourth pass: Add pins to existing connections
            if 'connections' in chat['data']:
                for i, conn_data in enumerate(chat['data']['connections']):
                    if i in connections_map and 'pins' in conn_data:
                        connection = connections_map[i]
                        # Clear any existing pins first
                        for pin in connection.pins[:]:
                            connection.remove_pin(pin)
                        # Add stored pins
                        for pin_data in conn_data['pins']:
                            self.deserialize_pin(pin_data, connection)
                
            # Load frames
            if 'frames' in chat['data']:
                for frame_data in chat['data']['frames']:
                    frame = self.deserialize_frame(frame_data, scene)

            # Load charts
            if 'charts' in chat['data']:
                for chart_data in chat['data']['charts']:
                    self.deserialize_chart(chart_data, scene)

            # Load notes with proper error handling
            notes_data = self.db.load_notes(chat_id)
            for note_data in notes_data:
                try:
                    note = scene.add_note(QPointF(
                        note_data['position']['x'],
                        note_data['position']['y']
                    ))
                    note.content = note_data['content']
                    note.width = note_data['size']['width']
                    note.height = note_data['size']['height']
                    note.color = note_data['color']
                    note.header_color = note_data['header_color']
                except Exception as e:
                    print(f"Error loading note: {str(e)}")
                    continue

            # Clear existing pins in overlay before loading new ones
            if self.window and hasattr(self.window, 'pin_overlay'):
                self.window.pin_overlay.clear_pins()
        
            # Load navigation pins with validation
            pins_data = self.db.load_pins(chat_id)
            for pin_data in pins_data:
                try:
                    pin = scene.add_navigation_pin(QPointF(
                        pin_data['position']['x'],
                        pin_data['position']['y']
                    ))
                    pin.title = pin_data['title']
                    pin.note = pin_data.get('note', '')

                    # Add pin to overlay if window exists
                    if self.window and hasattr(self.window, 'pin_overlay'):
                        self.window.pin_overlay.add_pin_button(pin)
                except Exception as e:
                    print(f"Error loading pin: {str(e)}")
                    continue
    
            # Restore view state
            if 'view_state' in chat['data']:
                view_state = chat['data']['view_state']
                self.window.chat_view._zoom_factor = view_state['zoom_factor']
                self.window.chat_view.setTransform(QTransform().scale(
                    view_state['zoom_factor'], 
                    view_state['zoom_factor']
                ))
                self.window.chat_view.horizontalScrollBar().setValue(
                    view_state['scroll_position']['x']
                )
                self.window.chat_view.verticalScrollBar().setValue(
                    view_state['scroll_position']['y']
                )
    
            # Set current chat ID and update connections
            self.current_chat_id = chat_id
            scene.update_connections()

        except Exception as e:
            print(f"Error loading chat: {str(e)}")
            # Clean up in case of error
            scene.clear()
            scene.nodes.clear()
            scene.connections.clear()
            scene.frames.clear()
            scene.pins.clear()
            if self.window and hasattr(self.window, 'pin_overlay'):
                self.window.pin_overlay.clear_pins()
            raise

        # Return loaded chat data
        return chat
        
    def save_current_chat(self):
        """Save the current chat session"""
        if not self.window.chat_view.scene().nodes:
            return
            
        try:
            chat_data = self.serialize_current_chat()
            
            # If this is a new chat, generate title from last message
            if not self.current_chat_id:
                last_message = self.window.chat_view.scene().nodes[-1].text
                title = self.title_generator.generate_title(last_message)
                self.current_chat_id = self.db.save_chat(title, chat_data)
            else:
                # For existing chats, fetch the current title from the database
                chat = self.db.load_chat(self.current_chat_id)
                if chat:
                    title = chat['title']
                    self.db.update_chat(self.current_chat_id, title, chat_data)
                else:
                    # Fallback if chat not found - create new chat
                    last_message = self.window.chat_view.scene().nodes[-1].text
                    title = self.title_generator.generate_title(last_message)
                    self.current_chat_id = self.db.save_chat(title, chat_data)
                    
        except Exception as e:
            print(f"Error saving chat: {str(e)}")
            raise

class ChatLibraryDialog(QDialog):
    def __init__(self, session_manager, parent=None):
        super().__init__(parent)
        self.session_manager = session_manager
        self.setWindowFlags(
            Qt.Window |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setAttribute(Qt.WA_TranslucentBackground)  # Enable transparent background
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
        screen = QApplication.primaryScreen().geometry()
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

    # The rest of the methods remain unchanged
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
            item.setData(Qt.UserRole, chat_id)
            
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
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.session_manager.current_chat_id = None
            scene = self.session_manager.window.chat_view.scene()
            scene.clear()
            scene.nodes.clear()
            scene.connections.clear()
            scene.frames.clear()
            self.close()
                
    def delete_selected(self):
        current_item = self.chat_list.currentItem()
        if current_item:
            chat_id = current_item.data(Qt.UserRole)
            reply = QMessageBox.question(
                self, 'Delete Chat',
                'Are you sure you want to delete this chat?\nThis action cannot be undone.',
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.session_manager.db.delete_chat(chat_id)
                self.refresh_chat_list()
                
    def rename_selected(self):
        current_item = self.chat_list.currentItem()
        if current_item:
            chat_id = current_item.data(Qt.UserRole)
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
        chat_id = item.data(Qt.UserRole)
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
    valueChanged = pyqtSignal(float)
    
    def __init__(self, orientation=Qt.Vertical, parent=None):
        super().__init__(parent)
        self.orientation = orientation
        self.value = 0
        self.handle_position = 0
        self.handle_pressed = False
        self.hover = False
        
        # Initialize range values
        self.min_val = 0
        self.max_val = 99  # Non-zero default range
        self.page_step = 10  # Default page step
        
        # Set fixed size based on orientation
        if orientation == Qt.Vertical:
            self.setFixedWidth(8)
        else:
            self.setFixedHeight(8)
            
        self.setMouseTracking(True)
        
    def setRange(self, min_val, max_val):
        self.min_val = min_val
        self.max_val = max(min_val + 0.1, max_val)  # Ensure non-zero range
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
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw track
        track_color = QColor("#2A2A2A")
        track_color.setAlpha(100)
        painter.setPen(Qt.NoPen)
        painter.setBrush(track_color)
        
        if self.orientation == Qt.Vertical:
            painter.drawRoundedRect(1, 0, self.width() - 2, self.height(), 4, 4)
        else:
            painter.drawRoundedRect(0, 1, self.width(), self.height() - 2, 4, 4)
            
        # Calculate handle size and position
        range_size = self.max_val - self.min_val
        if range_size <= 0:
            return  # Don't draw handle if range is invalid
            
        visible_ratio = min(1.0, self.page_step / (range_size + self.page_step))
        
        if self.orientation == Qt.Vertical:
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
            
        # Draw handle
        if self.hover:
            handle_color = QColor("#6C8EBF")  # Lighter blue when hovered
        else:
            handle_color = QColor("#5075B3")  # Base blue color
            
        painter.setBrush(handle_color)
        
        if self.orientation == Qt.Vertical:
            painter.drawRoundedRect(1, handle_position, self.width() - 2, handle_size, 3, 3)
        else:
            painter.drawRoundedRect(handle_position, 1, handle_size, self.height() - 2, 3, 3)
            
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.handle_pressed = True
            self.mouse_start_pos = event.pos()
            self.start_value = self.value
            
    def mouseMoveEvent(self, event):
        self.hover = True
        self.update()
        
        if self.handle_pressed:
            if self.orientation == Qt.Vertical:
                delta = event.pos().y() - self.mouse_start_pos.y()
                available_space = max(1, self.height() - 20)  # Prevent division by zero
                delta_ratio = delta / available_space
            else:
                delta = event.pos().x() - self.mouse_start_pos.x()
                available_space = max(1, self.width() - 20)  # Prevent division by zero
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
        
        # Create viewport widget to contain the main widget
        self.viewport = QWidget()
        self.viewport.setLayout(QVBoxLayout())
        self.viewport.layout().setContentsMargins(0, 0, 0, 0)
        self.viewport.layout().addWidget(widget)
        
        # Create scrollbars
        self.v_scrollbar = CustomScrollBar(Qt.Vertical)
        self.h_scrollbar = CustomScrollBar(Qt.Horizontal)
        
        # Add widgets to layout
        layout.addWidget(self.viewport, 0, 0)
        layout.addWidget(self.v_scrollbar, 0, 1)
        layout.addWidget(self.h_scrollbar, 1, 0)
        
        # Connect scrollbar signals
        self.v_scrollbar.valueChanged.connect(self.updateVerticalScroll)
        self.h_scrollbar.valueChanged.connect(self.updateHorizontalScroll)
        
    def updateScrollbars(self):
        # Update vertical scrollbar
        content_height = self.widget.height()
        viewport_height = self.viewport.height()
        
        if content_height > viewport_height:
            self.v_scrollbar.setRange(0, content_height - viewport_height)
            self.v_scrollbar.page_step = viewport_height
            self.v_scrollbar.show()
        else:
            self.v_scrollbar.hide()
            
        # Update horizontal scrollbar
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
        # Make the overlay cover the entire parent widget
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
        
        # Create inner container for the spinner
        self.container = QFrame(self)
        self.container.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                border: 1px solid #3f3f3f;
            }
        """)
        
        # Setup layout for the entire overlay
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Setup layout for the container
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        
        # Loading spinner frames using Unicode blocks
        self.spinner_frames = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
        self.current_frame = 0
        
        # Loading text
        self.loading_label = QLabel("Processing...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.loading_label)
        
        # Position the container in the center
        layout.addStretch()
        layout.addWidget(self.container, 0, Qt.AlignCenter)
        layout.addStretch()
        
        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_spinner)
        self.timer.start(100)  # Update every 100ms
        
        # Start hidden
        self.hide()
    
    def update_spinner(self):
        self.current_frame = (self.current_frame + 1) % len(self.spinner_frames)
        self.loading_label.setText(f"{self.spinner_frames[self.current_frame]} Processing...")
    
    def resizeEvent(self, event):
        # Make sure overlay covers the entire parent widget when resized
        self.setGeometry(self.parent().rect())
        # Calculate container size
        container_width = 200
        container_height = 100
        self.container.setFixedSize(container_width, container_height)
        super().resizeEvent(event)
    
    def showEvent(self, event):
        super().showEvent(event)
        self.raise_()  # Make sure overlay is on top
        self.timer.start()
    
    def hideEvent(self, event):
        super().hideEvent(event)
        self.timer.stop()

class ChatWorkerThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, agent, message, conversation_history):
        super().__init__()
        self.agent = agent
        self.message = message
        self.conversation_history = conversation_history
        
    def run(self):
        try:
            # Use agent's get_response directly
            response = self.agent.get_response(self.message)
            self.finished.emit(response)
        except Exception as e:
            self.error.emit(str(e))

class ChatWorker:
    def __init__(self, system_prompt, conversation_history):
        self.system_prompt = system_prompt
        self.conversation_history = conversation_history
        
    def run(self, user_message):
        try:
            messages = [
                {'role': 'system', 'content': self.system_prompt},
                *self.conversation_history,
                {'role': 'user', 'content': user_message}
            ]
            response = api_provider.chat(model='qwen2.5:7b', messages=messages)
            ai_message = response['message']['content']
            return ai_message
        except Exception as e:
            return f"Error: {str(e)}"

class ChatAgent:
    def __init__(self, name, persona):
        self.name = name or "AI Assistant"
        self.persona = persona or "(default persona)"
        self.system_prompt = f"You are {self.name}. {self.persona}"
        self.conversation_history = []
        
    def get_response(self, user_message):
        chat_worker = ChatWorker(self.system_prompt, self.conversation_history)
        ai_response = chat_worker.run(user_message)
        self.conversation_history.append({'role': 'user', 'content': user_message})
        self.conversation_history.append({'role': 'assistant', 'content': ai_response})
        return ai_response

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
        # Draw scrollbar handle with cute rounded corners
        painter.setRenderHint(QPainter.Antialiasing)
    
        if self.hover:
            color = QColor("#6C8EBF")  # Lighter blue when hovered
        else:
            color = QColor("#5075B3")  # Base blue color
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(color))
    
        # Fix: Convert float values to int for the rectangle dimensions
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
        self.value = 0  # Current scroll position (0-1)
        self.handle = ScrollHandle(self)
        self.update_handle_position()
        
    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)
        
    def paint(self, painter, option, widget=None):
        # Draw scrollbar track
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Semi-transparent track
        track_color = QColor("#2A2A2A")
        track_color.setAlpha(100)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(track_color))
        painter.drawRoundedRect(1, 0, self.width - 2, self.height, 4, 4)
        
    def set_range(self, visible_ratio):
        """Update handle size based on visible ratio"""
        self.handle.height = max(self.handle.min_height, 
                               self.height * visible_ratio)
        self.update_handle_position()
        
    def set_value(self, value):
        """Set scroll position (0-1)"""
        self.value = max(0, min(1, value))
        self.update_handle_position()
        
    def update_handle_position(self):
        """Update handle position based on current value"""
        max_y = self.height - self.handle.height
        self.handle.setPos(1, self.value * max_y)
        
    def mousePressEvent(self, event):
        handle_pos = self.handle.pos().y()
        click_pos = event.pos().y()
        
        # Click on handle - start drag
        if handle_pos <= click_pos <= handle_pos + self.handle.height:
            self.handle.dragging = True
            self.handle.start_drag_pos = click_pos
            self.handle.start_drag_value = self.value
            
        # Click on track - jump to position
        else:
            click_ratio = click_pos / self.height
            self.set_value(click_ratio)
            # Notify parent node
            if isinstance(self.parentItem(), ChatNode):
                self.parentItem().update_scroll_position(self.value)
                
    def mouseMoveEvent(self, event):
        if self.handle.dragging:
            delta = event.pos().y() - self.handle.start_drag_pos
            delta_ratio = delta / (self.height - self.handle.height)
            new_value = self.handle.start_drag_value + delta_ratio
            self.set_value(new_value)
            # Notify parent node
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
        

class ExplainerAgent:
    def __init__(self):
        self.system_prompt = """You are an expert at explaining complex topics in simple terms. Follow these principles in order:

1. Simplification: Break down complex ideas into their most basic form
2. Clarification: Remove any technical jargon or complex terminology
3. Distillation: Extract only the most important concepts
4. Breakdown: Present information in small, digestible chunks
5. Simple Language: Use everyday words and short sentences

Always use:
- Analogies: Connect ideas to everyday experiences
- Metaphors: Compare complex concepts to simple, familiar things

Format your response exactly like this:

Simple Explanation
[2-3 sentence overview using everyday language]

Think of it Like This:
[Add one clear analogy or metaphor that a child would understand]

Key Parts:
• [First simple point]
• [Second simple point]
• [Third point if needed]

Remember: Write as if explaining to a curious 5-year-old. No technical terms, no complex words."""
        
    def clean_text(self, text):
        """Clean special characters and format text"""
        # Remove markdown and special characters
        replacements = [
            ('```', ''),
            ('`', ''),
            ('**', ''),
            ('__', ''),
            ('*', ''),
            ('_', ''),
            ('•', '•'),
            ('→', '->'),
            ('\n\n\n', '\n\n'),
        ]
        
        cleaned = text
        for old, new in replacements:
            cleaned = cleaned.replace(old, new)
            
        # Split into lines and clean each line
        lines = cleaned.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                if line.lstrip().startswith('-'):
                    line = '• ' + line.lstrip('- ')
                cleaned_lines.append(line)
        
        # Rebuild text with proper spacing
        formatted = ''
        in_bullet_list = False
        
        for i, line in enumerate(cleaned_lines):
            # Handle title
            if i == 0 and "Simple Explanation" not in line:
                formatted += "Simple Explanation\n"
                
            # Add line with proper spacing
            if line.startswith('•'):
                if not in_bullet_list:
                    formatted += '\n' if formatted else ''
                in_bullet_list = True
                formatted += line + '\n'
            elif any(section in line for section in ['Think of it Like This:', 'Key Parts:']):
                formatted += '\n' + line + '\n'
            else:
                in_bullet_list = False
                formatted += line + '\n'
        
        return formatted.strip()

    def get_response(self, text):
        messages = [
            {'role': 'system', 'content': self.system_prompt},
            {'role': 'user', 'content': f"Explain this in simple terms: {text}"}
        ]
        response = api_provider.chat(model='qwen2.5:7b', messages=messages)
        raw_response = response['message']['content']

        # Clean and format the response
        formatted_response = self.clean_text(raw_response)
        return formatted_response
        
class KeyTakeawayAgent:
    def __init__(self):
        self.system_prompt = """You are a key takeaway generator. Format your response exactly like this:

Key Takeaway
[1-2 sentence overview]

Main Points:
• [First key point]
• [Second key point]
• [Third key point if needed]

Keep total output under 150 words. Be direct and focused on practical value.
No markdown formatting, no special characters."""
        
    def clean_text(self, text):
        """Clean special characters and format text"""
        # Remove markdown and special characters
        replacements = [
            ('```', ''),  # code blocks
            ('`', ''),    # inline code
            ('**', ''),   # bold
            ('__', ''),   # alternate bold
            ('*', ''),    # italic/bullet
            ('_', ''),    # alternate italic
            ('•', '•'),   # standardize bullets
            ('→', '->'),  # standardize arrows
            ('\n\n\n', '\n\n'),  # remove extra newlines
        ]
        
        cleaned = text
        for old, new in replacements:
            cleaned = cleaned.replace(old, new)
            
        # Split into lines and clean each line
        lines = cleaned.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Ensure bullet points are properly formatted
                if line.lstrip().startswith('-'):
                    line = '• ' + line.lstrip('- ')
                cleaned_lines.append(line)
        
        # Rebuild text with proper spacing
        formatted = ''
        in_bullet_list = False
        
        for i, line in enumerate(cleaned_lines):
            # Handle title
            if i == 0 and "Key Takeaway" not in line:
                formatted += "Key Takeaway\n"
                
            # Add line with proper spacing
            if line.startswith('•'):
                if not in_bullet_list:
                    formatted += '\n' if formatted else ''
                in_bullet_list = True
                formatted += line + '\n'
            elif 'Main Points:' in line:
                formatted += '\n' + line + '\n'
            else:
                in_bullet_list = False
                formatted += line + '\n'
        
        return formatted.strip()

    def get_response(self, text):
        messages = [
            {'role': 'system', 'content': self.system_prompt},
            {'role': 'user', 'content': f"Generate key takeaways from this text: {text}"}
        ]
        response = api_provider.chat(model='qwen2.5:7b', messages=messages)
        raw_response = response['message']['content']

        # Clean and format the response
        formatted_response = self.clean_text(raw_response)
        return formatted_response


class KeyTakeawayWorkerThread(QThread):
    finished = pyqtSignal(str, QPointF)  # Signal includes response and node position
    error = pyqtSignal(str)
    
    def __init__(self, agent, text, node_pos):
        super().__init__()
        self.agent = agent
        self.text = text
        self.node_pos = node_pos
        self._is_running = False
        
    def run(self):
        try:
            self._is_running = True
            response = self.agent.get_response(self.text)
            if self._is_running:  # Check if we should still emit
                self.finished.emit(response, self.node_pos)
        except Exception as e:
            if self._is_running:  # Check if we should still emit
                self.error.emit(str(e))
        finally:
            self._is_running = False
            
    def stop(self):
        """Safely stop the thread"""
        self._is_running = False
        
class ChartDataAgent:
    def __init__(self):
        self.system_prompt = """You are a data extraction agent that converts text into chart data. Always output valid JSON with these structures:

For histograms:
{
    "type": "histogram",
    "title": "Chart Title",
    "values": [numeric values],
    "bins": 10,
    "xAxis": "X Axis Label",
    "yAxis": "Frequency"
}

For bar charts:
{
    "type": "bar",
    "title": "Chart Title",
    "labels": ["label1", "label2", ...],
    "values": [numeric values],
    "xAxis": "X Axis Label",
    "yAxis": "Y Axis Label"
}

For line charts:
{
    "type": "line",
    "title": "Chart Title",
    "labels": ["label1", "label2", ...],
    "values": [numeric values],
    "xAxis": "X Axis Label",
    "yAxis": "Y Axis Label"
}

For pie charts:
{
    "type": "pie",
    "title": "Chart Title",
    "labels": ["label1", "label2", ...],
    "values": [numeric values]
}

For Sankey diagrams:
{
    "type": "sankey",
    "title": "Flow Diagram",
    "data": {
        "nodes": [
            {"name": "Node1"},
            {"name": "Node2"},
            ...
        ],
        "links": [
            {"source": 0, "target": 1, "value": 100},
            {"source": 1, "target": 2, "value": 50},
            ...
        ]
    }
}

IMPORTANT: 
- Always include ALL required fields for the specified chart type
- For non-histogram charts, ALWAYS include 'labels' array matching the length of 'values'
- For Sankey diagrams, ensure proper node indexing and valid links
- All numeric values must be valid numbers
- If you cannot extract proper data, return an error object"""

    def clean_response(self, text):
        """Clean the LLM response to ensure valid JSON"""
        # Remove any markdown code blocks
        text = text.replace("```json", "").replace("```", "").strip()
        
        # Remove any explanatory text before/after JSON
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                text = text[start:end]
        except:
            pass
            
        return text

    def validate_chart_data(self, data, chart_type):
        """Validate chart data based on type and requirements"""
        try:
            if chart_type == 'sankey':
                if not all(key in data for key in ['type', 'title', 'data']):
                    return False, "Missing required fields (type, title, or data)"
                    
                if not all(key in data['data'] for key in ['nodes', 'links']):
                    return False, "Missing nodes or links in data"
                    
                nodes = data['data']['nodes']
                links = data['data']['links']
                
                # Validate nodes
                if not nodes:
                    return False, "No nodes provided"
                    
                node_names = set()
                for i, node in enumerate(nodes):
                    if 'name' not in node:
                        return False, f"Node {i} missing name"
                    if node['name'] in node_names:
                        return False, f"Duplicate node name: {node['name']}"
                    node_names.add(node['name'])
                    
                # Validate links
                if not links:
                    return False, "No links provided"
                    
                node_count = len(nodes)
                for i, link in enumerate(links):
                    if not all(key in link for key in ['source', 'target', 'value']):
                        return False, f"Link {i} missing required fields"
                        
                    if not isinstance(link['value'], (int, float)) or link['value'] <= 0:
                        return False, f"Link {i} has invalid value"
                        
                    if not isinstance(link['source'], int) or not isinstance(link['target'], int):
                        return False, "Link source and target must be node indices"
                        
                    if not (0 <= link['source'] < node_count and 0 <= link['target'] < node_count):
                        return False, f"Link {i} references invalid node index"
                        
                    if link['source'] == link['target']:
                        return False, f"Link {i} has same source and target"
                
            elif chart_type == 'histogram':
                required = ['type', 'title', 'values', 'bins', 'xAxis', 'yAxis']
                if not all(key in data for key in required):
                    return False, f"Missing required fields for histogram: {[key for key in required if key not in data]}"
                if not isinstance(data['bins'], (int, float)):
                    return False, "Bins must be a number"
                    
            elif chart_type in ['bar', 'line']:
                required = ['type', 'title', 'labels', 'values', 'xAxis', 'yAxis']
                if not all(key in data for key in required):
                    return False, f"Missing required fields for {chart_type} chart: {[key for key in required if key not in data]}"
                if not isinstance(data.get('labels', []), list):
                    return False, "Labels must be a list"
                if len(data['labels']) != len(data['values']):
                    return False, "Labels and values must have the same length"
                    
            elif chart_type == 'pie':
                required = ['type', 'title', 'labels', 'values']
                if not all(key in data for key in required):
                    return False, f"Missing required fields for pie chart: {[key for key in required if key not in data]}"
                if not isinstance(data.get('labels', []), list):
                    return False, "Labels must be a list"
                if len(data['labels']) != len(data['values']):
                    return False, "Labels and values must have the same length"
            
            # Validate numeric values for non-Sankey charts
            if chart_type != 'sankey':
                try:
                    if isinstance(data['values'], list):
                        data['values'] = [float(v) for v in data['values']]
                except (ValueError, TypeError):
                    return False, "All values must be numeric"
                    
            return True, None
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def process_sankey_data(self, raw_data):
        """Convert raw Sankey data into proper format"""
        try:
            # Extract unique nodes from flows
            nodes = []
            node_indices = {}
            
            for flow in raw_data:
                for node_name in [flow['source'], flow['target']]:
                    if node_name not in node_indices:
                        node_indices[node_name] = len(nodes)
                        nodes.append({"name": node_name})
                        
            # Create links using node indices
            links = [
                {
                    "source": node_indices[flow['source']],
                    "target": node_indices[flow['target']],
                    "value": flow['value']
                }
                for flow in raw_data
            ]
            
            return {
                "nodes": nodes,
                "links": links
            }
        except Exception as e:
            raise ValueError(f"Error processing Sankey data: {str(e)}")

    def get_response(self, text, chart_type):
        """Extract chart data from text"""
        try:
            messages = [
                {'role': 'system', 'content': self.system_prompt},
                {'role': 'user', 'content': f"Create a {chart_type} chart from this text. Only return the JSON data: {text}"}
            ]

            response = api_provider.chat(model='qwen2.5-coder:14b', messages=messages)
            cleaned_response = self.clean_response(response['message']['content'])
            
            # Parse JSON
            try:
                data = json.loads(cleaned_response)
            except json.JSONDecodeError:
                return json.dumps({"error": "Invalid JSON response from model"})
            
            # Validate data
            is_valid, error_message = self.validate_chart_data(data, chart_type)
            if not is_valid:
                return json.dumps({"error": error_message})
            
            # Special handling for Sankey diagrams
            if chart_type == 'sankey' and 'flows' in data:
                try:
                    data['data'] = self.process_sankey_data(data['flows'])
                    del data['flows']
                except ValueError as e:
                    return json.dumps({"error": str(e)})
            
            # Return validated data
            return json.dumps(data)
            
        except Exception as e:
            return json.dumps({"error": f"Data extraction failed: {str(e)}"})

class ChartWorkerThread(QThread):
    finished = pyqtSignal(str, str)
    error = pyqtSignal(str)
    
    def __init__(self, text, chart_type):
        super().__init__()
        self.agent = ChartDataAgent()
        self.text = text
        self.chart_type = chart_type
        
    def run(self):
        try:
            data = self.agent.get_response(self.text, self.chart_type)
            # Validate data is proper JSON with numbers
            parsed = json.loads(data)
            if 'error' in parsed:
                raise ValueError(parsed['error'])
            self.finished.emit(data, self.chart_type)
        except Exception as e:
            self.error.emit(str(e))
        
class ChatNodeContextMenu(QMenu):
    def __init__(self, node, parent=None):
        super().__init__(parent)
        self.node = node
        self.takeaway_thread = None
        
        # Style the context menu
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
        
        # Copy action
        copy_action = QAction("Copy Text", self)
        copy_action.setIcon(qta.icon('fa5s.copy', color='white'))
        copy_action.triggered.connect(self.copy_text)
        self.addAction(copy_action)
        
        # Key Takeaway action
        takeaway_action = QAction("Generate Key Takeaway", self)
        takeaway_action.setIcon(qta.icon('fa5s.lightbulb', color='white'))
        takeaway_action.triggered.connect(self.generate_takeaway)
        self.addAction(takeaway_action)
        
        self.addSeparator()
        
        
        explainer_action = QAction("Generate Explainer Note", self)
        explainer_action.setIcon(qta.icon('fa5s.question', color='white'))  # Child icon for ELI5
        explainer_action.triggered.connect(self.generate_explainer)
        self.addAction(explainer_action)
        
        chart_menu = QMenu("Generate Chart", self)
        chart_menu.setIcon(qta.icon('fa5s.chart-bar', color='white'))
        chart_menu.setStyleSheet(self.styleSheet())  # Use same styling as parent menu
        
        # Add chart type options
        chart_types = [
            ("Bar Chart", "bar", 'fa5s.chart-bar'),
            ("Line Graph", "line", 'fa5s.chart-line'),
            ("Histogram", "histogram", 'fa5s.chart-area'),
            ("Pie Chart", "pie", 'fa5s.chart-pie'),
            ("Sankey Diagram", "sankey", 'fa5s.project-diagram')  # Added Sankey option
        ]
        
        for title, chart_type, icon in chart_types:
            action = QAction(title, chart_menu)
            action.setIcon(qta.icon(icon, color='white'))
            action.triggered.connect(lambda checked, t=chart_type: self.generate_chart(t))
            chart_menu.addAction(action)
            
        self.addMenu(chart_menu)
        
        self.addSeparator()
        
        # Delete action
        delete_action = QAction("Delete Node", self)
        delete_action.setIcon(qta.icon('fa5s.trash', color='white'))
        delete_action.triggered.connect(self.delete_node)
        self.addAction(delete_action)
        
        # Only show regenerate for AI nodes
        if not node.is_user:
            self.addSeparator()
            
            regenerate_action = QAction("Regenerate Response", self)
            regenerate_action.setIcon(qta.icon('fa5s.sync', color='white'))
            regenerate_action.triggered.connect(self.regenerate_response)
            self.addAction(regenerate_action)
            
        # Connect destroyed signal to cleanup
        self.destroyed.connect(self.cleanup_thread)
    
    def copy_text(self):
        """Copy node text to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.node.text)
    
    def delete_node(self):
        """Delete the node but preserve its children"""
        try:
            scene = self.node.scene()
            if not scene:
                return
            
            # Store references to children and parent before deletion
            children = self.node.children[:]  # Create a copy
            parent_node = self.node.parent_node
            
            # Remove from frames first
            for frame in scene.frames[:]:
                if self.node in frame.nodes:
                    if len(frame.nodes) == 1:
                        scene.removeItem(frame)
                        scene.frames.remove(frame)
                    else:
                        frame.nodes.remove(self.node)
                        frame.updateGeometry()
            
            # Update parent's children list
            if parent_node:
                if self.node in parent_node.children:
                    parent_node.children.remove(self.node)
                
                # Reconnect children to parent
                for child in children:
                    child.parent_node = parent_node
                    if child not in parent_node.children:
                        parent_node.children.append(child)
                    
                    # Create new connection
                    new_conn = ConnectionItem(parent_node, child)
                    scene.addItem(new_conn)
                    scene.connections.append(new_conn)
            else:
                # Handle root node deletion
                for child in children:
                    child.parent_node = None
            
            # Remove all connections involving this node
            for conn in scene.connections[:]:
                if self.node in (conn.start_node, conn.end_node):
                    # Clean up pins first
                    for pin in conn.pins[:]:
                        conn.remove_pin(pin)
                    scene.removeItem(conn)
                    if conn in scene.connections:
                        scene.connections.remove(conn)
            
            # Clear node's own references
            self.node.children.clear()
            self.node.parent_node = None
            
            # Remove from scene
            if self.node in scene.nodes:
                scene.nodes.remove(self.node)
            scene.removeItem(self.node)
            
            # Update connections
            scene.update_connections()
            
            # Reset current node if needed
            if scene.window and scene.window.current_node == self.node:
                scene.window.current_node = None
                scene.window.message_input.setPlaceholderText("Type your message...")
            
        except Exception as e:
            QMessageBox.critical(None, "Error", f"An error occurred while deleting the node: {str(e)}")
    
    def regenerate_response(self):
        """Regenerate the AI response"""
        if not self.node.parent_node:
            return
            
        # Get the parent (user) node's message and original history
        user_message = self.node.parent_node.text
        
        # Get conversation history up to the parent node only
        history = []
        temp_node = self.node.parent_node
        while temp_node:
            if hasattr(temp_node, 'conversation_history'):
                # Only include history up to parent node
                parent_history = [msg for msg in temp_node.conversation_history 
                                if msg['role'] != 'assistant' or 
                                temp_node.parent_node is not None]
                history = parent_history + history
            temp_node = temp_node.parent_node
        
        # Start regeneration
        main_window = self.node.scene().window
        if not main_window:
            return
            
        # Disable input during processing
        main_window.message_input.setEnabled(False)
        main_window.send_button.setEnabled(False)
        main_window.loading_overlay.show()
        
        # Create and start worker thread
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
        """Handle the regenerated AI response"""
        try:
            # Update node text
            self.node.text = new_response
            self.node.raw_text = new_response
            self.node.process_text(new_response)
            self.node._create_layouts()
            
            # Carefully update conversation history
            if self.node.parent_node:
                # Get parent's history
                parent_history = self.node.parent_node.conversation_history[:] if self.node.parent_node.conversation_history else []
                
                # Create new history for this node
                self.node.conversation_history = parent_history + [
                    {'role': 'assistant', 'content': new_response}
                ]
                
                # Update history for all child nodes
                for child in self.node.children:
                    if child.conversation_history:
                        # Find the point where child's history diverges from parent
                        divergence_point = len(parent_history)
                        child.conversation_history = (
                            self.node.conversation_history + 
                            child.conversation_history[divergence_point:]
                        )
            
            # Re-enable input
            main_window = self.node.scene().window
            if main_window:
                main_window.message_input.setEnabled(True)
                main_window.send_button.setEnabled(True)
                main_window.loading_overlay.hide()
                
                # Auto-save after regeneration
                main_window.session_manager.save_current_chat()
            
            # Update display
            self.node.update()
            
        except Exception as e:
            QMessageBox.critical(None, "Error", f"An error occurred while regenerating: {str(e)}")
            
            # Ensure UI is re-enabled
            main_window = self.node.scene().window
            if main_window:
                main_window.message_input.setEnabled(True)
                main_window.send_button.setEnabled(True)
                main_window.loading_overlay.hide()
                
    def cleanup_thread(self):
        """Clean up the thread properly"""
        if self.takeaway_thread is not None:
            self.takeaway_thread.finished.disconnect()
            self.takeaway_thread.error.disconnect()
            self.takeaway_thread.quit()
            self.takeaway_thread.wait()
            self.takeaway_thread = None
            
    def generate_takeaway(self):
            """Trigger takeaway generation in main window"""
            scene = self.node.scene()
            if scene and scene.window:
                scene.window.generate_takeaway(self.node)
                
    def handle_takeaway_response(self, response, node_pos):
        """Handle the key takeaway response and create a note"""
        try:
            scene = self.node.scene()
            if not scene:
                return
                
            # Calculate note position - offset from node
            note_pos = QPointF(node_pos.x() + self.node.width + 50, node_pos.y())
            
            # Create new note
            note = scene.add_note(note_pos)
            note.content = response
            note.color = "#2d2d2d"  # Dark background
            note.header_color = "#2ecc71"  # Green header
            
            # Hide loading overlay
            if scene.window:
                scene.window.loading_overlay.hide()
                
            # Clean up thread after successful execution
            self.cleanup_thread()
                
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error creating takeaway note: {str(e)}")
            if scene and scene.window:
                scene.window.loading_overlay.hide()
                
    def handle_takeaway_error(self, error_message):
        """Handle any errors during takeaway generation"""
        QMessageBox.critical(None, "Error", f"Error generating takeaway: {error_message}")
        scene = self.node.scene()
        if scene and scene.window:
            scene.window.loading_overlay.hide()
            
        # Clean up thread after error
        self.cleanup_thread()
        
    def generate_explainer(self):
        """Trigger explainer generation in main window"""
        scene = self.node.scene()
        if scene and scene.window:
            scene.window.generate_explainer(self.node)
            
    def generate_chart(self, chart_type):
        """Generate chart from node text"""
        scene = self.node.scene()
        if scene and scene.window:
            scene.window.generate_chart(self.node, chart_type)



class ChatNode(QGraphicsItem):
    MAX_HEIGHT = 300
    PADDING = 20
    
    def __init__(self, text, is_user=True, parent=None):
        super().__init__(parent)
        self.text = text  # Keep original text for reference
        self.raw_text = text  # Used for display processing
        self.is_user = is_user
        self.children = []
        self.parent_node = None
        self.conversation_history = []
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.hovered = False
        
        # Size properties
        self.width = 400
        self.height = 100
        self.content_height = 0
        
        # Text layout caching
        self._text_layout = None
        self._cached_text = None
        self._cached_width = None
        
        # Scrolling
        self.scroll_value = 0
        self.scrollbar = ScrollBar(self)
        self.scrollbar.width = 8
        
        # Initialize
        self.blocks = []
        self.process_text(self.raw_text)
        self._create_layouts()

    def boundingRect(self):
        return QRectF(-5, -5, self.width + 10, self.height + 10)

    def _create_layouts(self):
        """Create text layouts and calculate sizes"""
        available_width = self.width - (self.PADDING * 3) - self.scrollbar.width
        y_offset = 0
        
        for block in self.blocks:
            # Create text layout
            layout = QTextLayout(block.content)
            layout.setFont(block.font)
            
            # Set text options
            options = QTextOption()
            options.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
            layout.setTextOption(options)
            
            # Do layout
            layout.beginLayout()
            line_height = 0
            while True:
                line = layout.createLine()
                if not line.isValid():
                    break
                    
                line.setLineWidth(available_width)
                line.setPosition(QPointF(0, line_height))
                line_height += line.height() + 2  # Added small line spacing
                
            layout.endLayout()
            
            # Store layout info
            block.layout = layout
            block.y = y_offset
            block.height = line_height
            
            # Add spacing between blocks
            y_offset += line_height + 10  # Increased block spacing
            
        # Calculate total height
        self.content_height = y_offset + (self.PADDING * 2)
        self.height = min(self.MAX_HEIGHT, self.content_height)
        
        # Update scrollbar
        self.scrollbar.height = self.height
        self.scrollbar.setPos(self.width - self.scrollbar.width - self.PADDING, 0)
        
        visible_ratio = self.height / self.content_height if self.content_height > self.height else 1
        self.scrollbar.set_range(visible_ratio)
        self.scrollbar.setVisible(self.content_height > self.height)
        
        # Update geometry
        self.prepareGeometryChange()
        
    def contextMenuEvent(self, event):
        menu = ChatNodeContextMenu(self)
        menu.exec_(event.screenPos())

    def clean_text(self, text):
        """
        Clean special characters while preserving formatting structure.
        Returns cleaned text with formatting indicators for the layout process.
        """
        if not text:
            return ""

        lines = text.splitlines()
        cleaned_lines = []
        in_code_block = False
        list_indent = 0
    
        for line in lines:
            # Skip empty lines but preserve them
            if not line.strip():
                cleaned_lines.append('')
                continue
            
            # Handle code blocks
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            
            if in_code_block:
                cleaned_lines.append(line)
                continue
            
            cleaned_line = line
        
            # Preserve header level with a marker
            if cleaned_line.lstrip().startswith('#'):
                header_level = len(cleaned_line) - len(cleaned_line.lstrip('#'))
                cleaned_line = f"[h{header_level}]{cleaned_line.lstrip('#').strip()}"
            
            # Convert list markers while preserving structure
            elif cleaned_line.lstrip().startswith(('- ', '* ', '+ ')):
                indent = len(cleaned_line) - len(cleaned_line.lstrip())
                content = cleaned_line.lstrip('- *+').strip()
                cleaned_line = f"[bullet]{' ' * indent}{content}"
            
            # Preserve numbered lists
            elif cleaned_line.lstrip()[0:1].isdigit() and '. ' in cleaned_line.lstrip():
                indent = len(cleaned_line) - len(cleaned_line.lstrip())
                number, content = cleaned_line.lstrip().split('. ', 1)
                cleaned_line = f"[num{number}]{' ' * indent}{content}"
            
            # Remove inline formatting characters
            replacements = [
                ('`', ''),  # code
                ('**', ''), # bold
                ('__', ''), # bold
                ('*', ''),  # italic
                ('_', ''),  # italic
                ('~~', ''), # strikethrough
            ]
        
            for old, new in replacements:
                while old in cleaned_line:
                    # Only replace if there's a matching pair
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
                        
            # Clean HTML tags
            import re
            cleaned_line = re.sub(r'<[^>]+>', '', cleaned_line)
        
            # Preserve line
            cleaned_lines.append(cleaned_line)
    
        return '\n'.join(cleaned_lines)

    def process_text(self, text):
        """
        Convert cleaned text into properly formatted blocks.
        """
        self.blocks = []
        cleaned_text = self.clean_text(text)
        current_text = ""
    
        for line in cleaned_text.split('\n'):
            if not line.strip():
                if current_text:
                    self.blocks.append(TextBlock(current_text.strip()))
                    current_text = ""
                continue
            
            # Process headers
            if line.startswith('[h'):
                if current_text:
                    self.blocks.append(TextBlock(current_text.strip()))
                    current_text = ""
            
                # Extract header content and level
                level = int(line[2])
                content = line[4:].strip()
            
                # Create header block with appropriate font size
                font_size = max(10, 14 - level)  # h1=13, h2=12, h3=11, h4+=10
                font = QFont('Segoe UI', font_size, QFont.Bold)
                self.blocks.append(TextBlock(content, 'header', font))
                continue
            
            # Process bullet points
            elif line.startswith('[bullet]'):
                if current_text:
                    self.blocks.append(TextBlock(current_text.strip()))
                    current_text = ""
                
                content = line[8:].strip()  # Remove [bullet] marker
                font = QFont('Segoe UI', 10)
                self.blocks.append(TextBlock('• ' + content, 'bullet', font))
                continue
            
            # Process numbered lists
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
            
            # Accumulate regular text
            else:
                if current_text:
                    current_text += " " + line.strip()
                else:
                    current_text = line.strip()
    
        # Add any remaining text
        if current_text:
            self.blocks.append(TextBlock(current_text.strip()))

    

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
    
        # Draw shadow
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 30))
        shadow_path = QPainterPath()
        shadow_path.addRoundedRect(3, 3, self.width, self.height, 10, 10)
        painter.drawPath(shadow_path)
    
        # Main node body
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
    
        # Set up clipping for text
        content_rect = QRectF(
            self.PADDING, 
            self.PADDING, 
            self.width - (self.PADDING * 3) - self.scrollbar.width, 
            self.height - (self.PADDING * 2)
        )
        painter.setClipRect(content_rect)
    
        # Calculate scroll offset
        scroll_offset = (self.content_height - self.height) * self.scroll_value if self.content_height > self.height else 0
    
        # Draw text content
        painter.save()
        painter.translate(self.PADDING, self.PADDING - scroll_offset)
    
        for block in self.blocks:
            if block.type == 'header':
                # For headers, use green color for AI nodes, white for user nodes
                if self.is_user:
                    painter.setPen(QPen(QColor("#ffffff")))
                else:
                    painter.setPen(QPen(QColor("#2ecc71")))
            else:
                # For regular text, always use white
                painter.setPen(QPen(QColor("#ffffff")))
            
            painter.setFont(block.font)
            block.layout.draw(painter, QPointF(0, block.y))
    
        painter.restore()

    def wheelEvent(self, event):
        if self.content_height <= self.height:
            return
            
        delta = event.delta() / 120
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
        if event.button() == Qt.LeftButton:
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
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            self.scene().update_connections()
        return super().itemChange(change, value)

class Pin(QGraphicsItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)  # Important for tracking position changes
        self.setAcceptHoverEvents(True)
        self.hover = False
        self.radius = 5
        self._dragging = False
        
    def boundingRect(self):
        return QRectF(-self.radius, -self.radius, 
                     self.radius * 2, self.radius * 2)
        
    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        
        if self.isSelected():
            color = QColor("#2ecc71")  # Green when selected
        elif self.hover:
            color = QColor("#3498db")  # Blue when hovered
        else:
            color = QColor("#ffffff")  # White by default
            
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
        if event.button() == Qt.RightButton and event.modifiers() & Qt.ControlModifier:
            # Get parent connection
            parent_connection = self.parentItem()
            if isinstance(parent_connection, ConnectionItem):
                # Remove this pin from the parent connection
                parent_connection.remove_pin(self)
                # Remove the pin from the scene
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
        if change == QGraphicsItem.ItemPositionChange and self._dragging:
            # Snap to grid when moving
            grid_size = 5
            new_pos = QPointF(
                round(value.x() / grid_size) * grid_size,
                round(value.y() / grid_size) * grid_size
            )
            # Update parent connection path immediately during drag
            if isinstance(self.parentItem(), ConnectionItem):
                self.parentItem().prepareGeometryChange()
                self.parentItem().update_path()
            return new_pos
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
        
        # Animation properties
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
        
        # Add hover tracking
        self.setAcceptHoverEvents(True)
        
        # Force initial path update and make visible
        start_pos = self.start_node.scenePos()
        end_pos = self.end_node.scenePos()
        
        # Create initial path
        start_x = start_pos.x() + self.start_node.width
        start_y = start_pos.y() + (self.start_node.height / 2)
        end_x = end_pos.x()
        end_y = end_pos.y() + (self.end_node.height / 2)
        
        self.path = QPainterPath()
        self.path.moveTo(start_x, start_y)
        
        # Calculate control points for smooth curve
        distance = min((end_x - start_x) / 2, 200)
        ctrl1_x = start_x + distance
        ctrl1_y = start_y
        ctrl2_x = end_x - distance
        ctrl2_y = end_y
        
        self.path.cubicTo(ctrl1_x, ctrl1_y, ctrl2_x, ctrl2_y, end_x, end_y)
        self.update()
        
        # Enhanced caching for better performance
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

    def boundingRect(self):
        """Enhanced bounding rect for better hit detection"""
        if not self.path:
            return QRectF()
            
        # Increase the bounding rect padding
        padding = self.click_tolerance * 2
        return self.path.boundingRect().adjusted(-padding, -padding,
                                               padding, padding)

    def create_hover_path(self):
        """Create a wider hover detection path"""
        if not self.path:
            return None
            
        stroke = QPainterPathStroker()
        # Double the hover detection area
        stroke.setWidth(self.click_tolerance * 2)
        stroke.setCapStyle(Qt.RoundCap)
        stroke.setJoinStyle(Qt.RoundJoin)
        return stroke.createStroke(self.path)

    def contains_point(self, point):
        """More accurate and forgiving point containment test"""
        if not self.hover_path:
            self.hover_path = self.create_hover_path()
            
        if not self.hover_path:
            return False
            
        # Create a small rect around the point for more forgiving hit testing
        point_rect = QRectF(
            point.x() - self.click_tolerance/2,
            point.y() - self.click_tolerance/2,
            self.click_tolerance,
            self.click_tolerance
        )
        
        return self.hover_path.intersects(point_rect)

    def get_node_scene_pos(self, node):
        """Get the actual scene position of a node, accounting for frames"""
        return node.scenePos()
        
    def add_pin(self, scene_pos):
        """Add a new pin with proper coordinate transformation"""
        pin = Pin(self)
        # Convert scene position to connection's coordinate space
        local_pos = self.mapFromScene(scene_pos)
        pin.setPos(local_pos)
        self.pins.append(pin)
        self.update_path()
        return pin
        
    def remove_pin(self, pin):
        """Safely remove a pin"""
        if pin in self.pins:
            self.pins.remove(pin)
            if pin.scene():
                pin.scene().removeItem(pin)
            self.update_path()
                
    def clear(self):
        """Override clear to properly clean up pins"""
        # Clear pin overlay first
        if self.window and hasattr(self.window, 'pin_overlay'):
            self.window.pin_overlay.clear_pins()
        
        # Clear pins list
        self.pins.clear()
        
        # Clear other items
        self.nodes.clear()
        self.connections.clear()
        self.frames.clear()
        
        # Call parent clear
        super().clear()

    def update_path(self):
        """Update connection path with improved coordinate handling"""
        if not (self.start_node and self.end_node):
            return
            
        # Store current path for comparison
        old_path = self.path
        
        # Get scene positions of nodes, handling frame transformations
        start_scene_pos = self.start_node.mapToScene(QPointF(self.start_node.width, self.start_node.height/2))
        end_scene_pos = self.end_node.mapToScene(QPointF(0, self.end_node.height/2))
        
        # Convert scene positions to connection's coordinate space
        start_pos = self.mapFromScene(start_scene_pos)
        end_pos = self.mapFromScene(end_scene_pos)
        
        # Create new path
        new_path = QPainterPath()
        new_path.moveTo(start_pos)
        
        if self.pins:
            # Convert pin positions to connection's coordinate space
            sorted_pins = sorted(self.pins, key=lambda p: p.scenePos().x())
            points = [start_pos]
            
            # Add pin points
            for pin in sorted_pins:
                points.append(pin.pos())
            points.append(end_pos)
            
            # Create smooth path through points
            for i in range(len(points) - 1):
                current_point = points[i]
                next_point = points[i + 1]
                
                # Calculate control points for smooth curve
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
            # Direct curve without pins
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
        
        # Update path if changed
        if new_path != old_path:
            self.path = new_path
            self.hover_path = None
            self.prepareGeometryChange()
            self.update()

    def startArrowAnimation(self):
        """Start the arrow animation after hover delay"""
        if not self.is_animating:
            self.is_animating = True
            self.arrows = []
            path_length = self.path.length()
            
            # Initialize arrows along the entire path
            current_distance = 0
            while current_distance < path_length:
                self.arrows.append({
                    'pos': current_distance / path_length,
                    'opacity': 1.0,
                    'distance': current_distance
                })
                current_distance += self.arrow_spacing
            
            self.animation_timer.start(16)  # ~60 FPS
            self.update()

    def stopArrowAnimation(self):
        """Stop the arrow animation immediately"""
        self.is_animating = False
        self.animation_timer.stop()
        self.arrows.clear()
        self.update()

    def updateArrows(self):
        """Update arrow positions with continuous spawning"""
        if not self.is_animating:
            return
            
        path_length = self.path.length()
        arrows_to_remove = []
        
        # Update existing arrows
        for arrow in self.arrows:
            arrow['distance'] += self.animation_speed
            arrow['pos'] = arrow['distance'] / path_length
            
            # Remove arrows that have completed their journey
            if arrow['pos'] >= 1:
                arrows_to_remove.append(arrow)
                
        # Remove completed arrows
        for arrow in arrows_to_remove:
            self.arrows.remove(arrow)
            
        # Add new arrows at the start
        if not self.arrows or self.arrows[0]['distance'] >= self.arrow_spacing:
            self.arrows.insert(0, {
                'pos': 0,
                'opacity': 1.0,
                'distance': 0
            })
        
        self.update()

    def drawArrow(self, painter, pos, opacity):
        """Draw a single arrow at the given path position with color transition"""
        if pos < 0 or pos > 1:
            return
            
        # Get position and angle at current point
        point = self.path.pointAtPercent(pos)
        angle = self.path.angleAtPercent(pos)
        
        # Create arrow shape
        arrow = QPainterPath()
        arrow.moveTo(-self.arrow_size, -self.arrow_size/2)
        arrow.lineTo(0, 0)
        arrow.lineTo(-self.arrow_size, self.arrow_size/2)
        
        painter.save()
        
        painter.translate(point)
        painter.rotate(-angle)
        
        # Color transition from blue to green based on position
        start_color = QColor("#3498db")  # Blue
        end_color = QColor("#2ecc71")    # Green
        
        # Calculate interpolated color based on position
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
        """Return a more precise shape for collision detection"""
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
            
        painter.setRenderHint(QPainter.Antialiasing)
        
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
        pen = QPen(QBrush(gradient), width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.drawPath(self.path)
        
        if self.is_animating:
            for arrow in self.arrows:
                self.drawArrow(painter, arrow['pos'], arrow['opacity'])

    def hoverEnterEvent(self, event):
        """Enhanced hover detection with 1 second delay"""
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
                self.hover_start_timer.start(1000)  # 1 second delay
                self.update()
        super().hoverEnterEvent(event)

    def hoverMoveEvent(self, event):
        """Track hover movement"""
        if self.contains_point(event.pos()):
            if not self.hover:
                self.hover = True
                self.hover_start_timer.start(1000)  # 1 second delay
                self.update()
        else:
            if self.hover:
                self.hover = False
                self.hover_start_timer.stop()
                self.stopArrowAnimation()
                self.update()
        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event):
        """Handle hover leave immediately"""
        self.hover = False
        self.hover_start_timer.stop()
        # Ensure animation stops cleanly
        if self.is_animating:
            self.stopArrowAnimation()
        self.update()
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse press with proper coordinate transformation"""
        if self.contains_point(event.pos()):
            if event.button() == Qt.LeftButton and event.modifiers() & Qt.ControlModifier:
                # Convert event position to scene coordinates for pin placement
                scene_pos = self.mapToScene(event.pos())
                self.add_pin(scene_pos)
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()

    def focusOutEvent(self, event):
        """Handle focus loss"""
        self.is_selected = False
        self.update()
        super().focusOutEvent(event)
            
class ColorPickerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.Window |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Popup
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(False)
        self.resize(200, 180)  # Made taller for two rows
        
        # Main container layout
        self.container = QWidget(self)
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.setSpacing(0)
        dialog_layout.addWidget(self.container)
        
        # Container layout
        main_layout = QVBoxLayout(self.container)
        main_layout.setSpacing(15)  # Increased spacing between rows
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Labels for the two sections
        full_label = QLabel("Frame Colors")
        full_label.setStyleSheet("color: #ffffff; font-size: 10px;")
        main_layout.addWidget(full_label)
        
        # Full frame colors grid
        full_color_layout = QGridLayout()
        full_color_layout.setSpacing(8)
        
        # Add full frame color buttons
        col = 0
        full_colors = [c for c in FRAME_COLORS.items() if c[1]["type"] == "full"]
        for color_name, color_data in full_colors:
            btn = QPushButton()
            btn.setFixedSize(40, 40)
            btn.setToolTip(color_name)
            btn.setCursor(Qt.PointingHandCursor)
            
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
        
        # Header label
        header_label = QLabel("Header Colors Only")
        header_label.setStyleSheet("color: #ffffff; font-size: 10px;")
        main_layout.addWidget(header_label)
        
        # Header colors grid
        header_color_layout = QGridLayout()
        header_color_layout.setSpacing(8)
        
        # Add header-only color buttons
        col = 0
        header_colors = [c for c in FRAME_COLORS.items() if c[1]["type"] == "header"]
        for color_name, color_data in header_colors:
            btn = QPushButton()
            btn.setFixedSize(40, 40)
            btn.setToolTip(color_name)
            btn.setCursor(Qt.PointingHandCursor)
            
            # Create gradient preview for header-only buttons
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
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 0)
        self.container.setGraphicsEffect(shadow)
        
        # Set proper styling for transparent background
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
        """Close the dialog when it loses focus"""
        self.close()
        super().focusOutEvent(event)
    


class Frame(QGraphicsItem):
    PADDING = 30
    HEADER_HEIGHT = 40
    HANDLE_SIZE = 8
    
    def __init__(self, nodes, parent=None):
        super().__init__(parent)
        # Initialize nodes and flags
        self.nodes = nodes
        self.note = "Add note..."
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        
        self.lock_icon = qta.icon('fa.lock', color='#ffffff')
        self.unlock_icon = qta.icon('fa.unlock-alt', color='#ffffff')
        self.lock_icon_hover = qta.icon('fa.lock', color='#3498db')
        self.unlock_icon_hover = qta.icon('fa.unlock-alt', color='#2DBB6A')
        
        # Initialize attributes
        self.is_locked = True  # Default to locked state
        self.rect = QRectF()
        self.color = "#2d2d2d"  # Default frame color
        self.header_color = None 
        
        # Button states
        self.lock_button_rect = QRectF(0, 0, 24, 24)
        self.lock_button_hovered = False
        self.color_button_rect = QRectF(0, 0, 24, 24)
        self.color_button_hovered = False
        
        # Visual states
        self.hovered = False
        self.editing = False
        self.edit_text = ""
        self.cursor_pos = 0
        self.cursor_visible = True
        
        # Resize handles
        self.handles = ['nw', 'n', 'ne', 'e', 'se', 's', 'sw', 'w']
        self.handle_cursors = {
            'nw': Qt.SizeFDiagCursor,
            'se': Qt.SizeFDiagCursor,
            'ne': Qt.SizeBDiagCursor,
            'sw': Qt.SizeBDiagCursor,
            'n': Qt.SizeVerCursor,
            's': Qt.SizeVerCursor,
            'e': Qt.SizeHorCursor,
            'w': Qt.SizeHorCursor
        }
        self.handle_rects = {}
        self.resize_handle = None
        self.resizing = False
        self.resize_start_rect = None
        self.resize_start_pos = None
        
        # Store original positions before parenting
        self.original_positions = {node: node.scenePos() for node in nodes}
        
        # Animation setup
        self.outline_animation = QVariantAnimation()
        self.outline_animation.setDuration(2000)  # 2 seconds per cycle
        self.outline_animation.setStartValue(0.0)
        self.outline_animation.setEndValue(1.0)
        self.outline_animation.setLoopCount(-1)  # Infinite loop
        self.outline_animation.valueChanged.connect(self.update)
        
        # Initialize geometry
        self.updateGeometry()
        
        # Setup cursor blink timer
        self.cursor_timer = QTimer()
        self.cursor_timer.timeout.connect(self.toggle_cursor)
        self.cursor_timer.setInterval(500)
        
        # Lock nodes initially
        self._update_nodes_movable()
        
    def calculate_minimum_size(self):
        """Calculate the minimum size required to contain all nodes"""
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
        """Calculate handle positions with larger hit areas"""
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
        """Return the resize handle at given position using larger hit areas"""
        for handle, rects in self.get_handle_rects().items():
            if rects['hit'].contains(pos):
                return handle
        return None

    def updateGeometry(self):
        """Calculate frame bounds without forcing node centering"""
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
        """Update movable state of contained nodes based on lock state"""
        for node in self.nodes:
            scene_pos = node.scenePos()
            node.setParentItem(self)
            
            if not self.is_locked:
                node.setPos(self.mapFromScene(scene_pos))
            
            node.setFlag(QGraphicsItem.ItemIsMovable, not self.is_locked)
            node.setFlag(QGraphicsItem.ItemIsSelectable, not self.is_locked)

    def boundingRect(self):
        return self.rect

    def toggle_lock(self):
        """Toggle the lock state of the frame"""
        self.is_locked = not self.is_locked
    
        if not self.is_locked:
            self.outline_animation.start()
        else:
            self.outline_animation.stop()
    
        # ONLY update movable state of contained nodes
        for node in self.nodes:
            node.setFlag(QGraphicsItem.ItemIsMovable, not self.is_locked)
            node.setFlag(QGraphicsItem.ItemIsSelectable, not self.is_locked)

    def toggle_cursor(self):
        """Toggle cursor visibility for blinking effect"""
        self.cursor_visible = not self.cursor_visible
        self.update()

    def mouseDoubleClickEvent(self, event):
        if self.rect.top() <= event.pos().y() <= self.rect.top() + self.HEADER_HEIGHT:
            self.editing = True
            self.edit_text = self.note
            self.cursor_pos = len(self.edit_text)
            self.cursor_timer.start()
            self.setFlag(QGraphicsItem.ItemIsFocusable)
            self.setFocus()
            self.update()
        else:
            super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse press for resizing and other interactions"""
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
        """Handle resizing and movement with proper connection updates"""
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
    
            # Calculate minimum dimensions needed
            min_width = (max_x - min_x) + (self.PADDING * 2)
            min_height = (max_y - min_y) + (self.PADDING * 2) + self.HEADER_HEIGHT
    
            # Apply grid snapping
            grid_size = 10
            delta.setX(round(delta.x() / grid_size) * grid_size)
            delta.setY(round(delta.y() / grid_size) * grid_size)
    
            # Update rectangle based on handle being dragged
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
    
            # Update frame size and connections
            if new_rect != self.rect:
                self.prepareGeometryChange()
                self.rect = new_rect
            
                # Update connections for all nodes in the frame
                if self.scene():
                    scene_nodes = set()  # Track nodes to prevent duplicates
                    for node in self.nodes:
                        if node not in scene_nodes:
                            scene_nodes.add(node)
                            # Update connections where this node is start or end
                            for conn in self.scene().connections:
                                if conn.start_node == node or conn.end_node == node:
                                    # Update connection path
                                    conn.update_path()
                                    # Update pin positions
                                    for pin in conn.pins:
                                        scene_pos = pin.mapToScene(QPointF(0, 0))
                                        pin.setPos(conn.mapFromScene(scene_pos))
    
            event.accept()
    
        elif self.is_locked:
            # Store old scene positions of all nodes and pins
            old_positions = {}
            pin_positions = {}
            for node in self.nodes:
                old_positions[node] = node.scenePos()
                # Store positions of pins in connections involving this node
                for conn in self.scene().connections:
                    if conn.start_node == node or conn.end_node == node:
                        for pin in conn.pins:
                            pin_positions[pin] = pin.mapToScene(QPointF(0, 0))
    
            # Move the frame
            super().mouseMoveEvent(event)
        
            # Calculate position delta
            delta = event.pos() - self.resize_start_pos if self.resize_start_pos else QPointF(0, 0)
        
            # Update all nodes and their connections
            if self.scene():
                for node in self.nodes:
                    # Update node's scene position if needed
                    new_scene_pos = node.mapToScene(QPointF(0, 0))
                    if new_scene_pos != old_positions[node]:
                        # Update all connections involving this node
                        for conn in self.scene().connections:
                            if conn.start_node == node or conn.end_node == node:
                                conn.update_path()
                            
                                # Update pin positions relative to new connection position
                                for pin in conn.pins:
                                    if pin in pin_positions:
                                        old_scene_pos = pin_positions[pin]
                                        # Calculate new position maintaining relative position
                                        new_scene_pos = old_scene_pos + delta
                                        pin.setPos(conn.mapFromScene(new_scene_pos))

        else:
            # Handle regular mouse move when frame is unlocked
            super().mouseMoveEvent(event)
            # Update connections for individual node movement
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
        """Update all connections for nodes in this frame"""
        if not self.scene():
            return
            
        # Update connections for all nodes in the frame
        for node in self.nodes:
            # Update connections where this node is the start node
            for conn in self.scene().connections:
                if conn.start_node == node or conn.end_node == node:
                    conn.update_path()
                    # Update pin positions relative to new frame position
                    for pin in conn.pins:
                        # Convert pin position to scene coordinates
                        scene_pos = pin.mapToScene(QPointF(0, 0))
                        # Update pin position relative to connection
                        pin.setPos(conn.mapFromScene(scene_pos))

    def mouseReleaseEvent(self, event):
        """Handle end of resize or move operation"""
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
        """Update cursor based on hover position"""
        if self.isSelected():
            handle = self.handle_at(event.pos())
            if handle:
                self.setCursor(self.handle_cursors[handle])
                return
                
        # Update hover states
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
        
        # Position dialog near the frame
        frame_pos = self.mapToScene(self.color_button_rect.topRight())
        view_pos = self.scene().views()[0].mapFromScene(frame_pos)
        global_pos = self.scene().views()[0].mapToGlobal(view_pos)
        
        dialog.move(global_pos.x() + 10, global_pos.y())
        
        if dialog.exec_() == QDialog.Accepted:
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
            
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.finishEditing()
        elif event.key() == Qt.Key_Escape:
            self.editing = False
            self.cursor_timer.stop()
            self.update()
        elif event.key() == Qt.Key_Backspace:
            if self.cursor_pos > 0:
                self.edit_text = self.edit_text[:self.cursor_pos-1] + self.edit_text[self.cursor_pos:]
                self.cursor_pos -= 1
                self.update()
        elif event.key() == Qt.Key_Delete:
            if self.cursor_pos < len(self.edit_text):
                self.edit_text = self.edit_text[:self.cursor_pos] + self.edit_text[self.cursor_pos+1:]
                self.update()
        elif event.key() == Qt.Key_Left:
            self.cursor_pos = max(0, self.cursor_pos - 1)
            self.update()
        elif event.key() == Qt.Key_Right:
            self.cursor_pos = min(len(self.edit_text), self.cursor_pos + 1)
            self.update()
        elif event.key() == Qt.Key_Home:
            self.cursor_pos = 0
            self.update()
        elif event.key() == Qt.Key_End:
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
        painter.setRenderHint(QPainter.Antialiasing)
    
        # Draw frame background with custom color
        gradient = QLinearGradient(
            self.rect.topLeft(),
            self.rect.bottomLeft()
        )
        base_color = QColor(self.color)
        gradient.setColorAt(0, base_color)
        gradient.setColorAt(1, base_color.darker(120))
    
        # Frame outline
        if self.isSelected():
            outline_color = QColor("#2ecc71")
        elif self.hovered:
            outline_color = QColor("#3498db")
        else:
            outline_color = QColor("#555555")
        
        # Draw rounded rectangle for frame
        path = QPainterPath()
        path.addRoundedRect(self.rect, 10, 10)
    
        painter.setPen(QPen(outline_color, 2))
        painter.setBrush(QBrush(gradient))
        painter.drawPath(path)
    
        # Draw animated outline for unlocked state
        if not self.is_locked:
            # Create gradient for animated outline
            outline_path = QPainterPath()
            outline_path.addRoundedRect(self.rect.adjusted(-2, -2, 2, 2), 10, 10)
            
            gradient = QConicalGradient(self.rect.center(), 
                                      360 * self.outline_animation.currentValue())
            
            # Define gradient colors
            blue = QColor("#3498db")
            green = QColor("#2ecc71")
            
            # Create smooth transition between colors
            gradient.setColorAt(0.0, blue)
            gradient.setColorAt(0.5, green)
            gradient.setColorAt(1.0, blue)
            
            # Draw animated outline
            painter.setPen(QPen(QBrush(gradient), 3))
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(outline_path)
    
        # Draw header section
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
    
        # Draw lock button
        self.lock_button_rect = QRectF(
            self.rect.right() - 68,
            self.rect.top() + 8,
            24,
            24
        )
    
        # Draw circular lock button background
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
    
        # Draw color picker button
        self.color_button_rect = QRectF(
            self.rect.right() - 34,
            self.rect.top() + 8,
            24,
            24
        )
    
        # Draw circular color button
        painter.setPen(QPen(QColor("#555555")))
        if self.color_button_hovered:
            painter.setPen(QPen(QColor("#ffffff")))
    
        painter.setBrush(QBrush(QColor(self.header_color if self.header_color else self.color)))
        painter.drawEllipse(self.color_button_rect)
    
        # Draw palette icon
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
    
        # Draw text
        painter.setPen(QPen(QColor("#ffffff")))
        font = QFont("Segoe UI", 10)
        painter.setFont(font)
        text_rect = header_rect.adjusted(10, 0, -78, 0)
    
        if self.editing:
            text = self.edit_text
            cursor_x = painter.fontMetrics().width(text[:self.cursor_pos])
            painter.drawText(text_rect, Qt.AlignVCenter, text)
        
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
            painter.drawText(text_rect, Qt.AlignVCenter, self.note)
            
        # Draw resize handles when selected
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
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        
        # Size and state
        self.width = self.DEFAULT_WIDTH
        self.height = self.DEFAULT_HEIGHT
        self.color = "#2d2d2d"  # Default note color
        self.header_color = None
        
        # Editing state
        self.editing = False
        self.edit_text = ""
        self.cursor_pos = 0
        self.cursor_visible = True
        
        # Selection state
        self.selection_start = 0
        self.selection_end = 0
        self.selecting = False
        self.mouse_drag_start_pos = None
        
        # Visual state
        self.hovered = False
        self.resize_handle_hovered = False
        self.resizing = False
        self.color_button_hovered = False
        
        # Cursor blink timer
        self.cursor_timer = QTimer()
        self.cursor_timer.timeout.connect(self.toggle_cursor)
        self.cursor_timer.setInterval(500)
        
        # Initialize color button rect
        self.color_button_rect = QRectF(0, 0, 24, 24)

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)
        
    def toggle_cursor(self):
        self.cursor_visible = not self.cursor_visible
        self.update()

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw shadow
        shadow_path = QPainterPath()
        shadow_path.addRoundedRect(3, 3, self.width, self.height, 10, 10)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 30))
        painter.drawPath(shadow_path)
        
        # Main background
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
        
        # Header section
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
        
        # Draw color picker button
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
        
        # Draw palette icon
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
            
        # Draw content
        painter.setPen(QPen(QColor("#ffffff")))
        font = QFont("Segoe UI", 10)
        painter.setFont(font)
        
        # Content area for text
        content_rect = QRectF(
            self.PADDING,
            self.HEADER_HEIGHT + 10,
            self.width - (self.PADDING * 2),
            self.height - self.HEADER_HEIGHT - (self.PADDING * 2)
        )
        
        if self.editing:
            text = self.edit_text
            metrics = painter.fontMetrics()
            
            # Create text layout for proper word wrapping
            
            layout = QTextLayout(text, font)
            text_option = QTextOption()
            text_option.setAlignment(Qt.AlignLeft)
            text_option.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
            layout.setTextOption(text_option)
            
            # Do the layout
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
                
                # Store line information
                text_lines.append({
                    'line': line,
                    'y': height,
                    'text': text[line.textStart():line.textStart() + line.textLength()]
                })
                
                # Find cursor position
                if not cursor_found and line.textStart() <= self.cursor_pos <= (line.textStart() + line.textLength()):
                    # Calculate cursor position within this line
                    cursor_text = text[line.textStart():self.cursor_pos]
                    cursor_x = metrics.width(cursor_text)
                    cursor_y = height
                    cursor_found = True
                    
                height += line_height
                
            layout.endLayout()
            
            # Draw selection if exists
            if self.selection_start != self.selection_end:
                sel_start = min(self.selection_start, self.selection_end)
                sel_end = max(self.selection_start, self.selection_end)
                
                for line_info in text_lines:
                    line = line_info['line']
                    line_start = line.textStart()
                    line_length = line.textLength()
                    line_end = line_start + line_length
                    
                    # Check if selection intersects with this line
                    if sel_start < line_end and sel_end > line_start:
                        # Calculate selection bounds for this line
                        start_x = 0
                        width = 0
                        
                        if sel_start > line_start:
                            start_text = text[line_start:sel_start]
                            start_x = metrics.width(start_text)
                        
                        sel_text = text[
                            max(line_start, sel_start):
                            min(line_end, sel_end)
                        ]
                        width = metrics.width(sel_text)
                        
                        # Draw selection rectangle
                        sel_rect = QRectF(
                            content_rect.left() + start_x,
                            content_rect.top() + line_info['y'],
                            width,
                            metrics.height()
                        )
                        painter.fillRect(sel_rect, QColor("#2ecc71"))
            
            # Draw text lines
            for line_info in text_lines:
                line = line_info['line']
                painter.drawText(
                    QPointF(content_rect.left(), content_rect.top() + line_info['y'] + metrics.ascent()),
                    line_info['text']
                )
            
            # Draw cursor if visible
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
            # Draw non-editing text with word wrap
            text_option = QTextOption()
            text_option.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
            painter.drawText(content_rect, self.content, text_option)
            
        # Draw resize handle
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
        """Get character position for given x,y coordinates"""
        metrics = QFontMetrics(QFont("Segoe UI", 10))
        content_rect = QRectF(
            self.PADDING,
            self.HEADER_HEIGHT + 10,
            self.width - (self.PADDING * 2),
            self.height - self.HEADER_HEIGHT - (self.PADDING * 2)
        )
    
        # Create text layout
        layout = QTextLayout(self.edit_text, QFont("Segoe UI", 10))
        text_option = QTextOption()
        text_option.setAlignment(Qt.AlignLeft)
        text_option.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        layout.setTextOption(text_option)
    
        # Rest of the method remains the same
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
        
            # Check if click is on this line
            if height <= relative_y < (height + line_height):
                clicked_line = line
                break
            
            height += line_height
        
        layout.endLayout()
    
        if clicked_line:
            line_text = self.edit_text[clicked_line.textStart():clicked_line.textStart() + clicked_line.textLength()]
        
            # Find character position in line
            text_width = 0
            for i, char in enumerate(line_text):
                char_width = metrics.width(char)
                if text_width + (char_width / 2) > relative_x:
                    return clicked_line.textStart() + i
                text_width += char_width
            return clicked_line.textStart() + len(line_text)
    
        return len(self.edit_text)

    def mousePressEvent(self, event):
        if self.editing and event.pos().y() > self.HEADER_HEIGHT:
            # Start text selection
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
            # Update text selection
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
                
                # Find word boundaries
                text = self.edit_text
                start = end = char_pos
                
                # Find start of word
                while start > 0 and text[start-1].isalnum():
                    start -= 1
                    
                # Find end of word
                while end < len(text) and text[end].isalnum():
                    end += 1
                
                self.selection_start = start
                self.selection_end = end
                self.cursor_pos = end
                
            self.cursor_timer.start()
            self.setFlag(QGraphicsItem.ItemIsFocusable)
            self.setFocus()
            self.update()
        else:
            super().mouseDoubleClickEvent(event)

    def keyPressEvent(self, event):
        if not self.editing:
            return super().keyPressEvent(event)
            
        # Handle copy/paste shortcuts
        if event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_C:
                self.copy_selection()
                return
            elif event.key() == Qt.Key_V:
                self.paste_text()
                return
            elif event.key() == Qt.Key_X:
                self.cut_selection()
                return
            elif event.key() == Qt.Key_A:
                self.select_all()
                return
        
        if event.key() == Qt.Key_Return and event.modifiers() & Qt.ControlModifier:
            self.finishEditing()
        elif event.key() == Qt.Key_Escape:
            self.editing = False
            self.cursor_timer.stop()
            self.update()
        elif event.key() in (Qt.Key_Backspace, Qt.Key_Delete):
            if self.selection_start != self.selection_end:
                self.delete_selection()
            elif event.key() == Qt.Key_Backspace and self.cursor_pos > 0:
                self.edit_text = (
                    self.edit_text[:self.cursor_pos-1] + 
                    self.edit_text[self.cursor_pos:]
                )
                self.cursor_pos -= 1
            elif event.key() == Qt.Key_Delete and self.cursor_pos < len(self.edit_text):
                self.edit_text = (
                    self.edit_text[:self.cursor_pos] + 
                    self.edit_text[self.cursor_pos+1:]
                )
            self.selection_start = self.selection_end = self.cursor_pos
            self.update()
        elif event.key() in (Qt.Key_Left, Qt.Key_Right):
            if event.modifiers() & Qt.ShiftModifier:
                # Extend selection
                if self.selection_start == self.selection_end:
                    self.selection_start = self.cursor_pos
                if event.key() == Qt.Key_Left:
                    self.cursor_pos = max(0, self.cursor_pos - 1)
                else:
                    self.cursor_pos = min(len(self.edit_text), self.cursor_pos + 1)
                self.selection_end = self.cursor_pos
            else:
                # Move cursor and clear selection
                if self.selection_start != self.selection_end and not event.modifiers() & Qt.ShiftModifier:
                    # Jump to start/end of selection when arrow key is pressed
                    self.cursor_pos = min(self.selection_start, self.selection_end) if event.key() == Qt.Key_Left else max(self.selection_start, self.selection_end)
                else:
                    if event.key() == Qt.Key_Left:
                        self.cursor_pos = max(0, self.cursor_pos - 1)
                    else:
                        self.cursor_pos = min(len(self.edit_text), self.cursor_pos + 1)
                self.selection_start = self.selection_end = self.cursor_pos
            self.update()
        elif event.key() == Qt.Key_Home:
            if event.modifiers() & Qt.ShiftModifier:
                if self.selection_start == self.selection_end:
                    self.selection_start = self.cursor_pos
                self.cursor_pos = 0
                self.selection_end = self.cursor_pos
            else:
                self.cursor_pos = 0
                self.selection_start = self.selection_end = self.cursor_pos
            self.update()
        elif event.key() == Qt.Key_End:
            if event.modifiers() & Qt.ShiftModifier:
                if self.selection_start == self.selection_end:
                    self.selection_start = self.cursor_pos
                self.cursor_pos = len(self.edit_text)
                self.selection_end = self.cursor_pos
            else:
                self.cursor_pos = len(self.edit_text)
                self.selection_start = self.selection_end = self.cursor_pos
            self.update()
        elif event.key() == Qt.Key_Return:
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
            self.setCursor(Qt.SizeFDiagCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
            
    def hoverEnterEvent(self, event):
        self.hovered = True
        self.update()
        super().hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        self.hovered = False
        self.resize_handle_hovered = False
        self.color_button_hovered = False
        self.setCursor(Qt.ArrowCursor)
        self.update()
        super().hoverLeaveEvent(event)
        
    def show_color_picker(self):
        dialog = ColorPickerDialog(self.scene().views()[0])
        
        # Position dialog near the note
        note_pos = self.mapToScene(self.color_button_rect.topRight())
        view_pos = self.scene().views()[0].mapFromScene(note_pos)
        global_pos = self.scene().views()[0].mapToGlobal(view_pos)
        
        dialog.move(global_pos.x() + 10, global_pos.y())
        
        if dialog.exec_() == QDialog.Accepted:
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
        if change == QGraphicsItem.ItemPositionChange:
            # Snap to grid when moving
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
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        
        self.title = title
        self.note = note
        self.hovered = False
        self.size = 32  # Pin size
        
    def boundingRect(self):
        return QRectF(-self.size/2, -self.size/2, self.size, self.size)
        
    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Define colors
        if self.isSelected():
            pin_color = QColor("#2ecc71")  # Green when selected
        elif self.hovered:
            pin_color = QColor("#3498db")  # Blue when hovered
        else:
            pin_color = QColor("#e74c3c")  # Red by default
            
        # Draw pin head (circle)
        painter.setPen(Qt.NoPen)
        painter.setBrush(pin_color)
        head_rect = QRectF(-10, -10, 20, 20)
        painter.drawEllipse(head_rect)
        
        # Draw pin point (triangle)
        path = QPainterPath()
        path.moveTo(0, 10)
        path.lineTo(-8, 25)
        path.lineTo(8, 25)
        path.closeSubpath()
        
        painter.setBrush(pin_color)
        painter.drawPath(path)
        
        # Draw title if hovered
        if self.hovered or self.isSelected():
            painter.setPen(QPen(QColor("#ffffff")))
            font = QFont("Segoe UI", 8)
            painter.setFont(font)
            text_rect = QRectF(-50, -35, 100, 20)
            painter.drawText(text_rect, Qt.AlignCenter, self.title)
            
    def hoverEnterEvent(self, event):
        self.hovered = True
        self.update()
        super().hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        self.hovered = False
        self.update()
        super().hoverLeaveEvent(event)
        
    def mouseDoubleClickEvent(self, event):
        # Show edit dialog
        dialog = PinEditDialog(self.title, self.note, self.scene().views()[0])
        if dialog.exec_() == QDialog.Accepted:
            self.title = dialog.title_input.text()
            self.note = dialog.note_input.toPlainText()
            # Update pin in overlay
            if self.scene() and hasattr(self.scene().window, 'pin_overlay'):
                self.scene().window.pin_overlay.update_pin(self)
        super().mouseDoubleClickEvent(event)

class PinEditDialog(QDialog):
    def __init__(self, title="", note="", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        self.resize(300, 200)
        
        # Main container
        self.container = QWidget(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.container)
        
        # Container layout
        container_layout = QVBoxLayout(self.container)
        container_layout.setSpacing(10)
        container_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title input
        title_label = QLabel("Pin Title")
        container_layout.addWidget(title_label)
        
        self.title_input = QLineEdit(title)
        self.title_input.setPlaceholderText("Enter pin title...")
        container_layout.addWidget(self.title_input)
        
        # Note input
        note_label = QLabel("Note")
        container_layout.addWidget(note_label)
        
        self.note_input = QTextEdit()
        self.note_input.setPlaceholderText("Add a note...")
        self.note_input.setText(note)
        self.note_input.setMaximumHeight(80)
        container_layout.addWidget(self.note_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        container_layout.addLayout(button_layout)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 0)
        self.container.setGraphicsEffect(shadow)
        
        # Set styling
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

class PinOverlay(QWidget):
    def __init__(self, parent: 'ChatWindow' = None):
        super().__init__(parent)
        self.window = parent
        self.setFixedWidth(200)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        
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
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
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
        self.pin_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(self.pin_list)
        main_layout.addWidget(scroll)
        
        
        
        # Add pin button
        self.add_btn = QPushButton("Drop New Pin")
        self.add_btn.setIcon(qta.icon('fa5s.map-pin', color='white'))
        self.add_btn.setCursor(Qt.PointingHandCursor)
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
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(lambda: self.navigate_to_pin(pin))
        layout.addWidget(btn, stretch=1)
        
        del_btn = QPushButton()
        del_btn.setIcon(qta.icon('fa5s.times', color='#666666'))
        del_btn.setFixedSize(24, 24)
        del_btn.setCursor(Qt.PointingHandCursor)
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
        """Remove a pin safely"""
        if pin in self.pins:
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
            

# Chars and graph class
class ChartItem(QGraphicsItem):
    PADDING = 20
    HEADER_HEIGHT = 40
    
    def __init__(self, data, pos, parent=None):
        super().__init__(parent)
        self.setPos(pos)
        self.data = data
        self.title = data.get('title', 'Chart')
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        
        # Size
        self.width = 650
        self.height = 500
        
        # Visual state
        self.hovered = False
        self.resize_handle_hovered = False
        self.resizing = False
        
        # Create high DPI figure
        self.figure = Figure(figsize=(6, 4), dpi=300)
        self.figure.patch.set_facecolor('#2d2d2d')
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setStyleSheet("background-color: transparent;")
        
        # Generate the chart
        self.generate_chart()

    def generate_chart(self):
        """Generate the matplotlib chart with improved quality"""
        def abbreviate_text(text):
            """Only abbreviate words longer than 8 characters."""
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

        # Clear the figure
        self.figure.clear()
    
        # Create subplot with dark theme
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#2d2d2d')
    
        # Set style for dark theme
        plt.style.use('dark_background')
    
        # Set smaller font sizes
        plt.rcParams['axes.labelsize'] = 8
        plt.rcParams['axes.titlesize'] = 8
        plt.rcParams['xtick.labelsize'] = 7
        plt.rcParams['ytick.labelsize'] = 7
        plt.rcParams['legend.fontsize'] = 8
    
        # Get chart data
        chart_type = self.data.get('type', '')
    
        if chart_type == 'sankey':
            # Sankey requires specific data structure with flows
            flows = self.data.get('flows', [])
            if not flows:
                ax.text(0.5, 0.5, 'No flow data provided', 
                       ha='center', va='center')
                return
            
            # Process flows
            labels = []
            sources = []
            targets = []
            values = []
        
            # Collect unique labels and build index mapping
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
            
            # Create Sankey diagram
            from matplotlib.sankey import Sankey
        
            # Calculate figure size based on number of nodes
            figsize = max(6, len(labels) * 0.5)
            self.figure.set_size_inches(figsize, figsize * 0.75)
        
            # Create Sankey visualization
            sankey = Sankey(ax=ax, unit='', scale=0.01)
            sankey.add(flows=values,
                      labels=labels,
                      orientations=[0] * len(values),  # horizontal flows
                      pathlengths=[0.25] * len(values),  # path length
                      patchlabel=None,
                      alpha=0.7,  # transparency
                      facecolor='#3498db')  # flow color
                  
            # Remove axis for cleaner look
            ax.axis('off')
        
        else:
            # Original chart types (bar, line, pie, histogram)
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
        
                # Enhance grid
                ax.grid(True, linestyle='--', alpha=0.3, linewidth=0.5)
            
                # Rotate labels if needed
                if chart_type in ['bar', 'line']:
                    plt.xticks(rotation=45, ha='right')
    
        # Add padding
        self.figure.tight_layout(pad=1.8)
    
        # Render
        self.canvas.draw()
    
        # Create QImage
        width, height = self.canvas.get_width_height()
        self.chart_image = QImage(self.canvas.buffer_rgba(),
                                width, height,
                                QImage.Format_RGBA8888)
    
        # Set device pixel ratio for HiDPI
        if hasattr(self.chart_image, 'setDevicePixelRatio'):
            self.chart_image.setDevicePixelRatio(2.0)
        
    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)
        
    def paint(self, painter, option, widget=None):
        # Enable high-quality rendering
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        
        # Draw shadow
        shadow_path = QPainterPath()
        shadow_path.addRoundedRect(3, 3, self.width, self.height, 10, 10)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 30))
        painter.drawPath(shadow_path)
        
        # Main background
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
        
        # Header section
        header_rect = QRectF(0, 0, self.width, self.HEADER_HEIGHT)
        header_path = QPainterPath()
        header_path.addRoundedRect(header_rect, 10, 10)
        
        header_gradient = QLinearGradient(header_rect.topLeft(), header_rect.bottomLeft())
        header_color = QColor("#3498db")
        header_gradient.setColorAt(0, header_color)
        header_gradient.setColorAt(1, header_color.darker(110))
        
        painter.setBrush(QBrush(header_gradient))
        painter.drawPath(header_path)
        
        # Draw title
        painter.setPen(QPen(QColor("#ffffff")))
        font = QFont("Segoe UI", 10, QFont.Bold)
        painter.setFont(font)
        title_rect = header_rect.adjusted(10, 0, -10, 0)
        painter.drawText(title_rect, Qt.AlignVCenter, self.title)
        
        # Draw chart
        if hasattr(self, 'chart_image'):
            chart_rect = QRectF(
                self.PADDING,
                self.HEADER_HEIGHT + 10,
                self.width - (self.PADDING * 2),
                self.height - self.HEADER_HEIGHT - (self.PADDING * 2)
            )
            painter.drawImage(chart_rect, self.chart_image)
            
        # Draw resize handle
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
        self.setCursor(Qt.ArrowCursor)
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
            self.generate_chart()  # Regenerate chart for new size
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
        if change == QGraphicsItem.ItemPositionChange:
            # Snap to grid when moving
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
        """Add a new chat node to the scene with proper validation"""
        try:
            # Validate parent node if provided
            if parent_node is not None:
                # Check if parent node still exists in scene
                if parent_node not in self.nodes:
                    print("Warning: Parent node not found in scene")
                    parent_node = None
                elif not parent_node.scene():
                    print("Warning: Parent node no longer in scene")
                    parent_node = None
            
            # Create new node
            node = ChatNode(text, is_user)
            if conversation_history:
                node.conversation_history = conversation_history.copy()
            
            # Set up parent-child relationship
            if parent_node:
                try:
                    # Get parent position before modifying relationships
                    parent_pos = parent_node.pos()
                    
                    parent_node.children.append(node)
                    node.parent_node = parent_node
                    
                    # Calculate initial position based on parent
                    base_pos = QPointF(
                        parent_pos.x() + self.horizontal_spacing,
                        parent_pos.y()
                    )
                    
                    # Find free position near base position
                    node.setPos(self.find_free_position(base_pos, node))
                    
                    # Create connection
                    connection = ConnectionItem(parent_node, node)
                    self.addItem(connection)
                    self.connections.append(connection)
                except RuntimeError as e:
                    print(f"Error setting up parent relationship: {str(e)}")
                    # Reset relationships if parent is invalid
                    node.parent_node = None
                    if parent_node and hasattr(parent_node, 'children'):
                        if node in parent_node.children:
                            parent_node.children.remove(node)
                    # Position node as if it were a root node
                    node.setPos(50, 150)
            else:
                # Position root node
                node.setPos(50, 150)
            
            # Add node to scene
            self.addItem(node)
            self.nodes.append(node)
            
            # Validate node was added successfully
            if node not in self.nodes or not node.scene():
                raise RuntimeError("Node failed to add to scene")
                
            return node
            
        except Exception as e:
            print(f"Error adding chat node: {str(e)}")
            # Clean up any partial node creation
            if 'node' in locals():
                if node in self.nodes:
                    self.nodes.remove(node)
                if node.scene() == self:
                    self.removeItem(node)
            # Return None to indicate failure
            return None
        


    def nodeMoved(self, node):
        """Handle node movement with validation"""
        if node not in self.nodes or not node.scene():
            return
            
        # Update valid connections where this node is start or end
        for conn in self.connections[:]:  # Create copy to allow modification
            if node in (conn.start_node, conn.end_node):
                if (conn.start_node in self.nodes and 
                    conn.end_node in self.nodes and
                    conn.start_node.scene() and 
                    conn.end_node.scene()):
                    conn.update_path()
                else:
                    # Remove invalid connection
                    if conn in self.connections:
                        self.connections.remove(conn)
                    if conn.scene() == self:
                        self.removeItem(conn)
                        
    def add_navigation_pin(self, pos):
        """Add a new navigation pin with proper tracking"""
        pin = NavigationPin()
        pin.setPos(pos)
        self.addItem(pin)
        self.pins.append(pin)  # Track the pin
        return pin
    
    def add_chart(self, data, pos):
        """Add a new chart to the scene"""
        chart = ChartItem(data, pos)
        self.addItem(chart)
        return chart

    def createFrame(self):
        """Create a frame around selected nodes"""
        selected_nodes = [item for item in self.selectedItems() 
                         if isinstance(item, ChatNode)]
        
        if len(selected_nodes) < 1:
            return
            
        # Remove nodes from any existing frames
        for node in selected_nodes:
            if node.parentItem() and isinstance(node.parentItem(), Frame):
                old_frame = node.parentItem()
                
                # Store current scene position
                scene_pos = node.scenePos()
                
                # Remove from old frame
                node.setParentItem(None)
                node.setFlag(QGraphicsItem.ItemIsMovable, True)
                
                # Restore position in scene coordinates
                node.setPos(scene_pos)
                
                old_frame.nodes.remove(node)
                
                if not old_frame.nodes:
                    self.removeItem(old_frame)
                    self.frames.remove(old_frame)
                else:
                    old_frame.updateGeometry()
        
        # Create new frame
        frame = Frame(selected_nodes)
        self.addItem(frame)
        self.frames.append(frame)
        
        # Ensure frame is behind nodes but above connections
        frame.setZValue(-2)
        
        # Update all connections for the framed nodes
        for node in selected_nodes:
            self.nodeMoved(node)
            
    def add_note(self, pos):
        """Add a new note at the specified position"""
        note = Note(pos)
        self.addItem(note)
        return note
    
    def deleteSelectedNotes(self):
        """Delete all selected notes"""
        for item in list(self.selectedItems()):
            if isinstance(item, Note):
                self.removeItem(item)
    
    def deleteFrame(self, frame):
        """Delete a frame and restore its nodes"""
        for node in frame.nodes:
            # Store current scene position
            scene_pos = node.scenePos()
            
            # Remove from frame
            node.setParentItem(None)
            node.setFlag(QGraphicsItem.ItemIsMovable, True)
            
            # Restore position in scene coordinates
            node.setPos(scene_pos)
            
            # Update connections
            self.nodeMoved(node)
        
        self.removeItem(frame)
        if frame in self.frames:
            self.frames.remove(frame)

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_F:
                self.createFrame()
            elif event.key() == Qt.Key_A:
                self.selectAllNodes()
        elif event.key() == Qt.Key_Delete:
            # Handle frame and note deletion
            for item in list(self.selectedItems()):
                if isinstance(item, Frame):
                    self.deleteFrame(item)
                elif isinstance(item, Note):
                    self.removeItem(item)
                
        super().keyPressEvent(event)
        
    def selectAllNodes(self):
        """Select all nodes in the scene"""
        for node in self.nodes:
            node.setSelected(True)

    def calculate_node_rect(self, node, pos):
        """Calculate the bounding rectangle for a node at given position"""
        PADDING = 30  # Collision detection padding
        return QRectF(
            pos.x() - PADDING,
            pos.y() - PADDING,
            node.width + (PADDING * 2),
            node.height + (PADDING * 2)
        )

    def check_collision(self, test_rect, ignore_node=None):
        """Check if a rectangle collides with any existing nodes"""
        for node in self.nodes:
            if node == ignore_node:
                continue
            node_rect = self.calculate_node_rect(node, node.pos())
            if test_rect.intersects(node_rect):
                return True
        return False

    def find_free_position(self, base_pos, node, max_attempts=50):
        """Find nearest free position using spiral search pattern"""
        def spiral_positions():
            x, y = base_pos.x(), base_pos.y()
            layer = 1
            while True:
                # Move right
                for i in range(layer):
                    yield QPointF(x, y)
                    x += self.horizontal_spacing // 2
                # Move down
                for i in range(layer):
                    yield QPointF(x, y)
                    y += self.vertical_spacing
                # Move left
                for i in range(layer):
                    yield QPointF(x, y)
                    x -= self.horizontal_spacing // 2
                # Move up
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

        # If no free position found, return original with offset
        return QPointF(base_pos.x(), base_pos.y() + len(self.nodes) * self.vertical_spacing)

    def mousePressEvent(self, event):
        """Handle mouse press events for selection and pin creation"""
        # Check if clicking on empty space
        clicked_item = self.itemAt(event.scenePos(), QTransform())
        if not clicked_item:
            # Deselect all connections and stop their animations
            for item in self.items():
                if isinstance(item, ConnectionItem):
                    item.is_selected = False
                    item.stopArrowAnimation()  # Stop animation when deselecting
                    item.update()
                
        # Check if clicking on a connection with Ctrl
        if event.modifiers() & Qt.ControlModifier:
            item = self.itemAt(event.scenePos(), self.views()[0].transform())
            if isinstance(item, ConnectionItem):
                if event.button() == Qt.LeftButton:
                    # Add pin
                    item.add_pin(event.scenePos())
                    event.accept()
                    return
                
        super().mousePressEvent(event)
    
        # Clear selection if clicking on empty space with no modifiers
        if not event.modifiers() and not self.itemAt(event.scenePos(), self.views()[0].transform()):
            self.clearSelection()
            
    def update_connections(self):
        """Update all connections with improved validation"""
        # First remove any invalid connections
        valid_connections = []
        for conn in self.connections[:]:  # Create copy to allow modification
            try:
                if (conn.start_node in self.nodes and 
                    conn.end_node in self.nodes and 
                    conn.start_node.scene() == self and
                    conn.end_node.scene() == self and
                    hasattr(conn.start_node, 'children') and
                    conn.end_node in conn.start_node.children):
                    valid_connections.append(conn)
                    # Update connection path
                    conn.setZValue(-1)
                    conn.update_path()
                    conn.show()
                else:
                    # Remove any pins before removing connection
                    for pin in conn.pins[:]:
                        conn.remove_pin(pin)
                    if conn.scene() == self:
                        self.removeItem(conn)
            except RuntimeError:
                # Handle case where node was deleted
                if conn.scene() == self:
                    self.removeItem(conn)
                    
        self.connections = valid_connections

    def organize_nodes(self):
        """Organize nodes with proper spacing and frame awareness, positioning free nodes to the right of frames"""
        if not self.nodes:
            return
        
        # Constants for positioning
        START_X = 50
        START_Y = 150
        NODE_GAP_X = 500  # Horizontal gap between levels
        MIN_NODE_GAP_Y = 150  # Minimum vertical gap between nodes
        FRAME_CLEARANCE = 50  # Minimum distance to keep from frames
    
        def get_node_size(node):
            """Get total size including padding"""
            PADDING = 40
            return node.width + PADDING * 2, node.height + PADDING * 2
    
        def get_frame_rect(frame):
            """Get frame's bounding rectangle in scene coordinates"""
            return frame.mapRectToScene(frame.boundingRect())
    
        def is_node_in_frame(node):
            """Check if node is part of a frame"""
            return isinstance(node.parentItem(), Frame)
    
        def get_rightmost_frame_x():
            """Get the rightmost x-coordinate of all frames"""
            if not self.frames:
                return START_X
        
            max_x = START_X
            for frame in self.frames:
                frame_rect = get_frame_rect(frame)
                max_x = max(max_x, frame_rect.right())
            return max_x + FRAME_CLEARANCE
    
        def check_collision(node, pos_x, pos_y):
            """Check if placing node at (pos_x, pos_y) would cause collision with other nodes or frames"""
            node_width, node_height = get_node_size(node)
            test_rect = QRectF(pos_x, pos_y, node_width, node_height)
        
            # Check collision with other nodes
            for other in self.nodes:
                if other == node or is_node_in_frame(other):
                    continue
                other_width, other_height = get_node_size(other)
                other_rect = QRectF(other.pos().x(), other.pos().y(), 
                                  other_width, other_height)
                if test_rect.intersects(other_rect):
                    return True
        
            # Check collision with frames
            for frame in self.frames:
                frame_rect = get_frame_rect(frame)
                if test_rect.intersects(frame_rect):
                    return True
                
            return False
    
        def find_free_position(node, base_x, base_y):
            """Find nearest free position starting from base coordinates"""
            # If node is in a frame, keep its relative position within the frame
            if is_node_in_frame(node):
                return node.pos().x(), node.pos().y()
            
            # Start searching from the right of all frames
            rightmost_x = max(base_x, get_rightmost_frame_x())
        
            y_offset = 0
            y_step = MIN_NODE_GAP_Y
            max_attempts = 100
        
            # First try at the same y-level
            if not check_collision(node, rightmost_x, base_y):
                return rightmost_x, base_y
            
            # Then try positions above and below
            while max_attempts > 0:
                # Try position below (prefer downward expansion)
                if not check_collision(node, rightmost_x, base_y + y_offset):
                    return rightmost_x, base_y + y_offset
                
                # Try position above if needed
                if not check_collision(node, rightmost_x, base_y - y_offset):
                    return rightmost_x, base_y - y_offset
            
                y_offset += y_step
                max_attempts -= 1
            
            # If no free position found, return position far right and below
            return rightmost_x, base_y + (len(self.nodes) * MIN_NODE_GAP_Y)
    
        def position_node_and_children(node, level_x, level_y):
            """Position node and its children recursively"""
            # Don't reposition nodes that are in frames
            if not is_node_in_frame(node):
                # Find free position for current node
                free_x, free_y = find_free_position(node, level_x, level_y)
                node.setPos(free_x, free_y)
                current_x = free_x
            else:
                current_x = node.scenePos().x()
        
            if node.children:
                # Sort children by creation order
                sorted_children = sorted(node.children, 
                                      key=lambda n: self.nodes.index(n))
            
                # Calculate child positions
                next_level_x = current_x + NODE_GAP_X
            
                # Position each child with collision detection
                child_y = level_y
                for child in sorted_children:
                    position_node_and_children(child, next_level_x, child_y)
                    # Update next child's base y position
                    if not is_node_in_frame(child):
                        _, child_height = get_node_size(child)
                        child_y += child_height + MIN_NODE_GAP_Y

        # Find and position root nodes
        root_nodes = [node for node in self.nodes if not node.parent_node]
        current_y = START_Y
    
        for root in root_nodes:
            position_node_and_children(root, START_X, current_y)
            # Only increment Y position for non-framed nodes
            if not is_node_in_frame(root):
                _, root_height = get_node_size(root)
                current_y += root_height + MIN_NODE_GAP_Y * 2

        self.update_connections()

    def mousePressEvent(self, event):
        """Handle mouse press events for selection"""
        super().mousePressEvent(event)
        
        # Clear selection if clicking on empty space with no modifiers
        if not event.modifiers() and not self.itemAt(event.scenePos(), self.views()[0].transform()):
            self.clearSelection()
            
    def deleteSelectedItems(self):
        """Delete all selected items including pins"""
        for item in list(self.selectedItems()):
            if isinstance(item, Frame):
                self.deleteFrame(item)
            elif isinstance(item, Note):
                self.removeItem(item)
            elif isinstance(item, ChartItem):
                self.removeItem(item)
            elif isinstance(item, NavigationPin):
                self.remove_pin(item)
                if self.window and hasattr(self.window, 'pin_overlay'):
                    self.window.pin_overlay.remove_pin(item)

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_F:
                self.createFrame()
            elif event.key() == Qt.Key_A:
                self.selectAllNodes()
        elif event.key() == Qt.Key_Delete:
            # Handle deletion of frames, notes, and charts
            self.deleteSelectedItems()
                
        super().keyPressEvent(event)
            
class GridControl(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_size = 20
        self.grid_opacity = 0.1
        
        # Create the background canvas widget
        self.canvas = QWidget(self)
        main_layout = QVBoxLayout(self.canvas)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(6)

        # Set the canvas background style
        self.canvas.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 0.1);  /* Transparent background */
                border-radius: 10px;  /* Rounded corners */
            }
        """)

        # Layout for icon and slider
        icon_slider_layout = QHBoxLayout()
        icon_slider_layout.setContentsMargins(0, 0, 0, 0)
        icon_slider_layout.setSpacing(10)
        
        # Grid icon with transparent background
        label = QLabel("⊞", self.canvas)
        label.setAlignment(Qt.AlignCenter)
        label.setFixedWidth(30)
        label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 0);  /* Transparent background */
                border-radius: 5px;  /* Rounded corners */
            }
        """)
        icon_slider_layout.addWidget(label)
        
        # Opacity Slider
        self.opacity_slider = QSlider(Qt.Horizontal, self.canvas)
        self.opacity_slider.setFixedWidth(130)
        self.opacity_slider.setMinimum(0)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(int(self.grid_opacity * 100))
        self.opacity_slider.valueChanged.connect(self._update_opacity)
        self.opacity_slider.setToolTip(f"{self.opacity_slider.value()}%")
        self.opacity_slider.valueChanged.connect(
            lambda: self.opacity_slider.setToolTip(f"{self.opacity_slider.value()}%")
        )

        # Slider style matching drag control
        self.opacity_slider.setStyleSheet("""
            QSlider::handle:horizontal {
                background-color: #2ecc71;
                border-radius: 6px;
                width: 16px;
                margin: -6px 0;
            }
            QSlider::groove:horizontal {
                background-color: rgba(0, 0, 0, 0.2);  /* Transparent groove */
                height: 4px;
                border-radius: 2px;
            }
        """)
        
        icon_slider_layout.addWidget(self.opacity_slider)
        main_layout.addLayout(icon_slider_layout)
        
        # Grid size preset buttons layout
        grid_presets_layout = QHBoxLayout()
        grid_presets_layout.setContentsMargins(0, 0, 0, 0)
        grid_presets_layout.setSpacing(12)
        
        # Grid size preset buttons (25%, 50%, 75%, 100%)
        preset_sizes = [(10, "10px"), (20, "20px"), (50, "50px"), (100, "100px")]
        for size, label in preset_sizes:
            button = QPushButton(label, self.canvas)
            button.setFixedSize(40, 25)
            button.setStyleSheet("""
                QPushButton {
                    color: white;
                    background-color: rgba(63, 63, 63, 0.1); /* Slight transparency */
                    border: none;
                    border-radius: 5px;
                    font-size: 10px;
                    padding: 2px;
                }
                QPushButton:hover {
                    background-color: rgba(85, 85, 85, 0);
                }
                QPushButton:pressed {
                    background-color: rgba(46, 204, 113, 0.3); /* Slight transparency on press */
                    color: black;
                }
            """)
            button.clicked.connect(lambda checked, s=size: self._set_grid_size(s))
            grid_presets_layout.addWidget(button)
            
        main_layout.addLayout(grid_presets_layout)
        
        # Set size of both widgets
        self.setFixedSize(200, 90)
        self.canvas.setFixedSize(200, 90)
        
        # Add shadow effect
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
        self.setRenderHint(QPainter.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        
        # Hide default scrollbars
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Create custom scrollbars
        self.v_scrollbar = CustomScrollBar(Qt.Vertical, self)
        self.h_scrollbar = CustomScrollBar(Qt.Horizontal, self)
        
        # Connect scrollbar signals properly using lambdas
        self.v_scrollbar.valueChanged.connect(lambda v: self.verticalScrollBar().setValue(int(v)))
        self.h_scrollbar.valueChanged.connect(lambda v: self.horizontalScrollBar().setValue(int(v)))
        
        self.setScene(ChatScene(window))
        
        # Enable rubber band selection
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        
        # Panning settings
        self._panning = False
        self._last_mouse_pos = None
        self._zoom_factor = 1.0
        self._drag_factor = 1.0
        
        # Region expansion settings
        self._expanding = False
        self._expand_start = None
        self._expand_rect = None
        self._original_transform = None
        
        # Add drag control
        self._setup_drag_control()
        
        # Enable mouse tracking
        self.setMouseTracking(True)
        
        # Add grid control
        self.grid_control = GridControl(self)
        self._update_grid_control_position()
        
        self._current_mouse_pos = None
        
        # Set a very large scene rect for unlimited panning
        self.setSceneRect(-100000, -100000, 200000, 200000)
        
    def _setup_drag_control(self):
        # Main container layout
        self.control_widget = QWidget(self)
        main_layout = QVBoxLayout(self.control_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(6)

        # Set the background of the canvas with slight transparency and rounded corners
        self.control_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 0.1);  /* Transparent background */
                border-radius: 10px;  /* Rounded corners */
            }
        """)

        # Layout for icon and slider
        icon_slider_layout = QHBoxLayout()
        icon_slider_layout.setContentsMargins(0, 0, 0, 0)
        icon_slider_layout.setSpacing(10)

        # Icon with transparent background
        label = QLabel("⚡", self.control_widget)
        label.setAlignment(Qt.AlignCenter)
        label.setFixedWidth(30)
        label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 0);
                border-radius: 5px;
            }
        """)
        icon_slider_layout.addWidget(label)

        # Slider
        self.drag_slider = QSlider(Qt.Horizontal, self.control_widget)
        self.drag_slider.setFixedWidth(130)
        self.drag_slider.setMinimum(10)     # 0.1x speed (more drag)
        self.drag_slider.setMaximum(100)    # 1.0x speed (normal)
        self.drag_slider.setValue(100)      # Default to normal speed
        self.drag_slider.valueChanged.connect(self._update_drag)
        self.drag_slider.setToolTip(f"{self.drag_slider.value()}%")
        self.drag_slider.valueChanged.connect(
            lambda: self.drag_slider.setToolTip(f"{self.drag_slider.value()}%")
        )

        # Slider style
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

        # Notched buttons layout
        notches_layout = QHBoxLayout()
        notches_layout.setContentsMargins(0, 0, 0, 0)
        notches_layout.setSpacing(12)

        # Notched buttons (25%, 50%, 75%, 100%)
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

        # Set size and position
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
            120  # Position below drag control
        )

    def updateScrollbars(self):
        # Update vertical scrollbar
        v_bar = self.verticalScrollBar()
        self.v_scrollbar.setRange(v_bar.minimum(), v_bar.maximum())
        self.v_scrollbar.page_step = v_bar.pageStep()
        self.v_scrollbar.setValue(v_bar.value())
        
        # Update horizontal scrollbar
        h_bar = self.horizontalScrollBar()
        self.h_scrollbar.setRange(h_bar.minimum(), h_bar.maximum())
        self.h_scrollbar.page_step = h_bar.pageStep()
        self.h_scrollbar.setValue(h_bar.value())

    def mousePressEvent(self, event):
        if event.modifiers() & Qt.ShiftModifier:
            # Start region expansion
            self._expanding = True
            self._expand_start = event.pos()
            self._expand_rect = None
            self._original_transform = self.transform()
            event.accept()
        elif event.button() == Qt.MiddleButton:
            self._panning = True
            self._last_mouse_pos = event.pos()
            self.viewport().setCursor(Qt.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._expanding and self._expand_start:
            # Update expansion rectangle and current mouse position
            self._current_mouse_pos = event.pos()
            self._expand_rect = QRectF(
                self.mapToScene(self._expand_start),
                self.mapToScene(self._current_mouse_pos)
            ).normalized()
            
            # Create visual feedback
            self.viewport().update()
            event.accept()
        elif self._panning and self._last_mouse_pos is not None:
            delta = event.pos() - self._last_mouse_pos
            delta *= self._drag_factor
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            self.updateScrollbars()
            self._last_mouse_pos = event.pos()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._expanding and self._expand_rect:
            # Temporarily zoom into the selected region
            self.fitInView(self._expand_rect, Qt.KeepAspectRatio)
            self._zoom_factor = self.transform().m11()  # Update zoom factor
            self._expanding = False
            self._expand_rect = None
            event.accept()
        elif self._panning:
            self._panning = False
            self._last_mouse_pos = None
            self.viewport().setCursor(Qt.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Shift:
            # Restore original view if Shift is released during expansion
            if self._expanding and self._original_transform:
                self.setTransform(self._original_transform)
                self._zoom_factor = self._original_transform.m11()
                self._expanding = False
                self._expand_rect = None
                self.viewport().update()
        elif event.key() == Qt.Key_Escape:
            # Reset expansion on Escape
            if self._original_transform:
                self.setTransform(self._original_transform)
                self._zoom_factor = self._original_transform.m11()
                self._expanding = False
                self._expand_rect = None
                self.viewport().update()
        super().keyReleaseEvent(event)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            zoom_in = event.angleDelta().y() > 0
            
            # Calculate zoom factor
            if zoom_in:
                factor = 1.1
                self._zoom_factor *= factor
            else:
                factor = 0.9
                self._zoom_factor *= factor
                
            # Limit zoom range
            if 0.1 <= self._zoom_factor <= 4.0:
                self.scale(factor, factor)
            else:
                # Revert zoom factor if outside limits
                self._zoom_factor /= factor
        else:
            # Use custom scrollbars for regular scrolling
            v_bar = self.verticalScrollBar()
            h_bar = self.horizontalScrollBar()
            
            if event.modifiers() & Qt.ShiftModifier:
                # Horizontal scroll with Shift
                delta = event.angleDelta().y() if event.angleDelta().y() != 0 else event.angleDelta().x()
                h_bar.setValue(h_bar.value() - delta)
            else:
                # Vertical scroll
                delta = event.angleDelta().y()
                v_bar.setValue(v_bar.value() - delta)
                
            self.updateScrollbars()

    def paintEvent(self, event):
        super().paintEvent(event)
        
        if self._expanding and self._expand_start and self._current_mouse_pos:
            # Draw expansion rectangle overlay
            painter = QPainter(self.viewport())
            painter.setPen(QPen(QColor("#2ecc71"), 2, Qt.DashLine))
            painter.setBrush(QBrush(QColor(46, 204, 113, 30)))  # Semi-transparent green
            
            rect = QRectF(
                self._expand_start,
                self._current_mouse_pos
            ).normalized()
            
            painter.drawRect(rect)

    def resizeEvent(self, event):
        super().resizeEvent(event)
    
        # Update control positions
        self._update_control_position()
        self._update_grid_control_position()
    
        # Position custom scrollbars
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
    
        # Update scrollbar ranges
        self.updateScrollbars()

    def scrollContentsBy(self, dx, dy):
        super().scrollContentsBy(dx, dy)
        self.updateScrollbars()
            
    def reset_zoom(self):
        """Reset zoom level to 100%"""
        self.resetTransform()
        self._zoom_factor = 1.0
        
    def fit_all(self):
        """Fit all nodes in view"""
        if self.scene() and not self.scene().nodes:
            return
        self.fitInView(self.scene().itemsBoundingRect(), Qt.KeepAspectRatio)
        # Update zoom factor based on current transform
        self._zoom_factor = self.transform().m11()

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
    
        # Draw base background
        painter.fillRect(rect, QColor("#252526"))
    
        # Get grid properties
        grid_size = self.grid_control.grid_size
        opacity = self.grid_control.grid_opacity
    
        if opacity <= 0:
            return
        
        # Set up pen for grid lines
        grid_color = QColor(255, 255, 255, int(255 * opacity))
        painter.setPen(QPen(grid_color, 1, Qt.DotLine))
    
        # Calculate grid boundaries
        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)
        right = int(rect.right())
        bottom = int(rect.bottom())
    
        # Draw vertical lines
        for x in range(left, right, grid_size):
            painter.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))
        
        # Draw horizontal lines
        for y in range(top, bottom, grid_size):
            painter.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))
        
class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.Window |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(False)
        self.resize(800, 600)

        # Main container layout
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
        self.title_bar.title.setText("Graphite Help")
        main_layout.addWidget(self.title_bar)

        # Content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Create tab widget for different help sections
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

        # Navigation Tab
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

        # Chat Features Tab
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

        # Organization Tab
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

        # Connection Tab
        conn_widget = QWidget()
        conn_layout = QVBoxLayout(conn_widget)
        conn_layout.addWidget(self._create_section("Connection Management", [
            ("Add Pin", "Ctrl + Left Click on connection", "fa5s.dot-circle"),
            ("Remove Pin", "Ctrl + Right Click on pin", "fa5s.times-circle"),
            ("Move Pin", "Click and drag pin", "fa5s.arrows-alt"),
            ("Auto-Route", "Connections auto-adjust to avoid crossings", "fa5s.route")
        ]))
        tab_widget.addTab(conn_widget, "Connections")

        # Add tabs to content layout
        content_layout.addWidget(tab_widget)

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

        # Section title
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

        # Add items
        for action, description, icon_name in items:
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setSpacing(15)

            # Icon
            icon_label = QLabel()
            icon = qta.icon(icon_name, color='#2ecc71')
            icon_label.setPixmap(icon.pixmap(24, 24))
            item_layout.addWidget(icon_label)

            # Text content
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
        # Ensure the window stays within screen bounds
        screen = QApplication.primaryScreen().geometry()
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
        
class ExplainerWorkerThread(QThread):
    finished = pyqtSignal(str, QPointF)
    error = pyqtSignal(str)
    
    def __init__(self, agent, text, node_pos):
        super().__init__()
        self.agent = agent
        self.text = text
        self.node_pos = node_pos
        self._is_running = False
        
    def run(self):
        try:
            self._is_running = True
            response = self.agent.get_response(self.text)
            if self._is_running:
                self.finished.emit(response, self.node_pos)
        except Exception as e:
            if self._is_running:
                self.error.emit(str(e))
        finally:
            self._is_running = False
            
    def stop(self):
        """Safely stop the thread"""
        self._is_running = False

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(StyleSheet.DARK_THEME)
        self.library_dialog = None

        # Initialize AI agent
        self.agent = ChatAgent("Pick an identity", 
            """
            * you are an agent within the program Graphite, this is a node based Interface LLM. 
            * This program is currently up and running and you are the core part of this ap.
            * Give professional responses. 
            * Always think about what you say - be thoughtful - think things through.
            * If you feel unsure or unaware of a topic, say so. Do not give blind advice - 
            If you cannot explain how and why, maybe its NOT a good idea not to use that in your response.
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
        library_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        library_btn.setObjectName("actionButton")
        library_btn.clicked.connect(self.show_library)
        self.toolbar.addWidget(library_btn)
        
        save_btn = QToolButton()
        save_btn.setIcon(qta.icon('fa5s.save', color='#2ecc71'))
        save_btn.setText("Save")
        save_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
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
        screen = QDesktopWidget().screenGeometry()
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
        
        # Update pin overlay position
        if hasattr(self, 'pin_overlay'):
            self.pin_overlay.move(10, 
                                self.title_bar.height() + 
                                self.toolbar.height() + 10)
        
    def show_library(self):
        """Show the chat library dialog"""
        # Create new dialog and store reference
        self.library_dialog = ChatLibraryDialog(self.session_manager, self)
        self.library_dialog.setWindowTitle("Chat Library")
        self.library_dialog.resize(500, 600)
        # Use exec_() for modal dialog or show() for non-modal
        self.library_dialog.show()
        
    def keyPressEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_N:
                # Get cursor position in scene coordinates
                view_pos = self.chat_view.mapFromGlobal(QCursor.pos())
                scene_pos = self.chat_view.mapToScene(view_pos)
                self.chat_view.scene().add_note(scene_pos)
        elif event.key() == Qt.Key_Delete:
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
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
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

        # API Settings button (configure models per task)
        self.api_settings_btn = QToolButton()
        self.api_settings_btn.setIcon(qta.icon('fa5s.cog', color='#3498db'))
        self.api_settings_btn.setText("API Settings")
        self.api_settings_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.api_settings_btn.setObjectName("actionButton")
        self.api_settings_btn.setVisible(True)
        self.api_settings_btn.clicked.connect(self.show_api_settings)
        toolbar.addWidget(self.api_settings_btn)

        toolbar.addSeparator()

        # Organize Button
        organize_btn = QToolButton()
        organize_btn.setIcon(qta.icon('fa5s.project-diagram', color='#3498db'))
        organize_btn.setText("Organize")
        organize_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        organize_btn.setObjectName("actionButton")
        organize_btn.clicked.connect(lambda: self.chat_view.scene().organize_nodes())
        toolbar.addWidget(organize_btn)

        toolbar.addSeparator()

        # Zoom Controls
        zoom_in_btn = QToolButton()
        zoom_in_btn.setIcon(qta.icon('fa5s.search-plus', color='#3498db'))
        zoom_in_btn.setText("Zoom In")
        zoom_in_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        zoom_in_btn.setObjectName("actionButton")
        zoom_in_btn.clicked.connect(lambda: self.chat_view.scale(1.1, 1.1))
        toolbar.addWidget(zoom_in_btn)

        zoom_out_btn = QToolButton()
        zoom_out_btn.setIcon(qta.icon('fa5s.search-minus', color='#3498db'))
        zoom_out_btn.setText("Zoom Out")
        zoom_out_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        zoom_out_btn.setObjectName("actionButton")
        zoom_out_btn.clicked.connect(lambda: self.chat_view.scale(0.9, 0.9))
        toolbar.addWidget(zoom_out_btn)

        toolbar.addSeparator()

        # View Controls
        reset_btn = QToolButton()
        reset_btn.setIcon(qta.icon('fa5s.undo', color='#3498db'))
        reset_btn.setText("Reset")
        reset_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        reset_btn.setObjectName("actionButton")
        reset_btn.clicked.connect(self.chat_view.reset_zoom)
        toolbar.addWidget(reset_btn)

        fit_btn = QToolButton()
        fit_btn.setIcon(qta.icon('fa5s.expand', color='#3498db'))
        fit_btn.setText("Fit All")
        fit_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        fit_btn.setObjectName("actionButton")
        fit_btn.clicked.connect(self.chat_view.fit_all)
        toolbar.addWidget(fit_btn)

        # Add expanding spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        # Help Button
        help_btn = QToolButton()
        help_btn.setIcon(qta.icon('fa5s.question-circle', color='#9b59b6'))
        help_btn.setText("Help")
        help_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        help_btn.setObjectName("helpButton")
        help_btn.clicked.connect(self.show_help)
        toolbar.addWidget(help_btn)

    def show_help(self):
        """Show the help dialog"""
        help_dialog = HelpDialog(self)
        # Center the dialog relative to the main window
        center = self.geometry().center()
        help_dialog.move(center.x() - help_dialog.width() // 2,
                        center.y() - help_dialog.height() // 2)
        help_dialog.show()

    def on_mode_changed(self, index):
        """Handle mode toggle between Ollama and API"""
        use_api = self.mode_combo.itemData(index)
        api_provider.set_mode(use_api)

        # Show/hide API settings button
        self.api_settings_btn.setVisible(use_api)

    def show_api_settings(self):
        """Show API configuration dialog with per-task model selection"""
        dialog = QDialog(self)
        dialog.setWindowTitle("API Endpoint Configuration")
        dialog.setMinimumWidth(700)
        dialog.setStyleSheet(StyleSheet.DARK_THEME)

        layout = QVBoxLayout(dialog)

        # Info
        info = QLabel(
            "Configure your OpenAI-compatible API endpoint.\n"
            "Works with: OpenAI, LiteLLM proxy, Anthropic, OpenRouter, etc.\n\n"
            "Choose different models for different tasks (like Ollama does)."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #d4d4d4; margin-bottom: 15px;")
        layout.addWidget(info)

        # Base URL
        base_url_label = QLabel("Base URL:")
        base_url_label.setStyleSheet("color: #ffffff; font-weight: bold;")
        layout.addWidget(base_url_label)

        base_url_input = QLineEdit()
        base_url_input.setPlaceholderText("https://api.openai.com/v1")
        base_url_input.setText(os.getenv('GRAPHITE_API_BASE', 'https://api.openai.com/v1'))
        layout.addWidget(base_url_input)

        # API Key
        api_key_label = QLabel("API Key:")
        api_key_label.setStyleSheet("color: #ffffff; font-weight: bold; margin-top: 10px;")
        layout.addWidget(api_key_label)

        api_key_input = QLineEdit()
        api_key_input.setEchoMode(QLineEdit.Password)
        api_key_input.setPlaceholderText("Enter your API key...")
        api_key_input.setText(os.getenv('GRAPHITE_API_KEY', ''))
        layout.addWidget(api_key_input)

        # Load models button
        load_btn = QPushButton("Load Models from Endpoint")
        load_btn.clicked.connect(lambda: self.load_models_to_dialog(
            base_url_input.text().strip(),
            api_key_input.text().strip(),
            model_combos
        ))
        layout.addWidget(load_btn)

        # Model selection per task
        models_label = QLabel("Model Selection (per task):")
        models_label.setStyleSheet("color: #ffffff; font-weight: bold; margin-top: 15px;")
        layout.addWidget(models_label)

        model_combos = {}

        # Title generation model
        title_label = QLabel("Title Generation (fast, cheap model):")
        title_label.setStyleSheet("color: #d4d4d4; margin-top: 8px;")
        layout.addWidget(title_label)

        title_combo = QComboBox()
        title_combo.setPlaceholderText("Select model...")
        model_combos['qwen2.5:3b'] = title_combo
        layout.addWidget(title_combo)

        # Chat model
        chat_label = QLabel("Chat, Explain, Takeaways (main model):")
        chat_label.setStyleSheet("color: #d4d4d4; margin-top: 8px;")
        layout.addWidget(chat_label)

        chat_combo = QComboBox()
        chat_combo.setPlaceholderText("Select model...")
        model_combos['qwen2.5:7b'] = chat_combo
        layout.addWidget(chat_combo)

        # Chart generation model
        chart_label = QLabel("Chart Generation (code-capable model):")
        chart_label.setStyleSheet("color: #d4d4d4; margin-top: 8px;")
        layout.addWidget(chart_label)

        chart_combo = QComboBox()
        chart_combo.setPlaceholderText("Select model...")
        model_combos['qwen2.5-coder:14b'] = chart_combo
        layout.addWidget(chart_combo)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_btn = QPushButton("Save Configuration")
        save_btn.clicked.connect(lambda: self.save_api_settings(
            base_url_input.text().strip(),
            api_key_input.text().strip(),
            model_combos,
            dialog
        ))
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        dialog.exec_()

    def load_models_to_dialog(self, base_url, api_key, model_combos):
        """Load available models from API and populate dropdowns"""
        if not base_url or not api_key:
            QMessageBox.warning(self, "Missing Information", "Please enter both Base URL and API Key")
            return

        try:
            # Initialize API client
            api_provider.initialize_api(api_key, base_url)

            # Fetch models
            models = api_provider.get_available_models()

            # Populate all model dropdowns
            for combo in model_combos.values():
                combo.clear()
                for model in models:
                    combo.addItem(model)

            QMessageBox.information(
                self,
                "Models Loaded",
                f"Successfully loaded {len(models)} models!\n\n"
                f"Now select a model for each task."
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Failed to Load Models",
                f"Could not fetch models from API:\n\n{str(e)}"
            )

    def save_api_settings(self, base_url, api_key, model_combos, dialog):
        """Save API settings and model mappings"""
        if not base_url or not api_key:
            QMessageBox.warning(self, "Missing Information", "Please enter both Base URL and API Key")
            return

        # Check all models are selected
        for task_key, combo in model_combos.items():
            if not combo.currentText():
                QMessageBox.warning(
                    self,
                    "Missing Model Selection",
                    f"Please select a model for all tasks.\n\nMissing: {task_key}"
                )
                return

        try:
            # Save to environment
            os.environ['GRAPHITE_API_BASE'] = base_url
            os.environ['GRAPHITE_API_KEY'] = api_key

            # Initialize API client
            api_provider.initialize_api(api_key, base_url)

            # Save model mappings
            for task_key, combo in model_combos.items():
                api_provider.set_task_model(task_key, combo.currentText())

            task_models = api_provider.get_task_models()

            QMessageBox.information(
                self,
                "Configuration Saved",
                f"API configured successfully!\n\n"
                f"Title Model: {task_models['qwen2.5:3b']}\n"
                f"Chat Model: {task_models['qwen2.5:7b']}\n"
                f"Chart Model: {task_models['qwen2.5-coder:14b']}"
            )
            dialog.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Configuration Failed",
                f"Failed to save configuration:\n\n{str(e)}"
            )

    def setCurrentNode(self, node):
        self.current_node = node
        self.message_input.setPlaceholderText(f"Responding to: {node.text[:30]}...")
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Keep loading overlay centered
        self.loading_overlay.setGeometry(
            (self.width() - 200) // 2,
            (self.height() - 100) // 2,
            200, 
            100
        )
            
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

def main():
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
import json
import sqlite3
from datetime import datetime
from pathlib import Path
import ollama
from PySide6.QtCore import QPointF
from PySide6.QtGui import QTransform

# Import UI classes needed for serialization/deserialization
from graphite_ui import Note, NavigationPin, ChartItem, ConnectionItem, Frame
import graphite_config as config
import api_provider

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
            response = api_provider.chat(task=config.TASK_TITLE, messages=messages)
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
        self.window.current_node = None # <<< FIX: Reset stale reference

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

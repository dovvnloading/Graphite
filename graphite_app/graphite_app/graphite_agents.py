import ollama
import json
from PySide6.QtCore import QThread, Signal, QPointF
import graphite_config as config
import api_provider

class ChatWorkerThread(QThread):
    """Run chat generation off the UI thread and emit success/error signals."""
    finished = Signal(str)
    error = Signal(str)
    
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
    """Compose chat messages and call the configured provider synchronously."""
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
            response = api_provider.chat(task=config.TASK_CHAT, messages=messages)
            ai_message = response['message']['content']
            return ai_message
        except Exception as e:
            return f"Error: {str(e)}"

class ChatAgent:
    """Stateful assistant that tracks conversation history per node/session."""
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

class ExplainerAgent:
    """Generate plain-language explanations and normalize the output format."""
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
        """Normalize model output into the strict UI format expected by Graphite."""
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
        response = api_provider.chat(task=config.TASK_CHAT, messages=messages)
        raw_response = response['message']['content']
        
        # Clean and format the response
        formatted_response = self.clean_text(raw_response)
        return formatted_response
        
class KeyTakeawayAgent:
    """Produce concise actionable summaries with consistent section headings."""
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
        """Normalize model output into the strict UI format expected by Graphite."""
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
        response = api_provider.chat(task=config.TASK_CHAT, messages=messages)
        raw_response = response['message']['content']
        
        # Clean and format the response
        formatted_response = self.clean_text(raw_response)
        return formatted_response

class KeyTakeawayWorkerThread(QThread):
    """Thread wrapper for key-takeaway generation tied to a node position."""
    finished = Signal(str, QPointF)  # Signal includes response and node position
    error = Signal(str)
    
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
    """Extract structured chart payloads from natural language text."""
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

    def _normalize_numeric_list(self, values):
        """Convert model-produced values into a clean float list."""
        if not isinstance(values, list):
            raise ValueError("Values must be a list")
        normalized = []
        for index, value in enumerate(values):
            try:
                normalized.append(float(value))
            except (TypeError, ValueError):
                raise ValueError(f"Value at index {index} is not numeric")
        return normalized

    def normalize_chart_payload(self, data, chart_type):
        """Coerce near-valid model output into a strict chart schema."""
        normalized = dict(data)
        normalized['type'] = chart_type

        if 'title' not in normalized or not str(normalized['title']).strip():
            normalized['title'] = f"{chart_type.title()} Chart"

        if chart_type in ['bar', 'line', 'pie', 'histogram']:
            normalized['values'] = self._normalize_numeric_list(normalized.get('values', []))

        if chart_type in ['bar', 'line', 'pie']:
            labels = normalized.get('labels', [])
            if not isinstance(labels, list):
                labels = []

            # Keep payload renderable even when the model returns fewer labels.
            if len(labels) < len(normalized['values']):
                labels = labels + [f"Item {i + 1}" for i in range(len(labels), len(normalized['values']))]
            elif len(labels) > len(normalized['values']):
                labels = labels[:len(normalized['values'])]

            normalized['labels'] = [str(label) for label in labels]

        if chart_type == 'histogram':
            bins = normalized.get('bins', 10)
            try:
                bins = int(float(bins))
            except (TypeError, ValueError):
                bins = 10
            normalized['bins'] = max(1, bins)

        if chart_type == 'sankey':
            sankey_data = normalized.get('data', {})
            if not isinstance(sankey_data, dict):
                sankey_data = {}

            nodes = sankey_data.get('nodes', [])
            links = sankey_data.get('links', [])
            if not isinstance(nodes, list):
                nodes = []
            if not isinstance(links, list):
                links = []

            clean_nodes = []
            for i, node in enumerate(nodes):
                name = node.get('name') if isinstance(node, dict) else None
                clean_nodes.append({'name': str(name) if name else f'Node {i + 1}'})

            clean_links = []
            for link in links:
                if not isinstance(link, dict):
                    continue
                try:
                    source = int(link.get('source'))
                    target = int(link.get('target'))
                    value = float(link.get('value'))
                except (TypeError, ValueError):
                    continue
                clean_links.append({'source': source, 'target': target, 'value': value})

            normalized['data'] = {'nodes': clean_nodes, 'links': clean_links}

        if chart_type in ['bar', 'line', 'histogram']:
            normalized['xAxis'] = str(normalized.get('xAxis', 'X Axis'))
            normalized['yAxis'] = str(normalized.get('yAxis', 'Y Axis'))

        return normalized

    def validate_chart_data(self, data, chart_type):
        """Validate chart payload shape and value constraints by chart type."""
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
            
            # Using a more specialized model for code/JSON generation
            response = api_provider.chat(task=config.TASK_CHART, messages=messages)
            cleaned_response = self.clean_response(response['message']['content'])
            
            # Parse JSON
            try:
                data = json.loads(cleaned_response)
            except json.JSONDecodeError:
                return json.dumps({"error": "Invalid JSON response from model"})
            
            # Normalize and validate data
            data = self.normalize_chart_payload(data, chart_type)
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
    """Background worker that returns validated chart JSON for rendering."""
    finished = Signal(str, str)
    error = Signal(str)
    
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

class ExplainerWorkerThread(QThread):
    """Run explainer generation off-thread and emit node placement info."""
    finished = Signal(str, QPointF)
    error = Signal(str)
    
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

class ModelPullWorkerThread(QThread):
    """Ensure an Ollama model is locally available without blocking the UI."""
    status_update = Signal(str)
    finished = Signal(str, str)
    error = Signal(str)

    def __init__(self, model_name):
        super().__init__()
        self.model_name = model_name

    def run(self):
        try:
            self.status_update.emit(f"Ensuring model '{self.model_name}' is available...")
            
            ollama.pull(self.model_name)
            
            self.finished.emit(f"Model '{self.model_name}' is ready to use.", self.model_name)

        except Exception as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                self.error.emit(f"Model '{self.model_name}' not found on the Ollama hub. Please check the name for typos.")
            elif "connection refused" in error_message.lower():
                self.error.emit("Connection to Ollama server failed. Is Ollama running?")
            else:
                self.error.emit(f"An unexpected error occurred: {error_message}")

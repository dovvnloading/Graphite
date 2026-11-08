"""Regression coverage for Graphite's highest-priority reliability fixes."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "graphite_app" / "graphite_app"))

import api_provider
import graphite_config as config
from graphite_agents import (
    ChartDataAgent, MAX_CHART_VALUES, MAX_CHART_RESPONSE_CHARS, MAX_SANKEY_NODES
)
from graphite_app import ChatWindow
from graphite_core import ChatDatabase, ChatSessionManager
from graphite_ui import ChatNode, ChatNodeContextMenu


def point(x=0, y=0):
    return SimpleNamespace(x=lambda: x, y=lambda: y)


def snapshot():
    return {
        "chat_data": {
            "nodes": [], "connections": [], "frames": [], "charts": [],
            "view_state": {"zoom_factor": 1.0, "scroll_position": {"x": 0, "y": 0}},
        },
        "notes_data": [{
            "content": "Important", "position": {"x": 1, "y": 2},
            "size": {"width": 100, "height": 75},
            "color": "#444444", "header_color": None,
        }],
        "pins_data": [],
    }


class ParserTests(unittest.TestCase):
    def test_literal_header_prefix_is_safe(self):
        for literal in ("[hello]", "[h]", "[header]", "[huh]"):
            receiver = SimpleNamespace(blocks=[], clean_text=lambda text: text)
            with self.subTest(literal=literal), patch("graphite_ui.TextBlock") as block:
                ChatNode.process_text(receiver, literal)
                block.assert_called_once_with(literal)

    def test_failed_node_creation_restores_controls(self):
        message_input = SimpleNamespace(text=lambda: "[hello]", setEnabled=MagicMock())
        send_button = SimpleNamespace(setEnabled=MagicMock())
        loading_overlay = SimpleNamespace(show=MagicMock(), hide=MagicMock())
        scene = SimpleNamespace(add_chat_node=MagicMock(return_value=None))
        window = SimpleNamespace(
            is_generation_running=lambda: False,
            message_input=message_input,
            send_button=send_button,
            loading_overlay=loading_overlay,
            chat_view=SimpleNamespace(scene=lambda: scene),
            current_node=None,
            build_conversation_history=lambda node: [],
        )
        with patch("graphite_app.QMessageBox.critical") as error_dialog:
            ChatWindow.send_message(window)
        message_input.setEnabled.assert_any_call(True)
        send_button.setEnabled.assert_any_call(True)
        loading_overlay.hide.assert_called_once()
        error_dialog.assert_called_once()

    def test_running_worker_prevents_another_task(self):
        window = SimpleNamespace(chat_thread=SimpleNamespace(isRunning=lambda: True))
        self.assertTrue(ChatWindow.is_generation_running(window))

    def test_failed_ai_response_node_restores_controls_and_saves_question(self):
        user_node = SimpleNamespace(
            conversation_history=[{"role": "user", "content": "Question"}]
        )
        scene = SimpleNamespace(add_chat_node=MagicMock(return_value=None))
        window = SimpleNamespace(
            chat_view=SimpleNamespace(scene=lambda: scene),
            message_input=SimpleNamespace(setEnabled=MagicMock()),
            send_button=SimpleNamespace(setEnabled=MagicMock()),
            loading_overlay=SimpleNamespace(hide=MagicMock()),
            session_manager=SimpleNamespace(save_current_chat=MagicMock()),
        )
        with patch("graphite_app.QMessageBox.critical") as error_dialog:
            ChatWindow.handle_response(window, "Answer", user_node)
        window.message_input.setEnabled.assert_called_with(True)
        window.send_button.setEnabled.assert_called_with(True)
        window.loading_overlay.hide.assert_called_once()
        window.session_manager.save_current_chat.assert_called_once()
        error_dialog.assert_called_once()


class SessionSafetyTests(unittest.TestCase):
    def test_live_note_and_frame_buffers_are_serialized(self):
        manager = ChatSessionManager.__new__(ChatSessionManager)
        note = SimpleNamespace(
            editing=True, edit_text="Current edit", content="Old value",
            pos=lambda: point(), width=100, height=80,
            color="#444444", header_color=None
        )
        self.assertEqual(manager.serialize_note(note)["content"], "Current edit")

        frame = SimpleNamespace(
            editing=True, edit_text="New heading", note="Old heading",
            nodes=[], pos=lambda: point(),
            rect=SimpleNamespace(width=lambda: 200, height=lambda: 120),
            color="#555555", header_color=None
        )
        self.assertEqual(manager.serialize_frame(frame)["note"], "New heading")

    def test_deleting_active_chat_keeps_unsaved_copy(self):
        with tempfile.TemporaryDirectory() as folder:
            db = ChatDatabase.__new__(ChatDatabase)
            db.db_path = Path(folder) / "graphite.db"
            db.init_database()

            current = snapshot()
            old_id = db.save_snapshot("Old", current["chat_data"], current["notes_data"], [])
            manager = ChatSessionManager.__new__(ChatSessionManager)
            manager.db = db
            manager.current_chat_id = old_id
            manager._saved_snapshot = copy.deepcopy(current)
            manager.capture_current_snapshot = lambda: copy.deepcopy(current)
            manager.title_generator = SimpleNamespace(generate_title=lambda message: "Recovered")

            db.delete_chat(old_id)
            manager.detach_deleted_chat(old_id)
            self.assertIsNone(manager.current_chat_id)
            self.assertTrue(manager.has_unsaved_changes())
            self.assertTrue(manager.save_current_chat())
            self.assertNotEqual(manager.current_chat_id, old_id)
            self.assertEqual(db.load_notes(manager.current_chat_id)[0]["content"], "Important")


class RegenerationTests(unittest.TestCase):
    def test_regeneration_creates_sibling_without_overwriting_old_branch(self):
        question = SimpleNamespace(text="Question", is_user=True, parent_node=None)
        original = SimpleNamespace(text="Original response", parent_node=question)
        alternate = SimpleNamespace(text="Alternative response", parent_node=question)

        scene = SimpleNamespace(nodes=[question, original])
        scene.add_chat_node = MagicMock(return_value=alternate)
        original.scene = lambda: scene
        window = SimpleNamespace(
            build_conversation_history=MagicMock(return_value=[
                {"role": "user", "content": "Question"}
            ]),
            setCurrentNode=MagicMock(),
            chat_view=SimpleNamespace(centerOn=MagicMock()),
            session_manager=SimpleNamespace(save_current_chat=MagicMock()),
            message_input=SimpleNamespace(setEnabled=MagicMock()),
            send_button=SimpleNamespace(setEnabled=MagicMock()),
            loading_overlay=SimpleNamespace(hide=MagicMock()),
        )
        scene.window = window
        menu = SimpleNamespace(node=original)

        with patch("graphite_ui.QMessageBox.critical") as error_dialog:
            ChatNodeContextMenu.handle_regenerated_response(menu, "Alternative response")

        self.assertEqual(original.text, "Original response")
        self.assertIs(original.parent_node, question)
        self.assertIs(scene.add_chat_node.call_args.kwargs["parent_node"], question)
        self.assertEqual(scene.add_chat_node.call_args.kwargs["conversation_history"][-1],
                         {"role": "assistant", "content": "Alternative response"})
        window.setCurrentNode.assert_called_once_with(alternate)
        window.session_manager.save_current_chat.assert_called_once()
        error_dialog.assert_not_called()


class WorkerLifetimeTests(unittest.TestCase):
    def test_regeneration_keeps_context_menu_alive_until_completion(self):
        question = SimpleNamespace(text="Prompt", parent_node=None)
        node = SimpleNamespace(parent_node=question)
        scene = SimpleNamespace(window=None)
        node.scene = lambda: scene
        window = SimpleNamespace(
            agent=object(),
            is_generation_running=lambda: False,
            build_conversation_history=lambda parent: [
                {"role": "user", "content": "Prompt"}
            ],
            message_input=SimpleNamespace(setEnabled=MagicMock()),
            send_button=SimpleNamespace(setEnabled=MagicMock()),
            loading_overlay=SimpleNamespace(show=MagicMock()),
        )
        scene.window = window
        menu = SimpleNamespace(node=node)
        # Use real unbound method so no temporary QMenu needs a GUI to exist.
        with patch("graphite_agents.ChatWorkerThread") as thread_class:
            ChatNodeContextMenu.regenerate_response(menu)
        self.assertIs(window._pending_regeneration_menu, menu)
        thread_class.return_value.finished.connect.assert_called_once()
        thread_class.return_value.error.connect.assert_called_once()

        window.handle_error = MagicMock()
        ChatNodeContextMenu.handle_regeneration_error(menu, "Network error")
        self.assertIsNone(window._pending_regeneration_menu)
        window.handle_error.assert_called_once_with("Network error")


class ChartSafetyTests(unittest.TestCase):
    def setUp(self):
        self.agent = ChartDataAgent()

    def test_rejects_excessive_chart_values(self):
        with self.assertRaisesRegex(ValueError, "limit"):
            self.agent.normalize_chart_payload(
                {"values": [1] * (MAX_CHART_VALUES + 1)}, "histogram"
            )

    def test_rejects_nonfinite_chart_values(self):
        for bad in ("nan", "inf", "-inf", "1e309"):
            with self.subTest(value=bad), self.assertRaisesRegex(ValueError, "finite"):
                self.agent.normalize_chart_payload({"values": [bad]}, "histogram")

    def test_rejects_unreasonable_bins(self):
        with self.assertRaisesRegex(ValueError, "bins"):
            self.agent.normalize_chart_payload(
                {"values": [1, 2], "bins": 100_000_000}, "histogram"
            )

    def test_rejects_oversized_sankey(self):
        with self.assertRaisesRegex(ValueError, "Sankey"):
            self.agent.normalize_chart_payload(
                {"data": {"nodes": [{"name": str(i)} for i in range(MAX_SANKEY_NODES + 1)],
                          "links": []}}, "sankey"
            )

    def test_rejects_negative_pie_values(self):
        normalized = self.agent.normalize_chart_payload(
            {"labels": ["A", "B"], "values": [-1, 2]}, "pie"
        )
        valid, message = self.agent.validate_chart_data(normalized, "pie")
        self.assertFalse(valid)
        self.assertIn("non-negative", message)

    def test_rejects_oversized_llm_response_before_json_parse(self):
        with patch("graphite_agents.api_provider.chat",
                   return_value={"message": {"content": "x" * (MAX_CHART_RESPONSE_CHARS + 1)}}):
            response = json.loads(self.agent.get_response("Data", "bar"))
        self.assertIn("too large", response["error"])


class ProviderTests(unittest.TestCase):
    def test_ollama_chat_has_finite_timeout(self):
        with patch("api_provider.ollama.Client") as client:
            with patch.object(api_provider, "USE_API_MODE", False):
                api_provider.chat(config.TASK_CHAT, [{"role": "user", "content": "Hello"}])
        self.assertGreater(client.call_args.kwargs["timeout"], 0)
        client.return_value.chat.assert_called_once()


if __name__ == "__main__":
    unittest.main()

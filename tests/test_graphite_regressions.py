"""Regression tests for branch isolation and durable chat snapshots.

Run from the repository root:
    python -m unittest discover -s tests -v
"""
import copy
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "graphite_app" / "graphite_app"))

import api_provider
import graphite_config as config
from graphite_agents import ChatAgent
from graphite_core import ChatDatabase, ChatSessionManager
from graphite_app import ChatWindow


def empty_chat():
    return {
        "nodes": [],
        "connections": [],
        "frames": [],
        "charts": [],
        "view_state": {"zoom_factor": 1.0, "scroll_position": {"x": 0, "y": 0}},
    }


def note(text):
    return {
        "content": text,
        "position": {"x": 10, "y": 20},
        "size": {"width": 120, "height": 60},
        "color": "#444444",
        "header_color": None,
    }


def pin(title):
    return {"title": title, "note": "", "position": {"x": 1, "y": 2}}


class ChatBranchTests(unittest.TestCase):
    def test_branches_do_not_leak_context_or_duplicate_current_message(self):
        agent = ChatAgent("Test", "You are testing.")
        observed = []

        def provider_chat(task, messages):
            self.assertEqual(task, config.TASK_CHAT)
            observed.append(copy.deepcopy(messages))
            return {"message": {"content": "ok"}}

        branch_a = [
            {"role": "user", "content": "Common question"},
            {"role": "assistant", "content": "Common answer"},
            {"role": "user", "content": "Private branch A"},
        ]
        branch_b = [
            {"role": "user", "content": "Common question"},
            {"role": "assistant", "content": "Common answer"},
            {"role": "user", "content": "Branch B"},
        ]

        with patch("graphite_agents.api_provider.chat", side_effect=provider_chat):
            agent.get_response("Private branch A", branch_a)
            agent.get_response("Branch B", branch_b)

        self.assertEqual(observed[0][1:], branch_a)
        self.assertEqual(observed[1][1:], branch_b)
        self.assertNotIn("Private branch A", str(observed[1]))
        self.assertEqual(observed[1][-1]["content"], "Branch B")

    def test_ancestry_has_each_turn_once(self):
        root = SimpleNamespace(text="Hello", is_user=True, parent_node=None)
        answer = SimpleNamespace(text="Hi", is_user=False, parent_node=root)
        child = SimpleNamespace(text="Follow up", is_user=True, parent_node=answer)
        self.assertEqual(
            ChatWindow.build_conversation_history(None, child),
            [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi"},
                {"role": "user", "content": "Follow up"},
            ],
        )


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.db = ChatDatabase.__new__(ChatDatabase)
        self.db.db_path = Path(self.directory.name) / "test.db"
        self.db.init_database()

    def tearDown(self):
        self.directory.cleanup()

    def test_notes_only_canvas_can_be_saved(self):
        manager = ChatSessionManager.__new__(ChatSessionManager)
        manager.db = self.db
        manager.current_chat_id = None
        manager.title_generator = SimpleNamespace(generate_title=lambda msg: "Notes")
        snapshot = {"chat_data": empty_chat(), "notes_data": [note("Important")], "pins_data": []}
        manager._saved_snapshot = {"chat_data": empty_chat(), "notes_data": [], "pins_data": []}
        manager.capture_current_snapshot = lambda: copy.deepcopy(snapshot)

        self.assertTrue(manager.has_unsaved_changes())
        self.assertTrue(manager.save_current_chat())
        self.assertEqual(self.db.load_notes(manager.current_chat_id)[0]["content"], "Important")
        self.assertFalse(manager.has_unsaved_changes())

        snapshot["notes_data"][0]["content"] = "Edited"
        self.assertTrue(manager.has_unsaved_changes())
        self.assertTrue(manager.save_current_chat())
        self.assertEqual(self.db.load_notes(manager.current_chat_id)[0]["content"], "Edited")

    def test_failed_save_rolls_back_chat_notes_and_pins(self):
        original = empty_chat()
        chat_id = self.db.save_snapshot("Test", original, [note("Original")], [pin("First")])
        updated = {**original, "nodes": [{"text": "Changed"}]}

        with self.assertRaises(KeyError):
            self.db.save_snapshot("Test", updated, [{"content": "missing properties"}], [], chat_id)

        self.assertEqual(self.db.load_chat(chat_id)["data"], original)
        self.assertEqual(self.db.load_notes(chat_id)[0]["content"], "Original")
        self.assertEqual(self.db.load_pins(chat_id)[0]["title"], "First")

    def test_empty_new_canvas_is_not_written(self):
        manager = ChatSessionManager.__new__(ChatSessionManager)
        manager.current_chat_id = None
        manager.capture_current_snapshot = lambda: {
            "chat_data": empty_chat(), "notes_data": [], "pins_data": []
        }
        self.assertFalse(manager.save_current_chat())


class SetupTests(unittest.TestCase):
    def test_default_local_models_are_checked(self):
        installed = SimpleNamespace(models=[
            SimpleNamespace(model=config.OLLAMA_MODELS[config.TASK_CHAT])
        ])
        with patch("api_provider.ollama.Client") as client:
            client.return_value.list.return_value = installed
            missing = api_provider.get_missing_ollama_models()
        self.assertEqual(
            missing,
            sorted({
                config.OLLAMA_MODELS[config.TASK_TITLE],
                config.OLLAMA_MODELS[config.TASK_CHART],
            }),
        )


if __name__ == "__main__":
    unittest.main()

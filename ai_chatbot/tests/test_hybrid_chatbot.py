import tempfile
import unittest
from hybrid_chatbot import HybridChatbot, ConversationStore, ProviderError

class FakeProvider:
    def __init__(self, answer="پاسخ آزمایشی"): self.answer, self.calls = answer, []
    def complete(self, messages, **kwargs):
        self.calls.append(messages)
        return self.answer

class BrokenProvider:
    def complete(self, *args, **kwargs): raise ProviderError("offline")

class ChatbotTests(unittest.TestCase):
    def test_offline_mode_is_labeled(self):
        with tempfile.TemporaryDirectory() as d:
            r = HybridChatbot(memory_dir=d).chat("a", "سلام")
            self.assertEqual(r["mode"], "offline")
            self.assertIn("آفلاین", r["answer"])

    def test_provider_and_context(self):
        with tempfile.TemporaryDirectory() as d:
            p = FakeProvider("پاسخ")
            b = HybridChatbot(provider=p, memory_dir=d)
            b.chat("a", "سلام")
            self.assertEqual(b.chat("a", "ادامه بده")["mode"], "online")
            self.assertTrue(any(x["role"] == "assistant" for x in p.calls[1]))

    def test_history_persists(self):
        with tempfile.TemporaryDirectory() as d:
            HybridChatbot(provider=FakeProvider(), memory_dir=d).chat("a", "اول")
            self.assertEqual(len(HybridChatbot(memory_dir=d).get_history("a")), 2)

    def test_clear(self):
        with tempfile.TemporaryDirectory() as d:
            b = HybridChatbot(provider=FakeProvider(), memory_dir=d)
            b.chat("a", "سلام")
            b.clear_conversation("a")
            self.assertEqual(b.get_history("a"), [])

    def test_empty_message(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError): HybridChatbot(memory_dir=d).chat("a", " ")

    def test_provider_failure_fallback(self):
        with tempfile.TemporaryDirectory() as d:
            r = HybridChatbot(provider=BrokenProvider(), memory_dir=d).chat("a", "سوال")
            self.assertEqual(r["mode"], "offline_fallback")
            self.assertIn("provider_error", r)

    def test_store_limits_history(self):
        with tempfile.TemporaryDirectory() as d:
            s = ConversationStore(d, max_messages=4)
            s.save("a", [{"role":"user","content":str(i)} for i in range(8)])
            self.assertEqual(len(s.load("a")), 4)

    def test_store_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError): ConversationStore(d).save("../x", [])

if __name__ == "__main__": unittest.main()

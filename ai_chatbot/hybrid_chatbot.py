"""Provider-agnostic hybrid conversational AI core.
Supports OpenAI-compatible chat-completions endpoints, persistent history,
and a clearly-labeled offline fallback. Python standard library only.
"""
from __future__ import annotations
import json, os, time, urllib.error, urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_SYSTEM_PROMPT = """تو یک دستیار هوش مصنوعی فارسی‌زبان، دقیق، صمیمی و مسئولیت‌پذیر هستی.
- زبان کاربر را حفظ کن؛ اگر فارسی نوشت، فارسی روان و طبیعی پاسخ بده.
- مستقیم و روشن پاسخ بده و در صورت نیاز مرحله‌به‌مرحله توضیح بده.
- اگر چیزی را نمی‌دانی، صادقانه بگو و حدس را جای واقعیت نگذار.
- اطلاعات حساس را بدون اجازه در حافظه پایدار ذخیره نکن.
- ادعای انجام کاری را که انجام نداده‌ای مطرح نکن.
"""

class ChatbotError(RuntimeError): pass
class ProviderError(ChatbotError): pass

class ConversationStore:
    def __init__(self, directory: str | Path, max_messages: int = 80):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.max_messages = max(4, int(max_messages))

    def _path(self, conversation_id: str) -> Path:
        safe = "".join(c for c in str(conversation_id) if c.isalnum() or c in "-_")
        if not safe: raise ValueError("conversation_id must contain letters or digits")
        return self.directory / f"{safe}.json"

    def load(self, conversation_id: str) -> List[Dict[str, str]]:
        path = self._path(conversation_id)
        if not path.exists(): return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return [{"role": x["role"], "content": x["content"]}
                    for x in data.get("messages", [])
                    if x.get("role") in ("user", "assistant") and isinstance(x.get("content"), str)][-self.max_messages:]
        except (OSError, ValueError, TypeError, KeyError):
            return []

    def save(self, conversation_id: str, messages: List[Dict[str, str]]) -> None:
        path = self._path(conversation_id)
        payload = {"schema_version": 1, "updated_at": int(time.time()),
                   "messages": messages[-self.max_messages:]}
        temp = path.with_suffix(".tmp")
        temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        temp.replace(path)

    def clear(self, conversation_id: str) -> None:
        path = self._path(conversation_id)
        if path.exists(): path.unlink()


class OpenAICompatibleProvider:
    def __init__(self, base_url: str, model: str, api_key: Optional[str] = None,
                 timeout: float = 45.0, extra_headers: Optional[Dict[str, str]] = None):
        self.base_url, self.model = base_url.rstrip("/"), model
        self.api_key, self.timeout = api_key, timeout
        self.extra_headers = dict(extra_headers or {})

    def complete(self, messages: List[Dict[str, str]], temperature: float = 0.7,
                 max_tokens: int = 900) -> str:
        if not self.base_url or not self.model:
            raise ProviderError("آدرس سرویس یا نام مدل تنظیم نشده است.")
        url = self.base_url
        if not url.endswith("/chat/completions"): url += "/chat/completions"
        body = json.dumps({"model": self.model, "messages": messages,
                           "temperature": temperature, "max_tokens": max_tokens}).encode()
        headers = {"Content-Type": "application/json", **self.extra_headers}
        if self.api_key: headers["Authorization"] = f"Bearer {self.api_key}"
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
            answer = payload["choices"][0]["message"]["content"]
            if isinstance(answer, list):
                answer = "".join(p.get("text", "") for p in answer if isinstance(p, dict))
            if not isinstance(answer, str) or not answer.strip():
                raise ProviderError("مدل پاسخ متنی معتبری برنگرداند.")
            return answer.strip()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            raise ProviderError(f"خطای سرویس مدل ({exc.code}): {detail}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise ProviderError(f"ارتباط با مدل برقرار نشد: {exc}") from exc
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise ProviderError("ساختار پاسخ مدل معتبر نیست.") from exc


class HybridChatbot:
    def __init__(self, provider: Optional[OpenAICompatibleProvider] = None,
                 memory_dir: str | Path = ".chatbot_memory",
                 system_prompt: str = DEFAULT_SYSTEM_PROMPT,
                 max_context_messages: int = 24, offline_fallback: bool = True):
        self.provider = provider
        self.store = ConversationStore(memory_dir)
        self.system_prompt = system_prompt
        self.max_context_messages = max(2, int(max_context_messages))
        self.offline_fallback = offline_fallback

    @classmethod
    def from_env(cls, memory_dir: str | Path = ".chatbot_memory"):
        base, model = os.getenv("AI_BASE_URL", "").strip(), os.getenv("AI_MODEL", "").strip()
        key = os.getenv("AI_API_KEY", "").strip() or None
        provider = OpenAICompatibleProvider(base, model, key) if base and model else None
        return cls(provider=provider, memory_dir=memory_dir)

    def chat(self, conversation_id: str, user_text: str) -> Dict[str, Any]:
        text = str(user_text).strip()
        if not text: raise ValueError("پیام خالی است.")
        history = self.store.load(conversation_id)
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(history[-self.max_context_messages:])
        messages.append({"role": "user", "content": text})
        provider_error = None
        if self.provider:
            try:
                answer, mode = self.provider.complete(messages), "online"
            except ProviderError as exc:
                if not self.offline_fallback: raise
                answer, mode, provider_error = self._offline_reply(text), "offline_fallback", str(exc)
        else:
            if not self.offline_fallback: raise ProviderError("مدل آنلاین پیکربندی نشده است.")
            answer, mode = self._offline_reply(text), "offline"
        updated = history + [{"role": "user", "content": text}, {"role": "assistant", "content": answer}]
        self.store.save(conversation_id, updated)
        result = {"answer": answer, "mode": mode, "conversation_id": conversation_id,
                  "history_messages": len(updated), "engine_version": "2.0.0"}
        if provider_error: result["provider_error"] = provider_error
        return result

    @staticmethod
    def _offline_reply(text: str) -> str:
        q = text.casefold()
        if any(w in q for w in ("سلام", "درود", "hello", "hi")):
            return "سلام! خوش اومدی 😊 الان در حالت آفلاین پایه هستم. برای گفت‌وگوی هوشمندتر، اتصال مدل زبانی رو فعال کن."
        if any(w in q for w in ("تو کی هستی", "اسمت چیه", "who are you")):
            return "من هسته گفت‌وگوی ترکیبی تو هستم. فعلاً مدل زبانی آنلاین در دسترس نیست؛ بنابراین پاسخ‌هایم محدودند."
        return "پیامت دریافت شد، اما مدل زبانی در دسترس نیست. تنظیمات اتصال مدل را بررسی کن. این پاسخ آفلاین پایه است، نه پاسخ تولیدشده توسط یک مدل زبانی."

    def clear_conversation(self, conversation_id: str) -> None:
        self.store.clear(conversation_id)

    def get_history(self, conversation_id: str):
        return self.store.load(conversation_id)


def build_default_bot(memory_dir: str | Path = ".chatbot_memory"):
    return HybridChatbot.from_env(memory_dir)

"""
OpenRouter API client for Sentinel.
Handles chat completions via OpenRouter's API in a background thread.
"""

import json
import urllib.request
import urllib.error
from typing import List, Dict

from PyQt6.QtCore import QThread, pyqtSignal


class OpenRouterClient:
    """Client for the OpenRouter chat completions API."""

    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Send a chat completion request.

        Args:
            messages: List of {"role": "user"|"assistant"|"system", "content": "..."}.

        Returns:
            The assistant's response text.

        Raises:
            urllib.error.HTTPError: On API errors.
        """
        payload = json.dumps({
            "model": self.model,
            "messages": messages,
        }).encode("utf-8")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/sentinel-app",
            "X-Title": "Sentinel",
        }

        req = urllib.request.Request(
            self.BASE_URL,
            data=payload,
            headers=headers,
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        return data["choices"][0]["message"]["content"]


class ChatWorker(QThread):
    """Background thread for non-blocking API calls."""

    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, client: OpenRouterClient, messages: List[Dict[str, str]]):
        super().__init__()
        self.client = client
        self.messages = messages

    def run(self):
        try:
            response = self.client.chat(self.messages)
            self.response_ready.emit(response)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            try:
                err_data = json.loads(body)
                msg = err_data.get("error", {}).get("message", body)
            except json.JSONDecodeError:
                msg = body
            self.error_occurred.emit(f"API Error ({e.code}): {msg}")
            
            if "support image input" in msg.lower():
                self.error_occurred.emit(
                    "This model doesn't support images.\n"
                    "Try using a vision model like 'openai/gpt-4o' "
                    "or 'google/gemini-pro-1.5'."
                )
        except Exception as e:
            self.error_occurred.emit(str(e))

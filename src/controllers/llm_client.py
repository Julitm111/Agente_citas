from typing import Any, Dict, List, Optional

import requests

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = "gpt-4.1-mini"


class LLMClient:
    def __init__(self, api_key: str, model: str, api_url: str = OPENAI_API_URL):
        self.api_key = api_key
        self.model = model
        self.api_url = api_url

    def chat(
        self,
        messages: List[Dict[str, str]],
        response_format: Optional[Dict[str, str]] = None,
    ) -> Optional[str]:
        """Envia un chat completion a OpenAI y devuelve el contenido del mensaje del asistente.

        Devuelve None en caso de error o respuesta inesperada.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 200,
        }
        if response_format:
            payload["response_format"] = response_format

        try:
            response = requests.post(
                self.api_url, headers=headers, json=payload, timeout=30
            )
            if response.status_code != 200:
                return None
            data = response.json()
            return (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content")
            )
        except (requests.RequestException, ValueError):
            return None

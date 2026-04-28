import json
from collections.abc import AsyncIterator

import httpx
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class OllamaClient:
    """Async client for the Ollama local LLM daemon."""

    def __init__(self, base_url: str = settings.ollama_url, model: str = settings.ollama_model) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=10.0))

    async def health_check(self) -> bool:
        try:
            resp = await self._client.get(f"{self._base_url}/api/tags")
            return resp.status_code == 200
        except Exception:
            return False

    async def stream_completion(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.2,
    ) -> AsyncIterator[str]:
        payload = {
            "model": self._model,
            "prompt": prompt,
            "system": system,
            "stream": True,
            "options": {"temperature": temperature},
        }
        try:
            async with self._client.stream(
                "POST",
                f"{self._base_url}/api/generate",
                json=payload,
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        chunk = json.loads(line)
                        token = chunk.get("response", "")
                        if token:
                            yield token
                        if chunk.get("done"):
                            break
                    except json.JSONDecodeError:
                        logger.warning("ollama_chunk_parse_error", line=line[:100])
        except httpx.HTTPStatusError as exc:
            logger.error("ollama_http_error", status=exc.response.status_code)
            raise
        except httpx.ConnectError:
            logger.error("ollama_connect_error", url=self._base_url)
            raise

    async def complete(self, prompt: str, system: str = "", temperature: float = 0.2) -> str:
        """Non-streaming completion — accumulates all tokens."""
        tokens: list[str] = []
        async for token in self.stream_completion(prompt, system, temperature):
            tokens.append(token)
        return "".join(tokens)

    async def aclose(self) -> None:
        await self._client.aclose()


_client_instance: OllamaClient | None = None


def get_ollama_client() -> OllamaClient:
    global _client_instance
    if _client_instance is None:
        _client_instance = OllamaClient()
    return _client_instance

from typing import Any

import httpx

from app.config import Settings


class EmbeddingServiceError(RuntimeError):
    pass


class JinaEmbeddingService:
    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self.settings = settings
        self._client = client

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.settings.request_timeout_seconds)
        return self._client

    async def embed_query(self, text: str) -> list[float]:
        embeddings = await self.embed_texts([text], task=self.settings.jina_query_task)
        return embeddings[0]

    async def embed_passages(self, texts: list[str]) -> list[list[float]]:
        return await self.embed_texts(texts, task=self.settings.jina_passage_task)

    async def embed_texts(self, texts: list[str], *, task: str) -> list[list[float]]:
        cleaned = [text.strip() for text in texts if text and text.strip()]
        if not cleaned:
            return []

        payload: dict[str, Any] = {
            "model": self.settings.jina_embedding_model,
            "input": [
                _with_retrieval_prefix(text, task, self.settings.jina_embedding_model)
                for text in cleaned
            ],
            "dimensions": self.settings.jina_embedding_dimensions,
            "task": task,
            "truncate": True,
        }
        headers = {
            "Authorization": f"Bearer {self.settings.jina_api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = await self.client.post(
                self.settings.jina_embedding_endpoint,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise EmbeddingServiceError(f"Jina embedding request failed: {exc}") from exc

        body = response.json()
        data = body.get("data")
        if not isinstance(data, list):
            raise EmbeddingServiceError("Jina embedding response did not include a data array")

        embeddings = [_embedding_from_item(item) for item in sorted(data, key=_embedding_index)]
        if len(embeddings) != len(cleaned):
            raise EmbeddingServiceError("Jina embedding response count did not match input count")
        return embeddings


def _with_retrieval_prefix(text: str, task: str, model: str) -> str:
    if "v5" not in model:
        return text
    if task == "retrieval.query" and not text.startswith("Query:"):
        return f"Query: {text}"
    if task == "retrieval.passage" and not text.startswith("Document:"):
        return f"Document: {text}"
    return text


def _embedding_index(item: Any) -> int:
    if isinstance(item, dict):
        return int(item.get("index") or 0)
    return 0


def _embedding_from_item(item: Any) -> list[float]:
    if not isinstance(item, dict) or not isinstance(item.get("embedding"), list):
        raise EmbeddingServiceError("Jina embedding item did not include an embedding array")
    return [float(value) for value in item["embedding"]]

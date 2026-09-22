from __future__ import annotations

import json
import logging
from urllib import error, request

from app.core.config import Settings
from app.features.video_search.application.services.agent import (
    clean_string_list,
    local_plan,
)
from app.features.video_search.domain.models import SearchPlan

logger = logging.getLogger(__name__)


class LlmPlanner:
    """OpenAI-compatible planner that calls a chat completions endpoint."""

    name = "llm"

    def __init__(self, settings: Settings) -> None:
        self._api_key = settings.kis_llm_api_key.strip()
        self._endpoint = settings.kis_llm_endpoint.strip()
        self._model = settings.kis_llm_model.strip()

    def is_available(self) -> bool:
        return bool(self._api_key and self._endpoint and self._model)

    def plan(self, query: str, collection_ids: list[str]) -> SearchPlan:
        if not self.is_available():
            return local_plan(query, collection_ids)

        fallback = local_plan(query, collection_ids)
        prompt = (
            "Analyze this Vietnamese/English video retrieval goal. Return JSON only "
            "with string arrays objects, actions, scenes and a concise English search_query. "
            f"Goal: {query}"
        )
        payload = json.dumps(
            {
                "model": self._model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
                "response_format": {"type": "json_object"},
            }
        ).encode("utf-8")
        http_request = request.Request(
            self._endpoint,
            data=payload,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=20) as response:
                body = json.loads(response.read().decode("utf-8"))
            content = body["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            return SearchPlan(
                intent="video_retrieval",
                original_query=query.strip(),
                search_query=str(parsed.get("search_query") or fallback.search_query).strip(),
                objects=tuple(clean_string_list(parsed.get("objects"), fallback.objects)),
                actions=tuple(clean_string_list(parsed.get("actions"), fallback.actions)),
                scenes=tuple(clean_string_list(parsed.get("scenes"), fallback.scenes)),
                collection_ids=tuple(collection_ids),
                planner=f"llm:{self._model}",
            )
        except (error.URLError, TimeoutError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            logger.warning("LLM planner unavailable; using local planner: %s", exc)
            return fallback

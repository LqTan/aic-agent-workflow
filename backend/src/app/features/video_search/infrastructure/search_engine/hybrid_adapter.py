from __future__ import annotations

import logging

from app.core.config import Settings
from app.core.errors import SearchServiceUnavailable
from app.features.search_engine import demo as demo_engine
from app.features.search_engine import kis as kis_engine
from app.features.video_search.application.abstractions import SearchEnginePort

logger = logging.getLogger(__name__)


class HybridSearchEngineAdapter(SearchEnginePort):
    """Adapter that delegates to the real hybrid index, or to the demo fallback."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._mode = "demo" if settings.kis_demo_mode else "hybrid"

    @property
    def mode(self) -> str:
        return self._mode

    def search(
        self,
        *,
        query: str,
        collection_ids: list[str],
        top_k: int,
    ) -> tuple[dict, list[dict]]:
        engine = demo_engine if self._mode == "demo" else kis_engine
        results = self._call(engine.search, query=query, collection_ids=collection_ids, top_k=top_k)
        return (
            {"keys": query.split(), "effective_collection_ids": collection_ids},
            results,
        )

    def inspect(
        self,
        *,
        query: str,
        collection_ids: list[str],
        top_k: int,
    ) -> tuple[dict, dict]:
        engine = demo_engine if self._mode == "demo" else kis_engine
        trace = self._call(engine.inspect, query=query, collection_ids=collection_ids, top_k=top_k)
        return (
            {"keys": query.split(), "effective_collection_ids": collection_ids},
            trace,
        )

    def _call(self, function, **kwargs):
        try:
            return function(**kwargs)
        except Exception as exc:
            unavailable_errors = (FileNotFoundError, ImportError, ModuleNotFoundError, OSError)
            if isinstance(exc, unavailable_errors) or exc.__class__.__name__ == "SearchServiceUnavailable":
                raise SearchServiceUnavailable(
                    str(exc) or "Search index hoặc dữ liệu KIS chưa sẵn sàng."
                ) from exc
            logger.exception("KIS search engine failed")
            raise

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class DomainError(Exception):
    """Base error for any application/domain violation."""

    status_code: int = 400
    code: str = "domain_error"

    def __init__(self, message: str, *, details: Any | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.details is not None:
            payload["details"] = self.details
        return payload


class InvalidSearchRequest(DomainError):
    status_code = 400
    code = "invalid_search_request"


class SearchServiceUnavailable(DomainError):
    status_code = 503
    code = "search_service_unavailable"


class SearchServiceFailed(DomainError):
    status_code = 500
    code = "search_service_failed"


class RunNotFound(DomainError):
    status_code = 404
    code = "run_not_found"


@dataclass(frozen=True)
class ApiErrorResponse:
    error: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"error": self.error}

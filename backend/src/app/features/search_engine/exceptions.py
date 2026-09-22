from app.core.errors import SearchServiceUnavailable  # noqa: F401  (re-export)


class IndexBuildError(RuntimeError):
    """The input dataset is inconsistent and an index cannot be built safely."""

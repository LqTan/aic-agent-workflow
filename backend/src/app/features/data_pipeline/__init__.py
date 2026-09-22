"""Data pipeline for the AIC hybrid search index.

Ported from ``BE/data_processing/pipeline.py``. Generates a manifest CSV
from the raw dataset layout (``data/{keyframes, map-keyframes, objects,
videos, clip-features-32}``), validates it, and writes a
``collection.json`` summarising which videos belong to which collection.
"""

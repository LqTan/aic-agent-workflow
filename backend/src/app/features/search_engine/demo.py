from __future__ import annotations

import re

from .lang import VI_TO_EN, normalize_ascii

CATALOG = [
    {
        "keyframe_id": "DEMO_V001_000001",
        "collection_id": "DEMO",
        "video_id": "DEMO_V001",
        "frame_number": 75,
        "timestamp_ms": 3000,
        "image_path": "keyframes/DEMO_V001/001.png",
        "video_path": "videos/DEMO_V001.mp4",
        "concepts": {"person", "bicycle", "riding", "street", "outdoor"},
        "domains": ["transport", "outdoor"],
    },
    {
        "keyframe_id": "DEMO_V001_000002",
        "collection_id": "DEMO",
        "video_id": "DEMO_V001",
        "frame_number": 150,
        "timestamp_ms": 6000,
        "image_path": "keyframes/DEMO_V001/002.png",
        "video_path": "videos/DEMO_V001.mp4",
        "concepts": {"woman", "walking", "street", "outdoor", "red shirt"},
        "domains": ["people", "outdoor"],
    },
    {
        "keyframe_id": "DEMO_V001_000003",
        "collection_id": "DEMO",
        "video_id": "DEMO_V001",
        "frame_number": 225,
        "timestamp_ms": 9000,
        "image_path": "keyframes/DEMO_V001/003.png",
        "video_path": "videos/DEMO_V001.mp4",
        "concepts": {"man", "motorcycle", "riding", "street", "outdoor"},
        "domains": ["transport", "outdoor"],
    },
    {
        "keyframe_id": "DEMO_V001_000004",
        "collection_id": "DEMO",
        "video_id": "DEMO_V001",
        "frame_number": 300,
        "timestamp_ms": 12000,
        "image_path": "keyframes/DEMO_V001/004.png",
        "video_path": "videos/DEMO_V001.mp4",
        "concepts": {"person", "car", "driving", "street", "outdoor"},
        "domains": ["transport", "outdoor"],
    },
    {
        "keyframe_id": "DEMO_V001_000005",
        "collection_id": "DEMO",
        "video_id": "DEMO_V001",
        "frame_number": 375,
        "timestamp_ms": 15000,
        "image_path": "keyframes/DEMO_V001/005.png",
        "video_path": "videos/DEMO_V001.mp4",
        "concepts": {"child", "dog", "running", "beach", "outdoor"},
        "domains": ["animals", "outdoor"],
    },
    {
        "keyframe_id": "DEMO_V001_000006",
        "collection_id": "DEMO",
        "video_id": "DEMO_V001",
        "frame_number": 450,
        "timestamp_ms": 18000,
        "image_path": "keyframes/DEMO_V001/006.png",
        "video_path": "videos/DEMO_V001.mp4",
        "concepts": {"woman", "phone", "sitting", "office", "indoor"},
        "domains": ["people", "indoor"],
    },
]


def search(*, query: str, collection_ids: list[str], top_k: int) -> list[dict]:
    terms = _query_terms(query)
    allowed = {value.upper() for value in collection_ids}
    ranked = []
    for record in CATALOG:
        if allowed and record["collection_id"] not in allowed and "DEMO" not in allowed:
            continue
        matched = sorted(record["concepts"] & terms)
        coverage = len(matched) / max(len(terms), 1)
        precision = len(matched) / len(record["concepts"])
        score = 0.18 + 0.62 * coverage + 0.20 * precision if matched else 0.08
        ranked.append((min(score, 0.99), matched, record))

    ranked.sort(key=lambda item: (-item[0], item[2]["keyframe_id"]))
    output = []
    for rank, (score, matched, record) in enumerate(ranked[:top_k], start=1):
        output.append(
            {
                "rank": rank,
                "keyframe_id": record["keyframe_id"],
                "collection_id": record["collection_id"],
                "video_id": record["video_id"],
                "frame_number": record["frame_number"],
                "timestamp_ms": record["timestamp_ms"],
                "image_path": record["image_path"],
                "video_path": record["video_path"],
                "score": round(score, 4),
                "domains": list(record["domains"]),
                "routed_domains": list(record["domains"]),
                "matched_objects": matched,
                "score_components": {
                    "clip": round(score, 4),
                    "object_bow": round(len(matched) / max(len(terms), 1), 4),
                    "domain": 1.0 if matched else 0.0,
                },
            }
        )
    return output


def inspect(*, query: str, collection_ids: list[str], top_k: int) -> dict:
    terms = sorted(_query_terms(query))
    return {
        "query": query,
        "clip_query": query,
        "analysis": {
            "normalized_query": normalize_ascii(query),
            "keyword_candidates": terms,
            "expanded_terms": terms,
            "matched_object_vocabulary": [{"term": term, "match_score": 1.0} for term in terms],
        },
        "routing": {
            "selected_domains": ["demo"],
            "domains": [{"domain_id": "demo", "selected": True, "score": 1.0, "lexical_score": 1.0}],
        },
        "candidate_trace": {"trees": [{"tree_key": "demo", "role": "routed", "entry_count": len(CATALOG)}]},
        "index": {
            "format_version": "demo-1",
            "record_count": len(CATALOG),
            "feature_dimension": 0,
            "pca_dimensions": 0,
            "tree_count": 1,
        },
    }


def _query_terms(query: str) -> set[str]:
    normalized = normalize_ascii(query)
    expanded = normalized
    for source, target in sorted(VI_TO_EN.items(), key=lambda item: -len(item[0])):
        expanded = re.sub(rf"\b{re.escape(source)}\b", target, expanded)
    vocabulary = set().union(*(record["concepts"] for record in CATALOG))
    return {term for term in vocabulary if re.search(rf"\b{re.escape(term)}\b", expanded)}

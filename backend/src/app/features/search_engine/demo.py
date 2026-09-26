from __future__ import annotations

import json
import re
from pathlib import Path

from .lang import VI_TO_EN, normalize_ascii

_DATA_ROOT = Path(__file__).resolve().parents[5] / "data" / "objects"
_VIDEOS_ROOT = Path(__file__).resolve().parents[5] / "data" / "keyframes"


def _real_concepts(video_id: str, frame_id: int) -> set[str]:
    """Load object-detection labels for one frame, lowercased."""
    path = _DATA_ROOT / video_id / f"{frame_id:03d}.json"
    try:
        with path.open(encoding="utf-8") as handle:
            payload = json.load(handle)
    except FileNotFoundError:
        return set()
    return {label.lower() for label in payload.get("detection_class_entities", [])}


def _frame_ms(video_id: str, frame_id: int) -> int:
    """Best-effort timestamp lookup from manifest.csv; default 0 if missing."""
    manifest = Path(__file__).resolve().parents[5] / "data" / "manifest.csv"
    if not manifest.exists():
        return 0
    keyframe_id = f"{video_id}_{frame_id:06d}"
    with manifest.open(encoding="utf-8") as handle:
        next(handle)
        for line in handle:
            parts = line.rstrip("\n").split(",")
            if len(parts) < 7:
                continue
            if parts[0] == keyframe_id:
                try:
                    return int(parts[6])
                except ValueError:
                    return 0
    return 0


_BASE_RECORDS: list[dict] = [
    {"video_id": "L21_V001", "frame_number":   1, "hand_concepts": {"person", "bicycle", "street"}},
    {"video_id": "L21_V001", "frame_number":   2, "hand_concepts": {"woman", "walking", "street"}},
    {"video_id": "L21_V001", "frame_number":   3, "hand_concepts": {"motorcycle", "riding", "street"}},
    {"video_id": "L21_V001", "frame_number":   4, "hand_concepts": {"car", "airplane", "street"}},
    {"video_id": "L21_V001", "frame_number":   6, "hand_concepts": {"vehicle", "land vehicle"}},
    {"video_id": "L21_V001", "frame_number":  91, "hand_concepts": {"animal", "dog", "fish"}},
    {"video_id": "L21_V001", "frame_number": 106, "hand_concepts": {"bicycle", "motorcycle"}},
    {"video_id": "L21_V001", "frame_number": 166, "hand_concepts": {"bicycle", "motorcycle"}},
    {"video_id": "L21_V001", "frame_number": 181, "hand_concepts": {"airplane", "flower"}},
    {"video_id": "L21_V001", "frame_number": 211, "hand_concepts": {"airplane", "boat", "tree"}},
    {"video_id": "L21_V001", "frame_number": 256, "hand_concepts": {"animal", "fish"}},
    {"video_id": "L21_V001", "frame_number": 273, "hand_concepts": {"cat", "animal", "pet"}},
    {"video_id": "L21_V001", "frame_number": 301, "hand_concepts": {"bus", "street"}},
    {"video_id": "L21_V002", "frame_number":  27, "hand_concepts": {"flower", "tree"}},
    {"video_id": "L21_V002", "frame_number": 105, "hand_concepts": {"bus", "tree"}},
    {"video_id": "L21_V002", "frame_number": 209, "hand_concepts": {"motorcycle", "tree"}},
    {"video_id": "L21_V002", "frame_number": 248, "hand_concepts": {"airplane", "bicycle", "motorcycle"}},
    {"video_id": "L21_V002", "frame_number": 222, "hand_concepts": {"boat", "flower", "tree"}},
    {"video_id": "L21_V003", "frame_number":  43, "hand_concepts": {"boat", "bus", "tree"}},
    {"video_id": "L21_V003", "frame_number":  57, "hand_concepts": {"animal", "tree"}},
    {"video_id": "L21_V003", "frame_number":  71, "hand_concepts": {"flower", "tree"}},
    {"video_id": "L21_V003", "frame_number": 225, "hand_concepts": {"bird", "fish", "boat", "flower"}},
    {"video_id": "L21_V003", "frame_number": 239, "hand_concepts": {"cat", "dog", "animal"}},
    {"video_id": "L21_V003", "frame_number": 267, "hand_concepts": {"airplane", "animal", "bird"}},
]


def _domain_for(concepts: set[str]) -> list[str]:
    """Map concept vocabulary to display domains."""
    domains: set[str] = set()
    animal_kw = {"animal", "mammal", "dog", "cat", "bird", "fish", "pet", "wildlife"}
    transport_kw = {"car", "motorcycle", "bicycle", "bus", "vehicle", "land vehicle", "airplane", "boat"}
    plant_kw = {"tree", "flower", "plant"}
    people_kw = {"person", "woman", "man", "child", "girl", "boy", "clothing", "human face", "human arm"}
    if concepts & animal_kw:
        domains.add("animals")
    if concepts & transport_kw:
        domains.add("transport")
    if concepts & plant_kw:
        domains.add("nature")
    if concepts & people_kw:
        domains.add("people")
    return sorted(domains) or ["misc"]


CATALOG: list[dict] = [
    {
        "keyframe_id": f"{rec['video_id']}_{rec['frame_number']:06d}",
        "collection_id": rec["video_id"].split("_")[0],
        "video_id": rec["video_id"],
        "frame_number": rec["frame_number"],
        "timestamp_ms": _frame_ms(rec["video_id"], rec["frame_number"]),
        "image_path": f"keyframes/{rec['video_id']}/{rec['frame_number']:03d}.jpg",
        "video_path": f"videos/{rec['video_id']}.mp4",
        "concepts": (
            {c.lower() for c in rec["hand_concepts"]}
            | _real_concepts(rec["video_id"], rec["frame_number"])
        ),
    }
    for rec in _BASE_RECORDS
]

for _record in CATALOG:
    _record["domains"] = _domain_for(_record["concepts"])
    _record["routed_domains"] = _record["domains"]


def search(*, query: str, collection_ids: list[str], top_k: int) -> list[dict]:
    terms = _query_terms(query)
    allowed = {value.upper() for value in collection_ids}
    ranked = []
    for record in CATALOG:
        coll = record["collection_id"].upper()
        if allowed and coll not in allowed and "L21" not in allowed:
            continue
        matched = sorted(record["concepts"] & terms)
        if not matched:
            continue
        coverage = len(matched) / max(len(terms), 1)
        precision = len(matched) / max(len(record["concepts"]), 1)
        score = 0.18 + 0.62 * coverage + 0.20 * precision
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
                "routed_domains": list(record["routed_domains"]),
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
            "format_version": "demo-2",
            "record_count": len(CATALOG),
            "feature_dimension": 0,
            "pca_dimensions": 0,
            "tree_count": 1,
        },
    }


_IRREGULAR: dict[str, str] = {
    "women": "woman",
    "men": "man",
    "children": "child",
    "people": "person",
    "feet": "foot",
    "teeth": "tooth",
    "mice": "mouse",
    "geese": "goose",
    "aircraft": "airplane",
    "ships": "boat",
    "boats": "boat",
    "cars": "car",
    "buses": "bus",
    "dogs": "dog",
    "cats": "cat",
    "trees": "tree",
    "flowers": "flower",
    "birds": "bird",
    "fishes": "fish",
    "animals": "animal",
    "mammals": "mammal",
    "vehicles": "vehicle",
    "bicycles": "bicycle",
    "motorcycles": "motorcycle",
}


def _query_terms(query: str) -> set[str]:
    normalized = normalize_ascii(query)
    expanded = normalized
    for source, targets in sorted(VI_TO_EN.items(), key=lambda item: -len(item[0])):
        for target in targets:
            expanded = re.sub(rf"\b{re.escape(source)}\b", target, expanded)
    vocabulary = set().union(*(record["concepts"] for record in CATALOG))
    matched: set[str] = set()
    for term in vocabulary:
        for pattern in _match_patterns_for(term):
            if re.search(pattern, expanded):
                matched.add(term)
                break
    return matched


def _stem(word: str) -> str:
    """Naive English stemmer that strips plural/gerund/comparative suffixes."""
    if len(word) <= 4:
        return word
    for suffix in ("ies", "ing", "ed", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            stem = word[: -len(suffix)]
            if suffix == "ies":
                stem = stem + "y"
            return stem
    return word


def _match_patterns_for(term: str) -> list[str]:
    """Return regex patterns that match ``term`` plus its common inflections."""
    stem = _stem(term)
    if stem != term:
        inflections = f"(?:{re.escape(stem)})(?:s|ed|ing)?"
    else:
        inflections = re.escape(term)
    pattern = rf"\b{inflections}\b"
    irregular_forms = [form for form, base in _IRREGULAR.items() if base == term]
    extra = [rf"\b{re.escape(form)}\b" for form in irregular_forms]
    return [pattern, *extra]


def _stem(word: str) -> str:
    """Naive English stemmer that strips plural/gerund/comparative suffixes."""
    if len(word) <= 4:
        return word
    for suffix in ("ies", "ing", "ed", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            stem = word[: -len(suffix)]
            if suffix == "ies":
                stem = stem + "y"
            return stem
    return word



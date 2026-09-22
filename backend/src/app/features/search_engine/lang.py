"""Vietnamese ↔ English normalization helpers shared by the planner and demo index."""

from __future__ import annotations

VI_TO_EN: dict[str, str] = {
    "nguoi": "person",
    "dan ong": "man",
    "phu nu": "woman",
    "tre em": "child",
    "xe dap": "bicycle",
    "xe may": "motorcycle",
    "o to": "car",
    "xe buyt": "bus",
    "duong pho": "street",
    "ngoai duong": "street",
    "trong nha": "indoor",
    "ngoai troi": "outdoor",
    "ao do": "red shirt",
    "ao xanh": "blue shirt",
    "di bo": "walking",
    "dang di": "riding",
    "cho": "dog",
    "meo": "cat",
    "bien": "beach",
    "san bay": "airport",
}


_VIET_UNICODE = (
    "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễ"
    "ìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữ"
    "ỳýỵỷỹđ"
)
_VIET_ASCII = (
    "aaaaaaaaaaaaaaaaa"
    "eeeeeeeeeee"
    "iiiiiooooooooooooooooouuuuuuuuuuuyyyyyd"
)


def normalize_ascii(text: str) -> str:
    replacements = str.maketrans(_VIET_UNICODE, _VIET_ASCII)
    return " ".join(text.lower().translate(replacements).split())

from typing import Any, Dict


def normalize_id(doc: Dict[str, Any]) -> Dict[str, Any]:
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])  # type: ignore[assignment]
    return doc

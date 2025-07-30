from jsonpath_ng import parse
from pathlib import Path as FSPath
import json
from typing import Any, List
from dataclasses import dataclass


class Path:
    def __init__(self, path: str):
        if not path.startswith("$"):
            path = f"${path}"

        self.full_path = path
        try:
            self._parsed = parse(path)
        except Exception as e:
            raise ValueError(f"Invalid JSON path: {path}") from e

    def find(self, payload: Any):
        return self._parsed.find(payload)


@dataclass
class QueryResult:
    value: Any
    paths: List[str]


class ComponentData:
    def __init__(self, data: dict):
        if not data:
            raise ValueError("data dictionary cannot be empty")
        if 'merged_blob' not in data:
            raise ValueError("data must contain 'merged_blob' key")
        if 'metadata_instances' not in data:
            raise ValueError("data must contain 'metadata_instances' key")
        self._data = data

    @classmethod
    def from_file(cls, path: FSPath) -> 'ComponentData':
        if not path.is_absolute():
            raise ValueError("path must be an absolute path")

        with path.open() as f:
            data = json.load(f)

        return cls(data)

    @classmethod
    def from_json(cls, json_str: str) -> 'ComponentData':
        data = json.loads(json_str)
        return cls(data)

    @classmethod
    def from_component_json(cls, json_str: str) -> 'ComponentData':
        componentJSON = json.loads(json_str)
        return cls({
            'merged_blob': componentJSON,
            'metadata_instances': [
                {
                    'payload': componentJSON
                }
            ]
        })

    def get_merged(self, query: Path) -> QueryResult | None:
        if not isinstance(query, Path):
            raise ValueError("query must be a JsonPathExpression")

        payload = self._data.get('merged_blob', {})
        matches = list(query.find(payload))

        if len(matches) == 0:
            return None

        return QueryResult(
            value=(matches[0].value
                   if len(matches) == 1
                   else [match.value for match in matches]),
            paths=[str(match.full_path) for match in matches]
        )

    def get_all(self, query: Path) -> List[QueryResult]:
        if not isinstance(query, Path):
            raise ValueError("query must be a JsonPathExpression")

        deltas = self._data.get('metadata_instances', [])
        results = []

        for instance in reversed(deltas):
            payload = instance.get('payload', {})
            matches = list(query.find(payload))

            if len(matches) == 0:
                continue

            results.append(QueryResult(
                value=(matches[0].value
                       if len(matches) == 1
                       else [match.value for match in matches]),
                paths=[str(match.full_path) for match in matches]
            ))

        return results

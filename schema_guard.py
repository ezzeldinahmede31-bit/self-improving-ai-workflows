"""Structured output enforcement — #6.

A large share of weak-model failures isn't reasoning, it's FORMAT. This module
kills that class of errors for free by:
  1. `JsonSchemaGuard` — coerce + validate against a strict schema; a malformed
     answer is retried with the exact schema as the error message (zero token
     waste since it's the same weak model).
  2. `FunctionCallContract` — a lightweight imitation of function-calling:
     the model must return exactly {name, arguments{...}}; anything else is
     re-challenged.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


@dataclass
class SchemaResult:
    ok: bool
    value: Any = None
    errors: list[str] = field(default_factory=list)
    attempts: int = 1


class JsonSchemaGuard:
    """Strict JSON envelope. Supports the subset of JSON Schema we actually
    need: type, required, properties, items, enums. Anything more exotic is
    routed through a user-supplied `validator` if provided."""

    def __init__(self, schema: dict, max_attempts: int = 3,
                 validator: Optional[Callable[[dict], list[str]]] = None):
        self.schema = schema
        self.max_attempts = max_attempts
        self.validator = validator

    # ---- validation engine ----
    def validate(self, value: Any) -> list[str]:
        errors = []
        self._walk(self.schema, value, "$", errors)
        if not errors and self.validator is not None:
            errors = self.validator(value) or []
        return errors

    def _walk(self, schema: dict, value: Any, path: str, errors: list[str]) -> None:
        typ = schema.get("type")
        if typ == "object":
            if not isinstance(value, dict):
                errors.append(f"{path}: expected object, got {type(value).__name__}")
                return
            for req in schema.get("required", []):
                if req not in value:
                    errors.append(f"{path}: missing required key '{req}'")
            props = schema.get("properties", {})
            for k, vs in props.items():
                if k in value:
                    self._walk(vs, value[k], f"{path}.{k}", errors)
        elif typ == "array":
            if not isinstance(value, list):
                errors.append(f"{path}: expected array")
                return
            for i, item in enumerate(value):
                self._walk(schema.get("items", {}), item, f"{path}[{i}]", errors)
        elif typ == "string":
            if not isinstance(value, str):
                errors.append(f"{path}: expected string")
                return
            enum = schema.get("enum")
            if enum and value not in enum:
                errors.append(f"{path}: value '{value}' not in {enum}")
        elif typ == "integer":
            if not isinstance(value, int) or isinstance(value, bool):
                errors.append(f"{path}: expected integer")
        elif typ == "number":
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                errors.append(f"{path}: expected number")
        elif typ == "boolean":
            if not isinstance(value, bool):
                errors.append(f"{path}: expected boolean")

    # ---- production path: parse -> validate -> retry with schema as feedback ----
    def ensure(self, text: str, draw_fn: Optional[Callable[[str], str]] = None) -> SchemaResult:
        """Parse + validate `text`; on failure, ask the (same cheap) model to
        fix itself with the schema as context. `draw_fn` is the LLM call."""
        attempts = 0
        current = text
        while attempts < self.max_attempts:
            attempts += 1
            value = self._try_parse(current)
            if value is None:
                errors = ["not valid JSON"]
            else:
                errors = self.validate(value)
            if not errors:
                return SchemaResult(ok=True, value=value, attempts=attempts)
            if draw_fn is None:
                break
            # feedback: show the exact schema + errors, ask for corrected JSON
            current = draw_fn(
                "Your previous output was invalid. Fix ONLY the format. "
                f"Required schema: {json.dumps(self.schema)}\n"
                f"Errors: {errors}\n"
                f"Your invalid output was: {current[:400]}\n"
                "Return corrected JSON only."
            )
        return SchemaResult(ok=False, errors=errors, attempts=attempts)

    @staticmethod
    def _try_parse(text: str) -> Any:
        # extract the first balanced JSON object/array if the model wrapped it
        m = re.search(r"[\[\{]", text)
        if not m:
            try:
                return json.loads(text.strip())
            except Exception:
                return None
        start = m.start()
        depth = 0
        for i in range(start, len(text)):
            if text[i] in "[{":
                depth += 1
            elif text[i] in "]}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i + 1])
                    except Exception:
                        return None
        return None


@dataclass
class CallResult:
    ok: bool
    name: str = ""
    arguments: dict = field(default_factory=dict)
    raw: str = ""
    errors: list[str] = field(default_factory=list)


class FunctionCallContract:
    """Model must return {name, arguments}. Re-challenge until it does."""

    def __init__(self, allowed_names: set[str], max_attempts: int = 3,
                 draw_fn: Optional[Callable[[str], str]] = None):
        self.allowed = allowed_names
        self.max_attempts = max_attempts
        self.draw_fn = draw_fn

    def call(self, text: str) -> CallResult:
        attempts = 0
        current = text
        while attempts < self.max_attempts:
            attempts += 1
            parsed = JsonSchemaGuard._try_parse(current)
            errors: list[str] = []
            if isinstance(parsed, dict) and "name" in parsed and "arguments" in parsed:
                if parsed["name"] not in self.allowed:
                    errors.append(f"unknown function '{parsed['name']}'")
                elif not isinstance(parsed["arguments"], dict):
                    errors.append("arguments must be an object")
                else:
                    return CallResult(ok=True, name=parsed["name"],
                                      arguments=parsed["arguments"], raw=current)
            else:
                errors.append("expected {name, arguments} object")
            if self.draw_fn is None:
                return CallResult(ok=False, raw=current, errors=errors)
            current = self.draw_fn(
                f"Return ONLY a JSON object with name in {sorted(self.allowed)} "
                f"and arguments as an object. Errors: {errors}. Previous: {current[:200]}"
            )
        return CallResult(ok=False, raw=current, errors=errors)


if __name__ == "__main__":
    schema = {
        "type": "object",
        "required": ["nodes", "connections"],
        "properties": {
            "nodes": {"type": "array", "items": {"type": "object"}},
            "connections": {"type": "object"},
        },
    }
    good = '{"nodes": [{"name": "a"}], "connections": {}}'
    bad = "Here is my workflow: {nodes: [}, connections missing"
    print("good:", JsonSchemaGuard(schema).ensure(good).ok)
    print("bad :", JsonSchemaGuard(schema).ensure(bad).ok)
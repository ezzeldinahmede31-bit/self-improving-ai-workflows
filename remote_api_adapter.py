"""Universal Remote API Adapter.

Turns a raw cURL / API docs snippet into an n8n declarative configuration that
can be deployed locally as a Custom HTTP wrapper or Community Node — so any
cloud service without an official n8n node becomes a first-class Canvas node
with auth, endpoints and error handling baked in.
"""

import json
import re
import shlex
from dataclasses import dataclass, field
from typing import Any, Optional
from urllib.parse import urlparse, parse_qsl


@dataclass
class RemoteNodeSpec:
    service: str                  # e.g. "stripe"
    method: str
    url: str
    headers: dict = field(default_factory=dict)
    body: Optional[Any] = None
    auth_type: str = "none"       # none | bearer | basic | oauth2 | header
    auth_callback: str = ""       # n8n credential type to reuse

    def to_n8n_node(self, credential_id: str = "", credential_name: str = "") -> dict:
        """Emit an n8n HTTP Request node JSON with credential reference."""
        parameters = {
            "method": self.method.upper(),
            "url": self.url,
            "sendHeaders": True if self.headers else False,
            "headerParameters": {
                "parameters": [
                    {"name": k, "value": v} for k, v in self.headers.items()
                    if k.lower() not in ("authorization",)
                ]
            },
            "sendBody": True if self.body is not None else False,
        }
        if isinstance(self.body, dict) and self.body:
            parameters["bodyParameters"] = {
                "parameters": [
                    {"name": k, "value": v} for k, v in self.body.items()
                ]
            }
        node = {
            "name": f"{self.service.title()} API",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [0, 0],
            "parameters": parameters,
        }
        if self.auth_type in ("bearer", "oauth2", "header"):
            credentials = {}
            if self.auth_type == "bearer":
                credentials["httpHeaderAuth"] = (
                    {"id": credential_id, "name": credential_name or f"{self.service} Bearer"}
                    if credential_id else {}
                )
            node["credentials"] = credentials
        return node


class RemoteAPIAdapter:
    """Parse cURL or declarative descriptors into RemoteNodeSpec."""

    SUPPORTED_AUTH = {
        "bearer": "https://api.example.com/oauth/token",
        "oauth2": "https://api.example.com/oauth2/token",
        "basic": "basic_auth",
    }

    def from_curl(self, curl: str) -> RemoteNodeSpec:
        """Parse a cURL command string into a RemoteNodeSpec."""
        # tolerate the Linux `curl ...` quoting by using shlex with position arg
        try:
            tokens = shlex.split(curl)
        except ValueError as e:
            # fallback: split on whitespace keeping quotes
            tokens = re.findall(r'(\"[^\"]*\"|\'[^\']*\'|\S+)', curl)
            tokens = [t[1:-1] if len(t) > 1 and t[0] in "\"'" else t for t in tokens]
        method = "GET"
        url = ""
        headers: dict[str, str] = {}
        body = None

        i = 0
        while i < len(tokens):
            tok = tokens[i]
            if tok == "curl":
                i += 1
                continue
            if tok in ("-X", "--request"):
                if i + 1 < len(tokens):
                    method = tokens[i + 1].upper()
                    i += 2
                    continue
            elif tok in ("-H", "--header"):
                if i + 1 < len(tokens):
                    hdr = tokens[i + 1]
                    if ":" in hdr:
                        k, v = hdr.split(":", 1)
                        headers[k.strip()] = v.strip()
                    i += 2
                    continue
            elif tok in ("-d", "--data", "--data-raw"):
                if i + 1 < len(tokens):
                    val = tokens[i + 1]
                    try:
                        body = json.loads(val)
                    except json.JSONDecodeError:
                        body = dict(parse_qsl(val.lstrip('?')))
                    i += 2
                    continue
            elif tok in ("-b", "--cookie"):
                i += 2
                continue
            elif tok == "-u":
                i += 2
                continue
            # assume URL token
            if tok.startswith("http://") or tok.startswith("https://"):
                url = tok
            i += 1

        auth_type = "none"
        auth_header = headers.get("Authorization", headers.get("authorization", ""))
        if auth_header.startswith("Bearer"):
            auth_type = "bearer"
        elif auth_header.startswith("Basic"):
            auth_type = "basic"

        return RemoteNodeSpec(
            service=urlparse(url).netloc.split(".")[-2] if url else "api",
            method=method,
            url=url,
            headers=headers,
            body=body,
            auth_type=auth_type,
        )

    def from_openapi(self, openapi: dict, path: str, op: str = "get") -> RemoteNodeSpec:
        """Extract a spec from (part of) an OpenAPI/Swagger doc."""
        try:
            path_item = openapi["paths"].get(path, {})
            oper = path_item.get(op.lower(), {})
            method = op.upper()
            url = openapi.get("servers", [{}])[0].get("url", "") + path
            headers = {
                "Accept": "application/json",
            }
            params = oper.get("parameters", [])
            for p in params:
                if p.get("in") == "header" and "apiKey" in p.get("name", "").lower():
                    headers[p["name"]] = "{{$env.API_KEY}}"
            body_schema = oper.get("requestBody", {})
            body = None
            if body_schema:
                body = {"placeholder": "request body"}
            auth = "oauth2" if any(
                s.get("type") in ("oauth2", "http") for s in oper.get("security", [])
            ) else "none"
            name = openapi.get("info", {}).get("title", "api")
            return RemoteNodeSpec(
                service=name.lower().replace(" ", "-"),
                method=method, url=url, headers=headers, body=body, auth_type=auth,
            )
        except (KeyError, IndexError, TypeError) as e:
            raise ValueError(f"Cannot parse OpenAPI spec: {e}") from e

    def build_subworkflow(self, specs: list[RemoteNodeSpec]) -> dict:
        """Chain several remote API calls into one n8n subworkflow JSON (local)."""
        nodes = []
        connections: dict[str, dict] = {}
        for idx, spec in enumerate(specs):
            node = spec.to_n8n_node()
            node["name"] = f"{spec.service.title()} API" if not nodes else f"{spec.service.title()} {idx}"
            nid = node["name"]
            node["parameters"]["url"] = spec.url
            node["parameters"]["method"] = spec.method.upper()
            nodes.append(node)
            if idx > 0:
                prev = nodes[idx - 1]["name"]
                connections[prev] = {"main": [{"node": nid}]}
        return {"nodes": nodes, "connections": connections}


# ============================================================
# Self-test
# ============================================================
if __name__ == "__main__":
    adapter = RemoteAPIAdapter()
    sample = ("curl -X POST 'https://api.stripe.com/v1/charges' "
              "-H 'Authorization: Bearer sk_test_x' "
              "-H 'Content-Type: application/x-www-form-urlencoded' "
              "-d 'amount=2000&currency=usd'")
    spec = adapter.from_curl(sample)
    print("SPEC:", spec)
    node = spec.to_n8n_node()
    print("NODE:", json.dumps(node, indent=2))
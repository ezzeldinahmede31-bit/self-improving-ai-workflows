#!/usr/bin/env python3
"""Build an on-demand pull index of n8n templates for AI-agent / CRM / Telegram.

Fetches recursive git trees from 3 free GitHub template repos, filters paths
matching the user's 3 domains, and writes memory/n8n-template-index.json with
a direct raw_url per item. Refresh anytime: venv/bin/python scripts/build_template_index.py
Stdlib only. No secrets involved (public repos).
"""
import json
import re
import urllib.request
from datetime import datetime, timezone

REPOS = {
    "scrapernode": {
        "repo": "ScraperNode/awesome-n8n-templates",
        "branch": "main",
        "ai_agent_dirs": {"ai-and-llm", "ai-chatbots", "ai-rag", "ai-tools"},
        "crm_dirs": {"crm", "lead-generation", "lead-nurturing"},
    },
    "aslammac": {
        "repo": "aslammac/n8n-templates",
        "branch": "main",
        "ai_agent_dirs": {"Openai", "AI ML"},
        "crm_dirs": {"HubSpot", "Salesforce", "Pipedrive", "Agilecrm",
                      "Copper", "Zohocrm", "Activecampaign"},
        "telegram_dirs": {"Telegram"},
    },
    "aboalrejal": {
        "repo": "aboalrejal-ai/n8n-workflows",
        "branch": "main",
        "root": "workflows",
        "ai_keywords": re.compile(
            r"ai.agent|openai|rag|assistant|chatbot|gemini|deepseek|ollama|"
            r"langchain|anthropic|claude|mistral|qdrant|pinecone|vector|"
            r"mcp|perplexity|huggingface", re.I),
        "crm_keywords": re.compile(
            r"crm|hubspot|salesforce|pipedrive|copper|zoho|freshsales|"
            r"close\.io|lead|contact|deal|pipeline|customer", re.I),
        "telegram_keywords": re.compile(r"telegram|telebot", re.I),
    },
}

RAW = "https://raw.githubusercontent.com/{repo}/{branch}/{path}"
API = "https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"


def fetch_tree(repo, branch):
    url = API.format(repo=repo, branch=branch)
    req = urllib.request.Request(url, headers={"User-Agent": "template-index-builder"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            data = json.load(r)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        raise RuntimeError(f"tree fetch failed for {repo}@{branch}: {e}")
    if data.get("truncated"):
        raise RuntimeError(f"tree truncated for {repo}")
    return [e["path"] for e in data.get("tree", [])
            if e["type"] == "blob" and e["path"].endswith(".json")]


def label_from_path(path):
    base = path.rsplit("/", 1)[-1]
    name = base[:-5] if base.endswith(".json") else base
    return name.replace("-", " ").replace("_", " ").strip() or base


def build():
    items = []
    # --- scrapernode: templates/<category>/.../workflow.json
    cfg = REPOS["scrapernode"]
    for path in fetch_tree(cfg["repo"], cfg["branch"]):
        parts = path.split("/")
        if len(parts) < 2 or parts[0] != "templates" or "package" in path:
            continue
        cat = parts[1]
        domain = None
        if cat in cfg["ai_agent_dirs"]:
            domain = "ai_agent"
        elif cat in cfg["crm_dirs"]:
            domain = "crm"
        if "telegram" in path.lower():
            domain = "telegram"  # telegram match wins (most specific)
        if domain:
            items.append({"domain": domain, "source": "scrapernode",
                          "path": path,
                          "raw_url": RAW.format(repo=cfg["repo"], branch=cfg["branch"], path=path),
                          "label": label_from_path(path)})
    # --- aslammac: <tooldir>/.../*.json
    cfg = REPOS["aslammac"]
    for path in fetch_tree(cfg["repo"], cfg["branch"]):
        top = path.split("/")[0]
        domain = None
        if top in cfg["ai_agent_dirs"]:
            domain = "ai_agent"
        elif top in cfg["crm_dirs"]:
            domain = "crm"
        elif top in cfg.get("telegram_dirs", set()):
            domain = "telegram"
        if domain:
            items.append({"domain": domain, "source": "aslammac",
                          "path": path,
                          "raw_url": RAW.format(repo=cfg["repo"], branch=cfg["branch"], path=path),
                          "label": label_from_path(path)})
    # --- aboalrejal: workflows/<name>/...
    cfg = REPOS["aboalrejal"]
    for path in fetch_tree(cfg["repo"], cfg["branch"]):
        if not path.startswith(cfg["root"] + "/"):
            continue
        domain = None
        if cfg["telegram_keywords"].search(path):
            domain = "telegram"
        elif cfg["crm_keywords"].search(path):
            domain = "crm"
        elif cfg["ai_keywords"].search(path):
            domain = "ai_agent"
        if domain:
            items.append({"domain": domain, "source": "aboalrejal",
                          "path": path,
                          "raw_url": RAW.format(repo=cfg["repo"], branch=cfg["branch"], path=path),
                          "label": label_from_path(path)})

    counts = {}
    for it in items:
        counts[it["domain"]] = counts.get(it["domain"], 0) + 1
    index = {"generated": datetime.now(timezone.utc).isoformat(),
             "counts": counts, "total": len(items), "items": items}
    with open("memory/n8n-template-index.json", "w") as f:
        json.dump(index, f, ensure_ascii=False)
    print(json.dumps({"total": len(items), "counts": counts}, ensure_ascii=False))


if __name__ == "__main__":
    build()

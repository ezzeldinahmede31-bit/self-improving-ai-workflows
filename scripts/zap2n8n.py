#!/usr/bin/env python3
"""zap2n8n.py — Convert exported Zapier workflow JSON into an n8n workflow skeleton.

Usage:
    venv/bin/python scripts/zap2n8n.py <zap_export.json> [--out n8n_workflow.json]

Reads either:
  - a Zapier Editor Export JSON (File -> Export -> JSON), or
  - a JSON array of SDK draft steps.

Produces:
  1. n8n workflow JSON (draft): mapped nodes + connections + positions.
  2. A mapping report on stdout: each Zap step -> n8n node, plus GAPS list
     (unmapped / premium-only Zapier features that need a Code-node or an
     alternative design).

Mapping table: Zapier app/type -> n8n node type + parameter hints.
Unmapped nodes become Code-node placeholders flagged in the report for the
AI build phase (cloner skill) to fill with real logic.
"""

import argparse
import json
import sys
import uuid
from collections import OrderedDict



def uid():
    return uuid.uuid4().hex[:12]


# (app, operation) -> (n8n node type, typeVersion, param template)
TABLE = {
    ("webhook", "catch_hook"): ("n8n-nodes-base.webhook", 2, {"httpMethod": "POST", "path": "webhook"}),
    ("webhook", "catch_raw"): ("n8n-nodes-base.webhook", 2, {"httpMethod": "POST", "rawBody": True, "path": "zap-clone"}),
    ("schedule", "trigger"): ("n8n-nodes-base.scheduleTrigger", 1.2, {"rule": {"interval": [{"field": "minutes", "minutesInterval": 15}]}}),
    ("gmail", "new_email_inbox"): ("n8n-nodes-base.gmailTrigger", 2, {"pollTimes": {"item": [{"mode": "everyMinute"}]}, "simplify": True}),
    ("gmail", "send_email"): ("n8n-nodes-base.gmail", 2, {"resource": "message", "operation": "send"}),
    ("gmail", "create_draft"): ("n8n-nodes-base.gmail", 2, {"resource": "draft", "operation": "create"}),
    ("google_sheets", "new_spreadsheet_row"): ("n8n-nodes-base.googleSheets", 4, {"resource": "sheet", "operation": "appendOrUpdate"}),
    ("google_sheets", "create_spreadsheet_row"): ("n8n-nodes-base.googleSheets", 4, {"resource": "sheet", "operation": "append"}),
    ("google_sheets", "update_spreadsheet_row"): ("n8n-nodes-base.googleSheets", 4, {"resource": "sheet", "operation": "update"}),
    ("airtable", "new_record"): ("n8n-nodes-base.airtable", 2, {"resource": "record", "operation": "create"}),
    ("airtable", "create_record"): ("n8n-nodes-base.airtable", 2, {"resource": "record", "operation": "create"}),
    ("airtable", "update_record"): ("n8n-nodes-base.airtable", 2, {"resource": "record", "operation": "update"}),
    ("slack", "send_slack_message"): ("n8n-nodes-base.slack", 2, {"resource": "message", "operation": "post"}),
    ("slack", "new_message"): ("n8n-nodes-base.slackTrigger", 2, {"event": "message"}),
    ("discord", "send_message"): ("n8n-nodes-base.discord", 2, {"resource": "message", "operation": "send"}),
    ("telegram_bot", "send_text_message"): ("n8n-nodes-base.telegram", 1.1, {"resource": "message", "operation": "sendMessage"}),
    ("notion", "create_database_item"): ("n8n-nodes-base.notion", 2, {"resource": "databasePage", "operation": "create"}),
    ("notion", "update_database_item"): ("n8n-nodes-base.notion", 2, {"resource": "databasePage", "operation": "update"}),
    ("openai", "send_prompt"): ("n8n-nodes-base.openAi", 1.1, {"resource": "chat", "operation": "complete", "modelId": {"__rl": True, "mode": "list", "value": "gpt-4o-mini"}}),
    ("google_calendar", "new_event"): ("n8n-nodes-base.googleCalendarTrigger", 2, {}),
    ("google_calendar", "create_event"): ("n8n-nodes-base.googleCalendar", 2, {"resource": "event", "operation": "create"}),
    ("trello", "new_card"): ("n8n-nodes-base.trelloTrigger", 2, {}),
    ("trello", "create_card"): ("n8n-nodes-base.trello", 2, {"resource": "card", "operation": "create"}),
    ("typeform", "new_entry"): ("n8n-nodes-base.typeformTrigger", 2, {}),
    ("stripe", "new_payment"): ("n8n-nodes-base.stripeTrigger", 1, {"event": "checkout.session.completed"}),
    ("stripe", "create_payment_link"): ("n8n-nodes-base.stripe", 1, {"resource": "checkout", "operation": "createSession"}),
    ("github", "new_commit"): ("n8n-nodes-base.githubTrigger", 2, {"events": ["push"]}),
    ("github", "create_issue"): ("n8n-nodes-base.github", 2, {"resource": "issue", "operation": "create"}),
    ("hubspot", "new_contact"): ("n8n-nodes-base.hubspotTrigger", 2, {"event": "contact.creation"}),
    ("hubspot", "create_contact"): ("n8n-nodes-base.hubspot", 2, {"resource": "contact", "operation": "create"}),
    ("salesforce", "new_record"): ("n8n-nodes-base.salesforceTrigger", 2, {}),
    ("twilio", "send_sms"): ("n8n-nodes-base.twilio", 1, {"resource": "sms", "operation": "send"}),
    ("mailchimp", "subscribe"): ("n8n-nodes-base.mailchimp", 1, {"resource": "listMember", "operation": "add"}),
    ("rss", "new_item_in_feed"): ("n8n-nodes-base.rssFeedRead", 1, {"url": ""}),
    ("evernote", "create_note"): ("n8n-nodes-base.evernote", 1, {"resource": "note", "operation": "create"}),
    ("wordpress", "create_post"): ("n8n-nodes-base.wordpress", 1, {"resource": "post", "operation": "create"}),
    ("formatter", "date_time_format"): ("n8n-nodes-base.dateTime", 1, {"operation": "formatDate"}),
    ("formatter", "number_format"): ("n8n-nodes-base.code", 1, {"jsCode": "// number format — implement in code\nreturn $input.all();"}),
    ("formatter", "text_format"): ("n8n-nodes-base.code", 1, {"jsCode": "// text format — implement in code\nreturn $input.all();"}),
    ("filter", "only_continue_if"): ("n8n-nodes-base.if", 1, {"conditions": {"options": {"caseSensitive": True}, "conditions": [{}, {}]}}),
    ("code", "run_javascript"): ("n8n-nodes-base.code", 1, {"jsCode": "// ported from Zapier Code by Zapier\nreturn $input.all();"}),
    ("code", "run_python"): ("n8n-nodes-base.code", 1, {"pythonCode": "from typing import Any\n\ndef run(context: dict) -> list[dict]:\n    return context[\"input\"].all()\n", "mode": "runOnceForEachItem"}),
    ("delay", "delay_for"): ("n8n-nodes-base.wait", 1, {"amount": 30, "unit": "seconds"}),
    ("digest", "digest_entries"): ("n8n-nodes-base.code", 1, {"jsCode": "// DIGEST (aggregation) — Zapier-only premium; implement with\n// accumulate() + a schedule, or a data table + SQL aggregation.\nreturn $input.all();"}),
    ("ai", "run_ai_action"): ("n8n-nodes-base.openAi", 1.1, {"resource": "chat", "operation": "complete"}),
    ("paths", "parallel_branches"): ("n8n-nodes-base.switch", 2, {"dataType": "number", "values": [{"value": "1"}, {"value": "2"}]}),
    ("search", "find_record"): ("n8n-nodes-base.if", 1, {"conditions": {"options": {"caseSensitive": True}, "conditions": [{}, {}]}}),
}

# Apps where n8n has a node but we map generically (report as MAPPED_GENERIC)
GENERIC_APPS = [
    "cloudinary", "dropbox", "box", "drive", "google_drive", "onedrive",
    "firebase", "supabase", "postgres", "mysql", "sql_server", "mongodb",
    "google_contacts", "keap", "pipedrive", "close", "zendesk", "freshdesk",
    "intercom", "zoho_crm", "shopify", "woocommerce", "square", "paypal",
    "quickbooks", "xero", "freshbooks", "calendly", "zoom", "google_meet",
    "asana", "copper", "basecamp", "clickup", "linear", "jira", "notion",
    "monday", "todoist", "evernote", "trello", "pinterest", "youtube",
    "vimeo", "twitch", "instagram", "facebook_pages", "twitter", "linkedin",
]

# Zapier step "type" names -> n8n structural node
STEP_TYPES = {
    "trigger": None,   # handled via TABLE with app
    "action": None,
    "create": None,
    "search": ("n8n-nodes-base.if", 1),
    "filter": ("n8n-nodes-base.if", 1),
    "formatter": None,
    "code": ("n8n-nodes-base.code", 1),
    "delay": ("n8n-nodes-base.wait", 1),
    "digest": ("n8n-nodes-base.code", 1),
    "paths": ("n8n-nodes-base.switch", 2),
    "schedule": None,
}


def get_field(step, name, default=None):
    if isinstance(step, dict):
        for k in ("inputs", "params"):
            v = step.get(k)
            if isinstance(v, dict) and name in v:
                return v[name]
        return step.get(name, default)
    return default


def lookup(step):
    app = (get_field(step, "app") or "").lower()
    op = (get_field(step, "operation") or get_field(step, "type") or get_field(step, "action") or "").lower()
    key = (app, op)
    if key in TABLE:
        return TABLE[key], "MAP"
    # try app-only match
    for (a, o), v in TABLE.items():
        if a == app and (o == "" or o == op):
            return v, "MAP"
    # generic app?
    if any(g in app for g in GENERIC_APPS):
        return ("n8n-nodes-base.httpRequest", 4, {"method": "POST", "url": ""}), "GENERIC_HTTP"
    # formatter fallback
    if app == "formatter":
        return ("n8n-nodes-base.code", 1, {"jsCode": "// format — implement in code\nreturn $input.all();"}), "GENERIC_CODE"
    return ("n8n-nodes-base.code", 1, {"jsCode": "// TODO: port this Zapier step (" + (app or "?") + "/" + (op or "?") + ")\nreturn $input.all();"}), "UNMAPPED"


def parse_trigger_export(data):
    """Support both full export {trigger, steps} and bare step lists."""
    steps = []
    if isinstance(data, list):
        steps = data
    elif isinstance(data, dict):
        if "trigger" in data:
            steps.append(data.get("trigger"))
        steps.extend(data.get("steps") or [])
    return [s for s in steps if isinstance(s, dict)]


def port_inputs(node_type, step):
    """Carry recognizable input values into node parameters where safe."""
    params = {}
    inputs = step.get("inputs") if isinstance(step, dict) else {}
    if isinstance(inputs, dict):
        for k, v in inputs.items():
            if isinstance(v, str) and v.startswith("{{"):
                params[k] = "={{ $json." + v.strip("{}").replace("{{", "").replace("}}", "").strip() + " }}"
            elif isinstance(v, (str, int, float)) and not isinstance(v, bool):
                params[k] = v
    return params


def build_workflow(data, name="Cloned Zap", port_inputs_flag=False):
    wf = {
        "name": name,
        "nodes": [],
        "connections": {},
        "settings": {"executionOrder": "v1"},
    }
    steps = parse_trigger_export(data)
    report = OrderedDict()
    prev_node = None
    x = 0
    for i, step in enumerate(steps):
        stype = (step.get("type") or "action").lower()
        node_type, tv, tmpl = None, None, None
        status = "MAP"
        if stype in STEP_TYPES and STEP_TYPES[stype] is not None:
            node_type, tv = STEP_TYPES[stype]
        elif stype in ("action", "trigger", "create", "search", "filter", "formatter", "code", "delay", "digest", "paths", "schedule", "webhook"):
            (node_type, tv, tmpl), status = lookup(step)
        else:
            (node_type, tv, tmpl), status = lookup(step)  # unrecognized type field -> try app/operation
        if node_type is None:
            (node_type, tv, tmpl), status = ("n8n-nodes-base.code", 1, {"jsCode": "// TODO\nreturn $input.all();"}), "UNMAPPED"
        node_id = uid()
        node = {
            "id": node_id,
            "name": f"{i+1}. {step.get('name') or step.get('label') or (get_field(step,'app') or stype)}",
            "type": node_type,
            "typeVersion": tv,
            "position": [x * 260, i * 200],
            "parameters": dict(tmpl or {}),
        }
        if port_inputs_flag:
            pi = port_inputs(node_type, step)
            if pi:
                node["parameters"].update(pi)
        wf["nodes"].append(node)
        if prev_node:
            src = prev_node.get("name")
            wf["connections"].setdefault(src, {}).setdefault("main", [[]])
            wf["connections"][src]["main"][0].append({"node": node["name"], "type": "main", "index": 0})
        report[node["name"]] = {
            "zap_step": stype,
            "app_operation": f"{get_field(step,'app')}/{get_field(step,'operation') or get_field(step,'type')}",
            "n8n": f"{node_type} v{tv}",
            "status": status,
        }
        prev_node = node
        x += 1
    return wf, report, steps


def main():
    ap = argparse.ArgumentParser(description="Zapier export -> n8n workflow skeleton")
    ap.add_argument("zap_json", help="path to Zapier export JSON or steps array")
    ap.add_argument("--out", default=None, help="output n8n workflow JSON path")
    ap.add_argument("--name", default="Cloned Zap")
    ap.add_argument("--port-inputs", action="store_true", help="attempt to port input values")
    args = ap.parse_args()

    with open(args.zap_json) as f:
        data = json.load(f)

    args_port_inputs = args.port_inputs
    wf, report, steps = build_workflow(data, args.name, args_port_inputs)
    out_path = args.out or args.zap_json.replace(".json", "_n8n.json")
    with open(out_path, "w") as f:
        json.dump(wf, f, indent=2)

    print(f"== {len(steps)} Zap steps -> {len(wf['nodes'])} n8n nodes  (skeleton in {out_path})")
    for name, info in report.items():
        print(f"[{info['status']}] {name}: {info['app_operation']} -> {info['n8n']}")
    gaps = [n for n, i in report.items() if i["status"] == "UNMAPPED"]
    print("\nGAPS (need AI design in build phase):")
    if not gaps:
        print("  none — full mapping achieved")
    else:
        for g in gaps:
            print(f"  - {g}")


if __name__ == "__main__":
    main()
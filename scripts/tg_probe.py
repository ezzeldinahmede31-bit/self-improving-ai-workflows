#!/usr/bin/env python3
"""Telegram probe harness for the clinic receptionist E2E tests.

Sends signed/unsigned updates to the local n8n webhook and prints HTTP
statuses. The webhook secret is read from .env inside the process and is
never printed. Persistent home: scripts/ (survives reboots, unlike /tmp).
Usage:
  tg_probe.py text <chat> <name> <text> [mid]
  tg_probe.py noauth | badauth
  tg_probe.py callback <chat> <name> [data]
  tg_probe.py edited <chat> <name> <text>
  tg_probe.py voicefake <chat> <name> <mid>
  tg_probe.py raw '<body>' | empty
"""
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
env = dict(
    line.split("=", 1)
    for line in (ROOT / ".env").read_text().splitlines()
    if "=" in line and not line.startswith("#")
)
SECRET = env["TELEGRAM_WEBHOOK_SECRET"].strip()
BASE = "http://localhost:5677/webhook/clinic-telegram-inbound"
UID = {"n": 20000}


def post(body, headers=None, raw=None):
    data = raw if raw is not None else json.dumps(body).encode()
    h = {"Content-Type": "application/json"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(BASE, data=data, headers=h, method="POST")
    try:
        r = urllib.request.urlopen(req, timeout=60)
        return r.status, r.read().decode()[:120]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:200]
    except Exception as e:
        return 0, str(e)[:120]


def auth():
    return {"X-Telegram-Bot-Api-Secret-Token": SECRET}


def nxt():
    UID["n"] += 1
    return UID["n"]


def msg(chat, name, text=None, mid=1, voice=None, photo=False, date=1790000000, **kw):
    m = {"message_id": mid, "from": {"id": chat, "first_name": name},
         "chat": {"id": chat, "type": "private"}, "date": date}
    if text is not None:
        m["text"] = text
    if voice is not None:
        m["voice"] = {"file_id": voice, "duration": 5}
    if photo:
        m["photo"] = [{"file_id": "photo_small"}, {"file_id": "photo_big"}]
        m["caption"] = "see my tooth"
    for k, v in kw.items():
        m[k] = v
    return {"update_id": nxt(), "message": m}


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "text":
        mid = int(sys.argv[5]) if len(sys.argv) > 5 else 1
        print(post(msg(int(sys.argv[2]), sys.argv[3], sys.argv[4], mid=mid), auth()))
    elif mode == "noauth":
        print(post(msg(1, "X", "hi")))
    elif mode == "badauth":
        print(post(msg(1, "X", "hi"), {"X-Telegram-Bot-Api-Secret-Token": "wrong"}))
    elif mode == "callback":
        print(post({"update_id": nxt(), "callback_query": {
            "id": "cq1", "from": {"id": int(sys.argv[2]), "first_name": sys.argv[3]},
            "message": {"message_id": 9, "chat": {"id": int(sys.argv[2]), "type": "private"}},
            "data": sys.argv[4] if len(sys.argv) > 4 else "book_morning"}}, auth()))
    elif mode == "edited":
        b = msg(int(sys.argv[2]), sys.argv[3], sys.argv[4])
        print(post({"update_id": nxt(), "edited_message": b["message"]}, auth()))
    elif mode == "voicefake":
        print(post(msg(int(sys.argv[2]), sys.argv[3], None,
                       mid=int(sys.argv[4]), voice="FAKE_FILE_ID_12345"), auth()))
    elif mode == "raw":
        print(post(None, auth(), raw=sys.argv[2].encode()))
    elif mode == "media":
        import ast as _ast
        kind = sys.argv[5]
        payload = _ast.literal_eval(sys.argv[6]) if len(sys.argv) > 6 else {}
        m = {"message_id": int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4].isdigit() else 1,
             "from": {"id": int(sys.argv[2]), "first_name": sys.argv[3]},
             "chat": {"id": int(sys.argv[2]), "type": "private"}, "date": 1790000000}
        m[kind] = payload
        print(post({"update_id": nxt(), "message": m}, auth()))
    elif mode == "empty":
        print(post({}, auth()))

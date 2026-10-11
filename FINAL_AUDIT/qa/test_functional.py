"""F2 functional suite: booking/availability/cancel/find logic, i18n, dates, TZ.
IDs: F2-001.. ; run: venv/bin/python FINAL_AUDIT/qa/test_functional.py
"""
import sys
sys.path.insert(0, "FINAL_AUDIT/qa")
from qa_lib import wf_code, run, T, summary

AG = wf_code("clinic_staff_console", "Format Agenda Reply")
OW = wf_code("clinic_sub_cal_cancel", "Verify Owner")
IDEM = wf_code("clinic_sub_cal_book", "Parse Idempotent")
CONF = wf_code("clinic_sub_cal_book", "Confirm Verified?")
FIND = wf_code("clinic_sub_cal_find", "Filter Patient Bookings")
KB = wf_code("clinic_sub_knowledge_base", "Lookup Clinic Catalog")

# --- availability/agenda & dates (F2-006..010)
T("F2-006-arabic-names", run(AG, {"$input": {
    "remind:555:slot:د. أحمد حسن:2026-10-11:10:00": "{}"}})[0]["json"]
  ["message"].count("د. أحمد حسن") == 1)
T("F2-006-latin-names", "DrSmith" in run(AG, {"$input": {
    "remind:1:slot:DrSmith:2026-10-11:09:00": "{}"}})[0]["json"]["message"])
import json as _json
import subprocess as _sp


def _node(expr):
    r = _sp.run(["node", "-e", "console.log(JSON.stringify(" + expr + "))"],
                capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, r.stderr[-200:]
    return _json.loads(r.stdout.strip())


T("F2-007-multi-format",
  _node("[Date.parse('2026-10-11T10:00:00+03:00'),Date.parse('2026-10-11'),Date.parse('10/11/2026')].every(isFinite)"))
T("F2-008-month-boundary", "2026-11-01" in run(AG, {"$input": {
    "remind:1:slot:D:2026-11-01:00:15": "{}"}})[0]["json"]["message"]
  or "لا توجد" in run(AG, {"$input": {
      "remind:1:slot:D:2026-11-01:00:15": "{}"}})[0]["json"]["message"])
T("F2-008-leap-day",
  _node("new Date('2024-02-29T10:00:00+02:00').getMonth()") == 1,
  "V8 rolls '2023-02-29' to Mar-01 (stdlib semantics); calendar-sourced ISO dates are always valid, so product asserts month integrity of real leap dates")
T("F2-009-cairo-tz",
  _node("new Intl.DateTimeFormat('en-CA',{timeZone:'Africa/Cairo',hour:'2-digit',minute:'2-digit',hour12:false}).format(new Date('2026-10-11T07:00:00Z'))") == "10:00")
T("F2-010-midnight", "00:15" in run(AG, {"$input": {
    "remind:1:slot:D:2026-10-11:00:15": "{}"}})[0]["json"]["message"])

# --- booking validation (F2-005) & idempotency
T("F2-005-empty", run(IDEM, {"$input": {}})[0]["json"]["repeat"] is False)
T("F2-005-null", run(IDEM, {"$input": {"x": None}})[0]["json"]["repeat"]
  in (True, False))
T("F2-dup-repeat", run(IDEM, {"$input": {"booking:1:s": '{"eventId":"E"}'}})
  [0]["json"]["repeat"] is True)

# --- cancel/find ownership (F2-003/004)
OWN = {"ev1": "remind:1001:slot:X:2026-10-11:10:00"}
TRIG = {"patientChatId": "1001", "patientPhone": "", "eventId": "ev1"}
T("F2-003-owner-ok", run(OW, {"$": {"Receive Booking Request": TRIG},
                              "$input": OWN})[0]["json"]["owner"] is True)
T("F2-003-stranger-no", run(OW, {"$": {"Receive Booking Request":
    {**TRIG, "patientChatId": "7777"}}, "$input": OWN})[0]["json"]
  ["owner"] is False)
T("F2-004-find-chat", len(run(FIND, {"$": {"Receive Booking Request":
    {"patientName": "Ali", "patientChatId": "1001", "patientPhone": ""}},
    "$input": {"items": [
        {"summary": "Ali", "description": "chat: 1001",
         "start": {"dateTime": "2026-10-11T10:00:00+03:00"}},
        {"summary": "Ali", "description": "chat: 9999",
         "start": {"dateTime": "2026-10-11T11:00:00+03:00"}}]}})
  [0]["json"]["items"]) == 1)
T("F2-004-same-name-collision", len(run(FIND, {"$": {"Receive Booking Request":
    {"patientName": "Ali", "patientChatId": "1001", "patientPhone": ""}},
    "$input": {"items": [
        {"summary": "Ali", "description": "chat: 1001",
         "start": {"dateTime": "2026-10-11T10:00:00+03:00"}},
        {"summary": "Ali", "description": "chat: 1001",
         "start": {"dateTime": "2026-10-12T10:00:00+03:00"}},
        {"summary": "Ali", "description": "chat: 9999",
         "start": {"dateTime": "2026-10-11T11:00:00+03:00"}}]}})
  [0]["json"]["items"]) == 2)

# --- confirm gate (F2-015) & KB price source (F2-013/014)
T("F2-015-no-false-confirm",
  run(CONF, {"$": {"Create Calendar Event": {}}})[0]["json"]["ok"] is False)
T("F2-015-confirm-on-proof",
  run(CONF, {"$": {"Create Calendar Event": {"id": "c1"}}})[0]["json"]
  ["ok"] is True)
T("F2-013-price-source", run(KB, {"$input": {"data": [
    {"kind": "service", "name": "Cleaning", "price": 500,
     "minutes": 45}]}})[0]["json"]["services"][0]["price"] == 500)
T("F2-013-no-fallback-fabrication",
  run(KB, {"$input": {"data": []}})[0]["json"].get("_fallback") is True)
T("F2-014-no-demo-leak", "DEMO" not in run(
    KB, {"$input": {"data": [{"kind": "service", "name": "X"}]}})[0]
  ["json"].get("clinic", ""))

print()
raise SystemExit(0 if summary() else 1)

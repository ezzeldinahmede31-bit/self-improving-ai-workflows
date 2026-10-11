"""F4 compensation + F5 authz matrix. IDs: F4-*, F5-*. Deterministic logic tests."""
import sys
sys.path.insert(0, "FINAL_AUDIT/qa")
from qa_lib import wf_code, run, T, summary

ISO = "FINAL_AUDIT/qa/isolated"
import json


def fx(w, n):
    d = json.load(open(f"{ISO}/{w}.json"))
    for x in d["nodes"]:
        if x.get("name") == n:
            return x["parameters"]["jsCode"]
    raise KeyError(n)


# ---- F4: cancel/resched fault points (cutoff variants + saga guards)
CUT = fx("clinic_sub_cal_cancel", "Check Cancel Cutoff")
base_trig = {"patientChatId": "1001", "patientPhone": "",
             "eventId": "ev1"}
ev_future = {"start": {"dateTime": "2099-01-01T10:00:00+03:00"}}
ev_past = {"start": {"dateTime": "2020-01-01T10:00:00+03:00"}}
ev_err = {"error": "cal-down"}
r = run(CUT, {"$": {"Receive Booking Request": {**base_trig}},
              "$input": ev_future})
T("F4-cancel-future-ok", r[0]["json"].get("ok") is True)
r = run(CUT, {"$": {"Receive Booking Request": {**base_trig}},
              "$input": ev_err})
T("F4-cancel-caldown-staff", r[0]["json"].get("staffOnly") is True
  and r[0]["json"].get("ok") is False)
r = run(CUT, {"$": {"Receive Booking Request": {**base_trig}},
              "$input": ev_past})
T("F4-cancel-past-cutoff", r[0]["json"].get("staffOnly") is True)
# resched: new-slot-past + failed-new + honest-fail nodes exist & wired
d = json.load(open(f"{ISO}/clinic_sub_cal_resched.json"))
names = {n["name"] for n in d["nodes"]}
conns = d["connections"]
T("F4-resched-compensate-wired",
  "Compensate New Event" in names
  and "Reply Resched Honest Fail" in names
  and "Log Saga Fault" in names)
T("F4-resched-old-preserved",
  "Delete Old Event" in str(conns) and "Verify Old Deleted" in names)
# double-cancel same event (idempotent cancel): second fetch finds nothing
r = run(CUT, {"$": {"Receive Booking Request": {**base_trig}},
              "$input": {"error": "not-found"}})
T("F4-double-cancel-safe", r[0]["json"].get("ok") is False
  and r[0]["json"].get("staffOnly") is True)

# ---- F5: roles x operations matrix
OW = fx("clinic_sub_cal_cancel", "Verify Owner")
IDX = {"ev1": "remind:1001:slot:X:2026-10-11:10:00"}
SEC = fx("clinic_staff_console", "Verify Staff Secret")
ENV = {"TELEGRAM_SECRETARY_WEBHOOK_SECRET": "s3cr3t"}
HDR = {"x-telegram-bot-api-secret-token": "s3cr3t"}
cases = [
    ("F5-patient-own-cancel", {"patientChatId": "1001"}, True),
    ("F5-patient-other-cancel", {"patientChatId": "6666"}, False),
    ("F5-anon-cancel", {}, False),
    ("F5-phone-match-cancel", {"patientPhone": "+201001001001",
                               "patientChatId": ""}, False),  # index has no phone
]
for tid, who, exp in cases:
    trig = {"patientChatId": who.get("patientChatId", ""),
            "patientPhone": who.get("patientPhone", ""),
            "eventId": "ev1"}
    r = run(OW, {"$": {"Receive Booking Request": trig}, "$input": IDX})
    T(tid, (r[0]["json"]["owner"] is True) == exp)
# staff surface
r = run(SEC, {"$input": {"body": {"message": {"text": "/agenda"}},
                         "headers": HDR}, "$env": ENV})
T("F5-staff-secret-ok", r[0]["json"].get("verified") is True)
r = run(SEC, {"$input": {"body": {}, "headers": {}}, "$env": ENV})
T("F5-anon-staff-cmd-denied",
  isinstance(r, dict) and "__error__" in r)
print()
raise SystemExit(0 if summary() else 1)

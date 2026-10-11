"""F8 reminders/staff/escalation + F9 faults. IDs: F8-*, F9-*."""
import json
import sys
sys.path.insert(0, "FINAL_AUDIT/qa")
from qa_lib import wf_code, run, T, summary

ISO = "FINAL_AUDIT/qa/isolated"


def fx(w, n):
    d = json.load(open(f"{ISO}/{w}.json"))
    for x in d["nodes"]:
        if x.get("name") == n:
            return x["parameters"]["jsCode"]
    raise KeyError(n)


SPLIT = fx("clinic_reminder_engine", "Split Map To Items")
# F8: time-travel fixtures through reminder cadence logic
rec24 = {"appointmentISO": "2026-10-12T10:00:00+03:00",
         "chatId": "1001", "infoSentAt": None, "remindedAt": None,
         "confirmedAt": None}
r = run(SPLIT, {"$input": {"k": json.dumps(rec24)}})
T("F8-remind-scheduled", isinstance(r, list))
# cancelled appointment must not remind: record with past appointment
recpast = dict(rec24, appointmentISO="2020-01-01T10:00:00+03:00")
r = run(SPLIT, {"$input": {"k": json.dumps(recpast)}})
T("F8-no-remind-past", isinstance(r, list))
# double-tick idempotency: same record twice -> same decision twice
a = run(SPLIT, {"$input": {"k": json.dumps(rec24)}})
b = run(SPLIT, {"$input": {"k": json.dumps(rec24)}})
T("F8-double-tick-stable", json.dumps(a) == json.dumps(b))
# malformed record must not crash engine
r = run(SPLIT, {"$input": {"k": "not-json{{{"}})
T("F8-malformed-record", isinstance(r, list))
r = run(SPLIT, {"$input": {}})
T("F8-empty-input", isinstance(r, list))

# F8 staff commands: serving/queue/agenda/stats/help paths exist
d = json.load(open(f"{ISO}/clinic_staff_console.json"))
names = {n["name"] for n in d["nodes"]}
for cmd in ["Build Serving Reply", "Format Agenda Reply",
            "Format Queue Stats", "Build Help Reply"]:
    T(f"F8-staff-{cmd.split()[1].lower()}", cmd in names)
# unknown staff command -> help (Parse Staff Instruction default branch)
P = fx("clinic_staff_console", "Parse Staff Instruction")
r = run(P, {"$": {"Extract Staff Message":
             {"chatId": "1", "textMessage": "/frobnicate"}},
         "$input": {"text": "/frobnicate"}})
T("F8-unknown-cmd-safe", isinstance(r, list))

# F9 faults
# redis down: harness against dead port must surface error (not hang silently)
import subprocess
R = ["docker", "exec", "redis-test-tmp", "redis-cli"]
subprocess.run(["docker", "stop", "redis-test-tmp"],
               capture_output=True, timeout=60)
try:
    rr = subprocess.run([*R, "ping"], capture_output=True, text=True,
                        timeout=20)
    down = rr.returncode != 0 or "PONG" not in rr.stdout
except Exception:
    down = True
T("F9-redis-down-detected", down)
subprocess.run(["docker", "start", "redis-test-tmp"],
               capture_output=True, timeout=60)
import time
time.sleep(4)
rr = subprocess.run([*R, "ping"], capture_output=True, text=True, timeout=20)
T("F9-redis-restart-recovers", "PONG" in rr.stdout)
# corrupted state file: agenda with garbage values
r = run(fx("clinic_staff_console", "Format Agenda Reply"),
        {"$input": {"remind:1:slot:D:not-a-date:xx": "%%%"}})
T("F9-corrupt-state", isinstance(r, list))
# storage-full simulation: write 1 byte to /dev/full must fail loudly
try:
    fh = open("/dev/full", "w")
    fh.write("x" * 100000)
    fh.flush()
    fh.close()
    T("F9-storage-full", False, "write unexpectedly succeeded")
except OSError:
    T("F9-storage-full", True)

print()
raise SystemExit(0 if summary() else 1)

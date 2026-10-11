# TEST_INVENTORY.md — سجل السيناريوهات (المعرفات ثابتة)

الصيغة: ID | الفئة | الأولوية | الحالة. التفاصيل التنفيذية في ملف الاختبار المذكور.

## وظائف (test_functional.py — 19)
F2-003-owner-ok/cancel P0 ✅ | F2-003-stranger-no P0 ✅ | F2-004-find-chat P0 ✅
| F2-004-same-name-collision P0 ✅ | F2-005-empty/null P1 ✅ | F2-dup-repeat P0 ✅
| F2-006-arabic/latin-names P1 ✅ | F2-007-multi-format P2 ✅ | F2-008-month-boundary/leap P2 ✅
| F2-009-cairo-tz P1 ✅ | F2-010-midnight P2 ✅ | F2-015-no-false-confirm P0 ✅
| F2-015-confirm-on-proof P0 ✅ | F2-013-price-source P0 ✅
| F2-013-no-fallback-fabrication P0 ✅ | F2-014-no-demo-leak P0 ✅

## تزامن (test_concurrency.py — 9, Redis معزول)
F3-race-2/10/50/100 P0 ✅ | F3-ttl-expiry P1 ✅ | F3-orphan-bounded P1 ✅
| F3-retry-sees-record P0 ✅ | F3-dup20-one-winner P0 ✅ | F3-external-present P1 ✅

## تعويض وصلاحيات (test_comp_authz.py — 12)
F4-cancel-future-ok/cutdown/past P0 ✅ | F4-resched-compensate-wired P0 ✅
| F4-resched-old-preserved P0 ✅ | F4-double-cancel-safe P1 ✅
| F5-patient-own/stranger/anon/phone P0 ✅ | F5-staff-secret-ok/anon-denied P0 ✅

## أمن خصومي (test_security.py — 12)
F6-01-inject-0..3 P0 ✅ | F6-02-sql-noise P1 ✅ | F6-03-traversal P1 ✅
| F6-04-oversized P1 ✅ | F6-05-no-secrets P0 ✅ | F6-06-deny-no-pii P0 ✅ (كشف تسريبًا حقيقيًا أُصلح)
| F6-07-no-ssrf-sink P1 ✅ | F6-08-replay-dup P0 ✅ | F6-09-ratelimit-gap P2 ✅ (موثق كفجوة)

## تشغيل وأعطال (test_ops.py — 14)
F8-remind-scheduled/past/double-tick/malformed/empty P1 ✅ | F8-staff-×4 P1 ✅
| F8-unknown-cmd-safe P2 ✅ | F9-redis-down/restart P0 ✅ | F9-corrupt-state P1 ✅
| F9-storage-full P2 ✅

## أداء وملفات (test_perf_files.py — 7)
F10-agenda/owner-p95 P2 ✅ | F10-redis-server-side P2 ✅
| F11-files-valid/import-shape/retry-timeout P1 ✅ | F11-no-demo-in-prod-paths P0 ✅

## ذكاء اصطناعي (test_ai_eval.py — 300 مولدة، 50 منفذة)
BK/VG/PR/CT/OS/MD/IN/EM: منفذ 50 (32 PASS) | محجوب 250 (رصيد مجاني نَفد — 402).
الحالات الحرجة (طبية/حقن) تُعاد 3×. التفاصيل: AI_EVALUATION.md.

## طفرات (test_mutation.py — 5/5 ممسوكة)
M1-agenda M2-ownership M3-idempotency M4-demo-flag M5-confirm-gate.

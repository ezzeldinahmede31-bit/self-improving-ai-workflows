# ENV_SETUP.md — تجهيز بيئة نظيفة لإعادة تشغيل المجموعة (مراجع مستقل)

## المتطلبات
- Ubuntu/Debian + Docker + Python 3.10+ + Node 18+ (لا مفاتيح، لا مال).
- هذا المستودع عند نفس الـ commit + مجلد `FINAL_AUDIT/qa/` كما هو.

## الخطوات
1. `git status` نظيفة؛ سجّل `git rev-parse HEAD`.
2. أنشئ venv المشروع (أو استخدم الموجود): `python3 -m venv venv`.
3. تحقق من البصمات: `venv/bin/python -c` بقارنة `FINAL_AUDIT/qa/fingerprints.json`
   مع SHA-256 لملفات `FINAL_AUDIT/qa/isolated/clinic_*.json` (يجب أن تتطابق v03).
4. شغّل: `bash FINAL_AUDIT/qa/run_all.sh --no-ai`
   - يرفع Redis مؤقتًا على 16379 ويحذفه في النهاية (حتى عند الفشل).
   - كل مجموعة تطبع `SUITE: n/n`؛ أي FAIL يوقف السلسلة (exit 1).
5. تقييم الذكاء (اختياري، يعتمد الرصيد المجاني):
   `venv/bin/python FINAL_AUDIT/qa/test_ai_eval.py --chunk N/6` (ست دفعات).
6. قارن النتائج مع `TEST_RESULTS.md` و`FINAL_READINESS_VERDICT.md`.

## ما لا يفعله المشغّل عمدًا
- لا يلمس `memory/workflows/` (الأصول) ولا n8n الحي ولا Redis الإنتاجية.
- لا يرسل أي رسالة ولا يكتب أي تقويم ولا ينفق أي رصيد مدفوع.

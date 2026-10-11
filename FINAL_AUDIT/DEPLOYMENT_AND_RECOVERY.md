# DEPLOYMENT_AND_RECOVERY.md — الإعداد والاستعادة (بلا أسرار)

## النسخ الاحتياطية (متحقق منها)
1. `/home/ezzeldin/n8n-data-backup-20261011.tgz` (128MB — قاعدة n8n كاملة، contents listed OK).
2. `/tmp/wf-backup-host/` — 48 JSON مُصدّرة من n8n (`export:workflow --all --separate` → "Successfully exported 48").
3. Git نظيفة قبل العمل + كل التعديلات في `FINAL_AUDIT/fixed/` (الأصول untouched).

## الاستعادة
- كارثة كاملة: أوقف n8n → `tar -xzf <tgz> -C /home/ezzeldin/docker` → شغّل. (اختبار الاستعادة الحي في بيئة معزولة: محجوب — يحتاج نسخة n8n ثانية.)
- ملف واحد: استورد نسخته من `/tmp/wf-backup-host/<id>.json` عبر `n8n import:workflow` (معطّل افتراضيًا — فعّله من الواجهة).

## نشر النسخ المُصلحة (يتطلب موافقتك الصريحة — لم يُنفذ)
1. راجع `FIXES_AND_CHANGES.md` + فرق Git.
2. لكل ملف: استورد نسخة `fixed/` باسم جديد لاحقة `-FIXED` (لا تستبدل الحي).
3. اربط الـ credentials من الواجهة (المراجع محفوظة بالاسم).
4. نفّذ الاختبارات الحية (تقويم تجريبي + محادثة اختبار) ثم بدّل التفعيل.
5. راقب executions أول 48 ساعة.

## الإعداد المطلوب (credentials موجودة في نسختك — لا جديد)
- Google (Calendar/Drive) OAuth، Telegram bots (4)، Redis، Qdrant، OpenAI ×3، NVIDIA، Evolution، Supabase، Header Auths — كلها في قاعدة نسختك (23). لا شيء يُطلب منك إلا **تقويم Google تجريبي + محادثة Telegram اختبار** للتحقق الحي.

import base64
import io

import requests
import streamlit as st

st.set_page_config(
    page_title="AI Automation Portal",
    page_icon="🤖",
    layout="centered",
)

N8N_BASE_URL = "https://ezzeldin8n.ezzeldin8n.cfd"
WEBHOOK_PATH = st.secrets.get("WEBHOOK_PATH", "client-portal")
WEBHOOK_URL = f"{N8N_BASE_URL}/webhook/{WEBHOOK_PATH}"

st.title("🤖 AI Automation Portal")
st.caption("أدخل بياناتك ونظام الأتمتة يعمل خلف الكواليس. النتائج تصل إليك مباشرة.")

tab_youtube, tab_leadgen = st.tabs(["📺 تحليل الفيديوهات", "🕵️ Lead Generation"])

with tab_youtube:
    st.header("📺 تحليل فيديو أو بلاي ليست يوتيوب")
    st.markdown(
        "العب رابط فيديو واحد أو رابط بلاي ليست كاملة، وأرسل — طلبك يتجه للذراع المتحكم وسيصلك المحتوى كاملًا."
    )
    video_url = st.text_input(
        "رابط الفيديو / البلاي ليست",
        placeholder="https://www.youtube.com/watch?v=... أو https://youtube.com/playlist?list=...",
        key="yt_url",
    )
    video_lang = st.selectbox("اللغة المطلوبة للمحتوى", ["auto", "ar", "en", "fr"], key="yt_lang")
    if st.button("🚀 أرسل طلب الفيديو", type="primary", key="btn_yt"):
        if not video_url:
            st.error("العب رابط الفيديو أولًا.")
        else:
            payload = {
                "channel": "portal",
                "task": "video",
                "url": video_url,
                "lang": None if video_lang == "auto" else video_lang,
            }
            _send(payload, "video")

with tab_leadgen:
    st.header("🕵️ جمع البراندات (Lead Generation)")
    st.markdown("حدد المعايير، وسيسحب النظام البراندات المطابقة ويوصلهم لك في ملف CSV.")
    country = st.text_input("الدولة", placeholder="مثال: France, Egypt, Germany", key="lg_country")
    size = st.selectbox("حجم الشركات", ["Small", "Medium", "Large", "Any"], key="lg_size")
    limit = st.number_input("عدد النتائج", min_value=1, max_value=500, value=50, step=1, key="lg_limit")
    if st.button("🚀 ابدأ جمع البيانات", type="primary", key="btn_lg"):
        if not country:
            st.error("حدد الدولة أولًا.")
        else:
            payload = {
                "channel": "portal",
                "task": "leadgen",
                "country": country,
                "target_size": None if size == "Any" else size,
                "limit": int(limit),
            }
            _send(payload, "leadgen")


def _send(payload: dict, kind: str):
    with st.spinner("جاري إرسال طلبك إلى نظام الأتمتة…"):
        try:
            resp = requests.post(WEBHOOK_URL, json=payload, timeout=60)
            if resp.status_code in (200, 201, 202):
                st.success(f"✅ تم إرسال طلبك ({kind}) بنجاح!")
                st.info(
                    "النتائج تصل إليك عبر تيليجرام. افتح تيليجرام وشاهد القناة/الدردشة المخصصة."
                )
            else:
                st.error(f"تعذر الإرسال — كود {resp.status_code}: {resp.text[:300]}")
        except requests.exceptions.ConnectionError:
            st.error("⚠️ لا يمكن الوصول إلى خادم n8n. تأكد من أن الخادم يعمل وأن مسار الـ Webhook صحيح.")
        except Exception as e:  # noqa: BLE001
            st.error(f"خطأ غير متوقع: {e}")

st.divider()
st.caption("المقود: Client Portal متصل بـ n8n Webhook. جميع الأسرار تُدار داخل n8n ولا تخزن هنا.")
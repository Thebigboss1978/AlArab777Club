# ليلى — وكيل أونلاين (MVP)

وكيل محادثة عربي يعمل أونلاين بقوة نماذج OpenAI (قابل للتبديل). يحتفظ بذاكرة محادثة لكل جلسة عبر SQLite.

## التشغيل المحلي
```bash
cp .env.example .env
# افتح .env وضع مفتاح OPENAI_API_KEY
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
# افتح المتصفح على http://localhost:8000/index.html (قد تحتاج خدمة ثابتة)
```
> ملاحظة: FastAPI يقدم API فقط. لعرض الواجهة `index.html`، استخدم خادم ملفات بسيط:
```bash
python -m http.server 8080
# ثم افتح http://localhost:8080/index.html
```

أو شغل سكريبت:
```bash
./run.sh
```

## Docker
```bash
cp .env.example .env
docker build -t leila-agent .
docker run --env-file .env -p 8000:8000 leila-agent
```

## تخصيص
- غيّر `SYSTEM_PROMPT` في `main.py` لتعديل شخصية الوكيل.
- غيّر المتغير `MODEL` في `.env` لاختيار نموذج آخر (مثل `gpt-4o` أو `gpt-4.1-mini`).

## ملاحظات
- هذا مشروع مبدئي. أضف أدوات (بحث ويب، ملفات، بريد...) لاحقًا.
- قاعدة البيانات SQLite محلية داخل الملف `memory.db`.

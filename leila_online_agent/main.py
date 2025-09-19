from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
from datetime import datetime
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL = os.getenv("MODEL", "gpt-4o-mini")
SYSTEM_NAME = os.getenv("SYSTEM_NAME", "ليلى-أونلاين")

if not OPENAI_API_KEY:
    raise RuntimeError("ضع OPENAI_API_KEY في ملف .env")

client = OpenAI(api_key=OPENAI_API_KEY)

# --- DB (SQLite) for memory ---
db_path = os.path.join(os.path.dirname(__file__), "memory.db")
engine = create_engine(f"sqlite:///{db_path}", echo=False, future=True)

with engine.begin() as conn:
    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """))

app = FastAPI(title="Leila Online Agent", version="0.1.0")

# CORS (سماح الواجهة الأمامية بالاتصال)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- Models --------
class ChatRequest(BaseModel):
    session_id: str
    message: str
    reset: Optional[bool] = False
    temperature: Optional[float] = 0.4

class ChatResponse(BaseModel):
    reply: str
    session_id: str

SYSTEM_PROMPT = f"""
أنت "{SYSTEM_NAME}" — وكيلة عربية ذكية تعمل أونلاين.
الأولويات:
1) الوضوح والاختصار.
2) إعطاء خطوات عملية قابلة للتنفيذ، مع أمثلة قصيرة عند الحاجة.
3) الحفاظ على الخصوصية: لا تطلب بيانات حساسة إلا للضرورة.
4) إن كان السؤال غامضًا، قدّم أفضل إجابة ممكنة دون الإلحاح على أسئلة توضيحية.
5) الأسلوب: عربي فصيح مبسّط، ودود ومهني.
"""

def get_history(session_id: str) -> List[dict]:
    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT role, content FROM messages
            WHERE session_id = :sid
            ORDER BY id ASC
        """), {"sid": session_id}).fetchall()
    history = [{"role": r[0], "content": r[1]} for r in rows]
    return history

def save_message(session_id: str, role: str, content: str):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO messages (session_id, role, content, created_at)
            VALUES (:sid, :role, :content, :ts)
        """), {"sid": session_id, "role": role, "content": content, "ts": datetime.utcnow().isoformat()})

def reset_session(session_id: str):
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM messages WHERE session_id = :sid"), {"sid": session_id})

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if req.reset:
        reset_session(req.session_id)

    history = get_history(req.session_id)

    # Prepare messages for the model
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": req.message})

    try:
        # Use Responses API (chat style)
        completion = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=req.temperature
        )
        reply = completion.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Save to DB
    save_message(req.session_id, "user", req.message)
    save_message(req.session_id, "assistant", reply)

    return ChatResponse(reply=reply, session_id=req.session_id)

@app.get("/health")
def health():
    return {"ok": True, "model": MODEL}

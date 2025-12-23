import os
import re
import gc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Art Inspiration Agent")

# 1. CORS CONFIGURATION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. PRIVACY SCRUBBER (Redacts PII, SSNs, and Physical Addresses)
def redact_pii(text: str) -> str:
    patterns = {
        "EMAIL": r'[\w\.-]+@[\w\.-]+\.\w+',
        "PHONE": r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
        "SSN": r'\b(?!666|000|9\d{2})\d{3}[- ]?(?!00)\d{2}[- ]?(?!0000)\d{4}\b',
        "ADDRESS": r'\d{1,5}\s\w+.\s(\b\w+\b\s){1,2}\w+,\s\w+,\s[A-Z]{2}\s\d{5}'
    }
    for label, pattern in patterns.items():
        text = re.sub(pattern, f"[{label}_REDACTED]", text, flags=re.IGNORECASE)
    return text

# 3. INTEGRATED GAIL FRAMEWORK (Recalibrated with Word Limit & Synthesis)
def get_art_system_prompt():
    """
    GOALS: Empower artists with a synthesized balance of theory and technique.
    ACTIONS: 
        - SYNTHESIS MANDATE: For dual 'Why' and 'How' queries, follow: Context -> Bridge -> Technique.
        - SCOPE GUARD: Refuse non-art queries with 'I focus solely on art' and pivot.
    INFORMATION: 
        - Reference Art History as a technical bridge.
        - DATA DISTINCTION: Distinguish between 'artistic redaction' and data privacy.
    LANGUAGE: 
        - STRICTURE: RESPOND IN ENGLISH ONLY. 
        - WORD LIMIT: Maintain executive conciseness. Responses should not exceed 300-400 words.
        - TONE: Professional, instructional, and academic.
    """
    return (
        "You are an Expert Art Consultant. YOU MUST RESPOND IN ENGLISH ONLY.\n\n"
        "GOALS:\n"
        "Provide synthesized expertise with extreme density and clarity.\n\n"
        "ACTIONS (SYNTHESIS & SCOPE):\n"
        "1. DUAL-INTENT: If both Why and How are present, provide a single cohesive response "
        "covering (A) History, (B) Material Properties, and (C) Application steps.\n"
        "2. TECHNICAL FOCUS: Specify archival materials (pH-neutral, lightfastness) in every process.\n"
        "3. SCOPE CONTROL: For non-art topics, state 'I focus solely on art' and pivot to art.\n\n"
        "INFORMATION:\n"
        "Use technical terms accurately. Treat 'Redaction' as a conceptual topic. Use bullet points.\n\n"
        "LANGUAGE (WORD LIMIT & TONE):\n"
        "Maintain EXECUTIVE CONCISCENESS. Keep responses dense but brief (under 400 words). "
        "Avoid fluff. STRICTLY ENGLISH ONLY."
    )

class ChatRequest(BaseModel):
    message: str
    history: List[Dict] = []

# 4. HEALTH CHECK
@app.get("/")
async def health():
    return {
        "status": "Art Consultant Agent Online",
        "framework": "GAIL + Synthesis + Word Limit",
        "privacy": "Full-Scrub-Active"
    }

# 5. MAIN CHAT ENDPOINT
@app.post("/chat")
async def process_chat(request: ChatRequest):
    from openai import OpenAI

    safe_input = redact_pii(request.message)

    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if not api_key:
        return {"error": "DeepSeek API Key missing."}

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    messages = [{"role": "system", "content": get_art_system_prompt()}] + request.history
    messages.append({"role": "user", "content": safe_input})

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.6,
            # Hard token limit at the API level as a backup for the word limit
            max_tokens=800 
        )

        reply = response.choices[0].message.content
        del messages, safe_input
        gc.collect()
        return {"reply": reply}
    except Exception as e:
        gc.collect()
        return {"error": f"Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
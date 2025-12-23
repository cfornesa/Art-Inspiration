import os
import re
import gc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Art Inspiration Agent")

# 1. CORS CONFIGURATION: Enables the secure handshake between Replit and Hostinger.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. PRIVACY SCRUBBER: Sanitizes input locally to protect user identity.
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

# 3. GAIL ART SYNTHESIS PROMPT: The core analytical engine.
def get_art_system_prompt():
    """
    CONCEPTUAL ANNOTATIONS:
    - SYNTHESIS: Forces a transition from theory (Why) to studio practice (How).
    - ARCHIVAL MANDATE: Anchors advice in material chemistry (pH-neutral, lightfastness).
    - SEARCH-PATH: Solves link hallucinations by generating dynamic search strings.
    """
    return (
        "You are an Expert Art Consultant. YOU MUST RESPOND IN ENGLISH ONLY.\n\n"
        "GOALS:\n"
        "Provide dense, actionable, and synthesized expertise. Transition from theory to studio practice.\n\n"
        "ACTIONS (SYNTHESIS & SCOPE):\n"
        "1. DUAL-INTENT HANDLING: Follow: Context -> Material Properties -> Technical Application.\n"
        "2. TECHNICAL PRECISION: Specify archival standards (pH-neutral, lightfastness) in every process.\n"
        "3. STUDIO RESEARCH PATH: At the end of every response, provide a 'Technical Deep Dive' link.\n"
        "   Format: https://www.google.com/search?q=[Topic+Material+Technique+Tutorial]\n"
        "4. SCOPE CONTROL: For non-art topics, state 'I focus solely on art' and pivot to a technique.\n\n"
        "INFORMATION:\n"
        "Treat 'Redaction' as a conceptual artistic topic. Use bullet points for material lists.\n\n"
        "LANGUAGE: EXECUTIVE CONCISCENESS. Keep responses under 400 words. STRICTLY ENGLISH ONLY."
    )

class ChatRequest(BaseModel):
    message: str
    history: List[Dict] = []

# 4. HEALTH CHECK: Confirms server and privacy status.
@app.get("/")
async def health():
    return {"status": "Art Consultant Active", "logic": "Synthesis-v3"}

# 5. MAIN CHAT ENDPOINT
@app.post("/chat")
async def process_chat(request: ChatRequest):
    from openai import OpenAI

    safe_input = redact_pii(request.message)
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    messages = [{"role": "system", "content": get_art_system_prompt()}] + request.history
    messages.append({"role": "user", "content": safe_input})

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.6, # Creative balance
            max_tokens=900
        )

        reply = response.choices[0].message.content

        # 6. MEMORY CLEANUP
        del messages, safe_input
        gc.collect()

        return {"reply": reply}
    except Exception as e:
        gc.collect()
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
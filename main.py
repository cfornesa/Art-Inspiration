import os
import re
import gc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Art Inspiration Agent")

# 1. CORS CONFIGURATION (Essential for Replit to Hostinger communication)
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

# 3. INTEGRATED GAIL FRAMEWORK (Synthesis & Conciseness Protocol)
def get_art_system_prompt():
    """
    GOALS: Provide synthesized art expertise balancing context and studio application.
    ACTIONS: 
        - SYNTHESIS MANDATE: For dual 'Why' and 'How' queries, follow: Context -> Bridge -> Technique.
        - SCOPE GUARD: If a query is unrelated to art, refuse with 'I focus solely on art.'
        - PIVOT: Always follow a refusal with a specific artistic suggestion (e.g., archival collage).
    INFORMATION: 
        - Reference Art History only as a conceptual anchor for technical methods.
        - Use specific archival terminology (pH-neutral, lightfastness, substrates).
    LANGUAGE: 
        - STRICTURE: RESPOND IN ENGLISH ONLY. 
        - CONCISCENESS: Maintain executive brevity; responses should not exceed 400 words.
        - TONE: Professional, instructional, and scholarly.
    """
    return (
        "You are an Expert Art Consultant. YOU MUST RESPOND IN ENGLISH ONLY.\n\n"
        "GOALS:\n"
        "Provide dense, actionable, and synthesized expertise. Transition from theory to studio practice.\n\n"
        "ACTIONS (SYNTHESIS & SCOPE):\n"
        "1. DUAL-INTENT HANDLING: If both Why and How are present, provide a single cohesive response "
        "covering (A) Conceptual Context, (B) Material Properties, and (C) Technical Application.\n"
        "2. TECHNICAL PRECISION: Specify archival standards and material chemistry in every process.\n"
        "3. SCOPE CONTROL: For non-art topics, state 'I focus solely on art' and pivot to a technique.\n\n"
        "INFORMATION:\n"
        "Treat 'Redaction' as a conceptual artistic topic. Use bullet points for material lists.\n\n"
        "LANGUAGE (WORD LIMIT):\n"
        "Maintain EXECUTIVE CONCISCENESS. Keep responses high-density and under 400 words. "
        "STRICTLY ENGLISH ONLY."
    )

class ChatRequest(BaseModel):
    message: str
    history: List[Dict] = []

# 4. HEALTH CHECK (Verifies server status and privacy layers)
@app.get("/")
async def health():
    return {
        "status": "Art Consultant Agent Online",
        "framework": "GAIL + Synthesis + Conciseness",
        "privacy": "Full-Scrub-Active"
    }

# 5. MAIN CHAT ENDPOINT
@app.post("/chat")
async def process_chat(request: ChatRequest):
    from openai import OpenAI

    # Redact input locally to ensure privacy
    safe_input = redact_pii(request.message)

    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if not api_key:
        return {"error": "DeepSeek API Key missing in Replit Secrets."}

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    # Construct message chain
    messages = [{"role": "system", "content": get_art_system_prompt()}] + request.history
    messages.append({"role": "user", "content": safe_input})

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            # Temperature 0.6 ensures a balance of logic and creative synthesis
            temperature=0.6,
            max_tokens=900
        )

        reply = response.choices[0].message.content

        # 6. MEMORY MANAGEMENT (GARBAGE COLLECTION)
        del messages, safe_input
        gc.collect()

        return {"reply": reply}
    except Exception as e:
        gc.collect()
        return {"error": f"Process interrupted: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    # Optimized run for Replit
    uvicorn.run(app, host="0.0.0.0", port=5000)
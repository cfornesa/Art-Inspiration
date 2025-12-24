import os
import re
import gc
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Art Inspiration Agent - Mistral Edition")

# 1. CORS PROTOCOL (Digital Handshake)
# Essential for allowing your website frontend to communicate with this Replit backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. PRIVACY SCRUBBER (PII Sanitization)
# Complies with your mission to protect user data from being unethically used by LLMs.
PII_PATTERNS = {
    "EMAIL": re.compile(r'[\w\.-]+@[\w\.-]+\.\w+', re.IGNORECASE),
    "PHONE": re.compile(r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'),
    "SSN": re.compile(r'\b(?!666|000|9\d{2})\d{3}[- ]?(?!00)\d{2}[- ]?(?!0000)\d{4}\b'),
    "ADDRESS": re.compile(r'\d{1,5}\s\w+.\s(\b\w+\b\s){1,2}\w+,\s\w+,\s[A-Z]{2}\s\d{5}', re.IGNORECASE)
}

def redact_pii(text: str) -> str:
    for label, pattern in PII_PATTERNS.items():
        text = pattern.sub(f"[{label}_REDACTED]", text)
    return text

# 3. GAIL ART SYNTHESIS PROMPT
# Structured to provide MFA-level studio advice with archival precision.
def get_art_system_prompt():
    return (
        "You are an Expert Art Consultant. YOU MUST RESPOND IN ENGLISH ONLY.\n\n"
        "GOALS:\n"
        "Provide dense, actionable, and synthesized expertise. Transition from theory to studio practice.\n\n"
        "ACTIONS:\n"
        "1. DUAL-INTENT HANDLING: Structure as: (A) Conceptual Framework, (B) Material & Technical Application, and (C) Archival Standard.\n"
        "2. TECHNICAL PRECISION: Specify archival chemistry (pH-neutral, lightfastness, acid-free) in every process.\n"
        "3. RELEVANT LINKS: At the end of every response, provide a search-based technical resource link.\n"
        "   Format exactly: Relevant Links: https://www.google.com/search?q=[Topic+Material+Technique+Tutorial]\n"
        "4. SCOPE CONTROL: For non-art topics, state 'I focus solely on art' and pivot to an artistic technique.\n\n"
        "LANGUAGE:\n"
        "EXECUTIVE CONCISCENESS. Keep responses high-density and under 400 words. STRICTLY ENGLISH ONLY."
    )

class ChatRequest(BaseModel):
    message: str
    history: List[Dict] = []

# --- HEALTH CHECK ROUTE ---
# Prevents Replit Deployment termination by acknowledging the 'ping'.
@app.get("/")
async def health_check():
    return {
        "status": "online", 
        "agent": "Art Inspiration Agent",
        "system_version": "1.1.1",
        "provider": "Mistral AI",
        "model": "ministral-14b-2512"
    }

# 4. MAIN API ENDPOINT (/chat)
@app.post("/chat")
async def process_chat(request: ChatRequest):
    from openai import OpenAI

    # Local Redaction before the data leaves the Replit environment
    safe_input = redact_pii(request.message)
    api_key = os.environ.get('MISTRAL_API_KEY')

    if not api_key:
        return {"reply": "Error: MISTRAL_API_KEY is not configured in server secrets."}

    # Mistral uses /v1 for its OpenAI-compatible endpoint
    client = OpenAI(api_key=api_key, base_url="https://api.mistral.ai/v1")

    # Combine instructions, history, and the new sanitized query
    messages = [{"role": "system", "content": get_art_system_prompt()}] + request.history
    messages.append({"role": "user", "content": safe_input})

    try:
        # Utilizing the 14B Reasoning model for high-integrity studio advice
        response = client.chat.completions.create(
            model="ministral-14b-latest", 
            messages=messages,
            temperature=0.15, 
            max_tokens=900
        )

        # Explicitly extract the text to ensure the frontend receives a clean string
        reply_content = response.choices[0].message.content

        # Cleanup memory for Replit's efficiency
        del messages, safe_input
        gc.collect()

        return {"reply": reply_content.strip()}

    except Exception as e:
        gc.collect()
        # Returns the error as the 'reply' so it shows up in the Chat Window
        return {"reply": f"System Error: {str(e)}"}

# 5. REPLIT PRODUCTION RUNNER
if __name__ == "__main__":
    # Dynamically find the port assigned by Replit (Deployment or Workspace)
    port = int(os.environ.get("PORT", 5000))
    print(f"Server starting on port {port}...")

    # Using the string "main:app" allows for hot-reloads and better process management
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
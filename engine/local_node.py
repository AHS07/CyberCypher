from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import ollama
from config import supabase
from utils import log_to_supabase
import datetime

app = FastAPI()

class InferRequest(BaseModel):
    prompt: str
    model: str = "llama3.2"

@app.post("/infer")
def infer(req: InferRequest):
    try:
        # Call Ollama
        # prompt said: response = ollama.generate(model=req.model, prompt=req.prompt)
        response = ollama.generate(model=req.model, prompt=req.prompt)
        
        # In a real agent scenario, we'd want to parse this. 
        # For the "Skeptic", the prompt expects structured output.
        # But this endpoint is generic /infer. 
        # The prompt says: "Structured Output: ... Output: {is_bug: bool...}"
        # It's better if this endpoint returns the raw response or the structured one if the LLM followed instructions.
        # I'll return the full response object or just the text.
        # The prompt snippet: 
        # structured = { "is_bug": True, "reason": response["response"], ... }
        # This implies we are hardcoding the parsing here or the LLM is good.
        # Since this is a generic /infer, I should probably just return the text data, 
        # OR if this is specifically the "Local Node Agent", it might do the logic.
        # User said "Wrapper Endpoint... Takes prompt... Returns structured".
        # I will return the raw response content to be flexible, 
        # or wrapping it as requested.
        # The snippet had:
        # structured = { "is_bug": True, "reason": response["response"], "confidence": 0.85 }
        # This looks like just wrapping the text. I'll do that.
        
        result_text = response.get("response", "")
        
        # Log to reliability logs
        log_to_supabase("reliability_logs", {
            "timestamp": datetime.datetime.now().isoformat(),
            "provider": "local_llama",
            "error_type": "none"
        })
        
        return {
            "model": req.model,
            "response": result_text,
            "done": response.get("done", False)
        }
    except Exception as e:
        log_to_supabase("reliability_logs", {
            "timestamp": datetime.datetime.now().isoformat(),
            "provider": "local_llama",
            "error_type": str(e)
        })
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

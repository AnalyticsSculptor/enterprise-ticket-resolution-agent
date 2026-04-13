from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
from agent import ITSupportAgent

# 1. Initialize the FastAPI App
app = FastAPI(title="Enterprise AutoTriage API")

# 2. Configure CORS (Crucial!)
# This allows your frontend (HTML file) to securely talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Boot up the AI Agent (It loads ChromaDB and the Groq LLM)
print("Initializing AI Engine...")
ai_agent = ITSupportAgent()

# 4. Define the Data Schema
class TicketRequest(BaseModel):
    issue: str
    
@app.get("/")
def serve_homepage():
    """Serves the frontend UI when someone visits the main URL"""
    return FileResponse("index.html")
# 5. Create the API Endpoint
@app.post("/api/triage")
def triage_ticket(ticket: TicketRequest):
    """
    This is the endpoint the frontend will hit.
    It passes the user's issue to your Agent and returns the JSON.
    """
    decision = ai_agent.process_ticket(ticket.issue)
    
    if not decision:
        return {"status": "error", "message": "AI failed to process the ticket."}
    
    return decision

if __name__ == "__main__":
    print("🚀 Starting FastAPI Server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
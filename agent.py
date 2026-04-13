import os


os.environ["HF_TOKEN"] = os.environ.get("SECURE_HF_TOKEN", "")
import json
import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

load_dotenv()

class ITSupportAgent:
    def __init__(self):
        print("⚙️ Booting up Enterprise IT Triage Agent...")
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # 1. The Core Knowledge Base (The Long-Term Memory)
        self.db = Chroma(persist_directory="./chroma_db", embedding_function=self.embeddings)
        
        # 2. The Semantic Cache (The Short-Term Memory)
        self.cache_db = Chroma(collection_name="live_cache", embedding_function=self.embeddings)
        
        # 3. The LLM Router
        self.llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)

    def process_ticket(self, user_issue):
        print(f"\n🎫 NEW TICKET RECEIVED: '{user_issue}'")
        start_time = time.time()
        
        # ==========================================
        # LAYER 0: SEMANTIC CACHE INTERCEPT
        # ==========================================
        # Check if we've solved a highly similar ticket recently
        cache_results = self.cache_db.similarity_search_with_score(user_issue, k=1)
        
        # If the distance score is very low (e.g., < 0.2), it's basically the same issue!
        if cache_results and cache_results[0][1] < 0.2:
            print("⚡ CACHE HIT! Bypassing LLM. Saving API Cost and Time.")
            cached_decision = json.loads(cache_results[0][0].page_content)
            
            end_time = time.time()
            print("-" * 50)
            print(f"📂 ASSIGNED CATEGORY: {cached_decision.get('category')} (Pulled from Cache)")
            print(f"⏱️ LATENCY: {end_time - start_time:.3f} seconds")
            print("-" * 50)
            return cached_decision
            
        print("🔍 No cache hit. Querying Vector DB and waking up AI Agent...")

        # ==========================================
        # LAYER 1: RAG (Retrieval)
        # ==========================================
        retriever = self.db.as_retriever(search_kwargs={"k": 3})
        similar_tickets = retriever.invoke(user_issue)
        
        history_context = ""
        for i, doc in enumerate(similar_tickets):
            historic_cause = doc.metadata.get('Cause', 'Unknown')
            history_context += f"\n[Past Ticket {i+1}] Issue: {doc.page_content}\n  -> Historic Cause: {historic_cause}\n"

        # ==========================================
        # LAYER 2: AGENTIC REASONING
        # ==========================================
        prompt = f"""
        You are a Senior IT Triage Agent. Analyze the new ticket based ONLY on the provided history.
        
        NEW TICKET: "{user_issue}"
        
        SIMILAR PAST TICKETS FOR CONTEXT:
        {history_context}
        
        STRICT CATEGORY DEFINITIONS:
        - NETWORK: Firewalls, VPNs, DNS, routing, and connectivity blocks.
        - SECURITY: Hackers, malware, unauthorized logins, phishing, and 2FA alerts.
        - APPLICATION: Software bugs, 502/504 web errors, app crashes, UI issues.
        - INFRASTRUCTURE: Server outages, AWS/Azure resource limits, VM provisioning.
        - DATABASE: SQL timeouts, deadlocks, data corruption, table locks.
        - ACCESS MANAGEMENT: Passwords, AWS IAM permissions, role requests.
        - HARDWARE: Physical device failure, mice, monitors, burning smells.
        
        TASK: Output ONLY a valid JSON object with these exact keys:
        - "category": (MUST be exactly one of the categories above)
        - "reasoning_trace": (Briefly explain your logic)
        - "confidence_calculation": (Start at 0.0. Add 0.4 for exact definition match. Add 0.3 for tech match. Add 0.2 for identical symptoms. Subtract 0.4 if guessing.)
        - "confidence": (The calculated float)
        - "suggested_resolution": (Steps to fix based on history)
        - "is_repeated_issue": (true/false)
        """

        response = self.llm.invoke(prompt).content
        
        try:
            clean_json = response.replace("```json", "").replace("```", "").strip()
            decision = json.loads(clean_json)
        except Exception:
            return None

        # ==========================================
        # LAYER 3: SAVE TO CACHE
        # ==========================================
       
        cache_doc = Document(page_content=clean_json, metadata={"original_issue": user_issue})
        self.cache_db.add_documents([cache_doc])

        # ==========================================
        # LAYER 4: ROUTING LOGIC
        # ==========================================
        end_time = time.time()
        print("-" * 50)
        print(f"🧠 AI REASONING: {decision.get('reasoning_trace')}")
        print(f"📂 ASSIGNED CATEGORY: {decision.get('category').upper()} (Confidence: {decision.get('confidence') * 100}%)")
        print(f"⏱️ LATENCY: {end_time - start_time:.3f} seconds")
        print("-" * 50)
        
        return decision

if __name__ == "__main__":
    agent = ITSupportAgent()
    
    print("\n" + "="*50 + "\n🚀 TESTING CACHE PIPELINE\n" + "="*50)
    
    # 1. The first user reports an issue (Hits the LLM)
    print("\n--- TEST 1: First Occurrence ---")
    agent.process_ticket("Virtualization Platform reporting duplicate records.")
    
    # 2. A second user reports the EXACT same issue (Should hit cache)
    print("\n--- TEST 2: Exact Duplicate ---")
    agent.process_ticket("Patch Management experiencing resource constraints.")
    
    # 3. A third user reports the same issue, but uses DIFFERENT words (Semantic Cache Magic!)
    print("\n--- TEST 3: Semantic Duplicate ---")
    agent.process_ticket("Production SQL db is completely frozen, queries are hitting a timeout.")

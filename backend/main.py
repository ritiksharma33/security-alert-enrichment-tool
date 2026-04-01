import asyncio
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from fastapi.middleware.cors import CORSMiddleware
# Import our custom modules
from models.schemas import AlertRequest, EnrichedAlert
from services.enrichment import query_abuseipdb
from services.logic import analyze_threat

app = FastAPI(
    title="Automated Security Alert Enrichment Tool",
    description="Simulates a SOAR playbook by enriching IP addresses with Threat Intel.",
    version="1.0.0"
)

# --- CORS SETUP ---
# Crucial: This allows your React frontend (usually running on port 3000 or 5173) 
# to talk to this FastAPI backend (running on port 8000) without being blocked.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Your React dev URL
    allow_credentials=True,
    allow_methods=["*"], # Allows POST, GET, etc.
    allow_headers=["*"], # Allows all headers
)

# --- STANDARD REST ENDPOINT ---
@app.post("/api/enrich", response_model=EnrichedAlert)
async def process_alert(alert: AlertRequest):
    """
    Standard API endpoint. Takes a JSON payload, processes it instantly, 
    and returns the final enriched alert.
    """
    # 1. Get raw data from the internet
    raw_intel = query_abuseipdb(str(alert.source_ip))
    
    # 2. Run the SOAR logic
    risk_level, intel_model = analyze_threat(raw_intel)
    
    # 3. Return the fully packaged Pydantic model
    return EnrichedAlert(
        alert_id=alert.alert_id,
        source_ip=str(alert.source_ip),
        original_event=alert.event,
        risk_level=risk_level,
        threat_intel=intel_model
    )

# --- VISUAL LOG STREAMING ENDPOINT (SSE) ---
@app.get("/api/enrich/stream")
async def stream_enrichment_logs(ip: str):
    """
    Streaming endpoint for the React frontend terminal. 
    Yields text logs step-by-step to simulate real-time processing.
    """
    async def event_generator():
        # Step 1: Initialization
        yield {"data": f"[INFO] Initialization complete. Target IP: {ip}"}
        await asyncio.sleep(1) # Artificial delay so the UI looks cool!
        
        # Step 2: Querying
        yield {"data": f"[NETWORK] Initiating secure connection to AbuseIPDB API..."}
        await asyncio.sleep(1.5)
        
        # We wrap the synchronous request in a way that doesn't block the async generator
        raw_intel = await asyncio.to_thread(query_abuseipdb, ip)
        score = raw_intel.get("abuseConfidenceScore", "N/A")
        
        # Step 3: Response
        yield {"data": f"[SUCCESS] Payload received. Confidence Score: {score}/100."}
        await asyncio.sleep(1)
        
        # Step 4: Logic Execution
        yield {"data": f"[SYSTEM] Executing SOAR playbook logic matrix..."}
        await asyncio.sleep(1)
        
        risk_level, intel_model = analyze_threat(raw_intel)
        yield {"data": f"[ACTION] Logic applied. Risk Level classified as: {risk_level}"}
        await asyncio.sleep(1)
        
        # Step 5: Final output
        yield {"data": f"[COMPLETE] Pipeline finished successfully."}
        
    return EventSourceResponse(event_generator())
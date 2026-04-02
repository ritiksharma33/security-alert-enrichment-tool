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


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)


@app.post("/api/enrich", response_model=EnrichedAlert)
async def process_alert(alert: AlertRequest):
    """
    Standard API endpoint. Takes a JSON payload, processes it instantly, 
    and returns the final enriched alert.
    """
   
    raw_intel = query_abuseipdb(str(alert.source_ip))
    
   
    risk_level, intel_model = analyze_threat(raw_intel)
    
   
    return EnrichedAlert(
        alert_id=alert.alert_id,
        source_ip=str(alert.source_ip),
        original_event=alert.event,
        risk_level=risk_level,
        threat_intel=intel_model
    )


@app.get("/api/enrich/stream")
async def stream_enrichment_logs(ip: str):
    """
    Streaming endpoint for the React frontend terminal. 
    Yields text logs step-by-step to simulate real-time processing.
    """
    async def event_generator():
     
        yield {"data": f"[INFO] Initialization complete. Target IP: {ip}"}
        await asyncio.sleep(1) 
        
      
        yield {"data": f"[NETWORK] Initiating secure connection to AbuseIPDB API..."}
        await asyncio.sleep(1.5)
        
      
        raw_intel = await asyncio.to_thread(query_abuseipdb, ip)
        score = raw_intel.get("abuseConfidenceScore", "N/A")
        
      
        yield {"data": f"[SUCCESS] Payload received. Confidence Score: {score}/100."}
        await asyncio.sleep(1)
        
       
        yield {"data": f"[SYSTEM] Executing SOAR playbook logic matrix..."}
        await asyncio.sleep(1)
        
        risk_level, intel_model = analyze_threat(raw_intel)
        yield {"data": f"[ACTION] Logic applied. Risk Level classified as: {risk_level}"}
        await asyncio.sleep(1)
        

        yield {"data": f"[COMPLETE] Pipeline finished successfully."}
        
    return EventSourceResponse(event_generator())
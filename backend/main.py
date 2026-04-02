import asyncio
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from typing import Optional

# Import your models
from models.schemas import EnrichedAlert

# Import your services
from services.enrichment import get_ip_intel # Ensure this matches your filename!
from services.logic import analyze_threat, analyze_domain_risk
from services.domain_service import lookup_domain
from services.hash_service import lookup_hash
from services.bulk_service import process_bulk_csv

app = FastAPI(title="Sentinel SOAR Hub")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# This model fixes the "422 Field Required" error
class EnrichmentRequest(BaseModel):
    source_ip: str
    event: Optional[str] = "Manual UI Scan"
    alert_id: Optional[str] = "N/A"

# --- 1. IP ENRICHMENT ROUTE ---
@app.post("/api/enrich", response_model=EnrichedAlert)
async def process_alert(request: EnrichmentRequest):
    # Use 'await' because get_ip_intel is async
    raw_intel = await get_ip_intel(request.source_ip)
    risk_level, intel_model = analyze_threat(raw_intel)
    
    return EnrichedAlert(
        alert_id=request.alert_id,
        source_ip=request.source_ip,
        original_event=request.event,
        risk_level=risk_level,
        threat_intel=intel_model
    )

# --- 2. DOMAIN LOOKUP ROUTE (FIXED) ---
@app.get("/api/domain")
async def domain_intel(domain: str):
    # IMPORTANT: Added 'await' because domain lookup involves a network call
    # If your lookup_domain is NOT async, remove 'await' and use asyncio.to_thread
    data = await asyncio.to_thread(lookup_domain, domain) 
    
    if "error" in data:
        return data
        
    risk_level = analyze_domain_risk(data)
    return {**data, "risk_level": risk_level}

# --- 3. HASH ANALYSIS ROUTE ---
@app.get("/api/hash")
async def get_hash_intel(hash: str):
    result = await lookup_hash(hash)
    return result

# --- 4. BULK SCAN ROUTE ---
@app.post("/api/bulk-scan")
async def bulk_scan(file: UploadFile = File(...)):
    contents = await file.read()
    results = await process_bulk_csv(contents)
    return {"status": "success", "data": results}

# --- 5. STREAMING LOGS ---
@app.get("/api/enrich/stream")
async def stream_enrichment_logs(ip: str):
    async def event_generator():
        yield {"data": f"[INFO] Initialization complete. Target IP: {ip}"}
        await asyncio.sleep(0.5) 
        yield {"data": f"[NETWORK] Querying Threat Intelligence APIs..."}
        
        raw_intel = await get_ip_intel(ip)
        score = raw_intel.get("abuseConfidenceScore", 0)
        
        yield {"data": f"[SUCCESS] Data received. Confidence Score: {score}/100."}
        risk_level, _ = analyze_threat(raw_intel)
        yield {"data": f"[ACTION] Playbook logic applied: {risk_level}"}
        yield {"data": f"[COMPLETE] Pipeline finished."}
        
    return EventSourceResponse(event_generator())
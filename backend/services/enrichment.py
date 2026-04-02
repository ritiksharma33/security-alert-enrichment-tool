import requests
from core.config import settings


import os
import httpx
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ABUSEIPDB_API_KEY")

async def get_ip_intel(ip_address: str) -> dict:
    """
    Fetches threat intelligence for a single IP from AbuseIPDB.
    This is the core 'Enrichment' function.
    """
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {
        "Accept": "application/json",
        "Key": API_KEY
    }
    params = {
        "ipAddress": ip_address,
        "maxAgeInDays": "90"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params)
            if response.status_code == 200:
            
                return response.json().get("data", {})
            else:
                print(f"[ERROR] API returned status {response.status_code}")
                return {}
        except Exception as e:
            print(f"[ERROR] Connection to AbuseIPDB failed: {e}")
            return {}

def query_abuseipdb(ip_address: str) -> dict:
    """
    Queries AbuseIPDB API with proper error handling and dummy fallback.
    """
    
    if not settings.ABUSEIPDB_API_KEY or "your_api_key" in settings.ABUSEIPDB_API_KEY:
        return {
            "abuseConfidenceScore": 85,
            "totalReports": 120,
            "countryCode": "RU",
            "domain": "dummy-data.com"
        }
    
    
    url = "https://api.abuseipdb.com/api/v2/check"
    querystring = {"ipAddress": ip_address, "maxAgeInDays": "90"}
    headers = {"Accept": "application/json", "Key": settings.ABUSEIPDB_API_KEY}

    try:
        
        response = requests.get(url, headers=headers, params=querystring, timeout=5)
        
        
        if response.status_code == 422:
            print(f"[VALIDATION ERROR] {ip_address} is not a valid public IP.")
            return {"abuseConfidenceScore": 0, "totalReports": 0, "error": "Invalid IP format"}

       
        response.raise_for_status()
        
       
        json_response = response.json()
        return json_response.get("data", {})

    except requests.exceptions.Timeout:
        print(f"[ERROR] Connection to AbuseIPDB timed out for IP {ip_address}")
        return {"error": "timeout", "abuseConfidenceScore": 0, "totalReports": 0}
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to query AbuseIPDB: {e}")
        return {"error": str(e), "abuseConfidenceScore": 0, "totalReports": 0}
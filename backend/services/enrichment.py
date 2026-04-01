import requests
from core.config import settings

def query_abuseipdb(ip_address: str) -> dict:
    """
    Queries AbuseIPDB API with proper error handling and dummy fallback.
    """
    # 1. Dummy Data Fallback
    if not settings.ABUSEIPDB_API_KEY or "your_api_key" in settings.ABUSEIPDB_API_KEY:
        return {
            "abuseConfidenceScore": 85,
            "totalReports": 120,
            "countryCode": "RU",
            "domain": "dummy-data.com"
        }
    
    # 2. Setup Request
    url = "https://api.abuseipdb.com/api/v2/check"
    querystring = {"ipAddress": ip_address, "maxAgeInDays": "90"}
    headers = {"Accept": "application/json", "Key": settings.ABUSEIPDB_API_KEY}

    try:
        # 3. ACTUALLY MAKE THE REQUEST FIRST
        response = requests.get(url, headers=headers, params=querystring, timeout=5)
        
        # 4. Handle Specific Status Codes
        if response.status_code == 422:
            print(f"[VALIDATION ERROR] {ip_address} is not a valid public IP.")
            return {"abuseConfidenceScore": 0, "totalReports": 0, "error": "Invalid IP format"}

        # 5. Handle Other HTTP Errors (401, 429, 500, etc.)
        response.raise_for_status()
        
        # 6. Parse and Return Data
        json_response = response.json()
        return json_response.get("data", {})

    except requests.exceptions.Timeout:
        print(f"[ERROR] Connection to AbuseIPDB timed out for IP {ip_address}")
        return {"error": "timeout", "abuseConfidenceScore": 0, "totalReports": 0}
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to query AbuseIPDB: {e}")
        return {"error": str(e), "abuseConfidenceScore": 0, "totalReports": 0}
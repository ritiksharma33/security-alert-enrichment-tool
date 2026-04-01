import requests
from core.config import settings

def query_abuseipdb(ip_address: str) -> dict:
    """
    Reaches out to the AbuseIPDB API to get threat intelligence for a specific IP.
    """
    # If no API key is set in the .env file, return a dummy response for testing
    if not settings.ABUSEIPDB_API_KEY or settings.ABUSEIPDB_API_KEY == "your_api_key_here":
        print("[WARNING] No valid AbuseIPDB API key found. Returning dummy data.")
        return {
            "abuseConfidenceScore": 85,
            "totalReports": 120,
            "countryCode": "RU",
            "domain": "malicious-example.com"
        }

    url = "https://api.abuseipdb.com/api/v2/check"
    
    querystring = {
        "ipAddress": ip_address,
        "maxAgeInDays": "90"
    }
    
    headers = {
        "Accept": "application/json",
        "Key": settings.ABUSEIPDB_API_KEY
    }

    try:
        # We add a 5-second timeout so our app doesn't hang forever if the API is down
        response = requests.get(url, headers=headers, params=querystring, timeout=5)
        
        # This will raise an HTTPError if the status is 4xx or 5xx
        response.raise_for_status()
        
        # AbuseIPDB nests their actual data inside a "data" key
        json_response = response.json()
        return json_response.get("data", {})

    except requests.exceptions.Timeout:
        print(f"[ERROR] Connection to AbuseIPDB timed out for IP {ip_address}")
        return {"error": "timeout", "abuseConfidenceScore": 0, "totalReports": 0}
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to query AbuseIPDB: {e}")
        return {"error": str(e), "abuseConfidenceScore": 0, "totalReports": 0}
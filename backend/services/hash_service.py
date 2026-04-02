import os
import httpx
from dotenv import load_dotenv

load_dotenv()
VT_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")

async def lookup_hash(file_hash: str):
    """
    Queries VirusTotal for a file hash (SHA-256, SHA-1, or MD5).
    """
    url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
    headers = {
        "x-apikey": VT_API_KEY
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json().get("data", {})
                stats = data.get("attributes", {}).get("last_analysis_stats", {})
                
                # Logic: If more than 5 engines flag it, it's CRITICAL
                malicious_count = stats.get("malicious", 0)
                risk_level = "SAFE"
                if malicious_count > 10: risk_level = "CRITICAL"
                elif malicious_count > 0: risk_level = "SUSPICIOUS"

                return {
                    "hash": file_hash,
                    "malicious": malicious_count,
                    "suspicious": stats.get("suspicious", 0),
                    "undetected": stats.get("undetected", 0),
                    "risk_level": risk_level,
                    "type": data.get("attributes", {}).get("type_description", "Unknown")
                }
            else:
                return {"error": "Hash not found in VirusTotal database."}
        except Exception as e:
            return {"error": str(e)}
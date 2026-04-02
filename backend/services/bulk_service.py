import csv
import io
# This must match the filename and function name above
from services.enrichment import get_ip_intel 
from services.logic import analyze_threat

async def process_bulk_csv(file_content: bytes):
    """
    Parses a CSV file and runs enrichment on every IP found in the 'ip' column.
    """
    # Convert bytes to a file-like object
    stream = io.StringIO(file_content.decode("utf-8"))
    reader = csv.DictReader(stream)
    
    results = []
    
    for row in reader:
        target_ip = row.get("ip") or row.get("source_ip") or row.get("address")
        if target_ip:
            # Re-use our existing enrichment engine!
            raw_data = await get_ip_intel(target_ip)
            risk_level, intel = analyze_threat(raw_data)
            
            results.append({
                "ip": target_ip,
                "risk": risk_level,
                "score": intel.abuse_confidence_score,
                "country": intel.country_code
            })
            
    return results
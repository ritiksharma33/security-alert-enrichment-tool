import whois
from datetime import datetime

def lookup_domain(domain_name: str) -> dict:
    """
    Performs a WHOIS lookup and calculates domain age safely.
    """
    try:
        w = whois.whois(domain_name)
        
       
        creation_date = w.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]

       
        if creation_date:
           
            creation_date_naive = creation_date.replace(tzinfo=None)
            current_time_naive = datetime.now().replace(tzinfo=None)
            
            age_days = (current_time_naive - creation_date_naive).days
        else:
            age_days = 0

       
        return {
            "domain": domain_name,
            "registrar": w.registrar,
            "creation_date": str(creation_date_naive) if creation_date else "Unknown",
            "expiration_date": str(w.expiration_date) if w.expiration_date else "Unknown",
            "age_days": age_days,
            "status": w.status[0] if isinstance(w.status, list) else w.status,
        }
    except Exception as e:
      
        print(f"[ERROR] WHOIS lookup failed: {e}")
        return {"error": "Domain not found or lookup failed"}
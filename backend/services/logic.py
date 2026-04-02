from models.schemas import ThreatIntelligence
def analyze_domain_risk(domain_data: dict) -> str:
    """
    Heuristic for Domain Risk.
    New domains (< 30 days) = CRITICAL
    Recent domains (< 90 days) = WARNING
    """
    age = domain_data.get("age_days", 999)
    
    if age < 30:
        return "CRITICAL" 
    elif age < 90:
        return "WARNING"
    elif age > 365:
        return "SAFE"
    
    return "SUSPICIOUS"

WHITELIST = {
    "1.1.1.1", "1.0.0.1",       # Cloudflare
    "8.8.8.8", "8.8.4.4",       # Google DNS
    "9.9.9.9",                  # Quad9
    "127.0.0.1", "0.0.0.0"      # Localhost / Internal
}

def analyze_threat(raw_threat_data: dict) -> tuple[str, ThreatIntelligence]:
    """
    Advanced SOAR Playbook Logic:
    1. Checks Whitelist for Trusted Infrastructure.
    2. Applies a Tiered Sensitivity Matrix for Risk Classification.
    """

    ip = raw_threat_data.get("ipAddress", "Unknown")
    score = raw_threat_data.get("abuseConfidenceScore", 0)
    reports = raw_threat_data.get("totalReports", 0)
    country = raw_threat_data.get("countryCode", "Unknown")
    domain = raw_threat_data.get("domain", "N/A")


    if ip in WHITELIST:
        risk_level = "SAFE"
     
        intel_model = ThreatIntelligence(
            abuse_confidence_score=0,
            total_reports=reports,
            country_code=country,
            domain="TRUSTED_INFRASTRUCTURE"
        )
        return risk_level, intel_model

    
    if score >= 50:
        risk_level = "CRITICAL"
        
  
    elif score >= 20 or reports > 10:
        risk_level = "WARNING"
        

    elif score >= 5 or reports > 0:
        risk_level = "SUSPICIOUS"
        

    else:
        risk_level = "SAFE"



    intel_model = ThreatIntelligence(
        abuse_confidence_score=score,
        total_reports=reports,
        country_code=country,
        domain=domain
    )

    return risk_level, intel_model
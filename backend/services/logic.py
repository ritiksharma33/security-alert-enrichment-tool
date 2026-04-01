from models.schemas import ThreatIntelligence

def analyze_threat(raw_threat_data: dict) -> tuple[str, ThreatIntelligence]:
    """
    Redesigned logic to classify risk based on sensitivity.
    Now categorizes 10% activity as SUSPICIOUS instead of SAFE.
    """
    score = raw_threat_data.get("abuseConfidenceScore", 0)
    reports = raw_threat_data.get("totalReports", 0)
    country = raw_threat_data.get("countryCode")
    domain = raw_threat_data.get("domain")

    # --- THE SENSITIVITY MATRIX ---
    
    # 1. CRITICAL: High confidence of malicious activity (>= 50%)
    if score >= 50:
        risk_level = "CRITICAL"
        
    # 2. WARNING: Moderate confidence or high volume of reports
    elif score >= 20 or reports > 10:
        risk_level = "WARNING"
        
    # 3. SUSPICIOUS: Any measurable threat activity (Your 10% sits here!)
    elif score >= 5 or reports > 0:
        risk_level = "SUSPICIOUS"
        
    # 4. SAFE: Absolutely zero evidence of abuse
    else:
        risk_level = "SAFE"

    # Package data into the Pydantic schema
    intel_model = ThreatIntelligence(
        abuse_confidence_score=score,
        total_reports=reports,
        country_code=country,
        domain=domain
    )

    return risk_level, intel_model
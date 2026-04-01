from models.schemas import ThreatIntelligence

def analyze_threat(raw_threat_data: dict) -> tuple[str, ThreatIntelligence]:
    """
    Simulates a SOAR playbook by applying risk classification rules.
    Takes raw dictionary data and returns the calculated Risk Level 
    and a structured ThreatIntelligence object.
    """
    # 1. Safely extract data (using .get() prevents crashes if a key is missing)
    score = raw_threat_data.get("abuseConfidenceScore", 0)
    reports = raw_threat_data.get("totalReports", 0)
    country = raw_threat_data.get("countryCode")
    domain = raw_threat_data.get("domain")

    # 2. The "If-This-Then-That" Logic Matrix
    if score >= 80:
        risk_level = "CRITICAL"
    elif score >= 40:
        risk_level = "SUSPICIOUS"
    elif reports > 10 and score > 0:
        # Edge case: Low score but highly reported
        risk_level = "SUSPICIOUS" 
    else:
        risk_level = "SAFE"

    # 3. Package the extracted data into our Pydantic schema
    intel_model = ThreatIntelligence(
        abuse_confidence_score=score,
        total_reports=reports,
        country_code=country,
        domain=domain
    )

    return risk_level, intel_model
from pydantic import BaseModel, IPvAnyAddress
from typing import Optional


class AlertRequest(BaseModel):
    """
    Validates the incoming alert data.
    IPvAnyAddress automatically ensures the string is a valid IPv4 or IPv6 address.
    """
    alert_id: str
    source_ip: IPvAnyAddress
    event: str


class ThreatIntelligence(BaseModel):
    """
    Structures the data we get back from AbuseIPDB.
    """
    abuse_confidence_score: int
    total_reports: int
    country_code: Optional[str] = None
    domain: Optional[str] = None


class EnrichedAlert(BaseModel):
    """
    The final JSON structure that will be sent to your React frontend 
    or written to a database.
    """
    alert_id: str
    source_ip: str
    original_event: str
    risk_level: str  # e.g., "CRITICAL", "SUSPICIOUS", "SAFE"
    threat_intel: ThreatIntelligence
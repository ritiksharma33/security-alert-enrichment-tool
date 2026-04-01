import os
from dotenv import load_dotenv


load_dotenv()

class Settings:
    """
    Centralized configuration management.
    All environment variables should be accessed through this class.
    """
    PROJECT_NAME: str = "Automated Security Alert Enrichment Tool"
    

    ABUSEIPDB_API_KEY: str = os.getenv("ABUSEIPDB_API_KEY", "")


settings = Settings()
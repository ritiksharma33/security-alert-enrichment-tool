import os
from pathlib import Path
from dotenv import load_dotenv


current_file_dir = Path(__file__).resolve().parent 


project_root = current_file_dir.parent.parent


env_path = project_root / ".env"


load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_NAME: str = "Automated Security Alert Enrichment Tool"
    ABUSEIPDB_API_KEY: str = os.getenv("ABUSEIPDB_API_KEY", "")

settings = Settings()


print(f"🔍 Looking for .env at: {env_path}")
if not settings.ABUSEIPDB_API_KEY:
    print("❌ SYSTEM ALERT: .env file NOT found or Key is EMPTY")
else:

    print(f"✅ SYSTEM ALERT: API Key Loaded (Starts with: {settings.ABUSEIPDB_API_KEY[:4]}...)")
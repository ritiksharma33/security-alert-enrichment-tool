import os
from pathlib import Path
from dotenv import load_dotenv

# 1. Get the directory where THIS file (config.py) is located
current_file_dir = Path(__file__).resolve().parent 

# 2. Go up two levels to reach the project root (backend/core/ -> backend/ -> root/)
project_root = current_file_dir.parent.parent

# 3. Define the exact path to the .env file
env_path = project_root / ".env"

# 4. Load it and print the path to the terminal so we can see it
load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_NAME: str = "Automated Security Alert Enrichment Tool"
    ABUSEIPDB_API_KEY: str = os.getenv("ABUSEIPDB_API_KEY", "")

settings = Settings()

# --- VERIFICATION PRINT ---
print(f"🔍 Looking for .env at: {env_path}")
if not settings.ABUSEIPDB_API_KEY:
    print("❌ SYSTEM ALERT: .env file NOT found or Key is EMPTY")
else:
    # Shows the first 4 characters to prove it's real
    print(f"✅ SYSTEM ALERT: API Key Loaded (Starts with: {settings.ABUSEIPDB_API_KEY[:4]}...)")
import os
import subprocess
import sys
import json

def create_project_structure():
    print("🚀 Bootstrapping project environment...")

    # 1. Create the Virtual Environment
    venv_dir = "venv"
    if not os.path.exists(venv_dir):
        print(f"📦 Creating virtual environment in '{venv_dir}'...")
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
    else:
        print("⚡ Virtual environment already exists. Skipping...")

    # 2. Define the directory structure inside 'backend'
    folders = [
        "backend/core",
        "backend/models",
        "backend/services",
        "backend/data"
    ]

    # 3. Define the files to create
    files = [
        "backend/main.py",
        "backend/.env",
        "backend/core/config.py",
        "backend/models/schemas.py",
        "backend/services/enrichment.py",
        "backend/services/logic.py"
    ]

    # 4. Build Directories
    print("📁 Building backend directories...")
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

    # 5. Build Empty Files
    print("📄 Creating Python files...")
    for file in files:
        with open(file, 'w') as f:
            pass # Creates an empty file

    # 6. Populate sample_alert.json
    sample_data = {
        "alert_id": "10234",
        "timestamp": "2026-04-01T12:00:00Z",
        "source_ip": "198.51.100.4",
        "event": "Failed Login"
    }
    with open("backend/data/sample_alert.json", 'w') as f:
        json.dump(sample_data, f, indent=4)

    # 7. Create .gitignore
    with open("backend/.gitignore", 'w') as f:
        f.write("venv/\n__pycache__/\n.env\n*.pyc\n.pytest_cache/\n")

    # 8. Create requirements.txt
    print("📝 Writing requirements.txt...")
    with open("backend/requirements.txt", 'w') as f:
        f.write("fastapi\nuvicorn\nrequests\npython-dotenv\npydantic\nsse-starlette\n")

    print("\n✅ Bootstrap complete! Your project structure is ready.")

if __name__ == "__main__":
    create_project_structure()
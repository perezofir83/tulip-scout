#!/usr/bin/env python3
"""
Quick start script to set up and run TulipScout.
"""
import os
import sys
import subprocess
from pathlib import Path


def main():
    """Run quick start setup."""
    print("🍷 TulipScout Quick Start\n")
    
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("=" * 60)
    print("STEP 1: Environment Setup")
    print("=" * 60)
    
    # Check for .env
    if not (project_root / ".env").exists():
        print("❌ .env file not found")
        print("\n📋 To set up:")
        print("1. Copy .env.example to .env:")
        print("   cp .env.example .env")
        print("\n2. Edit .env and add your Gemini API key:")
        print("   GEMINI_API_KEY=your_api_key_here")
        print("\n3. Copy your OAuth credentials:")
        print("   cp ~/Downloads/client_secret_*.json ./credentials.json")
        print("\nRun this script again after setup.")
        return 1
    else:
        print("✅ .env file found")
    
    # Check for credentials
    if not (project_root / "credentials.json").exists():
        print("❌ credentials.json not found")
        print("\n📋 Copy your Gmail OAuth credentials:")
        print("   cp ~/Downloads/client_secret_*.json ./credentials.json")
        print("\nRun this script again after setup.")
        return 1
    else:
        print("✅ credentials.json found")
    
    print("\n" + "=" * 60)
    print("STEP 2: Database Initialization")
    print("=" * 60)
    
    if not (project_root / "tulip_scout.db").exists():
        print("📊 Initializing database...")
        result = subprocess.run([sys.executable, "scripts/setup_db.py"])
        if result.returncode != 0:
            print("❌ Database setup failed")
            return 1
    else:
        print("✅ Database already initialized")
    
    print("\n" + "=" * 60)
    print("STEP 3: Gmail OAuth")
    print("=" * 60)
    
    if not (project_root / "token.pickle").exists():
        print("🔐 Running Gmail OAuth setup...")
        print("   (Browser window will open for authentication)\n")
        result = subprocess.run([sys.executable, "scripts/oauth_setup.py"])
        if result.returncode != 0:
            print("❌ OAuth setup failed")
            return 1
    else:
        print("✅ Gmail OAuth token found")
    
    print("\n" + "=" * 60)
    print("READY TO GO! 🚀")
    print("=" * 60)
    
    print("\n📋 Next steps:")
    print("\n1. Start API server:")
    print("   uvicorn src.main:app --reload --port 8000")
    print("\n2. In another terminal, start dashboard:")
    print("   streamlit run dashboard/app.py --server.port 8501")
    print("\n3. Test Copywriter agent:")
    print("   python scripts/test_copywriter.py")
    print("\n4. Access:")
    print("   - Dashboard: http://localhost:8501")
    print("   - API: http://localhost:8000")
    print("   - API Docs: http://localhost:8000/docs")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

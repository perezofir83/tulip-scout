# TulipScout - B2B Lead Generation System

Multi-agent system for intelligent wine importer prospecting and outreach automation.

## Features

- 🔍 **Hunter Agent**: LinkedIn/web scraping with stealth mode
- ✍️ **Copywriter Agent**: Pain-point matching email generation
- 📊 **Interactive Dashboard**: Lead review and approval workflow
- 🔐 **Gmail Integration**: Automated draft creation
- 🌍 **Regional Targeting**: Eastern Europe + Far East markets
- 🤖 **AI-Powered**: Gemini 2.0 for lead scoring and personalization

## Quick Start

### Prerequisites

- Python 3.11+
- Google Cloud Project with Gmail API enabled
- OAuth credentials (credentials.json)

### Installation

```bash
# Clone or navigate to project
cd tulip-scout

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Initialize database
python scripts/setup_db.py

# Run OAuth setup (one-time)
python scripts/oauth_setup.py
```

### Running the Application

```bash
# Start API server
uvicorn src.main:app --reload --port 8000

# In another terminal, start dashboard
streamlit run dashboard/app.py --server.port 8501
```

Access:
- API: http://localhost:8000
- Dashboard: http://localhost:8501
- API Docs: http://localhost:8000/docs

## Project Structure

```
tulip-scout/
├── src/                    # Core application
│   ├── agents/            # Hunter, Copywriter, Manager
│   ├── api/               # FastAPI routes
│   ├── database/          # SQLAlchemy models
│   ├── services/          # Business logic
│   ├── utils/             # Rate limiter, validators
│   └── prompts/           # LLM prompt templates
├── dashboard/             # Streamlit UI
├── scripts/               # Setup and utility scripts
└── tests/                 # Test suite
```

## Architecture

- **Backend**: FastAPI (async Python)
- **Frontend**: Streamlit
- **Database**: SQLite → PostgreSQL
- **Browser Automation**: Playwright + Stealth
- **AI/LLM**: Google Gemini 2.0 Flash
- **Email**: Gmail API

## Documentation

- [OAuth Setup Guide](../brain/35b4e9f2-d450-4a01-820f-6599a12e528d/gmail_oauth_setup.md)
- [Implementation Plan](../brain/35b4e9f2-d450-4a01-820f-6599a12e528d/implementation_plan.md)
- [API Documentation](http://localhost:8000/docs)

## License

Proprietary - Tulip Winery

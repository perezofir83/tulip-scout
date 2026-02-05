# TulipScout Testing Guide 🧪

## Quick Start - Test in 5 Minutes!

### Step 1: Setup (One-Time)

```bash
cd /Users/perezweinberg/.gemini/antigravity/scratch/tulip-scout

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium
```

### Step 2: Configure Environment

```bash
# Create .env file
cp .env.example .env
```

**Edit `.env` and add your Gemini API key:**
```bash
GEMINI_API_KEY=your_actual_key_here
```

### Step 3: Initialize Database & Gmail

```bash
# Run the quickstart script
python scripts/quickstart.py
```

This will:
- ✅ Check your `.env` file
- ✅ Initialize the SQLite database
- ✅ Run Gmail OAuth (browser will open to log in)

---

## Testing Options

### 🎯 Option 1: Test Copywriter Agent (Easiest!)

**What it does:** Creates a fake lead and generates a personalized email

```bash
python scripts/test_copywriter.py
```

**What you'll see:**

```
🧪 Testing TulipScout Copywriter Agent

📊 Initializing database...
📋 Creating test campaign: abc-123
🎯 Creating test lead: def-456

✍️  Generating personalized email with Copywriter agent...
   - Analyzing pain points...
   - Matching to Tulip assets...
   - Generating email...
   - Creating Gmail draft...

✅ Email generated successfully! Email ID: xyz-789

============================================================
📧 GENERATED EMAIL
============================================================
To: jan.kowalski@premiumwines.pl
Subject: Tulip Winery x Premium Wines Distribution: Sustainable Excellence
Pain Point: ESG
Tulip Asset: Village_of_Hope

------------------------------------------------------------
BODY:
------------------------------------------------------------
Hi Jan,

I noticed Premium Wines Distribution's strong commitment to 
sustainable wine sourcing and ethical partnerships...

[Full personalized email with Village of Hope story]
============================================================

🔗 View draft in Gmail: https://mail.google.com/mail/u/0/#drafts
```

**Where to find it:**
1. Terminal shows the complete email
2. Gmail drafts folder → **You'll see the actual draft!**

---

### 🔍 Option 2: Test Hunter Agent (LinkedIn Scraping)

**What it does:** Opens browser, searches LinkedIn, scrapes profiles, creates leads

```bash
python scripts/test_hunter.py
```

**Interactive prompts:**
```
🧪 Testing TulipScout Hunter Agent

⚠️  WARNING: This will open a browser and search LinkedIn
   You may need to log in to LinkedIn manually

Continue? (y/n): y
```

**What you'll see:**

1. **Browser opens** (Chromium window appears)
2. **Navigates to LinkedIn**
3. **Searches for "wine importer Poland"**
4. **If not logged in:** LinkedIn prompts you to log in → **Log in manually**
5. **Scrapes 3 profiles** (you'll see pages changing)
6. **Closes browser**

**Terminal output:**
```
📊 Initializing database...
📋 Creating test campaign: abc-123

🔍 Starting Hunter agent...
   - Searching LinkedIn...
   - Scraping profiles...
   - Scoring leads...
   - Creating lead records...

✅ Hunter complete! Created 3 leads

============================================================
📊 CREATED LEADS
============================================================

🏢 Premium Wines Distribution Poland
   Location: Warsaw, Poland
   Decision Maker: Jan Kowalski (Chief Buyer)
   Fit Score: 8.5/10
   LinkedIn: https://linkedin.com/in/jan-kowalski-xyz
   Inferred Emails: jan.kowalski@premiumwines.pl, ...
   Status: pending

🏢 Warsaw Wine Imports
   Location: Warsaw, Poland
   Decision Maker: Anna Nowak (Procurement Director)
   Fit Score: 7.2/10
   LinkedIn: https://linkedin.com/in/anna-nowak-xyz
   Inferred Emails: a.nowak@warsawwine.pl, ...
   Status: pending

============================================================

✅ Test complete! View leads in dashboard:
   streamlit run dashboard/app.py
```

**Where to find results:**
- Terminal shows all created leads
- Database (`tulip_scout.db`) contains the lead records
- Dashboard will show them (see Option 3)

---

### 📊 Option 3: Full System with Dashboard

**What it does:** Runs the full web interface where you can manage campaigns, review leads, and generate emails

**Terminal 1 - Start API Server:**
```bash
cd /Users/perezweinberg/.gemini/antigravity/scratch/tulip-scout
source venv/bin/activate
uvicorn src.main:app --reload --port 8000
```

**Terminal 2 - Start Dashboard:**
```bash
cd /Users/perezweinberg/.gemini/antigravity/scratch/tulip-scout
source venv/bin/activate
streamlit run dashboard/app.py --server.port 8501
```

**Open in browser:**
- Dashboard: **http://localhost:8501**
- API Docs: **http://localhost:8000/docs**

**What you'll see in dashboard:**

1. **Campaigns Page:**
   - Create new campaign button
   - List of all campaigns
   - Quick stats sidebar

2. **Leads Page:**
   - All scraped leads (if you ran Hunter test)
   - Filters by status (pending, approved, rejected)
   - "📧 Generate Email" button for each lead
   - "✅ Approve" button
   - "👁️ View Details" button

3. **Emails Page:**
   - All generated emails
   - Subject, pain point, Tulip asset used
   - Email body preview
   - "🔗 Open in Gmail" link

**Interactive workflow:**
1. Go to **Campaigns** → Click "Create New Campaign"
2. Go to **Leads** → Click "📧 Generate Email" on any lead
3. Wait ~10 seconds
4. Go to **Emails** → See the generated email!
5. Click "🔗 Open in Gmail" → Your draft opens in Gmail!

---

## Where to See Results

### 1. **Terminal Output**
All test scripts print results directly:
- ✅ Success/failure messages
- 📧 Full email content (test_copywriter.py)
- 🏢 Lead details (test_hunter.py)
- 📊 Stats and summaries

### 2. **Gmail Drafts**
Every generated email creates a **real Gmail draft**:
1. Open Gmail: https://mail.google.com
2. Click **"Drafts"** in sidebar
3. See emails like: *"Tulip Winery x [Company Name]"*
4. You can edit and send them!

### 3. **Streamlit Dashboard** (http://localhost:8501)
Visual interface showing:
- 📋 All campaigns
- 🎯 All leads with fit scores
- 📧 All generated emails
- 📊 Quick stats

### 4. **API Docs** (http://localhost:8000/docs)
Interactive Swagger UI:
- Test any endpoint
- See request/response formats
- Manually trigger Hunter agent

### 5. **Database File** (`tulip_scout.db`)
SQLite database with all data:
```bash
# View database (optional)
sqlite3 tulip_scout.db
.tables  # Shows: campaigns, leads, emails, activities
SELECT * FROM leads;  # View all leads
.quit
```

---

## Troubleshooting

### "playwright install chromium command not found"
```bash
# Make sure venv is activated
source venv/bin/activate
pip install playwright
playwright install chromium
```

### "GEMINI_API_KEY not set"
Edit `.env` file and add your key:
```bash
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### "Gmail OAuth failed"
1. Make sure `credentials.json` is in project root
2. Run: `python scripts/oauth_setup.py`
3. Log in when browser opens

### "LinkedIn requires login" (Hunter test)
This is **normal**! LinkedIn detects automation:
1. Browser opens to LinkedIn
2. **Log in manually** with your LinkedIn account
3. Test continues automatically
4. Session persists for future runs

### "Browser not found"
```bash
playwright install chromium
```

---

## Recommended Testing Order

### First Time:
1. ✅ **Test Copywriter** (fastest, no browser)
   - `python scripts/test_copywriter.py`
   - Check Gmail drafts!

2. ✅ **Start Dashboard** (visual results)
   - Terminal 1: `uvicorn src.main:app --reload`
   - Terminal 2: `streamlit run dashboard/app.py`
   - Open http://localhost:8501

3. ✅ **Test Hunter** (requires LinkedIn login)
   - `python scripts/test_hunter.py`
   - Log in when prompted
   - View results in dashboard

### After Setup:
- Use **dashboard** for daily workflow
- Use **test scripts** for debugging
- Use **API docs** for automation

---

## Quick Commands Reference

```bash
# Activate environment
source venv/bin/activate

# Test Copywriter (email generation)
python scripts/test_copywriter.py

# Test Hunter (LinkedIn scraping)
python scripts/test_hunter.py

# Start API server
uvicorn src.main:app --reload

# Start dashboard
streamlit run dashboard/app.py

# View database
sqlite3 tulip_scout.db

# Check rate limiter status
python -c "from src.utils.rate_limiter import linkedin_rate_limiter; import asyncio; asyncio.run(linkedin_rate_limiter.get_status())"
```

---

## What Success Looks Like

✅ **Copywriter Test Success:**
- Email printed in terminal
- Gmail draft appears in drafts folder
- No errors

✅ **Hunter Test Success:**
- Browser opens and navigates LinkedIn
- 3 leads created (shown in terminal)
- Leads visible in dashboard
- No rate limit errors

✅ **Dashboard Success:**
- Both servers running (API + Streamlit)
- Can create campaigns
- Can generate emails with one click
- Gmail drafts open from dashboard

---

**Ready to test?** Start with the easiest:
```bash
python scripts/test_copywriter.py
```

Then check your Gmail drafts! 🎉

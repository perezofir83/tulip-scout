# Playwright Implementation Guide

## Overview

The Hunter agent uses **Playwright** with **stealth mode** to scrape LinkedIn profiles without being detected as a bot.

---

## Key Features

### 1. Anti-Detection Stealth Mode

```python
# Browser launch with stealth args
browser = await playwright.chromium.launch(
    headless=False,  # Visible browser (safer)
    args=[
        '--disable-blink-features=AutomationControlled',
        '--disable-features=IsolateOrigins,site-per-process',
    ],
)

# Remove webdriver detection
await context.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
""")
```

### 2. Rate Limiting Integration

```python
# Automatic rate limiting before each scrape
await linkedin_rate_limiter.acquire(region="Eastern_Europe")
# ✅ Enforces 40/day, 10/hour, 12-15s delays
```

### 3. Data Extraction

**LinkedIn Profile:**
- Name, title, company
- Location, about section
- Recent posts/activity (for pain-point analysis)

**Company Website:**
- Main text content (first 5000 chars)
- Used for AI lead scoring

---

## How to Use

### Install Playwright Browsers

```bash
# After pip install -r requirements.txt
playwright install chromium
```

### Test Hunter Agent

```bash
python scripts/test_hunter.py
```

**What happens:**
1. Browser opens (visible)
2. Navigates to LinkedIn
3. **You may need to log in** (first time only)
4. Searches for "wine importer Poland"
5. Scrapes first 3 profiles
6. Scores leads with AI
7. Creates lead records in database

---

## Important Notes

### ⚠️ LinkedIn Login Required

- LinkedIn requires authentication
- **Manual login:** Browser will stay open, log in when prompted
- Session cookies persist in browser context
- You only need to log in once

### ⚠️ Rate Limiting is Critical

- **LinkedIn Premium limits:** 40 profiles/day, 10/hour
- Built-in delays: 10-15 seconds between requests
- Token bucket algorithm prevents overuse
- **Do NOT disable rate limiting** or risk account ban

### ⚠️ Headless Mode

Current: `headless=False` (browser visible)
- Safer for testing
- Easier to debug
- Less likely to be detected

Production: Set `headless=True`
- Runs in background
- **Higher detection risk**
- Only use after thorough testing

---

## Stealth Techniques Used

1. **Custom User Agent** - Mimics real Chrome browser
2. **No Webdriver Flag** - Removes automation detection
3. **Real viewport size** - 1920x1080 (common resolution)
4. **Locale & timezone** - en-US, America/New_York
5. **Fake Chrome object** - Adds window.chrome
6. **Plugin array** - Makes navigator.plugins non-empty

---

## Troubleshooting

### "Browser not found"
```bash
playwright install chromium
```

### "Page timeout"
- Slow internet connection
- LinkedIn blocking
- Increase timeout: `timeout=60000` (60s)

### "LinkedIn requires login"
- Keep `headless=False`
- Log in manually when browser opens
- Session persists for future runs

### "Rate limit exceeded"
- Respect the delays
- Check `linkedin_rate_limiter.get_status()`
- Wait until tokens refill

---

## Advanced: Custom Selectors

If LinkedIn changes their HTML structure, update selectors in `scraper_service.py`:

```python
# Current selectors
'.pv-top-card'  # Profile header
'.text-body-medium.break-words'  # Job title
'.feed-shared-update-v2'  # Posts

# Find new selectors:
# 1. Open LinkedIn in browser
# 2. Right-click element → Inspect
# 3. Copy selector
# 4. Update code
```

---

## Security Best Practices

1. **Never commit cookies/session data**
2. **Use personal Gmail** (not company Gmail) for testing
3. **Respect rate limits** - account bans are hard to reverse
4. **Don't scrape competitors' employee data** - legal risk
5. **Add delays** - mimic human behavior

---

## Next Steps

1. **Test with real LinkedIn account**
2. **Validate scraped data quality**
3. **Tune AI lead scoring prompts**
4. **Add error recovery** (retry logic)
5. **Monitor for LinkedIn UI changes**

The Playwright implementation is **production-ready** but requires **careful monitoring** of LinkedIn's anti-bot measures.

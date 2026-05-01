---
description: Minimalist Garmin AI Coach - Build Guide
---

# Minimalist Garmin AI Coach Build

## Overview

A simple, single-file orchestrator that:

1. **Browser-based Garmin access** - No credentials needed! Uses Playwright with saved session cookies
2. WhatsApps user for additional info
3. Sends combined data to local LLM (Ollama)
4. Returns summary via WhatsApp

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Garmin    │────▶│ Orchestrator │────▶│  WhatsApp   │
│    API      │     │   (Python)   │◄────│  (Twilio)   │
└─────────────┘     └──────┬───────┘     └─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │    Ollama    │
                    │  (Local LLM) │
                    └──────────────┘
```

## Flow

1. **Check** → Launch browser (or use saved session), scrape Garmin Connect activities
2. **Notify** → Send WhatsApp: "New workout detected! Reply with RPE (1-10) and notes"
3. **Collect** → Receive user's WhatsApp reply
4. **Analyze** → Combine Garmin data + user input → Ollama prompt
5. **Respond** → Send LLM summary back via WhatsApp

## First Run - Browser Login

On first run, a browser window will open to Garmin Connect. Simply log in manually, then press ENTER in the terminal. Your session will be saved for future runs (no more logins needed!).

## Files

- `orchestrator.py` - Main polling loop
- `services/garmin_browser.py` - Browser-based Garmin Connect scraper (no credentials!)
- `services/whatsapp_service.py` - Twilio WhatsApp integration
- `services/llm_service.py` - Ollama local LLM calls
- `services/database.py` - SQLite for state tracking
- `.env` - API keys and config
- `data/garmin_cookies.pkl` - Saved browser session (auto-created)

## Dependencies

```
playwright
twilio
requests
python-dotenv
```

## Setup Steps

1. **Create and activate virtual environment:**

   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers:**

   ```bash
   playwright install chromium
   ```

4. **Edit `.env` with your Twilio credentials** (get SID/token from Twilio console)
   - No Garmin credentials needed!

5. **Ensure Ollama is running locally with a model:**

   ```bash
   ollama pull llama3.2:3b
   ollama serve
   ```

6. **Run:**
   ```bash
   python orchestrator.py
   ```

## Notes

- **No Garmin credentials stored** - uses browser cookies after first manual login
- Session saved to `data/garmin_cookies.pkl` - delete this file to force re-login
- Uses SQLite to track `last_checked` timestamp and `processed_activity_ids`
- Simple polling loop (no FastAPI/webhooks for minimalism)
- Assumes Ollama running on `http://localhost:11434`

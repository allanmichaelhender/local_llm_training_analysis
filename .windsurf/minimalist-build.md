---
description: Minimalist Strava AI Coach - Build Guide
---

# Minimalist Strava AI Coach Build

## Overview

A simple AI coach that pulls workout data from Strava, sends WhatsApp prompts for feedback, analyzes with a local LLM (Ollama), and returns personalized coaching summaries.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Strava    │────▶│ Orchestrator │────▶│  WhatsApp   │
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

1. **Check** → Poll Strava API for new activities
2. **Notify** → Send WhatsApp: "New workout detected! Reply with RPE (1-10) and notes"
3. **Collect** → Receive user's WhatsApp reply
4. **Analyze** → Combine Strava data + user input → Ollama prompt
5. **Respond** → Send LLM summary back via WhatsApp

## Files

- `orchestrator.py` - Main polling loop and workflow coordination
- `services/strava_client.py` - Strava API integration with OAuth
- `services/whatsapp_service.py` - Twilio WhatsApp integration
- `services/llm_service.py` - Ollama local LLM calls
- `services/database.py` - SQLite for activity and feedback tracking
- `.env` - API keys and configuration
- `working_strava_auth.py` - OAuth setup script (run once to get tokens)
- `manual_activity.py` - Backup manual entry mode
- `test_tokens.py` - Token validation test

## Dependencies

```
stravalib>=2.0.0
twilio>=9.0.0
requests>=2.31.0
python-dotenv>=1.0.0
```

## Setup Steps

1. **Create and activate virtual environment:**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Strava API access:**
   - Go to https://www.strava.com/settings/api
   - Create a new app (set callback URL to http://localhost:8080)
   - Get your Client ID and Client Secret
   - Run `python working_strava_auth.py` to get access tokens
   - Update `.env` with Strava credentials

4. **Configure Twilio (for WhatsApp):**
   - Get Account SID, Auth Token, and WhatsApp number from Twilio console
   - Update `.env` with Twilio credentials

5. **Ensure Ollama is running locally:**

   ```bash
   ollama pull phi3
   ollama serve
   ```

6. **Run:**
   ```bash
   python orchestrator.py
   ```

## Configuration (.env)

```bash
# Twilio WhatsApp
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=whatsapp:+14155238886
USER_PHONE_NUMBER=whatsapp:+your_number

# Ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=phi3

# Strava API
STRAVA_CLIENT_ID=your_client_id
STRAVA_CLIENT_SECRET=your_client_secret
STRAVA_REFRESH_TOKEN=your_refresh_token
STRAVA_ACCESS_TOKEN=your_access_token

# Polling Interval (seconds)
POLL_INTERVAL=300
```

## Notes

- **Strava API** requires OAuth2 authentication with `activity:read_all` scope
- Access tokens expire after 6 hours - use `working_strava_auth.py` to refresh
- Uses SQLite to track `last_checked` timestamp and `processed_activity_ids`
- Simple polling loop (no webhooks for minimalism)
- Fallback to manual entry via `manual_activity.py` if API issues occur

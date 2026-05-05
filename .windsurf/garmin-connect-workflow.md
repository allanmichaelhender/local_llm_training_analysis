---
description: Garmin Connect direct workflow
---

# Garmin Connect Direct Workflow

This workflow uses Garmin Connect API directly for workout detection and heart rate data retrieval.

## Overview

The system:
1. **Detects** new workouts via Garmin Connect API
2. **Extracts** complete raw activity data including HR time series
3. **Stores** all Garmin data in database
4. **Notifies** via WhatsApp and collects user feedback

## Components

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **GarminClient** | Garmin Connect API | Polls Garmin for activities, extracts HR data |
| **Orchestrator** | Main loop | Coordinates Garmin + WhatsApp services |
| **WhatsAppService** | Notifications | Sends prompts, collects feedback |
| **Database** | Storage | Stores raw Garmin data + HR time series |

## Setup

### 1. Install Dependencies
```bash
pip install garminconnect
```

### 2. Configure Environment
```bash
# .env file
GARMIN_EMAIL=your@email.com
GARMIN_PASSWORD=yourpassword
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=whatsapp:+14155238886
USER_PHONE_NUMBER=whatsapp:+447740954816
POLL_INTERVAL=60
```

### 3. Garmin Connect Account
- Sign in to Garmin Connect
- Enable MFA if required (handled automatically)

## Running System

### Start Monitoring
```bash
python orchestrator.py
```

The system will:
- Check Garmin Connect for new activities every 60 seconds
- Fetch complete raw activity data
- Extract HR time series (1000+ samples per activity)
- Store in database with all Garmin metrics
- Send WhatsApp notifications for new workouts
- Store user feedback from WhatsApp

### Manual Testing
```bash
# Test Garmin connection
python test_garmin_mcp.py
```

## Data Flow

```
Garmin Connect API → GarminClient → Orchestrator → Database → WhatsApp → User Feedback
```

1. **Activity Detection**: GarminClient fetches recent activities
2. **HR Extraction**: Extracts detailed HR time series from activity details
3. **Activity Storage**: Complete raw Garmin data + HR time series stored
4. **User Notification**: WhatsApp sends workout prompt
5. **Feedback Collection**: User replies with additional info

## Data Retrieved

The system stores **complete raw Garmin data** including:
- Activity summary (type, duration, distance, calories)
- Heart rate data (average, max, time series)
- Training effect labels (aerobic/anaerobic)
- Intensity minutes
- Respiration rate
- Temperature
- All other Garmin metrics

## Configuration

### Poll Interval
- Default: 60 seconds (1 minute)
- Adjust via `POLL_INTERVAL` in `.env`

### Activity Limit
- Default: 1 most recent activity (for testing)
- Change `limit=1` to `limit=10` in `orchestrator.py` for production

## Troubleshooting

### Authentication Failed
- Check GARMIN_EMAIL and GARMIN_PASSWORD in .env
- Verify Garmin Connect account is active
- MFA handled automatically by library

### No Activities Found
- Verify Garmin Connect has recent activities
- Check API rate limits (may see 429 errors but will retry)
- Run `python test_garmin_mcp.py` to test connection

### WhatsApp Not Working
- Verify Twilio credentials in .env
- Check phone numbers are in WhatsApp format

### Database Errors
- Ensure `data/` directory exists
- Delete `data/activities.db` and restart if corrupted
- Run `python force_delete_db.py` to clear database

## Privacy

- **Garmin Data**: All data stored locally
- **HR Data**: Complete time series stored (no aggregation)
- **100% Local**: All processing happens on your machine
- **No Cloud**: No data sent to external services (except Garmin API and Twilio)

## Migration from Strava/FIT

The Garmin Connect workflow replaces:
- **StravaClient** → GarminClient (direct Garmin API)
- **StravaFITSync** → Not needed (data from Garmin directly)
- **HRAggregator** → Not needed (raw HR stored, no aggregation)
- **FIT files** → Not needed (data from Garmin API)

Benefits:
- Simpler architecture (no file sync needed)
- More complete data (all Garmin metrics)
- Real-time data (no file transfer delay)
- No device connection required

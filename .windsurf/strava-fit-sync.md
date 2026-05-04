---
description: Strava + FIT file sync workflow
---

# Strava + FIT File Sync Workflow

This workflow uses Strava API for workout detection and syncs with local FIT files for detailed heart rate analysis.

## Overview

The system:
1. **Detects** new workouts via Strava API
2. **Syncs** Strava activities with local FIT files by start time
3. **Enriches** activity data with HR time series from FIT files
4. **Notifies** via WhatsApp and collects user feedback
5. **Analyzes** HR patterns + feedback with local LLM

## Components

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **StravaClient** | Workout detection | Polls Strava API for new activities |
| **StravaFITSync** | File synchronization | Matches Strava activities to FIT files by start time |
| **HRAggregator** | HR data processing | 10-second averages from FIT files |
| **LLMService** | AI analysis | Incorporates HR patterns into workout insights |
| **Orchestrator** | Main loop | Coordinates all services |

## Setup

### 1. Install Dependencies
```bash
pip install fitparse>=1.2.0 matplotlib
```

### 2. Configure Environment
```bash
# .env file
STRAVA_CLIENT_ID=your_client_id
STRAVA_CLIENT_SECRET=your_client_secret
STRAVA_REFRESH_TOKEN=your_refresh_token
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
POLL_INTERVAL=120
```

### 3. Prepare FIT Files
- Connect Garmin device via USB, OR
- Copy .fit files to `fit_files/` directory

## Running System

### Start Monitoring
```bash
python orchestrator.py
```

The system will:
- Check Strava API for new activities every 2 minutes
- Sync activities with local FIT files by start time
- Send WhatsApp notifications for new workouts
- Wait for your feedback message
- Generate AI-powered workout summary with HR analysis

### Manual Testing
```bash
# Test FIT file parsing
python test_fit.py

# Test Strava connection
python test_strava.py

# Generate HR graph
python hr_graph.py
```

## Data Flow

```
Strava API → StravaClient → StravaFITSync → FIT Files → HRAggregator → Database → WhatsApp → User Feedback → LLM → Summary
```

1. **Activity Detection**: StravaClient finds new activities
2. **File Matching**: StravaFITSync matches activities to FIT files by start time (±5 min)
3. **HR Processing**: HRAggregator creates 10-second averages from FIT files
4. **Activity Storage**: Enhanced activity stored with HR time series
5. **User Notification**: WhatsApp sends workout prompt
6. **Feedback Collection**: User replies with additional info
7. **AI Analysis**: LLM generates contextual workout insights

## Sync Algorithm

The StravaFITSync matches activities using:

1. **Time Window**: ±5 minutes around Strava start time
2. **FIT Parsing**: Extract actual start time from FIT file headers
3. **Closest Match**: Select FIT file with minimal time difference
4. **Fallback**: Use file modification time if FIT parsing fails

## Heart Rate Processing

The HRAggregator reduces raw HR data (1-second samples) to manageable 10-second averages:

- **Raw**: 1,214 data points (1-second intervals)
- **Processed**: ~121 data points (10-second averages)
- **Benefits**: Reduced prompt size, maintained HR patterns

## LLM Prompt Structure

The AI receives:
- **Workout Summary**: Strava data (type, duration, distance, HR stats)
- **HR Time Series**: First/last 5 data points (shows warmup/peak/cooldown)
- **User Feedback**: Qualitative workout experience
- **Instructions**: Analyze patterns, provide actionable tips

## Troubleshooting

### No Strava Activities
- Check Strava API credentials in .env
- Verify refresh token is valid
- Run `python test_strava.py` to test connection

### FIT Files Not Found
- Check device is connected via USB
- Verify files in `fit_files/` directory
- Check time window (±5 min) covers your activities
- Run `python test_fit.py` to verify detection

### WhatsApp Not Working
- Verify Twilio credentials in .env
- Check webhook configuration
- Test with `python test_tokens.py`

### LLM Not Responding
- Ensure Ollama is running: `ollama serve`
- Pull model: `ollama pull llama3.2:3b`
- Check URL: `http://localhost:11434/api/generate`

## Privacy

- **Strava Data**: Only activity summaries (no GPS tracks)
- **FIT Files**: Processed locally, never uploaded
- **HR Data**: Aggregated before LLM processing
- **100% Local**: All analysis happens on your machine

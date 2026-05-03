---
description: FIT file monitoring and analysis workflow
---

# FIT File Workout Analysis Workflow

This workflow monitors Garmin FIT files, prompts for user feedback, and generates AI-powered workout summaries with heart rate analysis.

## Overview

The system:
1. **Monitors** `fit_files/` directory for new .fit files
2. **Notifies** via WhatsApp when new workout detected
3. **Collects** user feedback about the workout
4. **Analyzes** HR data in 10-second averages
5. **Generates** AI summary using local LLM

## Components

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **FITMonitor** | File watching service | Auto-detects new .fit files, prevents duplicates |
| **HRAggregator** | HR data processing | 10-second averages, reduces data volume |
| **LLMService** | AI analysis | Incorporates HR time series into workout insights |
| **Orchestrator** | Main loop | Coordinates all services, manages polling |

## Setup

### 1. Install Dependencies
```bash
pip install fitparse>=1.2.0 matplotlib
```

### 2. Configure Environment
```bash
# .env file
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
POLL_INTERVAL=120
```

### 3. Prepare FIT Files
- Connect Garmin device via USB, OR
- Copy .fit files to `fit_files/` directory

## Running the System

### Start Monitoring
```bash
python orchestrator.py
```

The system will:
- Check for new .fit files every 2 minutes
- Send WhatsApp notifications for new workouts
- Wait for your feedback message
- Generate AI-powered workout summary

### Manual Testing
```bash
# Test FIT file parsing
python test_fit.py

# Inspect FIT file data
python inspect_fit.py

# Generate HR graph
python hr_graph.py
```

## Data Flow

```
FIT File → FITMonitor → Database → WhatsApp → User Feedback → HRAggregator → LLM → Summary
```

1. **File Detection**: FITMonitor finds new .fit files
2. **Activity Storage**: Workout data stored in SQLite database
3. **User Notification**: WhatsApp sends workout prompt
4. **Feedback Collection**: User replies with additional info
5. **HR Processing**: HRAggregator creates 10-second averages
6. **AI Analysis**: LLM generates contextual workout insights

## Heart Rate Processing

The HRAggregator reduces raw HR data (1-second samples) to manageable 10-second averages:

- **Raw**: 1,214 data points (1-second intervals)
- **Processed**: ~121 data points (10-second averages)
- **Benefits**: Reduced prompt size, maintained HR patterns

## LLM Prompt Structure

The AI receives:
- **Workout Summary**: Type, duration, HR stats
- **HR Time Series**: First/last 5 data points (shows warmup/peak/cooldown)
- **User Feedback**: Qualitative workout experience
- **Instructions**: Analyze patterns, provide actionable tips

## Troubleshooting

### No FIT Files Detected
- Check device is connected via USB
- Verify files in `fit_files/` directory
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

- **100% Local**: All data processed on your machine
- **No Cloud**: FIT files never leave your device
- **Secure**: HR data aggregated before LLM processing

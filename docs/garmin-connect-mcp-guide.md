# Garmin Connect MCP Server Guide

## Overview

The Garmin Connect MCP (Model Context Protocol) server provides programmatic access to Garmin Connect fitness and health data. It acts as a bridge between Garmin's internal API and any MCP-compatible client, enabling developers and users to access activity data, health metrics, sleep information, training analysis, and more.

## What is MCP?

MCP (Model Context Protocol) is a standardized protocol for accessing external data sources and tools. Think of it as a universal API that allows different clients (IDEs, LLMs, applications) to communicate with data services in a consistent way.

- **Protocol**: JSON-RPC over stdio
- **Purpose**: Standardized data access
- **Clients**: Windsurf, Claude Desktop, Cursor, custom applications
- **Servers**: Data bridges like Garmin Connect MCP

## Available Data Categories

The Garmin Connect MCP server provides **61 tools** across 7 categories:

### 🏃 Activities (12 tools)
- Get recent activities with pagination
- Activity details and summaries
- Activity splits and typed intervals
- Heart rate zones for activities
- Weather conditions during activities
- Exercise sets (for strength training)
- Activity types and progress summaries
- Activities by date range

### 💓 Daily Health (14 tools)
- Daily health summaries
- Step counts and charts
- Heart rate data (resting, average, max)
- Stress levels and time series
- Body battery energy levels
- Body battery charge/drain events
- Respiration rate
- Blood oxygen saturation (SpO2)
- Intensity minutes
- Floors climbed
- Hydration tracking
- Daily wellness events

### 📈 Trends (4 tools)
- Daily step ranges over time
- Weekly aggregated step counts
- Weekly stress data
- Weekly intensity minutes

### 😴 Sleep (2 tools)
- Detailed sleep data (stages, duration, score)
- Raw sleep data with heart rate and SpO2

### 🏋️ Body Composition (5 tools)
- Body composition metrics
- Weight tracking
- Daily weigh-ins
- Historical weigh-in data
- Blood pressure readings

### 🎯 Performance & Training (11 tools)
- VO2 max estimates
- Training readiness scores
- Training status analysis
- Heart Rate Variability (HRV)
- Endurance score
- Hill score
- Race predictions
- Fitness age estimates
- Personal records
- Lactate threshold
- Cycling FTP

### 👤 Profile & Devices (13 tools)
- User profile information
- User settings and preferences
- Registered Garmin devices
- Device settings and configurations
- Primary training device
- Device solar data
- Gear/equipment tracking
- Gear usage statistics
- Fitness goals
- Earned badges
- Saved workouts
- Workout details

## Installation & Setup

### Prerequisites
- Garmin Connect account
- Node.js (for npx) or Python environment
- MCP-compatible client

### Installation Options

#### Option 1: Direct NPM Package
```bash
GARMIN_EMAIL=your@email.com GARMIN_PASSWORD=yourpassword npx -y @nicolasvegam/garmin-connect-mcp
```

#### Option 2: Windsurf Configuration
Add to `~/.codeium/windsurf/mcp_config.json`:
```json
{
  "mcpServers": {
    "garmin": {
      "command": "npx",
      "args": ["-y", "@nicolasvegam/garmin-connect-mcp"],
      "env": {
        "GARMIN_EMAIL": "your@email.com",
        "GARMIN_PASSWORD": "yourpassword"
      }
    }
  }
}
```

#### Option 3: Claude Desktop Configuration
Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\\Claude\\claude_desktop_config.json` (Windows):
```json
{
  "mcpServers": {
    "garmin": {
      "command": "npx",
      "args": ["-y", "@nicolasvegam/garmin-connect-mcp"],
      "env": {
        "GARMIN_EMAIL": "your@email.com",
        "GARMIN_PASSWORD": "yourpassword"
      }
    }
  }
}
```

### Authentication
- **Email & Password**: Required for initial authentication
- **MFA Support**: Handles multi-factor authentication if enabled
- **Token Caching**: OAuth tokens are cached to avoid repeated authentication
- **Automatic Refresh**: Tokens are refreshed automatically

## Usage Examples

### Basic Activity Queries
```javascript
// Get recent activities
const activities = await client.call("get_activities", {limit: 10});

// Get specific activity details
const activity = await client.call("get_activity", {activityId: 12345});

// Get activities by date range
const activities = await client.call("get_activities_by_date", {
  startDate: "2026-05-01",
  endDate: "2026-05-05"
});
```

### Health Data Access
```javascript
// Get daily health summary
const health = await client.call("get_daily_summary", {date: "2026-05-05"});

// Get heart rate data
const hr = await client.call("get_heart_rate", {date: "2026-05-05"});

// Get sleep data
const sleep = await client.call("get_sleep_data", {date: "2026-05-04"});
```

### Training Analysis
```javascript
// Get training readiness
const readiness = await client.call("get_training_readiness", {date: "2026-05-05"});

// Get VO2 max
const vo2max = await client.call("get_vo2max", {date: "2026-05-05"});

// Get personal records
const records = await client.call("get_personal_records");
```

## Data Structure Examples

### Activity Summary
```json
{
  "activityId": 22770616512,
  "activityName": "Cardio",
  "startTimeLocal": "2026-05-05 10:05:29",
  "activityType": {"typeKey": "indoor_cardio"},
  "duration": 2743.172,
  "calories": 346,
  "averageHR": 135,
  "maxHR": 148,
  "trainingEffectLabel": "AEROBIC_BASE"
}
```

### Detailed Activity Metrics
```json
{
  "measurementCount": 8,
  "metricsCount": 1103,
  "metricDescriptors": [
    {"key": "directHeartRate", "unit": {"key": "bpm"}},
    {"key": "directTimestamp", "unit": {"key": "gmt"}},
    {"key": "directRespirationRate", "unit": {"key": "breathsPerMinute"}}
  ],
  "activityDetailMetrics": [
    {"metrics": [0, 107, 26, 0, 0, 0, 1777971929000, null]},
    {"metrics": [1, 109, 26, 0, 1, 0, 1777971930000, null]}
  ]
}
```

### Daily Health Summary
```json
{
  "steps": 8432,
  "calories": 2240,
  "distance": 5.2,
  "activeMinutes": 45,
  "heartRate": {
    "resting": 62,
    "average": 75,
    "max": 145
  },
  "stress": {
    "overall": 25,
    "restTime": 720,
    "lowStressTime": 480
  }
}
```

## Integration Options

### 1. MCP Client Integration
Use MCP client libraries in your preferred language:
- Node.js: `@modelcontextprotocol/sdk`
- Python: `mcp` package
- Other languages: Community implementations

### 2. Direct Library Usage
Bypass MCP and use the underlying library:
```python
from garminconnect import Garmin

garmin = Garmin("email", "password")
garmin.login()
activities = garmin.get_activities()
```

### 3. Custom API Wrapper
Build your own API around the MCP server:
```javascript
const { spawn } = require('child_process');

function createGarminClient() {
  const server = spawn('npx', ['-y', '@nicolasvegam/garmin-connect-mcp'], {
    env: {
      GARMIN_EMAIL: process.env.GARMIN_EMAIL,
      GARMIN_PASSWORD: process.env.GARMIN_PASSWORD
    }
  });
  
  return new MCPClient(server.stdin, server.stdout);
}
```

## Use Cases

### Fitness Tracking Apps
- Activity history and trends
- Performance analytics
- Goal tracking and achievements

### Health Monitoring
- Daily health dashboards
- Sleep quality analysis
- Stress and recovery tracking

### Training Analysis
- Workout intensity analysis
- Training load optimization
- Performance predictions

### Data Export & Backup
- Automated data exports
- Historical data archiving
- Cross-platform data sync

### Research & Analytics
- Population health studies
- Athletic performance research
- Health trend analysis

## Limitations & Considerations

### API Limitations
- **No Public API**: Uses reverse-engineered access to Garmin's services
- **Rate Limiting**: Garmin may impose usage limits
- **Authentication**: Requires user credentials
- **Service Changes**: Could break if Garmin changes internal APIs

### Data Limitations
- **No Raw FIT Files**: Only structured data access
- **Historical Limits**: May have limits on historical data access
- **Real-time**: Not designed for real-time monitoring

### Security Considerations
- **Credential Storage**: Store Garmin credentials securely
- **Token Caching**: Tokens are cached locally
- **Privacy**: Activity data is private by default

## Troubleshooting

### Common Issues
1. **Authentication Failures**: Check email/password and MFA status
2. **Rate Limiting**: Reduce request frequency
3. **Token Expiration**: Re-authenticate if tokens expire
4. **Network Issues**: Check internet connectivity

### Debug Tips
- Enable verbose logging in MCP client
- Check Garmin Connect website for account status
- Verify credentials work in Garmin Connect app
- Monitor token cache files

## Alternatives

### Official Garmin Options
- **Garmin Connect Web**: Manual data export
- **Garmin SDK**: Limited availability
- **Garmin Health API**: Enterprise solution

### Third-party Options
- **Strava API**: Limited Garmin sync
- **TrainingPeaks**: Manual import
- **Custom Solutions**: Direct API integration

## Resources

- **GitHub Repository**: https://github.com/Nicolasvegam/garmin-connect-mcp
- **MCP Specification**: https://modelcontextprotocol.io/
- **Python Garmin Connect**: https://github.com/cyberjunky/python-garminconnect
- **MCP SDK Documentation**: https://github.com/modelcontextprotocol/servers

## Conclusion

The Garmin Connect MCP server provides comprehensive access to Garmin fitness and health data through a standardized protocol. While it requires careful consideration of authentication and API limitations, it offers powerful capabilities for fitness tracking, health monitoring, and training analysis applications.

The 61 available tools cover virtually all aspects of Garmin Connect data, making it suitable for everything from simple activity logging to complex performance analytics and research applications.

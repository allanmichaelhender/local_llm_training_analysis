# Garmin Connect MCP Migration

## Overview

The system has been migrated from FIT file monitoring / Strava API to use the Garmin Connect MCP server for data retrieval. This provides a more reliable and comprehensive data source directly from Garmin Connect.

## Changes Made

### New Services

1. **`services/garmin_client.py`** - Garmin Connect MCP client
   - Wraps Garmin Connect MCP tools
   - `get_activities_since()` - Fetch activities by date range
   - `get_latest_activity()` - Get most recent activity
   - `get_activity_details()` - Get detailed metrics
   - `extract_hr_time_series()` - Extract HR time series from activity details

2. **`services/garmin_hr_aggregator.py`** - HR data aggregation for Garmin
   - Processes HR time series from Garmin MCP format
   - Creates 10-second averages to reduce data volume
   - Provides HR summary statistics

### Updated Files

1. **`orchestrator.py`** - Main workflow coordinator
   - Replaced `StravaClient` with `GarminClient`
   - Replaced `StravaFITSync` with `GarminHRAggregator`
   - Updated activity detection logic to use Garmin MCP
   - Updated HR extraction to use Garmin activity details

## Data Flow

### Previous Flow (Strava + FIT Files)
```
Strava API → StravaFITSync → FIT Files → HRAggregator → Database → WhatsApp → LLM → Summary
```

### New Flow (Garmin MCP)
```
Garmin MCP → GarminClient → GarminHRAggregator → Database → WhatsApp → LLM → Summary
```

## Key Features

- **Direct Garmin Access**: Pulls data directly from Garmin Connect via MCP
- **No FIT Files Required**: Eliminates need for local FIT file monitoring
- **No Strava API**: Removes dependency on Strava API and OAuth
- **Complete HR Data**: Access to full HR time series from Garmin
- **Data Reduction**: Still aggregates HR data into 10-second buckets
- **Same Workflow**: WhatsApp prompts and LLM summaries work the same way

## MCP Tools Used

- `mcp0_get_last_activity` - Get most recent activity
- `mcp0_get_activities_by_date` - Get activities in date range
- `mcp0_get_activity_details` - Get detailed metrics including HR time series

## Configuration

No additional configuration required. The Garmin MCP server is configured in the MCP client settings (Windsurf/Claude Desktop config).

Environment variables no longer needed:
- `STRAVA_CLIENT_ID`
- `STRAVA_CLIENT_SECRET`
- `STRAVA_REFRESH_TOKEN`
- `STRAVA_ACCESS_TOKEN`

## Testing

The Garmin MCP integration was tested successfully:
- Activity retrieval works
- HR time series extraction works
- HR aggregation works
- Data format is compatible with existing database and LLM service

## Benefits

1. **Simpler Architecture**: Single data source instead of dual (Strava + FIT)
2. **More Reliable**: Direct Garmin access eliminates sync issues
3. **No API Limits**: Garmin MCP doesn't have the same rate limits as Strava
4. **Complete Data**: Access to all Garmin metrics including training effect
5. **Privacy**: All data stays local, processed through MCP

## Rollback

To rollback to the previous Strava + FIT file approach:
1. Restore `orchestrator.py` from git
2. Remove `services/garmin_client.py`
3. Remove `services/garmin_hr_aggregator.py`
4. Add Strava credentials back to `.env`

# Complete Garmin Connect MCP Tools List

## Activities (12 tools)

### `get_activities`
Get recent activities with pagination support
- **Parameters**: `limit` (1-100, default 20), `start` (default 0), `activityType` (optional)
- **Returns**: Array of activity summaries with basic metrics

### `get_activities_by_date`
Search activities within a date range
- **Parameters**: `startDate` (YYYY-MM-DD), `endDate` (YYYY-MM-DD), `activityType` (optional)
- **Returns**: Activities within the specified date range

### `get_last_activity`
Get the most recent activity
- **Parameters**: None
- **Returns**: Single activity object with full details

### `count_activities`
Get total number of activities in Garmin Connect
- **Parameters**: None
- **Returns**: Integer count of all activities

### `get_activity`
Get summary data for a specific activity
- **Parameters**: `activityId` (required)
- **Returns**: Activity summary with basic metrics and metadata

### `get_activity_details`
Get detailed activity metrics with time series data
- **Parameters**: `activityId` (required)
- **Returns**: Second-by-second metrics (HR, pace, elevation, cadence, power)

### `get_activity_splits`
Get per-km or per-mile split data for an activity
- **Parameters**: `activityId` (required)
- **Returns**: Split summaries with pace, HR, and distance data

### `get_activity_weather`
Get weather conditions during an activity
- **Parameters**: `activityId` (required)
- **Returns**: Temperature, humidity, wind, and weather conditions

### `get_activity_hr_zones`
Get time spent in each heart rate zone during an activity
- **Parameters**: `activityId` (required)
- **Returns**: Time in HR zones 1-5 with zone descriptions

### `get_activity_exercise_sets`
Get exercise set details for strength training activities
- **Parameters**: `activityId` (required)
- **Returns**: Reps, weight, duration per set for strength workouts

### `get_activity_types`
Get all available activity types (running, cycling, swimming, etc.)
- **Parameters**: None
- **Returns**: List of activity types with IDs and descriptions

### `get_progress_summary`
Get fitness progress stats over a date range
- **Parameters**: `startDate`, `endDate`, `metric` (distance/duration/calories)
- **Returns**: Progress data grouped by activity type

## Daily Health (14 tools)

### `get_daily_summary`
Get full daily summary with steps, calories, distance, floors, active minutes, HR, stress, body battery
- **Parameters**: `date` (YYYY-MM-DD, defaults to today)
- **Returns**: Comprehensive daily health metrics

### `get_steps`
Get step count for a specific date
- **Parameters**: `date` (YYYY-MM-DD, defaults to today)
- **Returns**: Daily step count

### `get_steps_chart`
Get detailed intraday step data throughout the day
- **Parameters**: `date` (YYYY-MM-DD, defaults to today)
- **Returns**: Time series step chart data

### `get_heart_rate`
Get daily heart rate data: resting HR, max HR, min HR, and time series
- **Parameters**: `date` (YYYY-MM-DD, defaults to today)
- **Returns**: Heart rate metrics and intraday data

### `get_resting_heart_rate`
Get resting heart rate data for a specific date
- **Parameters**: `date` (YYYY-MM-DD, defaults to today)
- **Returns**: Resting HR value

### `get_stress`
Get daily stress levels: overall score, time in rest/low/medium/high stress, and time series
- **Parameters**: `date` (YYYY-MM-DD, defaults to today)
- **Returns**: Stress metrics and time series data

### `get_body_battery`
Get Body Battery energy levels: charged, drained, highest, lowest
- **Parameters**: `startDate` (YYYY-MM-DD), `endDate` (optional, defaults to startDate)
- **Returns**: Body battery metrics and daily values

### `get_body_battery_events`
Get Body Battery charge and drain events for a day
- **Parameters**: `date` (YYYY-MM-DD, defaults to today)
- **Returns**: Events that charged/drained your battery

### `get_respiration`
Get daily respiration rate data throughout the day
- **Parameters**: `date` (YYYY-MM-DD, defaults to today)
- **Returns**: Respiration rate time series data

### `get_spo2`
Get blood oxygen saturation (SpO2) data for a specific date
- **Parameters**: `date` (YYYY-MM-DD, defaults to today)
- **Returns**: SpO2 measurements and averages

### `get_intensity_minutes`
Get moderate and vigorous intensity minutes for a date
- **Parameters**: `date` (YYYY-MM-DD, defaults to today)
- **Returns**: Moderate and vigorous intensity minute counts

### `get_floors`
Get floors climbed chart data for a specific date
- **Parameters**: `date` (YYYY-MM-DD, defaults to today)
- **Returns**: Floors climbed data

### `get_hydration`
Get daily hydration data (water intake)
- **Parameters**: `date` (YYYY-MM-DD, defaults to today)
- **Returns**: Hydration volume in milliliters

### `get_daily_events`
Get daily wellness events for a specific date
- **Parameters**: `date` (YYYY-MM-DD, defaults to today)
- **Returns**: List of wellness events and notifications

## Trends (4 tools)

### `get_daily_steps_range`
Get daily step counts over a date range for trend analysis
- **Parameters**: `startDate`, `endDate` (YYYY-MM-DD)
- **Returns**: Array of daily step counts

### `get_weekly_steps`
Get weekly aggregated step counts for trend analysis
- **Parameters**: `endDate` (YYYY-MM-DD), `weeks` (1-52, default 52)
- **Returns**: Weekly step totals

### `get_weekly_stress`
Get weekly aggregated stress data for trend analysis
- **Parameters**: `endDate` (YYYY-MM-DD), `weeks` (1-52, default 52)
- **Returns**: Weekly stress averages

### `get_weekly_intensity_minutes`
Get weekly intensity minutes over a date range
- **Parameters**: `startDate`, `endDate` (YYYY-MM-DD)
- **Returns**: Weekly intensity minute totals

## Sleep (2 tools)

### `get_sleep_data`
Get detailed sleep data for a single night: duration, sleep stages, sleep score, bed/wake times
- **Parameters**: `date` (YYYY-MM-DD, defaults to today)
- **Returns**: Sleep stages, score, duration, and quality metrics

### `get_sleep_data_raw`
Get raw sleep data directly from wellness service with full detail including heart rate and SpO2 during sleep
- **Parameters**: `date` (YYYY-MM-DD, defaults to today)
- **Returns**: Raw sleep sensor data

## Body Composition (5 tools)

### `get_body_composition`
Get body composition data over a date range: weight, BMI, body fat %, muscle mass, bone mass, body water %
- **Parameters**: `startDate`, `endDate` (YYYY-MM-DD)
- **Returns**: Body composition metrics

### `get_latest_weight`
Get the most recent weight entry
- **Parameters**: None
- **Returns**: Latest weight measurement with date

### `get_daily_weigh_ins`
Get all weigh-in entries for a specific date
- **Parameters**: `date` (YYYY-MM-DD, defaults to today)
- **Returns**: Weight measurements for the day

### `get_weigh_ins`
Get weigh-in records over a date range
- **Parameters**: `startDate`, `endDate` (YYYY-MM-DD)
- **Returns**: Historical weight data

### `get_blood_pressure`
Get blood pressure readings over a date range
- **Parameters**: `startDate`, `endDate` (YYYY-MM-DD)
- **Returns**: Systolic, diastolic, and pulse measurements

## Performance & Training (11 tools)

### `get_vo2max`
Get VO2 Max estimate for a date (running and cycling)
- **Parameters**: `date` (YYYY-MM-DD, defaults to today)
- **Returns**: VO2 max estimates for running and cycling

### `get_training_readiness`
Get Training Readiness score: combines sleep, recovery, training load and HRV
- **Parameters**: `date` (YYYY-MM-DD, defaults to today)
- **Returns**: Readiness score and contributing factors

### `get_training_status`
Get Training Status: productive, maintaining, detraining, peaking, recovery, overreaching
- **Parameters**: `date` (YYYY-MM-DD, defaults to today)
- **Returns**: Training status and load information

### `get_hrv`
Get Heart Rate Variability (HRV) data - key recovery indicator
- **Parameters**: `date` (YYYY-MM-DD, defaults to today)
- **Returns**: HRV measurements and overnight averages

### `get_endurance_score`
Get Endurance Score for single date or date range with aggregation
- **Parameters**: `startDate`, `endDate` (optional), `aggregation` (daily/weekly/monthly)
- **Returns**: Endurance performance metrics

### `get_hill_score`
Get Hill Score for single date or date range with aggregation
- **Parameters**: `startDate`, `endDate` (optional), `aggregation` (daily/weekly/monthly)
- **Returns**: Hill running performance metrics

### `get_race_predictions`
Get race time predictions for 5K, 10K, half marathon, and marathon
- **Parameters**: `startDate`, `endDate` (optional), `type` (daily/monthly)
- **Returns**: Predicted race times

### `get_fitness_age`
Get Garmin Fitness Age estimate based on fitness level, activity, and body metrics
- **Parameters**: `date` (YYYY-MM-DD, defaults to today)
- **Returns**: Fitness age calculation

### `get_personal_records`
Get personal records: longest run, fastest 5K/10K/half/full marathon, longest ride
- **Parameters**: None
- **Returns**: All-time personal bests

### `get_lactate_threshold`
Get lactate threshold data: HR and pace with historical trends
- **Parameters**: `startDate`, `endDate` (optional), `aggregation` (daily/weekly/monthly)
- **Returns**: Lactate threshold measurements

### `get_cycling_ftp`
Get latest Functional Threshold Power (FTP) for cycling
- **Parameters**: None
- **Returns**: Current cycling FTP value

## Profile & Devices (13 tools)

### `get_user_profile`
Get user social profile: name, location, profile image, activity preferences, level
- **Parameters**: None
- **Returns**: User profile information

### `get_user_settings`
Get user settings: measurement system, time/date format, sleep schedule, HR zones, hydration preferences
- **Parameters**: None
- **Returns**: User account settings

### `get_devices`
Get all registered Garmin devices: model, firmware, last sync
- **Parameters**: None
- **Returns**: List of connected Garmin devices

### `get_device_settings`
Get settings and configuration for a specific Garmin device
- **Parameters**: `deviceId` (required)
- **Returns**: Device-specific settings

### `get_device_last_used`
Get the last used Garmin device info
- **Parameters**: None
- **Returns**: Most recently used device details

### `get_primary_training_device`
Get the primary training device info
- **Parameters**: None
- **Returns**: Primary device for training activities

### `get_device_solar_data`
Get solar charging data for solar-equipped Garmin devices
- **Parameters**: `deviceId`, `startDate`, `endDate` (YYYY-MM-DD)
- **Returns**: Solar charging statistics

### `get_gear`
Get all gear/equipment: shoes, bikes, and other tracked equipment
- **Parameters**: None
- **Returns**: List of tracked gear with usage stats

### `get_gear_stats`
Get usage statistics for a specific gear item (total distance, activities)
- **Parameters**: `gearUuid` (required)
- **Returns**: Gear usage metrics

### `get_goals`
Get active goals: step goals, activity goals, weight goals, and their progress
- **Parameters**: None
- **Returns**: Current goals and completion status

### `get_earned_badges`
Get all earned badges and achievements
- **Parameters**: None
- **Returns**: List of earned badges and achievements

### `get_workouts`
Get saved workouts/training plans
- **Parameters**: None
- **Returns**: List of saved workouts

### `get_workout`
Get a specific workout definition by ID
- **Parameters**: `workoutId` (required)
- **Returns**: Detailed workout structure and exercises

## Additional Management Tools

### `create_manual_activity`
Create a manual activity entry
- **Parameters**: `activityName`, `activityTypeKey`, `startTimeInGMT`, `elapsedDurationInSecs`, `distanceInMeters` (optional)
- **Returns**: Created activity details

### `delete_activity`
Delete an activity permanently
- **Parameters**: `activityId` (required)
- **Returns**: Deletion confirmation

### `set_activity_name`
Rename an activity
- **Parameters**: `activityId`, `name` (required)
- **Returns**: Updated activity name

### `add_weigh_in`
Record a weight measurement
- **Parameters**: `weight`, `date` (optional), `unitKey` (kg/lbs)
- **Returns**: Recorded weight entry

### `set_blood_pressure`
Record a blood pressure measurement
- **Parameters**: `systolic`, `diastolic`, `pulse`, `timestamp` (optional), `notes` (optional)
- **Returns**: Recorded blood pressure entry

### `set_hydration`
Set daily hydration intake in milliliters
- **Parameters**: `valueMl`, `date` (optional)
- **Returns**: Updated hydration record

### `add_gear_to_activity`
Link a gear item to an activity
- **Parameters**: `activityId`, `gearUuid` (required)
- **Returns**: Gear linkage confirmation

### `remove_gear_from_activity`
Unlink a gear item from an activity
- **Parameters**: `activityId`, `gearUuid` (required)
- **Returns**: Gear unlink confirmation

---

**Total Tools: 61** across 7 main categories plus additional management tools.

All tools return structured JSON data compatible with any MCP client implementation.

# MCP Server Specification for Sports Analytics

## Project Goal

Build a Model Context Protocol (MCP) server that exposes Garmin/Strava fitness data as tools for Claude and ChatGPT. This enables conversational querying of workout data (e.g., "Compare my last 5 runs", "How has my sleep affected my running performance?").

## Tech Stack

- **Docker Compose** - Container orchestration
- **FastAPI** - Python web framework for MCP server
- **PostgreSQL** - Production-grade database
- **pgAdmin** - Database management UI
- **Python 3.11+** - Runtime environment

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude/ChatGPT Apps                       │
│              (via MCP Protocol - stdio/HTTP)                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI MCP Server                         │
│  - MCP protocol implementation                              │
│  - Tool registration and execution                          │
│  - Function calling orchestration                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Access Layer                         │
│  - Garmin Connect API client                                 │
│  - Strava API client                                         │
│  - PostgreSQL database queries                               │
│  - HR data processing                                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                       │
│  - Activities table (raw Garmin/Strava data)                 │
│  - HR time series data                                       │
│  - User feedback                                             │
│  - LLM summaries                                             │
└─────────────────────────────────────────────────────────────┘
```

## Required Components

### 1. Docker Compose Configuration (`docker-compose.yml`)

Create services for:
- **mcp-server** - FastAPI application
- **postgres** - PostgreSQL database
- **pgadmin** - Database management UI

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: sports_analytics
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin"]
      interval: 10s
      timeout: 5s
      retries: 5

  pgadmin:
    image: dpage/pgadmin4:latest
    environment:
      PGADMIN_DEFAULT_EMAIL: ${PGADMIN_EMAIL}
      PGADMIN_DEFAULT_PASSWORD: ${PGADMIN_PASSWORD}
    ports:
      - "5050:80"
    depends_on:
      - postgres

  mcp-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://admin:${DB_PASSWORD}@postgres:5432/sports_analytics
      GARMIN_EMAIL: ${GARMIN_EMAIL}
      GARMIN_PASSWORD: ${GARMIN_PASSWORD}
      STRAVA_CLIENT_ID: ${STRAVA_CLIENT_ID}
      STRAVA_CLIENT_SECRET: ${STRAVA_CLIENT_SECRET}
      STRAVA_REFRESH_TOKEN: ${STRAVA_REFRESH_TOKEN}
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./app:/app
    command: uvicorn mcp_server:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data:
```

### 2. FastAPI MCP Server (`app/mcp_server.py`)

Implement MCP protocol with FastAPI. Key features:

**MCP Protocol Implementation:**
- Support both stdio and HTTP transport
- Tool registration system
- Function calling execution
- Resource definitions (if needed)

**Tool Functions to Expose:**

```python
# Activity retrieval
- get_recent_activities(limit: int = 20, activity_type: str = None)
- get_activity_details(activity_id: str)
- get_activity_by_date_range(start_date: str, end_date: str)

# HR data
- get_activity_hr_data(activity_id: str)
- get_hr_summary(activity_id: str)

# Analysis
- compare_activities(activity_ids: List[str], metrics: List[str])
- get_activity_splits(activity_id: str)
- get_training_load(days: int = 30)

# User data
- get_user_feedback(activity_id: str)
- get_llm_summary(activity_id: str)
```

**FastAPI Endpoints:**
- `POST /tools/list` - List available tools
- `POST /tools/call` - Execute a tool
- `POST /resources/list` - List resources (optional)
- `POST /prompts/list` - List prompts (optional)

### 3. Database Schema (`app/database.py`)

PostgreSQL tables:

```sql
-- Activities table
CREATE TABLE activities (
    id TEXT PRIMARY KEY,
    source VARCHAR(20) CHECK (source IN ('garmin', 'strava')),
    activity_data JSONB,
    modality TEXT,
    start_time TIMESTAMP,
    duration_seconds INTEGER,
    distance_meters FLOAT,
    has_hr_data BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- HR time series data
CREATE TABLE hr_data (
    id SERIAL PRIMARY KEY,
    activity_id TEXT REFERENCES activities(id),
    timestamp TIMESTAMP,
    heart_rate INTEGER,
    INDEX idx_activity_id (activity_id),
    INDEX idx_timestamp (timestamp)
);

-- User feedback
CREATE TABLE user_feedback (
    activity_id TEXT PRIMARY KEY REFERENCES activities(id),
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- LLM summaries
CREATE TABLE llm_summaries (
    activity_id TEXT PRIMARY KEY REFERENCES activities(id),
    summary TEXT,
    model_used VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. Garmin/Strava Integration

Reuse existing clients from parent project:
- Copy `services/garmin_client.py` → `app/clients/garmin.py`
- Copy `services/strava_client.py` → `app/clients/strava.py`
- Adapt to use PostgreSQL instead of SQLite

### 5. Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "mcp_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 6. Requirements (`requirements.txt`)

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0
psycopg2-binary==2.9.9
sqlalchemy==2.0.25
alembic==1.13.1
python-garminconnect==0.1.20
requests==2.31.0
python-dotenv==1.0.0
mcp==0.1.0  # MCP protocol library
```

### 7. Environment Configuration (`.env.example`)

```env
# Database
DB_PASSWORD=your_secure_password
PGADMIN_EMAIL=admin@example.com
PGADMIN_PASSWORD=your_pgadmin_password

# Garmin
GARMIN_EMAIL=your@email.com
GARMIN_PASSWORD=your_garmin_password

# Strava (optional)
STRAVA_CLIENT_ID=your_client_id
STRAVA_CLIENT_SECRET=your_client_secret
STRAVA_REFRESH_TOKEN=your_refresh_token
```

## Project Structure

```
mcp-server/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── .env (gitignored)
├── app/
│   ├── __init__.py
│   ├── mcp_server.py          # Main FastAPI + MCP implementation
│   ├── database.py            # PostgreSQL connection and models
│   ├── config.py              # Configuration from environment
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── garmin.py          # Garmin API client
│   │   └── strava.py          # Strava API client
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── activities.py     # Activity-related tools
│   │   ├── hr_data.py         # HR data tools
│   │   └── analysis.py        # Analysis tools
│   └── models/
│       ├── __init__.py
│       └── schemas.py         # Pydantic models
└── alembic/                   # Database migrations
    ├── versions/
    └── env.py
```

## MCP Protocol Details

### Tool Definition Format

Each tool must have:
- `name` - Unique identifier
- `description` - What the tool does (for LLM understanding)
- `inputSchema` - JSON Schema for parameters
- `handler` - Function to execute

Example:
```python
{
    "name": "get_recent_activities",
    "description": "Retrieve recent activities from Garmin or Strava",
    "inputSchema": {
        "type": "object",
        "properties": {
            "limit": {"type": "integer", "default": 20, "maximum": 100},
            "activity_type": {"type": "string", "enum": ["running", "cycling", "swimming"]}
        }
    }
}
```

### Transport Options

1. **stdio** - Standard input/output (for Claude Desktop)
2. **HTTP** - REST API endpoints (for remote access)

Support both for maximum compatibility.

## Development Workflow

1. **Setup:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   docker-compose up -d
   ```

2. **Database Migrations:**
   ```bash
   docker-compose exec mcp-server alembic upgrade head
   ```

3. **Test MCP Server:**
   ```bash
   # Test HTTP endpoint
   curl http://localhost:8000/tools/list
   
   # Test with Claude Desktop (stdio)
   # Configure Claude to connect to docker container
   ```

4. **Access pgAdmin:**
   - Open http://localhost:5050
   - Login with credentials from .env
   - Connect to postgres:5432

## Integration with Parent Project

This MCP server should:
- Use the same Garmin/Strava API clients from parent project
- Migrate existing SQLite data to PostgreSQL (optional)
- Provide tools that mirror the existing orchestrator functionality
- Maintain compatibility with existing data structures

## Success Criteria

- [ ] Docker containers start successfully
- [ ] PostgreSQL database initialized with correct schema
- [ ] pgAdmin accessible and can query database
- [ ] MCP server exposes tools via HTTP endpoint
- [ ] MCP server works with Claude Desktop via stdio
- [ ] Tools can query Garmin/Strava data
- [ ] Tools can query local PostgreSQL data
- [ ] LLM can successfully call tools and get results

## Notes

- Use SQLAlchemy ORM for database operations
- Implement connection pooling for PostgreSQL
- Add proper error handling and logging
- Consider caching for frequently accessed data
- Add rate limiting for API calls to Garmin/Strava
- Implement health check endpoint for monitoring

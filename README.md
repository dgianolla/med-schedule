# Schedule API

Standalone scheduling system for **Clínica Atend Já Sorocaba**.

A unified scheduling layer that acts as a proxy between the LIA assistant and multiple scheduling providers (Local database and AppHealth).

## Architecture

```
┌──────────────┐
│     LIA      │ → calls schedule-api (doesn't know about providers)
└──────┬───────┘
       │
       ▼
┌──────────────────────────────┐
│       schedule-api           │
│                              │
│  ┌────────────────────────┐  │
│  │   Unified Endpoints    │  │ ← LIA calls these
│  │  /availability/dates   │  │
│  │  /availability/times   │  │
│  │    /appointments       │  │
│  └────────┬───────────────┘  │
│           │                  │
│  ┌────────▼───────────────┐  │
│  │   Router/Dispatcher    │  │ ← decides which provider to use
│  │    (by specialty)      │  │
│  └────┬───────────────┬───┘  │
│       │               │      │
│  ┌────▼────┐   ┌──────▼─────┐│
│  │  Local  │   │ AppHealth  ││
│  │ Provider│   │  Provider  ││
│  └─────────┘   └────────────┘│
└──────────────────────────────┘
```

### Routing Rules

- **Enfermagem** → LocalProvider
- **Cardiologia, Ginecologia, etc.** → AppHealthProvider
- Configurable via `provider_routes` table (move specialties between providers over time)

## Stack

- **Language**: Python 3.12+
- **Framework**: FastAPI
- **Database**: PostgreSQL (Supabase)
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **HTTP Client**: httpx (async, for AppHealth proxy)
- **Settings**: pydantic-settings
- **Logging**: structlog (JSON structured logs)

## Setup

### Prerequisites

- Python 3.12+
- PostgreSQL database
- (Optional) AppHealth API credentials

### Local Development

1. **Clone and setup virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and AppHealth API key
   ```

3. **Run migrations**:
   ```bash
   alembic upgrade head
   ```

4. **Start the server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access the API**:
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/health

### Docker

```bash
# Build
docker build -t schedule-api .

# Run
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/schedule_db \
  -e APPHEALTH_BASE_URL=https://back.apphealth.com.br:9090/api-vita \
  -e APPHEALTH_API_KEY=<token> \
  schedule-api
```

## API Endpoints

### LIA-Compatible (mirror existing LIA tools)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/availability/dates` | Get available dates for a specialty |
| `GET` | `/api/v1/availability/times` | Get available time slots for a professional |
| `GET` | `/api/v1/availability/agenda` | Get existing appointments in a range |
| `POST` | `/api/v1/availability/appointments` | Create a new appointment |
| `PUT` | `/api/v1/availability/appointments/{id}/cancel` | Cancel an appointment |

### Admin / Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/appointments` | List appointments (paginated, filtered) |
| `GET` | `/api/v1/appointments/{id}` | Get appointment details |
| `POST` | `/api/v1/appointments` | Create appointment (admin) |
| `PUT` | `/api/v1/appointments/{id}` | Update appointment |
| `PUT` | `/api/v1/appointments/{id}/cancel` | Cancel appointment (admin) |
| `DELETE` | `/api/v1/appointments/{id}` | Delete appointment (alias for cancel) |
| `POST` | `/api/v1/availability/blocks` | Create unavailability block |
| `GET` | `/api/v1/availability/blocks` | List availability blocks |
| `GET` | `/api/v1/availability/settings` | Get scheduling settings |
| `PUT` | `/api/v1/availability/settings` | Update scheduling settings |
| `GET` | `/api/v1/appointment-types` | List appointment types |
| `GET` | `/api/v1/professionals` | List professionals |
| `GET` | `/api/v1/professionals/available` | List available professionals |
| `GET` | `/api/v1/reports/daily` | Daily report |
| `GET` | `/api/v1/reports/weekly` | Weekly report |

## LIA Integration

The LIA assistant communicates via tool-calling with these methods:

- `get_available_dates(specialty, month, year)` → list of available dates
- `get_available_times(professional_id, date)` → available time slots
- `get_agenda(professional_id, date_from, date_to)` → existing appointments for a range
- `schedule_appointment(patient_name, patient_phone, specialty, date, time, convenio)` → create
- `cancel_appointment(appointment_id)` → cancel

**The schedule-api exposes REST endpoints that mirror these exact operations.** The LIA can switch from calling AppHealth directly to calling schedule-api with minimal or zero code changes.

### Example: LIA calling schedule-api

```python
# Instead of calling AppHealth directly:
# response = await apphealth.get_available_dates(specialty, month, year)

# LIA now calls schedule-api:
response = await httpx.get(
    "http://schedule-api:8000/api/v1/availability/dates",
    params={"specialty": "cardiologia", "month": 4, "year": 2026}
)
available_dates = response.json()
```

## Business Rules

### Conflict Detection (LocalProvider)

- Overlapping check: `new.start < existing.end AND new.end > existing.start`
- Checks against `availability_blocks`
- Respects `buffer_minutes` from settings
- Returns `SLOT_UNAVAILABLE` error with conflict details

### Time Slot Generation

- Base slot duration = 30 minutes
- Generate slots from `opening_time` to `closing_time`
- Subtract existing appointments and availability blocks
- Respect `max_advance_days`

### Cancellation Policy

- **24h before**: free cancellation
- **< 24h**: allowed but flagged in notes
- **No-show**: tracked separately
- Cannot cancel already-cancelled or completed appointments

### AppHealthProvider

- Mirrors EXACT behavior of existing backend/integrations/scheduling_api.py
- Same professional IDs, same endpoints, same payload format
- Drop-in replacement — LIA code shouldn't need changes

## Error Responses

All errors follow a structured format:

```json
{
  "error": {
    "code": "SLOT_UNAVAILABLE",
    "message": "Horário não disponível para este profissional",
    "details": {
      "professional_id": "...",
      "requested_at": "2026-04-08T10:00:00Z",
      "conflicts": [
        {
          "appointment_id": "...",
          "patient": "João Silva",
          "time": "09:30-10:30"
        }
      ]
    }
  }
}
```

### Error Codes

| Code | Description |
|------|-------------|
| `SLOT_UNAVAILABLE` | Requested time slot is not available |
| `PROFESSIONAL_NOT_FOUND` | Professional does not exist |
| `INVALID_TIME` | Requested time is invalid |
| `NOT_FOUND` | Resource not found |
| `ALREADY_CANCELLED` | Appointment already cancelled |
| `PAST_APPOINTMENT` | Cannot modify past appointments |
| `OUTSIDE_CLINIC_HOURS` | Requested time is outside clinic hours |
| `BUFFER_VIOLATION` | Violates buffer time between appointments |
| `PROVIDER_ERROR` | Error from external provider (AppHealth) |

## Configuration

All configuration via environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | - |
| `APPHEALTH_BASE_URL` | AppHealth API base URL | - |
| `APPHEALTH_API_KEY` | AppHealth API authentication token | - |
| `CORS_ORIGINS` | JSON array of allowed CORS origins | `["http://localhost:3000"]` |
| `LOG_LEVEL` | Logging level | `info` |
| `ENV` | Environment name | `development` |
| `API_PREFIX` | API route prefix | `/api/v1` |

## Testing

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=html
```

## License

Private - Clínica Atend Já Sorocaba

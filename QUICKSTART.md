# Quick Start Guide

## Development Setup (5 minutes)

```bash
# 1. Setup
./setup.sh

# 2. Edit .env with your database URL
# DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/schedule_db

# 3. Start
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 4. Visit
open http://localhost:8000/docs
```

## Docker Setup (2 minutes)

```bash
# Start everything (database + API)
docker-compose up -d

# Run migrations
docker-compose exec api alembic upgrade head

# Visit
open http://localhost:8000/docs
```

## Key Endpoints

### LIA Integration (drop-in replacement)
```python
# Get available dates
GET /api/v1/availability/dates?specialty=enfermagem&month=4&year=2026

# Get available times
GET /api/v1/availability/times?professional_id=<uuid>&date=2026-04-15

# Create appointment
POST /api/v1/availability/appointments
{
  "patient_name": "João Silva",
  "patient_phone": "15999999999",
  "specialty": "Enfermagem",
  "date": "2026-04-15",
  "time": "10:00"
}

# Cancel appointment
PUT /api/v1/availability/appointments/{id}/cancel
{
  "reason": "Patient requested"
}
```

### Admin Dashboard
```python
# List appointments
GET /api/v1/appointments?date_from=2026-04-01&date_to=2026-04-30

# Get professional list
GET /api/v1/professionals?specialty=cardiologia

# Daily report
GET /api/v1/reports/daily?date=2026-04-07
```

## Architecture at a Glance

```
LIA → schedule-api → Router → Local Provider (DB)
                                  ↓
                          AppHealth Provider (HTTP)
```

**Routing**: Specialty-based configuration
- "Enfermagem" → Local
- "Cardiologia", "Ginecologia" → AppHealth
- Configurable in `provider_routes` table

## Common Tasks

### Add a new professional
```bash
# Via API
POST /api/v1/professionals
{
  "name": "Dr. Santos",
  "specialty": "Cardiologia",
  "specialty_slug": "cardiologia",
  "external_id": "apphealth-id-123",
  "provider": "apphealth"
}
```

### Move specialty from AppHealth to Local
```bash
# Update provider_routes table
PUT /api/v1/settings (admin endpoint)
# Or directly in DB:
UPDATE provider_routes 
SET provider = 'local' 
WHERE specialty_slug = 'enfermagem';
```

### Create unavailability block
```bash
POST /api/v1/availability/blocks
{
  "professional_id": "<uuid>",
  "start_at": "2026-04-15T12:00:00",
  "end_at": "2026-04-15T13:00:00",
  "reason": "Lunch break",
  "recurring": "daily"
}
```

## Testing

```bash
# Run tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=app --cov-report=html
```

## Troubleshooting

**Database connection error?**
- Check DATABASE_URL in .env
- Ensure PostgreSQL is running
- Run: `docker-compose up db`

**AppHealth integration failing?**
- Verify APPHEALTH_BASE_URL and APPHEALTH_API_KEY
- Check network connectivity to external API

**Import errors?**
- Ensure virtual environment is activated
- Run: `pip install -r requirements.txt`

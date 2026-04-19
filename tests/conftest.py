import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.database import get_db
from app.models.base import Base

# Test database URL (in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    """Create test database engine."""
    eng = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest.fixture
async def db_session(engine):
    """Create a new database session for each test."""
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session):
    """Create a test client with overridden database dependency."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def sample_professional():
    """Sample professional data."""
    return {
        "name": "Dr. Silva",
        "specialty": "Cardiologia",
        "specialty_slug": "cardiologia",
        "provider": "local",
        "active": True,
    }


@pytest.fixture
def sample_appointment_request():
    """Sample appointment creation request."""
    return {
        "patient_name": "João Silva",
        "patient_phone": "15999999999",
        "specialty": "Enfermagem",
        "date": "2026-04-15",
        "time": "10:00",
        "source": "lia",
    }


@pytest.fixture
def sample_availability_block():
    """Sample availability block."""
    return {
        "start_at": "2026-04-15T12:00:00",
        "end_at": "2026-04-15T13:00:00",
        "reason": "Almoço",
        "recurring": "daily",
    }

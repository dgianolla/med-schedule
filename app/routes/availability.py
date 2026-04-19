from datetime import date, datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.availability import AvailabilityBlock
from app.models.settings import SchedulingSettings
from app.schemas.availability import (
    AvailabilityBlockCreate,
    AvailabilityBlockResponse,
)
from app.schemas.settings import (
    SchedulingSettingsResponse,
    SchedulingSettingsUpdate,
)

router = APIRouter(prefix="/availability", tags=["Availability Management"])


@router.post(
    "/blocks",
    response_model=AvailabilityBlockResponse,
    status_code=201,
    summary="Create availability block",
)
async def create_availability_block(
    request: AvailabilityBlockCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new availability block (unavailable time period)."""
    block = AvailabilityBlock(
        professional_id=request.professional_id,
        specialty=request.specialty,
        start_at=request.start_at,
        end_at=request.end_at,
        reason=request.reason,
        recurring=request.recurring,
    )

    db.add(block)
    await db.commit()
    await db.refresh(block)

    return AvailabilityBlockResponse(
        id=block.id,
        professional_id=block.professional_id,
        specialty=block.specialty,
        start_at=block.start_at,
        end_at=block.end_at,
        reason=block.reason,
        recurring=block.recurring,
        created_at=block.created_at,
    )


@router.get(
    "/blocks",
    response_model=list[AvailabilityBlockResponse],
    summary="List availability blocks",
)
async def list_availability_blocks(
    professional_id: Optional[UUID] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List availability blocks with filters."""
    query = select(AvailabilityBlock)
    filters = []

    if professional_id:
        filters.append(AvailabilityBlock.professional_id == professional_id)
    if date_from:
        dt_from = datetime(date_from.year, date_from.month, date_from.day)
        filters.append(AvailabilityBlock.end_at >= dt_from)
    if date_to:
        dt_to = datetime(date_to.year, date_to.month, date_to.day, 23, 59, 59)
        filters.append(AvailabilityBlock.start_at <= dt_to)

    if filters:
        query = query.where(and_(*filters))

    query = query.order_by(AvailabilityBlock.start_at)
    result = await db.execute(query)
    blocks = result.scalars().all()

    return [
        AvailabilityBlockResponse(
            id=block.id,
            professional_id=block.professional_id,
            specialty=block.specialty,
            start_at=block.start_at,
            end_at=block.end_at,
            reason=block.reason,
            recurring=block.recurring,
            created_at=block.created_at,
        )
        for block in blocks
    ]


@router.get(
    "/settings",
    response_model=SchedulingSettingsResponse,
    summary="Get scheduling settings",
)
async def get_settings(
    db: AsyncSession = Depends(get_db),
):
    """Get clinic scheduling settings."""
    result = await db.execute(select(SchedulingSettings))
    settings = result.scalar_one_or_none()

    if not settings:
        settings = SchedulingSettings()
        db.add(settings)
        await db.commit()
        await db.refresh(settings)

    return SchedulingSettingsResponse(
        id=settings.id,
        weekday_opening=settings.weekday_opening,
        weekday_closing=settings.weekday_closing,
        saturday_opening=settings.saturday_opening,
        saturday_closing=settings.saturday_closing,
        sunday_closed=settings.sunday_closed,
        holidays_closed=settings.holidays_closed,
        buffer_minutes=settings.buffer_minutes,
        max_advance_days=settings.max_advance_days,
    )


@router.put(
    "/settings",
    response_model=SchedulingSettingsResponse,
    summary="Update scheduling settings",
)
async def update_settings(
    request: SchedulingSettingsUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update clinic scheduling settings."""
    result = await db.execute(select(SchedulingSettings))
    settings = result.scalar_one_or_none()

    if not settings:
        settings = SchedulingSettings()
        db.add(settings)

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)

    await db.commit()
    await db.refresh(settings)

    return SchedulingSettingsResponse(
        id=settings.id,
        weekday_opening=settings.weekday_opening,
        weekday_closing=settings.weekday_closing,
        saturday_opening=settings.saturday_opening,
        saturday_closing=settings.saturday_closing,
        sunday_closed=settings.sunday_closed,
        holidays_closed=settings.holidays_closed,
        buffer_minutes=settings.buffer_minutes,
        max_advance_days=settings.max_advance_days,
    )

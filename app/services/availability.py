from datetime import date, datetime, time, timedelta
from typing import Optional, List
from uuid import UUID

import calendar
import structlog
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment import Appointment as AppointmentModel
from app.models.availability import AvailabilityBlock
from app.models.settings import SchedulingSettings
from app.providers.base import TimeSlot

logger = structlog.get_logger()


async def generate_available_dates(
    db: AsyncSession,
    professional_id: UUID,
    month: int,
    year: int,
) -> List[date]:
    """Generate list of dates with available slots."""
    settings_result = await db.execute(select(SchedulingSettings))
    settings = settings_result.scalar_one_or_none()
    if not settings:
        settings = SchedulingSettings()
        db.add(settings)
        await db.commit()
        await db.refresh(settings)

    days_in_month = calendar.monthrange(year, month)[1]
    available_dates = []

    for day in range(1, days_in_month + 1):
        candidate = date(year, month, day)
        weekday = candidate.weekday()

        # Check if clinic is open
        if weekday == 6 and settings.sunday_closed:
            continue

        if weekday >= 5:
            opening = settings.saturday_opening if weekday == 5 else settings.weekday_opening
            closing = settings.saturday_closing if weekday == 5 else settings.weekday_closing
        else:
            opening = settings.weekday_opening
            closing = settings.weekday_closing

        # Check max advance days
        days_ahead = (candidate - date.today()).days
        if days_ahead > settings.max_advance_days:
            continue

        # Check if there's at least one slot available
        slots = await generate_slots_for_day(
            db, candidate, opening, closing, professional_id
        )
        if any(s.available for s in slots):
            available_dates.append(candidate)

    return available_dates


async def generate_slots_for_day(
    db: AsyncSession,
    day: date,
    opening: time,
    closing: time,
    professional_id: UUID,
    duration_minutes: int = 30,
) -> List[TimeSlot]:
    """Generate time slots for a specific day."""
    day_start = datetime(day.year, day.month, day.day)
    day_end = day_start + timedelta(days=1)

    # Get existing appointments
    appt_query = select(AppointmentModel).where(
        AppointmentModel.professional_id == professional_id,
        AppointmentModel.scheduled_at >= day_start,
        AppointmentModel.scheduled_at < day_end,
        AppointmentModel.status.notin_(["cancelled"]),
    )
    appt_result = await db.execute(appt_query)
    appointments = appt_result.scalars().all()

    # Get availability blocks
    block_query = select(AvailabilityBlock).where(
        or_(
            and_(
                AvailabilityBlock.professional_id == professional_id,
                AvailabilityBlock.start_at < day_end,
                AvailabilityBlock.end_at > day_start,
            ),
            and_(
                AvailabilityBlock.professional_id.is_(None),
                AvailabilityBlock.start_at < day_end,
                AvailabilityBlock.end_at > day_start,
            ),
        )
    )
    block_result = await db.execute(block_query)
    blocks = block_result.scalars().all()

    # Get settings for buffer
    settings_result = await db.execute(select(SchedulingSettings))
    settings = settings_result.scalar_one_or_none()
    buffer_minutes = settings.buffer_minutes if settings else 0

    # Generate slots
    slots = []
    current = datetime(day.year, day.month, day.day, opening.hour, opening.minute)
    end_time = datetime(day.year, day.month, day.day, closing.hour, closing.minute)

    while current < end_time:
        slot_end = current + timedelta(minutes=duration_minutes)

        # Check if slot end exceeds closing time
        if slot_end > end_time:
            break

        # Check conflicts with appointments
        available = True
        for appt in appointments:
            if current < appt.ends_at + timedelta(minutes=buffer_minutes) and \
               slot_end + timedelta(minutes=buffer_minutes) > appt.scheduled_at:
                available = False
                break

        # Check conflicts with blocks
        if available:
            for block in blocks:
                if current < block.end_at and slot_end > block.start_at:
                    available = False
                    break

        slots.append(
            TimeSlot(
                time=current.strftime("%H:%M"),
                available=available,
            )
        )

        current = slot_end

    return slots

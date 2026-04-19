from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment import Appointment as AppointmentModel
from app.models.availability import AvailabilityBlock


async def check_conflicts(
    db: AsyncSession,
    professional_id: Optional[str],
    scheduled_at,
    ends_at,
) -> List[dict]:
    """Check for scheduling conflicts.
    
    Returns list of conflicts if any, empty list if no conflicts.
    """
    conflicts = []

    # Check overlapping appointments
    if professional_id:
        appt_query = select(AppointmentModel).where(
            AppointmentModel.professional_id == UUID(professional_id),
            AppointmentModel.status.notin_(["cancelled"]),
            AppointmentModel.scheduled_at < ends_at,
            AppointmentModel.ends_at > scheduled_at,
        )
        appt_result = await db.execute(appt_query)
        overlapping_appointments = appt_result.scalars().all()

        for appt in overlapping_appointments:
            conflicts.append({
                "type": "appointment",
                "appointment_id": str(appt.id),
                "patient": appt.patient_name,
                "time": f"{appt.scheduled_at.strftime('%H:%M')}-{appt.ends_at.strftime('%H:%M')}",
            })

    # Check availability blocks
    block_conditions = [
        AvailabilityBlock.start_at < ends_at,
        AvailabilityBlock.end_at > scheduled_at,
    ]
    
    if professional_id:
        block_conditions.append(
            AvailabilityBlock.professional_id == UUID(professional_id)
        )
    else:
        block_conditions.append(
            AvailabilityBlock.professional_id.is_(None)
        )
    
    block_query = select(AvailabilityBlock).where(
        and_(*block_conditions)
    )
    block_result = await db.execute(block_query)
    blocks = block_result.scalars().all()

    for block in blocks:
        conflicts.append({
            "type": "availability_block",
            "block_id": str(block.id),
            "reason": block.reason,
            "time": f"{block.start_at.strftime('%H:%M')}-{block.end_at.strftime('%H:%M')}",
        })

    return conflicts


async def check_time_within_clinic_hours(
    db: AsyncSession,
    scheduled_at,
    settings,
) -> bool:
    """Check if the appointment time is within clinic operating hours."""
    from datetime import time

    appointment_time = scheduled_at.time()
    weekday = scheduled_at.weekday()

    if weekday >= 5:
        if weekday == 6 and settings.sunday_closed:
            return False
        opening = settings.saturday_opening if weekday == 5 else settings.weekday_opening
        closing = settings.saturday_closing if weekday == 5 else settings.weekday_closing
    else:
        opening = settings.weekday_opening
        closing = settings.weekday_closing

    return opening <= appointment_time < closing

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func, and_, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.professional import Professional
from app.models.appointment_type import AppointmentType
from app.models.appointment import Appointment as AppointmentModel

from app.schemas.professional import (
    ProfessionalResponse,
    ProfessionalCreate,
    ProfessionalUpdate,
    AppointmentTypeResponse,
    AppointmentTypeCreate,
    AppointmentTypeUpdate,
)
from app.schemas.settings import DailyReportResponse, WeeklyReportResponse

router = APIRouter(tags=["Reference Data & Reports"])


@router.get(
    "/appointment-types",
    response_model=list[AppointmentTypeResponse],
    summary="List appointment types",
)
async def list_appointment_types(
    db: AsyncSession = Depends(get_db),
):
    """List all active appointment types."""
    result = await db.execute(
        select(AppointmentType)
        .where(AppointmentType.active == True)
        .order_by(AppointmentType.name)
    )
    types = result.scalars().all()

    return [
        AppointmentTypeResponse(
            id=t.id,
            name=t.name,
            slug=t.slug,
            default_duration_minutes=t.default_duration_minutes,
            description=t.description,
            active=t.active,
        )
        for t in types
    ]


@router.post(
    "/appointment-types",
    response_model=AppointmentTypeResponse,
    status_code=201,
    summary="Create appointment type",
)
async def create_appointment_type(
    request: AppointmentTypeCreate,
    db: AsyncSession = Depends(get_db),
):
    appt_type = AppointmentType(**request.model_dump())
    db.add(appt_type)
    await db.commit()
    await db.refresh(appt_type)
    return AppointmentTypeResponse.model_validate(appt_type)


@router.put(
    "/appointment-types/{type_id}",
    response_model=AppointmentTypeResponse,
    summary="Update appointment type",
)
async def update_appointment_type(
    type_id: UUID,
    request: AppointmentTypeUpdate,
    db: AsyncSession = Depends(get_db),
):
    appt_type = await db.get(AppointmentType, type_id)
    if not appt_type:
        raise HTTPException(status_code=404, detail="Appointment type not found")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(appt_type, field, value)

    await db.commit()
    await db.refresh(appt_type)
    return AppointmentTypeResponse.model_validate(appt_type)


@router.delete(
    "/appointment-types/{type_id}",
    status_code=204,
    summary="Delete appointment type",
)
async def delete_appointment_type(
    type_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    appt_type = await db.get(AppointmentType, type_id)
    if not appt_type:
        raise HTTPException(status_code=404, detail="Appointment type not found")

    appt_type.active = False
    await db.commit()
    return None


@router.get(
    "/professionals",
    response_model=list[ProfessionalResponse],
    summary="List professionals",
)
async def list_professionals(
    specialty: Optional[str] = Query(None),
    active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List professionals with optional filters."""
    query = select(Professional)
    filters = []

    if specialty:
        filters.append(
            Professional.specialty.ilike(f"%{specialty}%")
        )
    if active is not None:
        filters.append(Professional.active == active)

    if filters:
        query = query.where(and_(*filters))

    query = query.order_by(Professional.name)
    result = await db.execute(query)
    professionals = result.scalars().all()

    return [
        ProfessionalResponse(
            id=p.id,
            name=p.name,
            specialty=p.specialty,
            specialty_slug=p.specialty_slug,
            external_id=p.external_id,
            provider=p.provider,
            active=p.active,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in professionals
    ]


@router.get(
    "/professionals/available",
    response_model=list[ProfessionalResponse],
    summary="List available professionals",
)
async def list_available_professionals(
    specialty: str = Query(...),
    date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List professionals with availability on a given date."""
    query = select(Professional).where(
        Professional.specialty.ilike(f"%{specialty}%"),
        Professional.active == True,
    )

    result = await db.execute(query.order_by(Professional.name))
    professionals = result.scalars().all()

    # For now, return all active professionals for the specialty
    # Can be enhanced to check actual availability
    return [
        ProfessionalResponse(
            id=p.id,
            name=p.name,
            specialty=p.specialty,
            specialty_slug=p.specialty_slug,
            external_id=p.external_id,
            provider=p.provider,
            active=p.active,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in professionals
    ]


@router.post(
    "/professionals",
    response_model=ProfessionalResponse,
    status_code=201,
    summary="Create professional",
)
async def create_professional(
    request: ProfessionalCreate,
    db: AsyncSession = Depends(get_db),
):
    professional = Professional(**request.model_dump())
    db.add(professional)
    await db.commit()
    await db.refresh(professional)
    return ProfessionalResponse.model_validate(professional)


@router.put(
    "/professionals/{professional_id}",
    response_model=ProfessionalResponse,
    summary="Update professional",
)
async def update_professional(
    professional_id: UUID,
    request: ProfessionalUpdate,
    db: AsyncSession = Depends(get_db),
):
    professional = await db.get(Professional, professional_id)
    if not professional:
        raise HTTPException(status_code=404, detail="Professional not found")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(professional, field, value)

    await db.commit()
    await db.refresh(professional)
    return ProfessionalResponse.model_validate(professional)


@router.delete(
    "/professionals/{professional_id}",
    status_code=204,
    summary="Deactivate professional",
)
async def delete_professional(
    professional_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    professional = await db.get(Professional, professional_id)
    if not professional:
        raise HTTPException(status_code=404, detail="Professional not found")

    professional.active = False
    await db.commit()
    return None


@router.get(
    "/settings",
    summary="Get clinic settings",
)
async def get_settings(
    db: AsyncSession = Depends(get_db),
):
    """Get clinic settings."""
    from app.models.settings import SchedulingSettings

    result = await db.execute(select(SchedulingSettings))
    settings = result.scalar_one_or_none()

    if not settings:
        settings = SchedulingSettings()
        db.add(settings)
        await db.commit()
        await db.refresh(settings)

    return {
        "id": settings.id,
        "weekday_opening": settings.weekday_opening.isoformat(),
        "weekday_closing": settings.weekday_closing.isoformat(),
        "saturday_opening": settings.saturday_opening.isoformat(),
        "saturday_closing": settings.saturday_closing.isoformat(),
        "sunday_closed": settings.sunday_closed,
        "holidays_closed": settings.holidays_closed,
        "buffer_minutes": settings.buffer_minutes,
        "max_advance_days": settings.max_advance_days,
    }


@router.put(
    "/settings",
    summary="Update clinic settings",
)
async def update_settings(
    data: dict,
    db: AsyncSession = Depends(get_db),
):
    """Update clinic settings."""
    from app.models.settings import SchedulingSettings

    result = await db.execute(select(SchedulingSettings))
    settings = result.scalar_one_or_none()

    if not settings:
        settings = SchedulingSettings()
        db.add(settings)

    for field, value in data.items():
        if hasattr(settings, field):
            setattr(settings, field, value)

    await db.commit()
    await db.refresh(settings)

    return {
        "id": settings.id,
        "weekday_opening": settings.weekday_opening.isoformat(),
        "weekday_closing": settings.weekday_closing.isoformat(),
        "saturday_opening": settings.saturday_opening.isoformat(),
        "saturday_closing": settings.saturday_closing.isoformat(),
        "sunday_closed": settings.sunday_closed,
        "holidays_closed": settings.holidays_closed,
        "buffer_minutes": settings.buffer_minutes,
        "max_advance_days": settings.max_advance_days,
    }


@router.get(
    "/reports/daily",
    response_model=DailyReportResponse,
    summary="Daily report",
)
async def daily_report(
    date: date = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Get daily appointment report."""
    dt_start = datetime(date.year, date.month, date.day)
    dt_end = datetime(date.year, date.month, date.day, 23, 59, 59)

    # Total appointments
    total_query = select(func.count(AppointmentModel.id)).where(
        AppointmentModel.scheduled_at >= dt_start,
        AppointmentModel.scheduled_at <= dt_end,
    )
    total_result = await db.execute(total_query)
    total = total_result.scalar()

    # By status
    status_query = select(
        AppointmentModel.status,
        func.count(AppointmentModel.id)
    ).where(
        AppointmentModel.scheduled_at >= dt_start,
        AppointmentModel.scheduled_at <= dt_end,
    ).group_by(AppointmentModel.status)
    status_result = await db.execute(status_query)
    by_status = {row[0]: row[1] for row in status_result.all()}

    # By professional
    prof_query = select(
        AppointmentModel.professional_name,
        func.count(AppointmentModel.id)
    ).where(
        AppointmentModel.scheduled_at >= dt_start,
        AppointmentModel.scheduled_at <= dt_end,
    ).group_by(AppointmentModel.professional_name)
    prof_result = await db.execute(prof_query)
    by_professional = {row[0] or "Unassigned": row[1] for row in prof_result.all()}

    # By specialty
    type_query = select(
        AppointmentModel.specialty,
        func.count(AppointmentModel.id)
    ).where(
        AppointmentModel.scheduled_at >= dt_start,
        AppointmentModel.scheduled_at <= dt_end,
    ).group_by(AppointmentModel.specialty)
    type_result = await db.execute(type_query)
    by_type = {row[0]: row[1] for row in type_result.all()}

    return DailyReportResponse(
        date=date.isoformat(),
        total=total,
        by_status=by_status,
        by_professional=by_professional,
        by_type=by_type,
    )


@router.get(
    "/reports/weekly",
    response_model=WeeklyReportResponse,
    summary="Weekly report",
)
async def weekly_report(
    week_start: date = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Get weekly appointment report."""
    from datetime import timedelta

    week_end = week_start + timedelta(days=6)
    dt_start = datetime(week_start.year, week_start.month, week_start.day)
    dt_end = datetime(week_end.year, week_end.month, week_end.day, 23, 59, 59)

    # Total
    total_query = select(func.count(AppointmentModel.id)).where(
        AppointmentModel.scheduled_at >= dt_start,
        AppointmentModel.scheduled_at <= dt_end,
    )
    total_result = await db.execute(total_query)
    total = total_result.scalar()

    # By status
    status_query = select(
        AppointmentModel.status,
        func.count(AppointmentModel.id)
    ).where(
        AppointmentModel.scheduled_at >= dt_start,
        AppointmentModel.scheduled_at <= dt_end,
    ).group_by(AppointmentModel.status)
    status_result = await db.execute(status_query)
    by_status = {row[0]: row[1] for row in status_result.all()}

    # By professional
    prof_query = select(
        AppointmentModel.professional_name,
        func.count(AppointmentModel.id)
    ).where(
        AppointmentModel.scheduled_at >= dt_start,
        AppointmentModel.scheduled_at <= dt_end,
    ).group_by(AppointmentModel.professional_name)
    prof_result = await db.execute(prof_query)
    by_professional = {row[0] or "Unassigned": row[1] for row in prof_result.all()}

    # By specialty
    type_query = select(
        AppointmentModel.specialty,
        func.count(AppointmentModel.id)
    ).where(
        AppointmentModel.scheduled_at >= dt_start,
        AppointmentModel.scheduled_at <= dt_end,
    ).group_by(AppointmentModel.specialty)
    type_result = await db.execute(type_query)
    by_type = {row[0]: row[1] for row in type_result.all()}

    # Daily breakdown
    daily_breakdown = {}
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_start = datetime(day.year, day.month, day.day)
        day_end = day_start + timedelta(days=1)

        day_query = select(func.count(AppointmentModel.id)).where(
            AppointmentModel.scheduled_at >= day_start,
            AppointmentModel.scheduled_at < day_end,
        )
        day_result = await db.execute(day_query)
        daily_breakdown[day.isoformat()] = day_result.scalar()

    return WeeklyReportResponse(
        week_start=week_start.isoformat(),
        week_end=week_end.isoformat(),
        total=total,
        by_status=by_status,
        by_professional=by_professional,
        by_type=by_type,
        daily_breakdown=daily_breakdown,
    )

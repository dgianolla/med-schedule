from datetime import date, datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.appointment import Appointment as AppointmentModel
from app.schemas.appointment import (
    AppointmentResponse,
    AppointmentListResponse,
    CreateAppointmentRequest,
    AppointmentUpdateRequest,
    CancelAppointmentRequest,
)
from app.schemas.common import PaginatedResponse, ErrorResponse
from app.services.router import ProviderRouter
from app.providers.base import CreateAppointmentRequest as ProviderCreateRequest

router = APIRouter(prefix="/appointments", tags=["Admin Appointments"])


@router.get(
    "",
    response_model=PaginatedResponse[AppointmentListResponse],
    summary="List appointments with pagination",
)
async def list_appointments(
    date: Optional[date] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    professional_id: Optional[UUID] = Query(None),
    patient_phone: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List appointments with filters."""
    query = select(AppointmentModel)

    filters = []
    if date:
        dt_start = datetime(date.year, date.month, date.day)
        dt_end = datetime(date.year, date.month, date.day, 23, 59, 59)
        filters.append(AppointmentModel.scheduled_at >= dt_start)
        filters.append(AppointmentModel.scheduled_at <= dt_end)
    if date_from:
        dt_start = datetime(date_from.year, date_from.month, date_from.day)
        filters.append(AppointmentModel.scheduled_at >= dt_start)
    if date_to:
        dt_end = datetime(date_to.year, date_to.month, date_to.day, 23, 59, 59)
        filters.append(AppointmentModel.scheduled_at <= dt_end)
    if status:
        filters.append(AppointmentModel.status == status)
    if professional_id:
        filters.append(AppointmentModel.professional_id == professional_id)
    if patient_phone:
        filters.append(AppointmentModel.patient_phone.like(f"%{patient_phone}%"))

    if filters:
        query = query.where(and_(*filters))

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.order_by(AppointmentModel.scheduled_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)

    result = await db.execute(query)
    appointments = result.scalars().all()

    pages = (total + per_page - 1) // per_page

    return PaginatedResponse(
        items=[
            AppointmentListResponse(
                id=appt.id,
                patient_name=appt.patient_name,
                patient_phone=appt.patient_phone,
                specialty=appt.specialty,
                professional_name=appt.professional_name,
                scheduled_at=appt.scheduled_at,
                status=appt.status,
                source=appt.source,
            )
            for appt in appointments
        ],
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    summary="Get appointment details",
)
async def get_appointment(
    appointment_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get appointment by ID."""
    appt = await db.get(AppointmentModel, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    return AppointmentResponse(
        id=appt.id,
        patient_name=appt.patient_name,
        patient_phone=appt.patient_phone,
        patient_email=appt.patient_email,
        professional_id=appt.professional_id,
        professional_name=appt.professional_name,
        specialty=appt.specialty,
        scheduled_at=appt.scheduled_at,
        ends_at=appt.ends_at,
        duration_minutes=appt.duration_minutes,
        status=appt.status,
        source=appt.source,
        convenio_id=appt.convenio_id,
        convenio_name=appt.convenio_name,
        notes=appt.notes,
        patient_notes=appt.patient_notes,
        cancelled_at=appt.cancelled_at,
        cancellation_reason=appt.cancellation_reason,
        created_at=appt.created_at,
        updated_at=appt.updated_at,
    )


@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=201,
    summary="Create appointment (Admin)",
)
async def create_appointment_admin(
    request: CreateAppointmentRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create appointment via admin."""
    try:
        router_service = ProviderRouter(db)
        provider = await router_service.resolve_provider(
            specialty_slug=request.specialty.lower(),
            professional_id=str(request.professional_id) if request.professional_id else None,
        )

        provider_request = ProviderCreateRequest(
            patient_name=request.patient_name,
            patient_phone=request.patient_phone,
            patient_email=request.patient_email,
            specialty=request.specialty,
            professional_id=str(request.professional_id) if request.professional_id else None,
            date=request.date.isoformat(),
            time=request.time,
            convenio_id=str(request.convenio_id) if request.convenio_id else None,
            convenio_name=request.convenio_name,
            source=request.source,
            notes=request.notes,
            patient_notes=request.patient_notes,
        )

        appointment = await provider.create_appointment(provider_request)

        return AppointmentResponse(
            id=UUID(appointment.id),
            patient_name=appointment.patient_name,
            patient_phone=appointment.patient_phone,
            patient_email=appointment.patient_email,
            professional_id=UUID(appointment.professional_id) if appointment.professional_id else None,
            professional_name=appointment.professional_name,
            specialty=appointment.specialty,
            scheduled_at=datetime.fromisoformat(appointment.scheduled_at),
            ends_at=datetime.fromisoformat(appointment.ends_at),
            duration_minutes=appointment.duration_minutes,
            status=appointment.status,
            source=appointment.source,
            convenio_id=UUID(appointment.convenio_id) if appointment.convenio_id else None,
            convenio_name=appointment.convenio_name,
            notes=appointment.notes,
            patient_notes=appointment.patient_notes,
            created_at=datetime.fromisoformat(appointment.created_at) if appointment.created_at else None,
            updated_at=datetime.fromisoformat(appointment.updated_at) if appointment.updated_at else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    summary="Update appointment",
)
async def update_appointment(
    appointment_id: UUID,
    request: AppointmentUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update appointment fields."""
    appt = await db.get(AppointmentModel, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(appt, field, value)

    await db.commit()
    await db.refresh(appt)

    return AppointmentResponse(
        id=appt.id,
        patient_name=appt.patient_name,
        patient_phone=appt.patient_phone,
        patient_email=appt.patient_email,
        professional_id=appt.professional_id,
        professional_name=appt.professional_name,
        specialty=appt.specialty,
        scheduled_at=appt.scheduled_at,
        ends_at=appt.ends_at,
        duration_minutes=appt.duration_minutes,
        status=appt.status,
        source=appt.source,
        convenio_id=appt.convenio_id,
        convenio_name=appt.convenio_name,
        notes=appt.notes,
        patient_notes=appt.patient_notes,
        cancelled_at=appt.cancelled_at,
        cancellation_reason=appt.cancellation_reason,
        created_at=appt.created_at,
        updated_at=appt.updated_at,
    )


@router.put(
    "/{appointment_id}/cancel",
    response_model=AppointmentResponse,
    summary="Cancel appointment",
)
async def cancel_appointment_admin(
    appointment_id: UUID,
    request: CancelAppointmentRequest = CancelAppointmentRequest(),
    db: AsyncSession = Depends(get_db),
):
    """Cancel appointment via admin."""
    appt = await db.get(AppointmentModel, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if appt.status == "cancelled":
        raise HTTPException(status_code=400, detail="Appointment already cancelled")

    if appt.status == "completed":
        raise HTTPException(status_code=400, detail="Cannot cancel completed appointment")

    appt.status = "cancelled"
    appt.cancelled_at = datetime.utcnow()
    appt.cancellation_reason = request.reason

    await db.commit()
    await db.refresh(appt)

    return AppointmentResponse(
        id=appt.id,
        patient_name=appt.patient_name,
        patient_phone=appt.patient_phone,
        patient_email=appt.patient_email,
        professional_id=appt.professional_id,
        professional_name=appt.professional_name,
        specialty=appt.specialty,
        scheduled_at=appt.scheduled_at,
        ends_at=appt.ends_at,
        duration_minutes=appt.duration_minutes,
        status=appt.status,
        source=appt.source,
        convenio_id=appt.convenio_id,
        convenio_name=appt.convenio_name,
        notes=appt.notes,
        patient_notes=appt.patient_notes,
        cancelled_at=appt.cancelled_at,
        cancellation_reason=appt.cancellation_reason,
        created_at=appt.created_at,
        updated_at=appt.updated_at,
    )


@router.delete(
    "/{appointment_id}",
    status_code=204,
    summary="Delete appointment (alias for cancel)",
)
async def delete_appointment(
    appointment_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete/cancel appointment."""
    appt = await db.get(AppointmentModel, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appt.status = "cancelled"
    appt.cancelled_at = datetime.utcnow()

    await db.commit()
    return None

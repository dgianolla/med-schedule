from datetime import date, datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.availability import (
    TimeSlotResponse,
    AvailableDateResponse,
)
from app.schemas.appointment import (
    CreateAppointmentRequest,
    AppointmentResponse,
    CancelAppointmentRequest,
)
from app.schemas.common import ErrorResponse
from app.services.router import ProviderRouter
from app.providers.base import CreateAppointmentRequest as ProviderCreateRequest

router = APIRouter(prefix="/availability", tags=["LIA Compatibility"])


@router.get(
    "/dates",
    response_model=list[str],
    summary="Get available dates for a specialty",
    description="LIA-compatible endpoint: returns list of ISO date strings with available slots",
)
async def get_available_dates(
    specialty: str = Query(..., description="Specialty name"),
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020, le=2030),
    db: AsyncSession = Depends(get_db),
):
    """Get available dates for LIA."""
    try:
        router_service = ProviderRouter(db)
        provider = await router_service.resolve_provider(specialty_slug=specialty.lower())

        # For now, we need a professional_id to get dates
        # This endpoint will need to be enhanced to find professionals by specialty
        dates = await provider.get_available_dates("", month, year)

        return [d.isoformat() for d in dates]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/times",
    response_model=list[TimeSlotResponse],
    summary="Get available times for a professional on a date",
    description="LIA-compatible endpoint: returns list of time slots",
)
async def get_available_times(
    professional_id: UUID = Query(...),
    date: date = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Get available times for LIA."""
    try:
        router_service = ProviderRouter(db)
        provider = await router_service.resolve_provider(professional_id=str(professional_id))

        slots = await provider.get_available_times(
            professional_id=str(professional_id),
            date=date,
        )

        return slots
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/agenda",
    response_model=list[dict],
    summary="Get existing appointments in a date range",
    description="LIA-compatible endpoint: returns appointments in range",
)
async def get_agenda(
    professional_id: Optional[UUID] = Query(None),
    date_from: date = Query(...),
    date_to: date = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Get agenda for LIA."""
    try:
        router_service = ProviderRouter(db)
        provider = await router_service.resolve_provider(
            professional_id=str(professional_id) if professional_id else None
        )

        records = await provider.get_agenda(
            professional_id=str(professional_id) if professional_id else None,
            date_from=date_from,
            date_to=date_to,
        )

        return [r.model_dump() for r in records]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/appointments",
    response_model=AppointmentResponse,
    status_code=201,
    summary="Create a new appointment",
    description="LIA-compatible endpoint: creates appointment",
    responses={
        400: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def create_appointment(
    request: CreateAppointmentRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create appointment for LIA."""
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
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        if "not available" in str(e).lower() or "conflict" in str(e).lower():
            raise HTTPException(
                status_code=409,
                detail={
                    "error": {
                        "code": "SLOT_UNAVAILABLE",
                        "message": str(e),
                    }
                },
            )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/appointments/{appointment_id}/cancel",
    response_model=AppointmentResponse,
    summary="Cancel an appointment",
    description="LIA-compatible endpoint: cancels appointment",
    responses={
        404: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
    },
)
async def cancel_appointment(
    appointment_id: UUID,
    request: CancelAppointmentRequest = CancelAppointmentRequest(),
    db: AsyncSession = Depends(get_db),
):
    """Cancel appointment for LIA."""
    try:
        # We need to find the appointment first to determine which provider
        from app.models.appointment import Appointment as AppointmentModel
        from sqlalchemy import select

        result = await db.execute(
            select(AppointmentModel).where(AppointmentModel.id == appointment_id)
        )
        appt = result.scalar_one_or_none()

        if not appt:
            raise HTTPException(status_code=404, detail="Appointment not found")

        # Use appropriate provider
        if appt.external_id and appt.source == "apphealth":
            from app.providers.apphealth import AppHealthProvider
            provider = AppHealthProvider()
            appointment = await provider.cancel_appointment(
                appointment_id=appt.external_id,
                reason=request.reason,
            )
        else:
            from app.providers.local import LocalProvider
            provider = LocalProvider(db)
            appointment = await provider.cancel_appointment(
                appointment_id=str(appointment_id),
                reason=request.reason,
            )

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
            cancelled_at=datetime.fromisoformat(appointment.cancelled_at) if appointment.cancelled_at else None,
            cancellation_reason=appointment.cancellation_reason,
            created_at=datetime.fromisoformat(appointment.created_at) if appointment.created_at else None,
            updated_at=datetime.fromisoformat(appointment.updated_at) if appointment.updated_at else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

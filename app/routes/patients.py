from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.patient import Patient as PatientModel
from app.models.appointment import Appointment as AppointmentModel
from app.schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientListResponse,
)
from app.schemas.appointment import AppointmentListResponse
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get(
    "",
    response_model=PaginatedResponse[PatientListResponse],
    summary="List patients with pagination",
)
async def list_patients(
    search: Optional[str] = Query(None, description="Search by name, phone or document"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(PatientModel)

    if search:
        search_filter = or_(
            PatientModel.name.ilike(f"%{search}%"),
            PatientModel.phone.like(f"%{search}%"),
            PatientModel.document.like(f"%{search}%"),
        )
        query = query.where(search_filter)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.order_by(PatientModel.name)
    query = query.offset((page - 1) * per_page).limit(per_page)

    result = await db.execute(query)
    patients = result.scalars().all()

    pages = (total + per_page - 1) // per_page if total else 0

    return PaginatedResponse(
        items=[PatientListResponse.model_validate(p) for p in patients],
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Get patient details",
)
async def get_patient(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    patient = await db.get(PatientModel, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return PatientResponse.model_validate(patient)


@router.post(
    "",
    response_model=PatientResponse,
    status_code=201,
    summary="Create patient",
)
async def create_patient(
    request: PatientCreate,
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(
        select(PatientModel).where(PatientModel.phone == request.phone)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail="Patient with this phone already exists",
        )

    patient = PatientModel(**request.model_dump())
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return PatientResponse.model_validate(patient)


@router.post(
    "/upsert",
    response_model=PatientResponse,
    summary="Create or update patient by phone",
)
async def upsert_patient(
    request: PatientCreate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PatientModel).where(PatientModel.phone == request.phone)
    )
    patient = result.scalar_one_or_none()

    if patient:
        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(patient, field, value)
    else:
        patient = PatientModel(**request.model_dump())
        db.add(patient)

    await db.commit()
    await db.refresh(patient)
    return PatientResponse.model_validate(patient)


@router.put(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Update patient",
)
async def update_patient(
    patient_id: UUID,
    request: PatientUpdate,
    db: AsyncSession = Depends(get_db),
):
    patient = await db.get(PatientModel, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)

    await db.commit()
    await db.refresh(patient)
    return PatientResponse.model_validate(patient)


@router.delete(
    "/{patient_id}",
    status_code=204,
    summary="Delete patient",
)
async def delete_patient(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    patient = await db.get(PatientModel, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    await db.delete(patient)
    await db.commit()
    return None


@router.get(
    "/{patient_id}/appointments",
    response_model=PaginatedResponse[AppointmentListResponse],
    summary="Get patient appointment history",
)
async def get_patient_appointments(
    patient_id: UUID,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    patient = await db.get(PatientModel, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    query = select(AppointmentModel).where(
        or_(
            AppointmentModel.patient_id == patient_id,
            AppointmentModel.patient_phone == patient.phone,
        )
    )

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.order_by(AppointmentModel.scheduled_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)

    result = await db.execute(query)
    appointments = result.scalars().all()

    pages = (total + per_page - 1) // per_page if total else 0

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

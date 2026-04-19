from datetime import date, datetime, time, timedelta
from typing import Optional
from uuid import UUID

import calendar
import structlog
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.providers.base import (
    AppointmentProvider,
    TimeSlot,
    AppointmentRecord,
    CreateAppointmentRequest,
    Appointment,
)
from app.models.appointment import Appointment as AppointmentModel
from app.models.professional import Professional
from app.models.availability import AvailabilityBlock
from app.models.settings import SchedulingSettings
from app.services.scheduling import check_conflicts

logger = structlog.get_logger()


class LocalProvider(AppointmentProvider):
    """Direct database scheduling (enfermagem, future full migration)."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_available_dates(
        self, professional_id: str, month: int, year: int
    ) -> list[date]:
        logger.info(
            "get_available_dates",
            professional_id=professional_id,
            month=month,
            year=year,
        )

        prof = await self.db.get(Professional, UUID(professional_id))
        if not prof:
            return []

        settings = await self._get_settings()
        days_in_month = calendar.monthrange(year, month)[1]
        available_dates = []

        for day in range(1, days_in_month + 1):
            candidate = date(year, month, day)
            weekday = candidate.weekday()

            if weekday >= 5:
                if weekday == 6 and settings.sunday_closed:
                    continue
                if weekday == 5:
                    opening = settings.saturday_opening
                    closing = settings.saturday_closing
                else:
                    continue
            else:
                opening = settings.weekday_opening
                closing = settings.weekday_closing

            days_ahead = (candidate - date.today()).days
            if days_ahead > settings.max_advance_days:
                continue

            slots = await self._generate_slots_for_day(
                candidate, opening, closing, professional_id
            )
            if any(s.available for s in slots):
                available_dates.append(candidate)

        return available_dates

    async def get_available_times(
        self, professional_id: str, date: date
    ) -> list[TimeSlot]:
        logger.info(
            "get_available_times",
            professional_id=professional_id,
            date=date,
        )

        settings = await self._get_settings()
        weekday = date.weekday()

        if weekday >= 5:
            if weekday == 6 and settings.sunday_closed:
                return []
            opening = settings.saturday_opening if weekday == 5 else settings.weekday_opening
            closing = settings.saturday_closing if weekday == 5 else settings.weekday_closing
        else:
            opening = settings.weekday_opening
            closing = settings.weekday_closing

        return await self._generate_slots_for_day(
            date, opening, closing, professional_id
        )

    async def get_agenda(
        self, professional_id: str | None, date_from: date, date_to: date
    ) -> list[AppointmentRecord]:
        logger.info(
            "get_agenda",
            professional_id=professional_id,
            date_from=date_from,
            date_to=date_to,
        )

        dt_from = datetime(date_from.year, date_from.month, date_from.day, 0, 0, 0)
        dt_to = datetime(date_to.year, date_to.month, date_to.day, 23, 59, 59)

        query = select(AppointmentModel).where(
            AppointmentModel.scheduled_at >= dt_from,
            AppointmentModel.scheduled_at <= dt_to,
            AppointmentModel.status.notin_(["cancelled"]),
        )

        if professional_id:
            query = query.where(AppointmentModel.professional_id == UUID(professional_id))

        result = await self.db.execute(query.order_by(AppointmentModel.scheduled_at))
        appointments = result.scalars().all()

        return [
            AppointmentRecord(
                id=str(appt.id),
                patient_name=appt.patient_name,
                patient_phone=appt.patient_phone,
                professional_id=str(appt.professional_id) if appt.professional_id else "",
                scheduled_at=appt.scheduled_at.isoformat(),
                ends_at=appt.ends_at.isoformat(),
                status=appt.status,
                specialty=appt.specialty,
                external_id=appt.external_id,
            )
            for appt in appointments
        ]

    async def create_appointment(
        self, payload: CreateAppointmentRequest
    ) -> Appointment:
        logger.info("create_appointment", payload=payload.model_dump())

        scheduled_at = datetime.fromisoformat(f"{payload.date}T{payload.time}:00")

        if payload.professional_id:
            prof_result = await self.db.execute(
                select(Professional).where(Professional.id == UUID(payload.professional_id))
            )
            prof = prof_result.scalar_one_or_none()
            if not prof:
                raise ValueError("Professional not found")
            professional_name = prof.name
        else:
            professional_name = None

        duration_minutes = 30
        ends_at = scheduled_at + timedelta(minutes=duration_minutes)

        conflicts = await check_conflicts(
            self.db,
            payload.professional_id,
            scheduled_at,
            ends_at,
        )

        if conflicts:
            raise ValueError(f"Slot unavailable. Conflicts: {conflicts}")

        appt = AppointmentModel(
            patient_name=payload.patient_name,
            patient_phone=payload.patient_phone,
            patient_email=payload.patient_email,
            professional_id=UUID(payload.professional_id) if payload.professional_id else None,
            professional_name=professional_name,
            specialty=payload.specialty,
            scheduled_at=scheduled_at,
            ends_at=ends_at,
            duration_minutes=duration_minutes,
            status="scheduled",
            source=payload.source,
            convenio_id=UUID(payload.convenio_id) if payload.convenio_id else None,
            convenio_name=payload.convenio_name,
            notes=payload.notes,
            patient_notes=payload.patient_notes,
        )

        self.db.add(appt)
        await self.db.commit()
        await self.db.refresh(appt)

        logger.info("appointment_created", appointment_id=str(appt.id))

        return Appointment(
            id=str(appt.id),
            patient_name=appt.patient_name,
            patient_phone=appt.patient_phone,
            patient_email=appt.patient_email,
            professional_id=str(appt.professional_id) if appt.professional_id else None,
            professional_name=appt.professional_name,
            specialty=appt.specialty,
            scheduled_at=appt.scheduled_at.isoformat(),
            ends_at=appt.ends_at.isoformat(),
            duration_minutes=appt.duration_minutes,
            status=appt.status,
            source=appt.source,
            convenio_id=str(appt.convenio_id) if appt.convenio_id else None,
            convenio_name=appt.convenio_name,
            notes=appt.notes,
            patient_notes=appt.patient_notes,
            created_at=appt.created_at.isoformat(),
            updated_at=appt.updated_at.isoformat(),
        )

    async def cancel_appointment(
        self, appointment_id: str, reason: str | None = None
    ) -> Appointment:
        logger.info("cancel_appointment", appointment_id=appointment_id)

        appt = await self.db.get(AppointmentModel, UUID(appointment_id))
        if not appt:
            raise ValueError("Appointment not found")

        if appt.status == "cancelled":
            raise ValueError("Appointment already cancelled")

        if appt.status == "completed":
            raise ValueError("Cannot cancel completed appointment")

        appt.status = "cancelled"
        appt.cancelled_at = datetime.utcnow()
        appt.cancellation_reason = reason

        await self.db.commit()
        await self.db.refresh(appt)

        logger.info("appointment_cancelled", appointment_id=appointment_id)

        return Appointment(
            id=str(appt.id),
            patient_name=appt.patient_name,
            patient_phone=appt.patient_phone,
            patient_email=appt.patient_email,
            professional_id=str(appt.professional_id) if appt.professional_id else None,
            professional_name=appt.professional_name,
            specialty=appt.specialty,
            scheduled_at=appt.scheduled_at.isoformat(),
            ends_at=appt.ends_at.isoformat(),
            duration_minutes=appt.duration_minutes,
            status=appt.status,
            source=appt.source,
            convenio_id=str(appt.convenio_id) if appt.convenio_id else None,
            convenio_name=appt.convenio_name,
            notes=appt.notes,
            patient_notes=appt.patient_notes,
            cancelled_at=appt.cancelled_at.isoformat() if appt.cancelled_at else None,
            cancellation_reason=appt.cancellation_reason,
            created_at=appt.created_at.isoformat(),
            updated_at=appt.updated_at.isoformat(),
        )

    async def _get_settings(self) -> SchedulingSettings:
        result = await self.db.execute(select(SchedulingSettings))
        settings = result.scalar_one_or_none()
        if not settings:
            settings = SchedulingSettings()
            self.db.add(settings)
            await self.db.commit()
            await self.db.refresh(settings)
        return settings

    async def _generate_slots_for_day(
        self,
        day: date,
        opening: time,
        closing: time,
        professional_id: str,
    ) -> list[TimeSlot]:
        day_start = datetime(day.year, day.month, day.day)
        day_end = day_start + timedelta(days=1)

        appt_query = select(AppointmentModel).where(
            AppointmentModel.professional_id == UUID(professional_id),
            AppointmentModel.scheduled_at >= day_start,
            AppointmentModel.scheduled_at < day_end,
            AppointmentModel.status.notin_(["cancelled"]),
        )
        appt_result = await self.db.execute(appt_query)
        appointments = appt_result.scalars().all()

        block_query = select(AvailabilityBlock).where(
            or_(
                and_(
                    AvailabilityBlock.professional_id == UUID(professional_id),
                    AvailabilityBlock.start_at >= day_start,
                    AvailabilityBlock.end_at <= day_end,
                ),
                and_(
                    AvailabilityBlock.professional_id.is_(None),
                    AvailabilityBlock.start_at >= day_start,
                    AvailabilityBlock.end_at <= day_end,
                ),
            )
        )
        block_result = await self.db.execute(block_query)
        blocks = block_result.scalars().all()

        slots = []
        current = datetime(day.year, day.month, day.day, opening.hour, opening.minute)
        end_time = datetime(day.year, day.month, day.day, closing.hour, closing.minute)

        while current < end_time:
            slot_end = current + timedelta(minutes=30)

            available = True
            for appt in appointments:
                if current < appt.ends_at and slot_end > appt.scheduled_at:
                    available = False
                    break

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

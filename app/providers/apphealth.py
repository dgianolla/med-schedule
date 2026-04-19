from datetime import date, datetime
from typing import Optional

import httpx
import structlog

from app.providers.base import (
    AppointmentProvider,
    TimeSlot,
    AppointmentRecord,
    CreateAppointmentRequest,
    Appointment,
)
from app.config import settings

logger = structlog.get_logger()


class AppHealthProvider(AppointmentProvider):
    """Proxy to external AppHealth API via httpx."""

    def __init__(self):
        self.base_url = settings.APPHEALTH_BASE_URL
        self.api_key = settings.APPHEALTH_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def _get_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=30.0,
        )

    async def get_available_dates(
        self, professional_id: str, month: int, year: int
    ) -> list[date]:
        logger.info(
            "apphealth.get_available_dates",
            professional_id=professional_id,
            month=month,
            year=year,
        )

        async with await self._get_client() as client:
            response = await client.get(
                "/agenda/datas-disponiveis",
                params={
                    "profissional_id": professional_id,
                    "mes": month,
                    "ano": year,
                },
            )
            response.raise_for_status()
            data = response.json()

        dates = []
        for date_str in data.get("datas", []):
            try:
                dates.append(date.fromisoformat(date_str))
            except ValueError:
                continue

        return dates

    async def get_available_times(
        self, professional_id: str, date: date
    ) -> list[TimeSlot]:
        logger.info(
            "apphealth.get_available_times",
            professional_id=professional_id,
            date=date,
        )

        async with await self._get_client() as client:
            response = await client.get(
                "/agenda/horarios-disponiveis",
                params={
                    "profissional_id": professional_id,
                    "data": date.isoformat(),
                },
            )
            response.raise_for_status()
            data = response.json()

        slots = []
        for slot_data in data.get("horarios", []):
            slots.append(
                TimeSlot(
                    time=slot_data["hora"],
                    available=slot_data.get("disponivel", True),
                )
            )

        return slots

    async def get_agenda(
        self, professional_id: str | None, date_from: date, date_to: date
    ) -> list[AppointmentRecord]:
        logger.info(
            "apphealth.get_agenda",
            professional_id=professional_id,
            date_from=date_from,
            date_to=date_to,
        )

        params = {
            "data_de": date_from.isoformat(),
            "data_ate": date_to.isoformat(),
        }
        if professional_id:
            params["profissional_id"] = professional_id

        async with await self._get_client() as client:
            response = await client.get("/agenda/consultas", params=params)
            response.raise_for_status()
            data = response.json()

        records = []
        for appt_data in data.get("consultas", []):
            records.append(
                AppointmentRecord(
                    id=str(appt_data["id"]),
                    patient_name=appt_data.get("paciente_nome", ""),
                    patient_phone=appt_data.get("paciente_telefone", ""),
                    professional_id=str(appt_data.get("profissional_id", "")),
                    scheduled_at=appt_data["data_hora"],
                    ends_at=appt_data.get("data_hora_fim"),
                    status=appt_data.get("status", "scheduled"),
                    specialty=appt_data.get("especialidade", ""),
                    external_id=str(appt_data["id"]),
                )
            )

        return records

    async def create_appointment(
        self, payload: CreateAppointmentRequest
    ) -> Appointment:
        logger.info("apphealth.create_appointment", payload=payload.model_dump())

        request_data = {
            "paciente_nome": payload.patient_name,
            "paciente_telefone": payload.patient_phone,
            "paciente_email": payload.patient_email,
            "especialidade": payload.specialty,
            "data": payload.date,
            "hora": payload.time,
            "convenio_id": payload.convenio_id,
            "convenio_nome": payload.convenio_name,
        }

        if payload.professional_id:
            request_data["profissional_id"] = payload.professional_id

        async with await self._get_client() as client:
            response = await client.post("/agenda/consultas", json=request_data)
            response.raise_for_status()
            data = response.json()

        return Appointment(
            id=str(data["id"]),
            patient_name=data.get("paciente_nome", payload.patient_name),
            patient_phone=data.get("paciente_telefone", payload.patient_phone),
            patient_email=payload.patient_email,
            professional_id=data.get("profissional_id"),
            professional_name=data.get("profissional_nome"),
            specialty=payload.specialty,
            scheduled_at=data["data_hora"],
            ends_at=data.get("data_hora_fim"),
            duration_minutes=data.get("duracao_minutos", 30),
            status=data.get("status", "scheduled"),
            source=payload.source,
            convenio_id=data.get("convenio_id"),
            convenio_name=data.get("convenio_nome"),
            notes=payload.notes,
            patient_notes=payload.patient_notes,
            external_id=str(data["id"]),
            created_at=data.get("criado_em"),
            updated_at=data.get("atualizado_em"),
        )

    async def cancel_appointment(
        self, appointment_id: str, reason: str | None = None
    ) -> Appointment:
        logger.info("apphealth.cancel_appointment", appointment_id=appointment_id)

        request_data = {}
        if reason:
            request_data["motivo"] = reason

        async with await self._get_client() as client:
            response = await client.delete(
                f"/agenda/consultas/{appointment_id}",
                json=request_data,
            )
            response.raise_for_status()
            data = response.json()

        return Appointment(
            id=str(data["id"]),
            patient_name=data.get("paciente_nome", ""),
            patient_phone=data.get("paciente_telefone", ""),
            professional_id=data.get("profissional_id"),
            specialty=data.get("especialidade", ""),
            scheduled_at=data["data_hora"],
            ends_at=data.get("data_hora_fim"),
            duration_minutes=data.get("duracao_minutos", 30),
            status=data.get("status", "cancelled"),
            source=data.get("origem", "lia"),
            cancelled_at=data.get("cancelado_em"),
            cancellation_reason=data.get("motivo_cancelamento"),
            created_at=data.get("criado_em"),
            updated_at=data.get("atualizado_em"),
        )

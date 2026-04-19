import { apiFetch } from "./client";
import type {
  Appointment,
  AppointmentListItem,
  CreateAppointmentRequest,
  UpdateAppointmentRequest,
} from "@/types/appointment";
import type { PaginatedResponse } from "@/types/api";

export async function listAppointments(filters: {
  date?: string;
  date_from?: string;
  date_to?: string;
  status?: string;
  professional_id?: string;
  patient_phone?: string;
  page?: number;
  per_page?: number;
}) {
  return apiFetch<PaginatedResponse<AppointmentListItem>>("/appointments", {
    params: {
      date: filters.date,
      date_from: filters.date_from,
      date_to: filters.date_to,
      status: filters.status,
      professional_id: filters.professional_id,
      patient_phone: filters.patient_phone,
      page: filters.page?.toString(),
      per_page: filters.per_page?.toString(),
    },
  });
}

export async function getAppointment(id: string) {
  return apiFetch<Appointment>(`/appointments/${id}`);
}

export async function createAppointment(data: CreateAppointmentRequest) {
  return apiFetch<Appointment>("/appointments", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateAppointment(
  id: string,
  data: UpdateAppointmentRequest
) {
  return apiFetch<Appointment>(`/appointments/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function cancelAppointment(id: string, reason?: string) {
  return apiFetch<Appointment>(`/appointments/${id}/cancel`, {
    method: "PUT",
    body: JSON.stringify({ reason }),
  });
}

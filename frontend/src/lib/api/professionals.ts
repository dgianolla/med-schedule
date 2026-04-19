import { apiFetch } from "./client";
import type {
  Professional,
  CreateProfessionalRequest,
  UpdateProfessionalRequest,
  AppointmentType,
  CreateAppointmentTypeRequest,
} from "@/types/professional";

export async function listProfessionals(params?: {
  specialty?: string;
  active?: boolean;
}) {
  return apiFetch<Professional[]>("/professionals", {
    params: {
      specialty: params?.specialty,
      active: params?.active?.toString(),
    },
  });
}

export async function listAvailableProfessionals(params: {
  specialty: string;
  date?: string;
}) {
  return apiFetch<Professional[]>("/professionals/available", {
    params: {
      specialty: params.specialty,
      date: params.date,
    },
  });
}

export async function createProfessional(data: CreateProfessionalRequest) {
  return apiFetch<Professional>("/professionals", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateProfessional(
  id: string,
  data: UpdateProfessionalRequest
) {
  return apiFetch<Professional>(`/professionals/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteProfessional(id: string) {
  return apiFetch<void>(`/professionals/${id}`, { method: "DELETE" });
}

export async function listAppointmentTypes() {
  return apiFetch<AppointmentType[]>("/appointment-types");
}

export async function createAppointmentType(
  data: CreateAppointmentTypeRequest
) {
  return apiFetch<AppointmentType>("/appointment-types", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateAppointmentType(
  id: string,
  data: Partial<CreateAppointmentTypeRequest>
) {
  return apiFetch<AppointmentType>(`/appointment-types/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteAppointmentType(id: string) {
  return apiFetch<void>(`/appointment-types/${id}`, { method: "DELETE" });
}

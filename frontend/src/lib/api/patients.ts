import { apiFetch } from "./client";
import type {
  Patient,
  PatientListItem,
  CreatePatientRequest,
  UpdatePatientRequest,
} from "@/types/patient";
import type { AppointmentListItem } from "@/types/appointment";
import type { PaginatedResponse } from "@/types/api";

export async function listPatients(params?: {
  search?: string;
  page?: number;
  per_page?: number;
}) {
  return apiFetch<PaginatedResponse<PatientListItem>>("/patients", {
    params: {
      search: params?.search,
      page: params?.page?.toString(),
      per_page: params?.per_page?.toString(),
    },
  });
}

export async function getPatient(id: string) {
  return apiFetch<Patient>(`/patients/${id}`);
}

export async function createPatient(data: CreatePatientRequest) {
  return apiFetch<Patient>("/patients", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function upsertPatient(data: CreatePatientRequest) {
  return apiFetch<Patient>("/patients/upsert", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updatePatient(id: string, data: UpdatePatientRequest) {
  return apiFetch<Patient>(`/patients/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deletePatient(id: string) {
  return apiFetch<void>(`/patients/${id}`, { method: "DELETE" });
}

export async function getPatientAppointments(
  id: string,
  params?: { page?: number; per_page?: number }
) {
  return apiFetch<PaginatedResponse<AppointmentListItem>>(
    `/patients/${id}/appointments`,
    {
      params: {
        page: params?.page?.toString(),
        per_page: params?.per_page?.toString(),
      },
    }
  );
}

import { apiFetch } from "./client";
import type {
  Convenio,
  CreateConvenioRequest,
  UpdateConvenioRequest,
} from "@/types/convenio";
import type { PaginatedResponse } from "@/types/api";

export async function listConvenios(params?: {
  active?: boolean;
  search?: string;
  page?: number;
  per_page?: number;
}) {
  return apiFetch<PaginatedResponse<Convenio>>("/convenios", {
    params: {
      active: params?.active?.toString(),
      search: params?.search,
      page: params?.page?.toString(),
      per_page: params?.per_page?.toString(),
    },
  });
}

export async function getConvenio(id: string) {
  return apiFetch<Convenio>(`/convenios/${id}`);
}

export async function createConvenio(data: CreateConvenioRequest) {
  return apiFetch<Convenio>("/convenios", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateConvenio(id: string, data: UpdateConvenioRequest) {
  return apiFetch<Convenio>(`/convenios/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteConvenio(id: string) {
  return apiFetch<void>(`/convenios/${id}`, { method: "DELETE" });
}

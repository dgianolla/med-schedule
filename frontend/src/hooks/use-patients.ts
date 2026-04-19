"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  listPatients,
  getPatient,
  createPatient,
  upsertPatient,
  updatePatient,
  deletePatient,
  getPatientAppointments,
} from "@/lib/api/patients";
import type { CreatePatientRequest, UpdatePatientRequest } from "@/types/patient";

export function usePatients(params?: { search?: string; page?: number; per_page?: number }) {
  return useQuery({
    queryKey: ["patients", params],
    queryFn: () => listPatients(params),
    enabled: params?.search === undefined || params.search.length >= 2,
  });
}

export function usePatient(id: string) {
  return useQuery({
    queryKey: ["patients", id],
    queryFn: () => getPatient(id),
    enabled: !!id,
  });
}

export function useCreatePatient() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreatePatientRequest) => createPatient(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["patients"] }),
  });
}

export function useUpsertPatient() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreatePatientRequest) => upsertPatient(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["patients"] }),
  });
}

export function useUpdatePatient() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdatePatientRequest }) =>
      updatePatient(id, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["patients"] }),
  });
}

export function useDeletePatient() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deletePatient(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["patients"] }),
  });
}

export function usePatientAppointments(id: string, params?: { page?: number; per_page?: number }) {
  return useQuery({
    queryKey: ["patients", id, "appointments", params],
    queryFn: () => getPatientAppointments(id, params),
    enabled: !!id,
  });
}

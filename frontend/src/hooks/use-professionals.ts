"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  listProfessionals,
  listAvailableProfessionals,
  createProfessional,
  updateProfessional,
  deleteProfessional,
  listAppointmentTypes,
  createAppointmentType,
  updateAppointmentType,
  deleteAppointmentType,
} from "@/lib/api/professionals";
import type { CreateProfessionalRequest, UpdateProfessionalRequest, CreateAppointmentTypeRequest } from "@/types/professional";

export function useProfessionals(params?: { specialty?: string; active?: boolean }) {
  return useQuery({
    queryKey: ["professionals", params],
    queryFn: () => listProfessionals(params),
  });
}

export function useAvailableProfessionals(params: { specialty: string; date?: string }) {
  return useQuery({
    queryKey: ["professionals", "available", params],
    queryFn: () => listAvailableProfessionals(params),
    enabled: !!params.specialty,
  });
}

export function useCreateProfessional() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateProfessionalRequest) => createProfessional(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["professionals"] }),
  });
}

export function useUpdateProfessional() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateProfessionalRequest }) =>
      updateProfessional(id, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["professionals"] }),
  });
}

export function useDeleteProfessional() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteProfessional(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["professionals"] }),
  });
}

export function useAppointmentTypes() {
  return useQuery({
    queryKey: ["appointment-types"],
    queryFn: listAppointmentTypes,
  });
}

export function useCreateAppointmentType() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateAppointmentTypeRequest) => createAppointmentType(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["appointment-types"] }),
  });
}

export function useUpdateAppointmentType() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateAppointmentTypeRequest> }) =>
      updateAppointmentType(id, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["appointment-types"] }),
  });
}

export function useDeleteAppointmentType() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteAppointmentType(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["appointment-types"] }),
  });
}

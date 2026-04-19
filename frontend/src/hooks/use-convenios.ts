"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  listConvenios,
  getConvenio,
  createConvenio,
  updateConvenio,
  deleteConvenio,
} from "@/lib/api/convenios";
import type { CreateConvenioRequest, UpdateConvenioRequest } from "@/types/convenio";

export function useConvenios(params?: { active?: boolean; search?: string }) {
  return useQuery({
    queryKey: ["convenios", params],
    queryFn: () => listConvenios(params),
  });
}

export function useConvenio(id: string) {
  return useQuery({
    queryKey: ["convenios", id],
    queryFn: () => getConvenio(id),
    enabled: !!id,
  });
}

export function useCreateConvenio() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateConvenioRequest) => createConvenio(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["convenios"] }),
  });
}

export function useUpdateConvenio() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateConvenioRequest }) =>
      updateConvenio(id, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["convenios"] }),
  });
}

export function useDeleteConvenio() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteConvenio(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["convenios"] }),
  });
}

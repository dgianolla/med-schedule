"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  getSchedulingSettings,
  updateSchedulingSettings,
  type SchedulingSettings,
} from "@/lib/api/settings";

export function useSchedulingSettings() {
  return useQuery({
    queryKey: ["scheduling-settings"],
    queryFn: getSchedulingSettings,
  });
}

export function useUpdateSchedulingSettings() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<SchedulingSettings>) => updateSchedulingSettings(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scheduling-settings"] });
    },
  });
}

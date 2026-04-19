"use client";

import { useQuery } from "@tanstack/react-query";
import { getAvailableDates, getAvailableTimes } from "@/lib/api/availability";

export function useAvailableDates(params: {
  specialty: string;
  month: number;
  year: number;
}) {
  return useQuery({
    queryKey: ["availability", "dates", params],
    queryFn: () => getAvailableDates(params),
    enabled: !!params.specialty && !!params.month && !!params.year,
  });
}

export function useAvailableTimes(params: {
  professional_id: string;
  date: string;
}) {
  return useQuery({
    queryKey: ["availability", "times", params],
    queryFn: () => getAvailableTimes(params),
    enabled: !!params.professional_id && !!params.date,
  });
}

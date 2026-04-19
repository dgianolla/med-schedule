"use client";

import { useQuery } from "@tanstack/react-query";
import { getDailyReport, getWeeklyReport } from "@/lib/api/reports";

export function useDailyReport(date: string) {
  return useQuery({
    queryKey: ["reports", "daily", date],
    queryFn: () => getDailyReport(date),
    enabled: !!date,
  });
}

export function useWeeklyReport(weekStart: string) {
  return useQuery({
    queryKey: ["reports", "weekly", weekStart],
    queryFn: () => getWeeklyReport(weekStart),
    enabled: !!weekStart,
  });
}

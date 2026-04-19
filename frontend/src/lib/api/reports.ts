import { apiFetch } from "./client";

export interface DailyReport {
  date: string;
  total: number;
  by_status: Record<string, number>;
  by_professional: Record<string, number>;
  by_type: Record<string, number>;
}

export interface WeeklyReport {
  week_start: string;
  week_end: string;
  total: number;
  by_status: Record<string, number>;
  by_professional: Record<string, number>;
  by_type: Record<string, number>;
  daily_breakdown: Record<string, number>;
}

export async function getDailyReport(date: string) {
  return apiFetch<DailyReport>("/reports/daily", {
    params: { date },
  });
}

export async function getWeeklyReport(week_start: string) {
  return apiFetch<WeeklyReport>("/reports/weekly", {
    params: { week_start },
  });
}

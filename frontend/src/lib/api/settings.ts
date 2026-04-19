import { apiFetch } from "./client";

export interface SchedulingSettings {
  id?: string;
  weekday_opening: string; // HH:MM
  weekday_closing: string; // HH:MM
  saturday_opening: string; // HH:MM
  saturday_closing: string; // HH:MM
  sunday_closed: boolean;
  holidays_closed: boolean;
  buffer_minutes: number;
  max_advance_days: number;
}

export async function getSchedulingSettings() {
  return apiFetch<SchedulingSettings>("/settings");
}

export async function updateSchedulingSettings(data: Partial<SchedulingSettings>) {
  return apiFetch<SchedulingSettings>("/settings", {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

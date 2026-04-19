import { apiFetch } from "./client";
import type { AvailableDate, TimeSlot } from "@/types/professional";

export async function getAvailableDates(params: {
  specialty: string;
  month: number;
  year: number;
}) {
  return apiFetch<AvailableDate[]>("/availability/dates", {
    params: {
      specialty: params.specialty,
      month: params.month.toString(),
      year: params.year.toString(),
    },
  });
}

export async function getAvailableTimes(params: {
  professional_id: string;
  date: string;
}) {
  return apiFetch<TimeSlot[]>("/availability/times", {
    params: {
      professional_id: params.professional_id,
      date: params.date,
    },
  });
}

export async function getAgenda(params: {
  professional_id?: string;
  date_from: string;
  date_to: string;
}) {
  return apiFetch<unknown[]>("/availability/agenda", {
    params: {
      professional_id: params.professional_id,
      date_from: params.date_from,
      date_to: params.date_to,
    },
  });
}

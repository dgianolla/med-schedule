export interface Professional {
  id: string;
  name: string;
  specialty: string;
  specialty_slug: string;
  external_id?: string | null;
  provider: string;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateProfessionalRequest {
  name: string;
  specialty: string;
  specialty_slug: string;
  external_id?: string;
  provider?: string;
  active?: boolean;
}

export interface UpdateProfessionalRequest {
  name?: string;
  specialty?: string;
  specialty_slug?: string;
  external_id?: string;
  provider?: string;
  active?: boolean;
}

export interface AppointmentType {
  id: string;
  name: string;
  slug: string;
  default_duration_minutes: number;
  description?: string | null;
  active: boolean;
}

export interface CreateAppointmentTypeRequest {
  name: string;
  slug: string;
  default_duration_minutes?: number;
  description?: string;
  active?: boolean;
}

export interface TimeSlot {
  time: string;
  available: boolean;
}

export interface AvailableDate {
  date: string;
  slots_available: number;
}

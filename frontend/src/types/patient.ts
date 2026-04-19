export interface Patient {
  id: string;
  name: string;
  phone: string;
  email?: string | null;
  document?: string | null;
  birth_date?: string | null;
  address?: string | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface PatientListItem {
  id: string;
  name: string;
  phone: string;
  document?: string | null;
  birth_date?: string | null;
}

export interface CreatePatientRequest {
  name: string;
  phone: string;
  email?: string;
  document?: string;
  birth_date?: string;
  address?: string;
  notes?: string;
}

export interface UpdatePatientRequest {
  name?: string;
  phone?: string;
  email?: string;
  document?: string;
  birth_date?: string;
  address?: string;
  notes?: string;
}

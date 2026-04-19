export interface Appointment {
  id: string;
  patient_name: string;
  patient_phone: string;
  patient_email?: string | null;
  patient_id?: string | null;
  professional_id?: string | null;
  professional_name?: string | null;
  appointment_type_id?: string | null;
  specialty: string;
  scheduled_at: string;
  ends_at: string;
  duration_minutes: number;
  status: string;
  source: string;
  convenio_id?: string | null;
  convenio_name?: string | null;
  notes?: string | null;
  patient_notes?: string | null;
  medical_notes?: string | null;
  external_id?: string | null;
  cancelled_at?: string | null;
  cancellation_reason?: string | null;
  created_at: string;
  updated_at: string;
}

export interface AppointmentListItem {
  id: string;
  patient_name: string;
  patient_phone: string;
  specialty: string;
  professional_name?: string | null;
  scheduled_at: string;
  status: string;
  source: string;
}

export interface CreateAppointmentRequest {
  patient_name: string;
  patient_phone: string;
  patient_email?: string;
  patient_id?: string;
  specialty: string;
  professional_id?: string;
  appointment_type_id?: string;
  date: string;
  time: string;
  duration_minutes?: number;
  convenio_id?: string;
  convenio_name?: string;
  source?: string;
  notes?: string;
  patient_notes?: string;
  medical_notes?: string;
}

export interface UpdateAppointmentRequest {
  patient_name?: string;
  patient_phone?: string;
  patient_email?: string;
  patient_id?: string;
  professional_id?: string;
  professional_name?: string;
  specialty?: string;
  scheduled_at?: string;
  ends_at?: string;
  duration_minutes?: number;
  status?: string;
  convenio_id?: string;
  convenio_name?: string;
  notes?: string;
  patient_notes?: string;
  medical_notes?: string;
}

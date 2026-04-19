import { z } from "zod";

export const appointmentSchema = z.object({
  patient_name: z.string().min(1, "Nome é obrigatório"),
  patient_phone: z.string().min(8, "Telefone deve ter pelo menos 8 dígitos"),
  patient_document: z.string().optional(),
  patient_birth_date: z.string().optional(),
  specialty: z.string().min(1, "Especialidade é obrigatória"),
  professional_id: z.string().optional(),
  appointment_type_id: z.string().optional(),
  date: z.string().min(1, "Data é obrigatória"),
  time: z.string().min(1, "Horário é obrigatório"),
  duration_minutes: z.number().min(1, "Duração é obrigatória"),
  payment_type: z.enum(["particular", "convenio"]),
  convenio_id: z.string().optional(),
  notes: z.string().optional(),
});

export type AppointmentFormData = z.infer<typeof appointmentSchema>;

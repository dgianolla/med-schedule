"use client";

import { useState, useEffect, useCallback } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  appointmentSchema,
  type AppointmentFormData,
} from "@/lib/validations/appointment.schema";
import { useCreateAppointment } from "@/hooks/use-appointments";
import { useAvailableProfessionals, useAppointmentTypes } from "@/hooks/use-professionals";
import { useAvailableTimes } from "@/hooks/use-availability";
import { useConvenios } from "@/hooks/use-convenios";
import { useUpsertPatient } from "@/hooks/use-patients";
import { listPatients } from "@/lib/api/patients";
import { todayISO } from "@/lib/utils/date";
import { formatPhone } from "@/lib/utils/phone";
import { formatCPF } from "@/lib/utils/cpf";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { TimeSlotPicker } from "./time-slot-picker";
import { CalendarPlus, Search, Loader2 } from "lucide-react";

interface AppointmentFormProps {
  onDateChange: (date: string) => void;
}

export function AppointmentForm({ onDateChange }: AppointmentFormProps) {
  const [patientSearching, setPatientSearching] = useState(false);
  const [foundPatientId, setFoundPatientId] = useState<string | null>(null);

  const form = useForm<AppointmentFormData>({
    resolver: zodResolver(appointmentSchema),
    defaultValues: {
      patient_name: "",
      patient_phone: "",
      patient_document: "",
      patient_birth_date: "",
      specialty: "",
      professional_id: "",
      appointment_type_id: "",
      date: todayISO(),
      time: "",
      duration_minutes: 30,
      payment_type: "particular",
      convenio_id: "",
      notes: "",
    } as AppointmentFormData,
  });

  const specialty = form.watch("specialty");
  const professionalId = form.watch("professional_id");
  const date = form.watch("date");
  const paymentType = form.watch("payment_type");
  const appointmentTypeId = form.watch("appointment_type_id");

  const { data: professionals } = useAvailableProfessionals({
    specialty,
    date,
  });
  const { data: appointmentTypes } = useAppointmentTypes();
  const { data: timeSlots, isLoading: timeSlotsLoading } = useAvailableTimes({
    professional_id: professionalId || "",
    date,
  });
  const { data: conveniosData } = useConvenios({ active: true });
  const convenios = conveniosData?.items || [];

  const createAppointment = useCreateAppointment();
  const upsertPatient = useUpsertPatient();

  // Update duration when appointment type changes
  useEffect(() => {
    if (appointmentTypeId && appointmentTypes) {
      const type = appointmentTypes.find((t) => t.id === appointmentTypeId);
      if (type) {
        form.setValue("duration_minutes", type.default_duration_minutes);
      }
    }
  }, [appointmentTypeId, appointmentTypes, form]);

  // Notify parent of date changes
  useEffect(() => {
    onDateChange(date);
  }, [date, onDateChange]);

  // Patient phone search with debounce
  const searchPatientByPhone = useCallback(
    async (phone: string) => {
      const digits = phone.replace(/\D/g, "");
      if (digits.length < 10) return;

      setPatientSearching(true);
      try {
        const result = await listPatients({ search: digits, per_page: 1 });
        if (result.items.length > 0) {
          const patient = result.items[0];
          setFoundPatientId(patient.id);
          form.setValue("patient_name", patient.name);
          if (patient.document)
            form.setValue("patient_document", patient.document);
          if (patient.birth_date)
            form.setValue("patient_birth_date", patient.birth_date);
        } else {
          setFoundPatientId(null);
        }
      } catch {
        // ignore search errors
      } finally {
        setPatientSearching(false);
      }
    },
    [form]
  );

  const onSubmit = async (data: AppointmentFormData) => {
    // Upsert patient first
    const patient = await upsertPatient.mutateAsync({
      name: data.patient_name,
      phone: data.patient_phone.replace(/\D/g, ""),
      document: data.patient_document || undefined,
      birth_date: data.patient_birth_date || undefined,
    });

    await createAppointment.mutateAsync({
      patient_name: data.patient_name,
      patient_phone: data.patient_phone.replace(/\D/g, ""),
      patient_id: patient.id,
      specialty: data.specialty,
      professional_id: data.professional_id || undefined,
      appointment_type_id: data.appointment_type_id || undefined,
      date: data.date,
      time: data.time,
      duration_minutes: data.duration_minutes,
      convenio_id:
        data.payment_type === "convenio" ? data.convenio_id || undefined : undefined,
      convenio_name:
        data.payment_type === "convenio"
          ? convenios.find((c) => c.id === data.convenio_id)?.name
          : undefined,
      source: "admin",
      notes: data.notes || undefined,
    });

    form.reset();
    setFoundPatientId(null);
  };

  const isSubmitting = createAppointment.isPending || upsertPatient.isPending;

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
      {/* Seção Paciente */}
      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="text-base font-semibold text-gray-900 mb-4">
          Dados do Paciente
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="col-span-2 sm:col-span-1">
            <Label htmlFor="patient_phone">Telefone</Label>
            <div className="relative mt-1">
              <Input
                id="patient_phone"
                placeholder="(00) 00000-0000"
                {...form.register("patient_phone")}
                onChange={(e) => {
                  const formatted = formatPhone(e.target.value);
                  form.setValue("patient_phone", formatted);
                  searchPatientByPhone(formatted);
                }}
              />
              {patientSearching && (
                <Search className="absolute right-3 top-2.5 h-5 w-5 text-gray-400 animate-pulse" />
              )}
            </div>
            {form.formState.errors.patient_phone && (
              <p className="text-xs text-red-500 mt-1">
                {form.formState.errors.patient_phone.message}
              </p>
            )}
          </div>

          <div className="col-span-2 sm:col-span-1">
            <Label htmlFor="patient_name">Nome</Label>
            <Input
              id="patient_name"
              className="mt-1"
              placeholder="Nome completo"
              {...form.register("patient_name")}
            />
            {form.formState.errors.patient_name && (
              <p className="text-xs text-red-500 mt-1">
                {form.formState.errors.patient_name.message}
              </p>
            )}
          </div>

          <div>
            <Label htmlFor="patient_document">Documento (CPF/RG)</Label>
            <Input
              id="patient_document"
              className="mt-1"
              placeholder="000.000.000-00"
              {...form.register("patient_document")}
              onChange={(e) => {
                form.setValue("patient_document", formatCPF(e.target.value));
              }}
            />
          </div>

          <div>
            <Label htmlFor="patient_birth_date">Data de Nascimento</Label>
            <Input
              id="patient_birth_date"
              type="date"
              className="mt-1"
              {...form.register("patient_birth_date")}
            />
          </div>
        </div>

        {foundPatientId && (
          <p className="text-xs text-green-600 mt-2">
            Paciente encontrado no sistema.
          </p>
        )}
      </div>

      {/* Seção Agendamento */}
      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="text-base font-semibold text-gray-900 mb-4">
          Dados do Agendamento
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="specialty">Especialidade</Label>
            <select
              id="specialty"
              className="mt-1 flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              {...form.register("specialty")}
            >
              <option value="">Selecione...</option>
              {professionals && [
                ...new Set(
                  (professionals || []).map((p) => p.specialty)
                ),
              ].map((spec) => (
                <option key={spec} value={spec}>
                  {spec}
                </option>
              ))}
              {/* Fallback options */}
              <option value="Enfermagem">Enfermagem</option>
              <option value="Cardiologia">Cardiologia</option>
              <option value="Ginecologia">Ginecologia</option>
              <option value="Pediatria">Pediatria</option>
              <option value="Clínico Geral">Clínico Geral</option>
            </select>
            {form.formState.errors.specialty && (
              <p className="text-xs text-red-500 mt-1">
                {form.formState.errors.specialty.message}
              </p>
            )}
          </div>

          <div>
            <Label htmlFor="professional_id">Profissional</Label>
            <select
              id="professional_id"
              className="mt-1 flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              {...form.register("professional_id")}
            >
              <option value="">Selecione...</option>
              {(professionals || []).map((prof) => (
                <option key={prof.id} value={prof.id}>
                  {prof.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <Label htmlFor="appointment_type_id">Procedimento</Label>
            <select
              id="appointment_type_id"
              className="mt-1 flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              {...form.register("appointment_type_id")}
            >
              <option value="">Selecione...</option>
              {(appointmentTypes || []).map((type) => (
                <option key={type.id} value={type.id}>
                  {type.name} ({type.default_duration_minutes}min)
                </option>
              ))}
            </select>
          </div>

          <div>
            <Label htmlFor="duration_minutes">Duração (min)</Label>
            <Input
              id="duration_minutes"
              type="number"
              min={5}
              step={5}
              className="mt-1"
              {...form.register("duration_minutes")}
            />
          </div>

          <div>
            <Label htmlFor="date">Data da Consulta</Label>
            <Input
              id="date"
              type="date"
              className="mt-1"
              {...form.register("date")}
            />
            {form.formState.errors.date && (
              <p className="text-xs text-red-500 mt-1">
                {form.formState.errors.date.message}
              </p>
            )}
          </div>

          <div className="col-span-2">
            <Label>Horário</Label>
            <div className="mt-2">
              <TimeSlotPicker
                slots={timeSlots || []}
                selectedTime={form.watch("time")}
                onSelect={(time) => form.setValue("time", time)}
                isLoading={timeSlotsLoading}
              />
            </div>
            {form.formState.errors.time && (
              <p className="text-xs text-red-500 mt-1">
                {form.formState.errors.time.message}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Seção Tipo / Convênio */}
      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="text-base font-semibold text-gray-900 mb-4">Tipo</h3>
        <div className="flex gap-4 mb-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              value="particular"
              className="text-blue-600 focus:ring-blue-500"
              {...form.register("payment_type")}
            />
            <span className="text-sm font-medium text-gray-700">
              Particular
            </span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              value="convenio"
              className="text-blue-600 focus:ring-blue-500"
              {...form.register("payment_type")}
            />
            <span className="text-sm font-medium text-gray-700">Convênio</span>
          </label>
        </div>

        {paymentType === "convenio" && (
          <div>
            <Label htmlFor="convenio_id">Convênio</Label>
            <select
              id="convenio_id"
              className="mt-1 flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              {...form.register("convenio_id")}
            >
              <option value="">Selecione o convênio...</option>
              {convenios.map((conv) => (
                <option key={conv.id} value={conv.id}>
                  {conv.name}
                  {conv.code ? ` (${conv.code})` : ""}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Observações */}
      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <Label htmlFor="notes">Observações</Label>
        <Textarea
          id="notes"
          className="mt-1"
          placeholder="Observações sobre o agendamento..."
          rows={3}
          {...form.register("notes")}
        />
      </div>

      {/* Erros da API */}
      {createAppointment.isError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-700">
          Erro ao criar agendamento. Verifique os dados e tente novamente.
        </div>
      )}

      {createAppointment.isSuccess && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-sm text-green-700">
          Agendamento realizado com sucesso!
        </div>
      )}

      <Button type="submit" className="w-full" disabled={isSubmitting}>
        {isSubmitting ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Agendando...
          </>
        ) : (
          <>
            <CalendarPlus className="h-4 w-4" />
            Agendar
          </>
        )}
      </Button>
    </form>
  );
}

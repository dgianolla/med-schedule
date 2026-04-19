"use client";

import { use } from "react";
import Link from "next/link";
import { usePatient, usePatientAppointments } from "@/hooks/use-patients";
import { useUpdateAppointment } from "@/hooks/use-appointments";
import { formatDate, formatDateTime } from "@/lib/utils/date";
import { getStatusInfo } from "@/lib/constants/statuses";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  User,
  Phone,
  FileText,
  Calendar,
  Pencil,
  CalendarPlus,
} from "lucide-react";
import { useState } from "react";

export default function ProntuarioPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { data: patient, isLoading: patientLoading } = usePatient(id);
  const { data: appointmentsData, isLoading: appointmentsLoading } =
    usePatientAppointments(id, { per_page: 50 });
  const updateAppointment = useUpdateAppointment();

  const [activeTab, setActiveTab] = useState<"historico" | "dados">(
    "historico"
  );
  const [editingNotes, setEditingNotes] = useState<string | null>(null);
  const [notesValue, setNotesValue] = useState("");

  const appointments = appointmentsData?.items || [];

  if (patientLoading) {
    return (
      <div className="space-y-4">
        <div className="h-32 bg-white border border-gray-200 rounded-lg animate-pulse" />
        <div className="h-64 bg-white border border-gray-200 rounded-lg animate-pulse" />
      </div>
    );
  }

  if (!patient) {
    return (
      <div className="text-center py-12 text-gray-500">
        Paciente não encontrado.
      </div>
    );
  }

  const age = patient.birth_date
    ? Math.floor(
        (Date.now() - new Date(patient.birth_date).getTime()) /
          (365.25 * 24 * 60 * 60 * 1000)
      )
    : null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div className="h-14 w-14 rounded-full bg-blue-100 flex items-center justify-center">
              <User className="h-7 w-7 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                {patient.name}
              </h2>
              <div className="flex items-center gap-4 mt-1 text-sm text-gray-500">
                <span className="flex items-center gap-1">
                  <Phone className="h-3.5 w-3.5" />
                  {patient.phone}
                </span>
                {patient.document && (
                  <span className="flex items-center gap-1">
                    <FileText className="h-3.5 w-3.5" />
                    {patient.document}
                  </span>
                )}
                {patient.birth_date && (
                  <span className="flex items-center gap-1">
                    <Calendar className="h-3.5 w-3.5" />
                    {formatDate(patient.birth_date)}
                    {age !== null && ` (${age} anos)`}
                  </span>
                )}
              </div>
            </div>
          </div>
          <div className="flex gap-2">
            <Link href={`/pacientes/${id}/editar`}>
              <Button variant="outline" size="sm">
                <Pencil className="h-4 w-4" />
                Editar
              </Button>
            </Link>
            <Link href="/agendamento">
              <Button size="sm">
                <CalendarPlus className="h-4 w-4" />
                Novo Agendamento
              </Button>
            </Link>
          </div>
        </div>

        <div className="mt-4">
          <Badge variant="secondary">
            {appointments.length} consulta{appointments.length !== 1 ? "s" : ""}
          </Badge>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-gray-200">
        <button
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === "historico" ? "border-blue-600 text-blue-600" : "border-transparent text-gray-500 hover:text-gray-700"}`}
          onClick={() => setActiveTab("historico")}
        >
          Histórico de Consultas
        </button>
        <button
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === "dados" ? "border-blue-600 text-blue-600" : "border-transparent text-gray-500 hover:text-gray-700"}`}
          onClick={() => setActiveTab("dados")}
        >
          Dados do Paciente
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === "historico" && (
        <div className="space-y-3">
          {appointmentsLoading ? (
            Array.from({ length: 3 }).map((_, i) => (
              <div
                key={i}
                className="h-24 bg-white border border-gray-200 rounded-lg animate-pulse"
              />
            ))
          ) : appointments.length === 0 ? (
            <div className="bg-white border border-gray-200 rounded-lg p-8 text-center text-sm text-gray-500">
              Nenhuma consulta registrada.
            </div>
          ) : (
            appointments.map((appt) => {
              const status = getStatusInfo(appt.status);
              return (
                <div
                  key={appt.id}
                  className="bg-white border border-gray-200 rounded-lg p-4"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold text-gray-900">
                          {formatDateTime(appt.scheduled_at)}
                        </span>
                        <Badge className={status.color}>{status.label}</Badge>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">
                        {appt.specialty}
                        {appt.professional_name &&
                          ` - ${appt.professional_name}`}
                      </p>
                    </div>
                  </div>

                  {/* Medical notes */}
                  <div className="mt-3 border-t border-gray-100 pt-3">
                    {editingNotes === appt.id ? (
                      <div className="space-y-2">
                        <Textarea
                          value={notesValue}
                          onChange={(e) => setNotesValue(e.target.value)}
                          placeholder="Notas da consulta..."
                          rows={3}
                        />
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            onClick={async () => {
                              await updateAppointment.mutateAsync({
                                id: appt.id,
                                data: { medical_notes: notesValue },
                              });
                              setEditingNotes(null);
                            }}
                          >
                            Salvar
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setEditingNotes(null)}
                          >
                            Cancelar
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <button
                        className="text-sm text-gray-400 hover:text-gray-600 w-full text-left"
                        onClick={() => {
                          setEditingNotes(appt.id);
                          setNotesValue("");
                        }}
                      >
                        + Adicionar notas da consulta
                      </button>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      )}

      {activeTab === "dados" && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <dl className="grid grid-cols-2 gap-4">
            <div>
              <dt className="text-sm font-medium text-gray-500">Nome</dt>
              <dd className="text-sm text-gray-900 mt-1">{patient.name}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Telefone</dt>
              <dd className="text-sm text-gray-900 mt-1">{patient.phone}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Email</dt>
              <dd className="text-sm text-gray-900 mt-1">
                {patient.email || "-"}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Documento</dt>
              <dd className="text-sm text-gray-900 mt-1">
                {patient.document || "-"}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Nascimento</dt>
              <dd className="text-sm text-gray-900 mt-1">
                {patient.birth_date ? formatDate(patient.birth_date) : "-"}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Endereço</dt>
              <dd className="text-sm text-gray-900 mt-1">
                {patient.address || "-"}
              </dd>
            </div>
            {patient.notes && (
              <div className="col-span-2">
                <dt className="text-sm font-medium text-gray-500">
                  Observações
                </dt>
                <dd className="text-sm text-gray-900 mt-1">{patient.notes}</dd>
              </div>
            )}
          </dl>
        </div>
      )}
    </div>
  );
}

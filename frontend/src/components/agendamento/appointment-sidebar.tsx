"use client";

import { useAppointments, useCancelAppointment } from "@/hooks/use-appointments";
import { formatTime } from "@/lib/utils/date";
import { getStatusInfo } from "@/lib/constants/statuses";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { X } from "lucide-react";

interface AppointmentSidebarProps {
  date: string;
}

export function AppointmentSidebar({ date }: AppointmentSidebarProps) {
  const { data, isLoading } = useAppointments({ date, per_page: 50 });
  const cancelMutation = useCancelAppointment();

  const appointments = data?.items || [];

  return (
    <div className="bg-white border border-gray-200 rounded-lg h-full">
      <div className="p-4 border-b border-gray-200">
        <h3 className="font-semibold text-gray-900">Agendamentos do dia</h3>
        <p className="text-sm text-gray-500 mt-0.5">
          {appointments.length} agendamento{appointments.length !== 1 ? "s" : ""}
        </p>
      </div>

      <div className="overflow-y-auto max-h-[calc(100vh-300px)]">
        {isLoading ? (
          <div className="p-4 space-y-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-20 rounded-md bg-gray-100 animate-pulse" />
            ))}
          </div>
        ) : appointments.length === 0 ? (
          <div className="p-4 text-center text-sm text-gray-500">
            Nenhum agendamento para esta data.
          </div>
        ) : (
          <ul className="divide-y divide-gray-100">
            {appointments.map((appt) => {
              const status = getStatusInfo(appt.status);
              return (
                <li key={appt.id} className="p-4 hover:bg-gray-50">
                  <div className="flex items-start justify-between">
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {appt.patient_name}
                      </p>
                      <p className="text-sm text-gray-500">
                        {formatTime(appt.scheduled_at)} - {appt.specialty}
                      </p>
                      {appt.professional_name && (
                        <p className="text-xs text-gray-400 mt-0.5">
                          {appt.professional_name}
                        </p>
                      )}
                    </div>
                    <div className="flex items-center gap-2 ml-2">
                      <Badge className={status.color}>{status.label}</Badge>
                      {appt.status === "scheduled" && (
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7 text-gray-400 hover:text-red-600"
                          onClick={() =>
                            cancelMutation.mutate({ id: appt.id })
                          }
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </div>
  );
}

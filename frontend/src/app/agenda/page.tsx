"use client";

import { useState } from "react";
import { format, addDays, startOfWeek, parseISO } from "date-fns";
import { ptBR } from "date-fns/locale";
import { useAppointments } from "@/hooks/use-appointments";
import { useProfessionals } from "@/hooks/use-professionals";
import { formatTime } from "@/lib/utils/date";
import { getStatusInfo } from "@/lib/constants/statuses";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";

export default function AgendaPage() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [view, setView] = useState<"week" | "day">("week");
  const [professionalFilter, setProfessionalFilter] = useState("");

  const { data: professionals } = useProfessionals();

  const weekStart = startOfWeek(currentDate, { weekStartsOn: 1 });
  const dateFrom = format(
    view === "week" ? weekStart : currentDate,
    "yyyy-MM-dd"
  );
  const dateTo = format(
    view === "week" ? addDays(weekStart, 6) : currentDate,
    "yyyy-MM-dd"
  );

  const { data, isLoading } = useAppointments({
    date_from: dateFrom,
    date_to: dateTo,
    professional_id: professionalFilter || undefined,
    per_page: 100,
  });

  const appointments = data?.items || [];

  const days =
    view === "week"
      ? Array.from({ length: 7 }, (_, i) => addDays(weekStart, i))
      : [currentDate];

  const navigate = (dir: number) => {
    setCurrentDate((d) =>
      addDays(d, view === "week" ? dir * 7 : dir)
    );
  };

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex items-center justify-between bg-white border border-gray-200 rounded-lg p-4">
        <div className="flex items-center gap-2">
          <Button variant="outline" size="icon" onClick={() => navigate(-1)}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <span className="text-sm font-medium text-gray-900 min-w-[200px] text-center">
            {view === "week"
              ? `${format(weekStart, "dd MMM", { locale: ptBR })} - ${format(addDays(weekStart, 6), "dd MMM yyyy", { locale: ptBR })}`
              : format(currentDate, "EEEE, dd 'de' MMMM 'de' yyyy", {
                  locale: ptBR,
                })}
          </span>
          <Button variant="outline" size="icon" onClick={() => navigate(1)}>
            <ChevronRight className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentDate(new Date())}
          >
            Hoje
          </Button>
        </div>

        <div className="flex items-center gap-3">
          <select
            className="h-8 rounded-md border border-gray-300 bg-white px-3 text-sm"
            value={professionalFilter}
            onChange={(e) => setProfessionalFilter(e.target.value)}
          >
            <option value="">Todos os profissionais</option>
            {(professionals || []).map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>

          <div className="flex bg-gray-100 rounded-md p-0.5">
            <button
              className={`px-3 py-1 text-xs font-medium rounded ${view === "week" ? "bg-white shadow-sm" : "text-gray-600"}`}
              onClick={() => setView("week")}
            >
              Semana
            </button>
            <button
              className={`px-3 py-1 text-xs font-medium rounded ${view === "day" ? "bg-white shadow-sm" : "text-gray-600"}`}
              onClick={() => setView("day")}
            >
              Dia
            </button>
          </div>
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div
          className={`grid ${view === "week" ? "grid-cols-7" : "grid-cols-1"} divide-x divide-gray-200`}
        >
          {days.map((day) => {
            const dayStr = format(day, "yyyy-MM-dd");
            const dayAppointments = appointments.filter(
              (a) => a.scheduled_at.startsWith(dayStr)
            );
            const isToday = dayStr === format(new Date(), "yyyy-MM-dd");

            return (
              <div key={dayStr} className="min-h-[500px]">
                <div
                  className={`p-3 border-b border-gray-200 text-center ${isToday ? "bg-blue-50" : "bg-gray-50"}`}
                >
                  <p className="text-xs text-gray-500 uppercase">
                    {format(day, "EEE", { locale: ptBR })}
                  </p>
                  <p
                    className={`text-lg font-semibold ${isToday ? "text-blue-600" : "text-gray-900"}`}
                  >
                    {format(day, "dd")}
                  </p>
                </div>
                <div className="p-2 space-y-1.5">
                  {isLoading ? (
                    <div className="space-y-1.5">
                      {Array.from({ length: 3 }).map((_, i) => (
                        <div
                          key={i}
                          className="h-14 rounded bg-gray-100 animate-pulse"
                        />
                      ))}
                    </div>
                  ) : dayAppointments.length === 0 ? (
                    <p className="text-xs text-gray-400 text-center pt-4">
                      Sem agendamentos
                    </p>
                  ) : (
                    dayAppointments
                      .sort((a, b) => a.scheduled_at.localeCompare(b.scheduled_at))
                      .map((appt) => {
                        const status = getStatusInfo(appt.status);
                        return (
                          <div
                            key={appt.id}
                            className="p-2 rounded-md border border-gray-200 hover:bg-gray-50 cursor-pointer transition-colors"
                          >
                            <div className="flex items-center justify-between">
                              <span className="text-xs font-semibold text-blue-600">
                                {formatTime(appt.scheduled_at)}
                              </span>
                              <Badge className={`${status.color} text-[10px] px-1.5 py-0`}>
                                {status.label}
                              </Badge>
                            </div>
                            <p className="text-xs font-medium text-gray-900 truncate mt-0.5">
                              {appt.patient_name}
                            </p>
                            <p className="text-[10px] text-gray-500 truncate">
                              {appt.specialty}
                              {appt.professional_name &&
                                ` - ${appt.professional_name}`}
                            </p>
                          </div>
                        );
                      })
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

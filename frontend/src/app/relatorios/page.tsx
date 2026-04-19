"use client";

import { useState } from "react";
import { format, startOfWeek, addDays } from "date-fns";
import { ptBR } from "date-fns/locale";
import { useDailyReport, useWeeklyReport } from "@/hooks/use-reports";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ChevronLeft, ChevronRight, Calendar, BarChart3 } from "lucide-react";

export default function RelatoriosPage() {
  const [view, setView] = useState<"daily" | "weekly">("daily");
  const [currentDate, setCurrentDate] = useState(new Date());

  const dateStr = format(currentDate, "yyyy-MM-dd");
  const weekStart = startOfWeek(currentDate, { weekStartsOn: 1 });
  const weekStartStr = format(weekStart, "yyyy-MM-dd");

  const { data: dailyReport, isLoading: dailyLoading } = useDailyReport(
    view === "daily" ? dateStr : ""
  );
  const { data: weeklyReport, isLoading: weeklyLoading } = useWeeklyReport(
    view === "weekly" ? weekStartStr : ""
  );

  const isLoading = view === "daily" ? dailyLoading : weeklyLoading;

  const navigateDate = (direction: number) => {
    if (view === "daily") {
      setCurrentDate((prev) => addDays(prev, direction));
    } else {
      setCurrentDate((prev) => addDays(prev, direction * 7));
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "scheduled":
        return "bg-blue-100 text-blue-800";
      case "completed":
        return "bg-green-100 text-green-800";
      case "cancelled":
        return "bg-red-100 text-red-800";
      case "no_show":
        return "bg-gray-100 text-gray-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "scheduled":
        return "Agendado";
      case "completed":
        return "Realizado";
      case "cancelled":
        return "Cancelado";
      case "no_show":
        return "Não compareceu";
      default:
        return status;
    }
  };

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex items-center justify-between bg-white border border-gray-200 rounded-lg p-4">
        <div className="flex items-center gap-2">
          <Button variant="outline" size="icon" onClick={() => navigateDate(-1)}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <span className="text-sm font-medium text-gray-900 min-w-[250px] text-center">
            {view === "daily"
              ? format(currentDate, "EEEE, dd 'de' MMMM 'de' yyyy", { locale: ptBR })
              : `${format(weekStart, "dd MMM", { locale: ptBR })} - ${format(
                  addDays(weekStart, 6),
                  "dd MMM yyyy",
                  { locale: ptBR }
                )}`}
          </span>
          <Button variant="outline" size="icon" onClick={() => navigateDate(1)}>
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

        <div className="flex bg-gray-100 rounded-md p-0.5">
          <button
            className={`px-3 py-1 text-xs font-medium rounded ${
              view === "daily" ? "bg-white shadow-sm" : "text-gray-600"
            }`}
            onClick={() => setView("daily")}
          >
            <Calendar className="h-3 w-3 inline mr-1" />
            Diário
          </button>
          <button
            className={`px-3 py-1 text-xs font-medium rounded ${
              view === "weekly" ? "bg-white shadow-sm" : "text-gray-600"
            }`}
            onClick={() => setView("weekly")}
          >
            <BarChart3 className="h-3 w-3 inline mr-1" />
            Semanal
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <Card key={i} className="p-6">
              <div className="h-20 bg-gray-100 rounded animate-pulse" />
            </Card>
          ))}
        </div>
      ) : view === "daily" && dailyReport ? (
        <div className="space-y-4">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="p-6">
              <p className="text-sm text-gray-500">Total de Agendamentos</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {dailyReport.total}
              </p>
            </Card>
            <Card className="p-6">
              <p className="text-sm text-gray-500">Realizados</p>
              <p className="text-3xl font-bold text-green-600 mt-2">
                {dailyReport.by_status["completed"] || 0}
              </p>
            </Card>
            <Card className="p-6">
              <p className="text-sm text-gray-500">Cancelados</p>
              <p className="text-3xl font-bold text-red-600 mt-2">
                {dailyReport.by_status["cancelled"] || 0}
              </p>
            </Card>
            <Card className="p-6">
              <p className="text-sm text-gray-500">Não compareceram</p>
              <p className="text-3xl font-bold text-gray-600 mt-2">
                {dailyReport.by_status["no_show"] || 0}
              </p>
            </Card>
          </div>

          {/* By Status */}
          <Card className="p-6">
            <h3 className="text-base font-semibold text-gray-900 mb-4">
              Por Status
            </h3>
            <div className="space-y-2">
              {Object.entries(dailyReport.by_status).map(([status, count]) => (
                <div key={status} className="flex items-center justify-between">
                  <Badge className={getStatusColor(status)}>
                    {getStatusLabel(status)}
                  </Badge>
                  <span className="text-sm font-medium text-gray-900">
                    {count}
                  </span>
                </div>
              ))}
            </div>
          </Card>

          {/* By Professional */}
          <Card className="p-6">
            <h3 className="text-base font-semibold text-gray-900 mb-4">
              Por Profissional
            </h3>
            <div className="space-y-2">
              {Object.entries(dailyReport.by_professional)
                .sort((a, b) => (b[1] as number) - (a[1] as number))
                .map(([professional, count]) => (
                  <div key={professional} className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">{professional}</span>
                    <span className="text-sm font-medium text-gray-900">
                      {count}
                    </span>
                  </div>
                ))}
            </div>
          </Card>

          {/* By Type */}
          <Card className="p-6">
            <h3 className="text-base font-semibold text-gray-900 mb-4">
              Por Tipo
            </h3>
            <div className="space-y-2">
              {Object.entries(dailyReport.by_type)
                .sort((a, b) => (b[1] as number) - (a[1] as number))
                .map(([type, count]) => (
                  <div key={type} className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">{type}</span>
                    <span className="text-sm font-medium text-gray-900">
                      {count}
                    </span>
                  </div>
                ))}
            </div>
          </Card>
        </div>
      ) : view === "weekly" && weeklyReport ? (
        <div className="space-y-4">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="p-6">
              <p className="text-sm text-gray-500">Total Semanal</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {weeklyReport.total}
              </p>
            </Card>
            <Card className="p-6">
              <p className="text-sm text-gray-500">Realizados</p>
              <p className="text-3xl font-bold text-green-600 mt-2">
                {weeklyReport.by_status["completed"] || 0}
              </p>
            </Card>
            <Card className="p-6">
              <p className="text-sm text-gray-500">Cancelados</p>
              <p className="text-3xl font-bold text-red-600 mt-2">
                {weeklyReport.by_status["cancelled"] || 0}
              </p>
            </Card>
            <Card className="p-6">
              <p className="text-sm text-gray-500">Não compareceram</p>
              <p className="text-3xl font-bold text-gray-600 mt-2">
                {weeklyReport.by_status["no_show"] || 0}
              </p>
            </Card>
          </div>

          {/* Daily Breakdown */}
          <Card className="p-6">
            <h3 className="text-base font-semibold text-gray-900 mb-4">
              Distribuição Diária
            </h3>
            <div className="space-y-2">
              {Object.entries(weeklyReport.daily_breakdown)
                .sort((a, b) => a[0].localeCompare(b[0]))
                .map(([date, count]) => (
                  <div key={date} className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">
                      {format(new Date(date + "T00:00:00"), "dd/MM/yyyy", {
                        locale: ptBR,
                      })}
                    </span>
                    <span className="text-sm font-medium text-gray-900">
                      {count || 0}
                    </span>
                  </div>
                ))}
            </div>
          </Card>

          {/* By Professional */}
          <Card className="p-6">
            <h3 className="text-base font-semibold text-gray-900 mb-4">
              Por Profissional
            </h3>
            <div className="space-y-2">
              {Object.entries(weeklyReport.by_professional)
                .sort((a, b) => (b[1] as number) - (a[1] as number))
                .map(([professional, count]) => (
                  <div key={professional} className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">{professional}</span>
                    <span className="text-sm font-medium text-gray-900">
                      {count}
                    </span>
                  </div>
                ))}
            </div>
          </Card>

          {/* By Type */}
          <Card className="p-6">
            <h3 className="text-base font-semibold text-gray-900 mb-4">
              Por Tipo
            </h3>
            <div className="space-y-2">
              {Object.entries(weeklyReport.by_type)
                .sort((a, b) => (b[1] as number) - (a[1] as number))
                .map(([type, count]) => (
                  <div key={type} className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">{type}</span>
                    <span className="text-sm font-medium text-gray-900">
                      {count}
                    </span>
                  </div>
                ))}
            </div>
          </Card>
        </div>
      ) : (
        <Card className="p-12 text-center">
          <Calendar className="h-12 w-12 mx-auto mb-4 text-gray-300" />
          <p className="text-gray-500">
            Selecione uma data para visualizar o relatório.
          </p>
        </Card>
      )}
    </div>
  );
}

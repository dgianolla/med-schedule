"use client";

import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { useSchedulingSettings, useUpdateSchedulingSettings } from "@/hooks/use-settings";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loader2, Settings } from "lucide-react";

export default function ConfiguracoesPage() {
  const { data: settings, isLoading } = useSchedulingSettings();
  const update = useUpdateSchedulingSettings();
  const form = useForm({
    defaultValues: {
      weekday_opening: "08:00",
      weekday_closing: "17:00",
      saturday_opening: "08:00",
      saturday_closing: "12:00",
      sunday_closed: true,
      holidays_closed: true,
      buffer_minutes: 0,
      max_advance_days: 60,
    },
  });

  useEffect(() => {
    if (settings) {
      form.reset({
        weekday_opening: settings.weekday_opening.slice(0, 5),
        weekday_closing: settings.weekday_closing.slice(0, 5),
        saturday_opening: settings.saturday_opening.slice(0, 5),
        saturday_closing: settings.saturday_closing.slice(0, 5),
        sunday_closed: settings.sunday_closed,
        holidays_closed: settings.holidays_closed,
        buffer_minutes: settings.buffer_minutes,
        max_advance_days: settings.max_advance_days,
      });
    }
  }, [settings, form]);

  const onSubmit = async (data: any) => {
    await update.mutateAsync(data);
  };

  if (isLoading) {
    return (
      <div className="max-w-3xl">
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="space-y-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-10 bg-gray-100 rounded animate-pulse" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl">
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        {/* Horário de Funcionamento */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Horário de Funcionamento
          </h2>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="weekday_opening">Seg-Sex Abertura</Label>
              <Input
                id="weekday_opening"
                type="time"
                className="mt-1"
                {...form.register("weekday_opening")}
              />
            </div>

            <div>
              <Label htmlFor="weekday_closing">Seg-Sex Fechamento</Label>
              <Input
                id="weekday_closing"
                type="time"
                className="mt-1"
                {...form.register("weekday_closing")}
              />
            </div>

            <div>
              <Label htmlFor="saturday_opening">Sábado Abertura</Label>
              <Input
                id="saturday_opening"
                type="time"
                className="mt-1"
                {...form.register("saturday_opening")}
              />
            </div>

            <div>
              <Label htmlFor="saturday_closing">Sábado Fechamento</Label>
              <Input
                id="saturday_closing"
                type="time"
                className="mt-1"
                {...form.register("saturday_closing")}
              />
            </div>
          </div>

          <div className="mt-4 space-y-3">
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="sunday_closed"
                {...form.register("sunday_closed")}
                className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <Label htmlFor="sunday_closed" className="cursor-pointer">
                Domingo fechado
              </Label>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="holidays_closed"
                {...form.register("holidays_closed")}
                className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <Label htmlFor="holidays_closed" className="cursor-pointer">
                Feriados fechado
              </Label>
            </div>
          </div>
        </div>

        {/* Regras de Agendamento */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Regras de Agendamento
          </h2>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="buffer_minutes">
                Intervalo entre consultas (minutos)
              </Label>
              <Input
                id="buffer_minutes"
                type="number"
                min={0}
                step={5}
                className="mt-1"
                {...form.register("buffer_minutes")}
              />
              <p className="text-xs text-gray-500 mt-1">
                Tempo de espera entre agendamentos
              </p>
            </div>

            <div>
              <Label htmlFor="max_advance_days">
                Máximo de dias antecipados
              </Label>
              <Input
                id="max_advance_days"
                type="number"
                min={1}
                className="mt-1"
                {...form.register("max_advance_days")}
              />
              <p className="text-xs text-gray-500 mt-1">
                Limite de dias para agendar antecipadamente
              </p>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <Button type="submit" disabled={update.isPending}>
            {update.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
            Salvar Configurações
          </Button>
        </div>
      </form>
    </div>
  );
}

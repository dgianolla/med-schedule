"use client";

import { useState } from "react";
import { AppointmentForm } from "@/components/agendamento/appointment-form";
import { AppointmentSidebar } from "@/components/agendamento/appointment-sidebar";
import { todayISO } from "@/lib/utils/date";

export default function AgendamentoPage() {
  const [selectedDate, setSelectedDate] = useState(todayISO());

  return (
    <div className="grid grid-cols-1 lg:grid-cols-[1fr_380px] gap-6">
      <div>
        <AppointmentForm onDateChange={setSelectedDate} />
      </div>
      <div className="hidden lg:block">
        <div className="sticky top-24">
          <AppointmentSidebar date={selectedDate} />
        </div>
      </div>
    </div>
  );
}

"use client";

import { usePathname } from "next/navigation";

const pageTitles: Record<string, string> = {
  "/agendamento": "Novo Agendamento",
  "/agenda": "Agenda",
  "/pacientes": "Pacientes",
  "/convenios": "Convênios",
  "/tipos": "Tipos de Agendamento",
  "/profissionais": "Profissionais",
  "/relatorios": "Relatórios",
  "/configuracoes": "Configurações",
};

export function Header() {
  const pathname = usePathname();

  const baseRoute = "/" + (pathname.split("/")[1] || "");
  const title = pageTitles[baseRoute] || "Med Schedule";

  return (
    <header className="h-16 border-b border-gray-200 bg-white flex items-center px-6">
      <h1 className="text-xl font-semibold text-gray-900">{title}</h1>
    </header>
  );
}

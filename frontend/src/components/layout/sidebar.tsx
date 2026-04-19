"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  CalendarPlus,
  CalendarDays,
  Users,
  Building2,
  ClipboardList,
  Stethoscope,
  BarChart3,
  Settings,
} from "lucide-react";
import { cn } from "@/lib/utils/cn";

const navigation = [
  { name: "Agendamento", href: "/agendamento", icon: CalendarPlus },
  { name: "Agenda", href: "/agenda", icon: CalendarDays },
  { name: "Pacientes", href: "/pacientes", icon: Users },
  { name: "Convênios", href: "/convenios", icon: Building2 },
  { name: "Tipos", href: "/tipos", icon: ClipboardList },
  { name: "Profissionais", href: "/profissionais", icon: Stethoscope },
  { name: "Relatórios", href: "/relatorios", icon: BarChart3 },
  { name: "Configurações", href: "/configuracoes", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 flex flex-col">
      <div className="h-16 flex items-center px-6 border-b border-gray-200">
        <Link href="/agendamento" className="flex items-center gap-2">
          <Stethoscope className="h-7 w-7 text-blue-600" />
          <span className="text-lg font-bold text-gray-900">Atend Já</span>
        </Link>
      </div>

      <nav className="flex-1 overflow-y-auto py-4 px-3">
        <ul className="space-y-1">
          {navigation.map((item) => {
            const isActive =
              pathname === item.href || pathname.startsWith(item.href + "/");
            return (
              <li key={item.name}>
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-blue-50 text-blue-700"
                      : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                  )}
                >
                  <item.icon
                    className={cn(
                      "h-5 w-5 shrink-0",
                      isActive ? "text-blue-600" : "text-gray-400"
                    )}
                  />
                  {item.name}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="border-t border-gray-200 p-4">
        <p className="text-xs text-gray-400 text-center">
          Clínica Atend Já Sorocaba
        </p>
      </div>
    </aside>
  );
}

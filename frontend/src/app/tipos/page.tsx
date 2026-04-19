"use client";

import Link from "next/link";
import { useAppointmentTypes, useDeleteAppointmentType } from "@/hooks/use-professionals";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Plus, ClipboardList } from "lucide-react";

export default function TiposPage() {
  const { data: types, isLoading } = useAppointmentTypes();
  const deleteMutation = useDeleteAppointmentType();

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Link href="/tipos/novo">
          <Button>
            <Plus className="h-4 w-4" />
            Novo Tipo
          </Button>
        </Link>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nome</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Slug</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Duração</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {isLoading ? (
              Array.from({ length: 3 }).map((_, i) => (
                <tr key={i}><td colSpan={5} className="px-6 py-4"><div className="h-5 bg-gray-100 rounded animate-pulse" /></td></tr>
              ))
            ) : !types || types.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center text-sm text-gray-500">
                  <ClipboardList className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                  Nenhum tipo de agendamento cadastrado.
                </td>
              </tr>
            ) : (
              types.map((type) => (
                <tr key={type.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{type.name}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{type.slug}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{type.default_duration_minutes} min</td>
                  <td className="px-6 py-4">
                    <Badge variant={type.active ? "default" : "secondary"}>
                      {type.active ? "Ativo" : "Inativo"}
                    </Badge>
                  </td>
                  <td className="px-6 py-4 text-right space-x-2">
                    <Link href={`/tipos/${type.id}/editar`}>
                      <Button variant="ghost" size="sm">Editar</Button>
                    </Link>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-red-600"
                      onClick={() => deleteMutation.mutate(type.id)}
                    >
                      Desativar
                    </Button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

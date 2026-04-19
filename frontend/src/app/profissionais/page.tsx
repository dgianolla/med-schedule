"use client";

import { useState } from "react";
import Link from "next/link";
import { useProfessionals, useDeleteProfessional } from "@/hooks/use-professionals";
import { SPECIALTIES } from "@/lib/constants/specialties";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Plus, Users } from "lucide-react";

export default function ProfissionaisPage() {
  const [showInactive, setShowInactive] = useState(false);
  const [specialtyFilter, setSpecialtyFilter] = useState("");
  
  const { data, isLoading } = useProfessionals({
    specialty: specialtyFilter || undefined,
    active: showInactive ? undefined : true,
  });
  const deleteMutation = useDeleteProfessional();

  const professionals = data || [];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <select
            className="h-9 rounded-md border border-gray-300 bg-white px-3 text-sm"
            value={specialtyFilter}
            onChange={(e) => setSpecialtyFilter(e.target.value)}
          >
            <option value="">Todas especialidades</option>
            {SPECIALTIES.map((spec) => (
              <option key={spec} value={spec}>
                {spec}
              </option>
            ))}
          </select>
          <label className="flex items-center gap-2 text-sm text-gray-600">
            <input
              type="checkbox"
              checked={showInactive}
              onChange={(e) => setShowInactive(e.target.checked)}
            />
            Mostrar inativos
          </label>
        </div>
        <Link href="/profissionais/novo">
          <Button>
            <Plus className="h-4 w-4" />
            Novo Profissional
          </Button>
        </Link>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nome</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Especialidade</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Provedor</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i}>
                  <td colSpan={5} className="px-6 py-4">
                    <div className="h-5 bg-gray-100 rounded animate-pulse" />
                  </td>
                </tr>
              ))
            ) : professionals.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center text-sm text-gray-500">
                  <Users className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                  Nenhum profissional cadastrado.
                </td>
              </tr>
            ) : (
              professionals.map((prof) => (
                <tr key={prof.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{prof.name}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{prof.specialty}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    <Badge variant={prof.provider === "local" ? "default" : "secondary"}>
                      {prof.provider === "local" ? "Local" : "AppHealth"}
                    </Badge>
                  </td>
                  <td className="px-6 py-4">
                    <Badge variant={prof.active ? "default" : "secondary"}>
                      {prof.active ? "Ativo" : "Inativo"}
                    </Badge>
                  </td>
                  <td className="px-6 py-4 text-right space-x-2">
                    <Link href={`/profissionais/${prof.id}/editar`}>
                      <Button variant="ghost" size="sm">Editar</Button>
                    </Link>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-red-600 hover:text-red-700"
                      onClick={() => {
                        if (confirm(`Deseja desativar o profissional ${prof.name}?`)) {
                          deleteMutation.mutate(prof.id);
                        }
                      }}
                    >
                      Remover
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

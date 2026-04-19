"use client";

import { useState } from "react";
import Link from "next/link";
import { usePatients } from "@/hooks/use-patients";
import { formatDate } from "@/lib/utils/date";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search, Plus, User } from "lucide-react";

export default function PacientesPage() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading } = usePatients({
    search: search.length >= 2 ? search : undefined,
    page,
  });

  const patients = data?.items || [];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="relative w-96">
          <Search className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
          <Input
            placeholder="Buscar por nome, telefone ou documento..."
            className="pl-10"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
          />
        </div>
        <Link href="/pacientes/novo">
          <Button>
            <Plus className="h-4 w-4" />
            Novo Paciente
          </Button>
        </Link>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Nome
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Telefone
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Documento
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Nascimento
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                Ações
              </th>
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
            ) : patients.length === 0 ? (
              <tr>
                <td
                  colSpan={5}
                  className="px-6 py-12 text-center text-sm text-gray-500"
                >
                  <User className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                  {search
                    ? "Nenhum paciente encontrado."
                    : "Nenhum paciente cadastrado."}
                </td>
              </tr>
            ) : (
              patients.map((patient) => (
                <tr key={patient.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">
                    <Link
                      href={`/pacientes/${patient.id}`}
                      className="hover:text-blue-600"
                    >
                      {patient.name}
                    </Link>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {patient.phone}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {patient.document || "-"}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {patient.birth_date
                      ? formatDate(patient.birth_date)
                      : "-"}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Link href={`/pacientes/${patient.id}`}>
                      <Button variant="ghost" size="sm">
                        Prontuário
                      </Button>
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>

        {data && data.pages > 1 && (
          <div className="border-t border-gray-200 px-6 py-3 flex items-center justify-between">
            <p className="text-sm text-gray-500">
              {data.total} paciente{data.total !== 1 ? "s" : ""} encontrado{data.total !== 1 ? "s" : ""}
            </p>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={page === 1}
                onClick={() => setPage((p) => p - 1)}
              >
                Anterior
              </Button>
              <Button
                variant="outline"
                size="sm"
                disabled={page >= data.pages}
                onClick={() => setPage((p) => p + 1)}
              >
                Próxima
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

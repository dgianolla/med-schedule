"use client";

import { useState } from "react";
import Link from "next/link";
import { useConvenios, useDeleteConvenio } from "@/hooks/use-convenios";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Plus, Building2 } from "lucide-react";

export default function ConveniosPage() {
  const [showInactive, setShowInactive] = useState(false);
  const { data, isLoading } = useConvenios({
    active: showInactive ? undefined : true,
  });
  const deleteMutation = useDeleteConvenio();

  const convenios = data?.items || [];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <label className="flex items-center gap-2 text-sm text-gray-600">
          <input
            type="checkbox"
            checked={showInactive}
            onChange={(e) => setShowInactive(e.target.checked)}
          />
          Mostrar inativos
        </label>
        <Link href="/convenios/novo">
          <Button>
            <Plus className="h-4 w-4" />
            Novo Convênio
          </Button>
        </Link>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nome</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Código</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Contato</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {isLoading ? (
              Array.from({ length: 3 }).map((_, i) => (
                <tr key={i}><td colSpan={5} className="px-6 py-4"><div className="h-5 bg-gray-100 rounded animate-pulse" /></td></tr>
              ))
            ) : convenios.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center text-sm text-gray-500">
                  <Building2 className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                  Nenhum convênio cadastrado.
                </td>
              </tr>
            ) : (
              convenios.map((conv) => (
                <tr key={conv.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{conv.name}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{conv.code || "-"}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{conv.contact || "-"}</td>
                  <td className="px-6 py-4">
                    <Badge variant={conv.active ? "default" : "secondary"}>
                      {conv.active ? "Ativo" : "Inativo"}
                    </Badge>
                  </td>
                  <td className="px-6 py-4 text-right space-x-2">
                    <Link href={`/convenios/${conv.id}/editar`}>
                      <Button variant="ghost" size="sm">Editar</Button>
                    </Link>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-red-600 hover:text-red-700"
                      onClick={() => deleteMutation.mutate(conv.id)}
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

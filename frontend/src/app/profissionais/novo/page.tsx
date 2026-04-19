"use client";

import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { useCreateProfessional } from "@/hooks/use-professionals";
import { SPECIALTIES } from "@/lib/constants/specialties";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loader2 } from "lucide-react";

export default function NovoProfissionalPage() {
  const router = useRouter();
  const create = useCreateProfessional();
  const form = useForm({
    defaultValues: {
      name: "",
      specialty: "",
      external_id: "",
      provider: "local",
    },
  });

  const onSubmit = async (data: Record<string, string>) => {
    const specialtySlug = data.specialty
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/\s+/g, "-");

    await create.mutateAsync({
      name: data.name,
      specialty: data.specialty,
      specialty_slug: specialtySlug,
      external_id: data.external_id || undefined,
      provider: data.provider,
    });
    router.push("/profissionais");
  };

  return (
    <div className="max-w-2xl">
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Dados do Profissional
          </h2>

          <div>
            <Label htmlFor="name">Nome *</Label>
            <Input
              id="name"
              className="mt-1"
              {...form.register("name", { required: true })}
              placeholder="Nome completo do profissional"
            />
          </div>

          <div>
            <Label htmlFor="specialty">Especialidade *</Label>
            <select
              id="specialty"
              className="mt-1 flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              {...form.register("specialty", { required: true })}
            >
              <option value="">Selecione...</option>
              {SPECIALTIES.map((spec) => (
                <option key={spec} value={spec}>
                  {spec}
                </option>
              ))}
            </select>
          </div>

          <div>
            <Label htmlFor="provider">Provedor</Label>
            <select
              id="provider"
              className="mt-1 flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              {...form.register("provider")}
            >
              <option value="local">Local (Banco de dados)</option>
              <option value="apphealth">AppHealth</option>
            </select>
          </div>

          <div>
            <Label htmlFor="external_id">ID Externo (AppHealth)</Label>
            <Input
              id="external_id"
              className="mt-1"
              {...form.register("external_id")}
              placeholder="ID no sistema externo (se aplicável)"
            />
            <p className="text-xs text-gray-500 mt-1">
              Identificador no sistema AppHealth (opcional)
            </p>
          </div>
        </div>

        <div className="flex gap-3">
          <Button type="submit" disabled={create.isPending}>
            {create.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
            Salvar
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => router.back()}
          >
            Cancelar
          </Button>
        </div>
      </form>
    </div>
  );
}

"use client";

import { useRouter, useParams } from "next/navigation";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { useProfessionals, useUpdateProfessional } from "@/hooks/use-professionals";
import { SPECIALTIES } from "@/lib/constants/specialties";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Loader2 } from "lucide-react";

export default function EditarProfissionalPage() {
  const router = useRouter();
  const params = useParams();
  const id = params.id as string;

  const { data: professionals, isLoading: loading } = useProfessionals();
  const update = useUpdateProfessional();
  const form = useForm({
    defaultValues: {
      name: "",
      specialty: "",
      external_id: "",
      provider: "local",
      active: true,
    },
  });

  const professional = professionals?.find((p) => p.id === id);

  useEffect(() => {
    if (professional) {
      form.reset({
        name: professional.name,
        specialty: professional.specialty,
        external_id: professional.external_id || "",
        provider: professional.provider,
        active: professional.active,
      });
    }
  }, [professional, form]);

  const onSubmit = async (data: Record<string, any>) => {
    const specialtySlug = data.specialty
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/\s+/g, "-");

    await update.mutateAsync({
      id,
      data: {
        name: data.name,
        specialty: data.specialty,
        specialty_slug: specialtySlug,
        external_id: data.external_id || undefined,
        provider: data.provider,
        active: data.active,
      },
    });
    router.push("/profissionais");
  };

  if (loading) {
    return (
      <div className="max-w-2xl">
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="h-5 bg-gray-100 rounded animate-pulse mb-4" />
          <div className="space-y-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-10 bg-gray-100 rounded animate-pulse" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!professional) {
    return (
      <div className="max-w-2xl">
        <div className="bg-white border border-gray-200 rounded-lg p-6 text-center">
          <p className="text-gray-500">Profissional não encontrado.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl">
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">
              Editar Profissional
            </h2>
            <Badge variant={form.watch("active") ? "default" : "secondary"}>
              {form.watch("active") ? "Ativo" : "Inativo"}
            </Badge>
          </div>

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

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="active"
              {...form.register("active")}
              className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <Label htmlFor="active" className="cursor-pointer">
              Profissional ativo
            </Label>
          </div>
        </div>

        <div className="flex gap-3">
          <Button type="submit" disabled={update.isPending}>
            {update.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
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

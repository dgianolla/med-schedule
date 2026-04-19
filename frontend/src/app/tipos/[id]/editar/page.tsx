"use client";

import { use } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { useAppointmentTypes, useUpdateAppointmentType } from "@/hooks/use-professionals";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Loader2 } from "lucide-react";

export default function EditarTipoPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();
  const { data: types } = useAppointmentTypes();
  const update = useUpdateAppointmentType();

  const type = types?.find((t) => t.id === id);
  const form = useForm({
    values: {
      name: type?.name || "",
      slug: type?.slug || "",
      default_duration_minutes: String(type?.default_duration_minutes || 30),
      description: type?.description || "",
    },
  });

  const onSubmit = async (data: Record<string, string>) => {
    await update.mutateAsync({
      id,
      data: {
        name: data.name,
        slug: data.slug,
        default_duration_minutes: parseInt(data.default_duration_minutes) || 30,
        description: data.description || undefined,
      },
    });
    router.push("/tipos");
  };

  return (
    <div className="max-w-xl">
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
          <div>
            <Label>Nome *</Label>
            <Input className="mt-1" {...form.register("name")} />
          </div>
          <div>
            <Label>Slug</Label>
            <Input className="mt-1" {...form.register("slug")} />
          </div>
          <div>
            <Label>Duração padrão (min)</Label>
            <Input className="mt-1" type="number" min={5} step={5} {...form.register("default_duration_minutes")} />
          </div>
          <div>
            <Label>Descrição</Label>
            <Textarea className="mt-1" rows={3} {...form.register("description")} />
          </div>
        </div>
        <div className="flex gap-3">
          <Button type="submit" disabled={update.isPending}>
            {update.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
            Salvar
          </Button>
          <Button type="button" variant="outline" onClick={() => router.back()}>Cancelar</Button>
        </div>
      </form>
    </div>
  );
}

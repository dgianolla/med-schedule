"use client";

import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { useCreateAppointmentType } from "@/hooks/use-professionals";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Loader2 } from "lucide-react";

export default function NovoTipoPage() {
  const router = useRouter();
  const create = useCreateAppointmentType();
  const form = useForm({
    defaultValues: { name: "", slug: "", default_duration_minutes: "30", description: "" },
  });

  const onSubmit = async (data: Record<string, string>) => {
    await create.mutateAsync({
      name: data.name,
      slug: data.slug || data.name.toLowerCase().replace(/\s+/g, "-"),
      default_duration_minutes: parseInt(data.default_duration_minutes) || 30,
      description: data.description || undefined,
    });
    router.push("/tipos");
  };

  return (
    <div className="max-w-xl">
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
          <div>
            <Label>Nome *</Label>
            <Input className="mt-1" {...form.register("name", { required: true })} />
          </div>
          <div>
            <Label>Slug</Label>
            <Input className="mt-1" placeholder="auto-gerado se vazio" {...form.register("slug")} />
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
          <Button type="submit" disabled={create.isPending}>
            {create.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
            Salvar
          </Button>
          <Button type="button" variant="outline" onClick={() => router.back()}>Cancelar</Button>
        </div>
      </form>
    </div>
  );
}

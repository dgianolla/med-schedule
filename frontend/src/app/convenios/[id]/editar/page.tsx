"use client";

import { use, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { useConvenio, useUpdateConvenio } from "@/hooks/use-convenios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Loader2 } from "lucide-react";

export default function EditarConvenioPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();
  const { data: convenio, isLoading } = useConvenio(id);
  const updateConvenio = useUpdateConvenio();
  const form = useForm({ defaultValues: { name: "", code: "", contact: "", notes: "", active: true } });

  useEffect(() => {
    if (convenio) {
      form.reset({
        name: convenio.name,
        code: convenio.code || "",
        contact: convenio.contact || "",
        notes: convenio.notes || "",
        active: convenio.active,
      });
    }
  }, [convenio, form]);

  if (isLoading) return <div className="h-64 bg-white border rounded-lg animate-pulse" />;

  const onSubmit = async (data: { name: string; code: string; contact: string; notes: string; active: boolean }) => {
    await updateConvenio.mutateAsync({
      id,
      data: {
        name: data.name,
        code: data.code || undefined,
        contact: data.contact || undefined,
        notes: data.notes || undefined,
        active: data.active,
      },
    });
    router.push("/convenios");
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
            <Label>Código</Label>
            <Input className="mt-1" {...form.register("code")} />
          </div>
          <div>
            <Label>Contato</Label>
            <Input className="mt-1" {...form.register("contact")} />
          </div>
          <div>
            <Label>Observações</Label>
            <Textarea className="mt-1" rows={3} {...form.register("notes")} />
          </div>
          <label className="flex items-center gap-2">
            <input type="checkbox" {...form.register("active")} />
            <span className="text-sm">Ativo</span>
          </label>
        </div>
        <div className="flex gap-3">
          <Button type="submit" disabled={updateConvenio.isPending}>
            {updateConvenio.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
            Salvar
          </Button>
          <Button type="button" variant="outline" onClick={() => router.back()}>Cancelar</Button>
        </div>
      </form>
    </div>
  );
}

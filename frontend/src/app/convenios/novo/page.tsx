"use client";

import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { useCreateConvenio } from "@/hooks/use-convenios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Loader2 } from "lucide-react";

export default function NovoConvenioPage() {
  const router = useRouter();
  const createConvenio = useCreateConvenio();
  const form = useForm({ defaultValues: { name: "", code: "", contact: "", notes: "" } });

  const onSubmit = async (data: Record<string, string>) => {
    await createConvenio.mutateAsync({
      name: data.name,
      code: data.code || undefined,
      contact: data.contact || undefined,
      notes: data.notes || undefined,
    });
    router.push("/convenios");
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
        </div>
        <div className="flex gap-3">
          <Button type="submit" disabled={createConvenio.isPending}>
            {createConvenio.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
            Salvar
          </Button>
          <Button type="button" variant="outline" onClick={() => router.back()}>Cancelar</Button>
        </div>
      </form>
    </div>
  );
}

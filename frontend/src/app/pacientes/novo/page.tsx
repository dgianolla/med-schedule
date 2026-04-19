"use client";

import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { useCreatePatient } from "@/hooks/use-patients";
import { formatPhone } from "@/lib/utils/phone";
import { formatCPF } from "@/lib/utils/cpf";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Loader2 } from "lucide-react";

export default function NovoPacientePage() {
  const router = useRouter();
  const createPatient = useCreatePatient();
  const form = useForm({
    defaultValues: {
      name: "",
      phone: "",
      email: "",
      document: "",
      birth_date: "",
      address: "",
      notes: "",
    },
  });

  const onSubmit = async (data: Record<string, string>) => {
    await createPatient.mutateAsync({
      name: data.name,
      phone: data.phone.replace(/\D/g, ""),
      email: data.email || undefined,
      document: data.document || undefined,
      birth_date: data.birth_date || undefined,
      address: data.address || undefined,
      notes: data.notes || undefined,
    });
    router.push("/pacientes");
  };

  return (
    <div className="max-w-2xl">
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <Label>Nome *</Label>
              <Input className="mt-1" {...form.register("name", { required: true })} />
            </div>
            <div>
              <Label>Telefone *</Label>
              <Input
                className="mt-1"
                placeholder="(00) 00000-0000"
                {...form.register("phone", { required: true })}
                onChange={(e) => form.setValue("phone", formatPhone(e.target.value))}
              />
            </div>
            <div>
              <Label>Email</Label>
              <Input className="mt-1" type="email" {...form.register("email")} />
            </div>
            <div>
              <Label>Documento (CPF/RG)</Label>
              <Input
                className="mt-1"
                {...form.register("document")}
                onChange={(e) => form.setValue("document", formatCPF(e.target.value))}
              />
            </div>
            <div>
              <Label>Data de Nascimento</Label>
              <Input className="mt-1" type="date" {...form.register("birth_date")} />
            </div>
            <div className="col-span-2">
              <Label>Endereço</Label>
              <Input className="mt-1" {...form.register("address")} />
            </div>
            <div className="col-span-2">
              <Label>Observações</Label>
              <Textarea className="mt-1" rows={3} {...form.register("notes")} />
            </div>
          </div>
        </div>
        <div className="flex gap-3">
          <Button type="submit" disabled={createPatient.isPending}>
            {createPatient.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
            Salvar
          </Button>
          <Button type="button" variant="outline" onClick={() => router.back()}>
            Cancelar
          </Button>
        </div>
      </form>
    </div>
  );
}

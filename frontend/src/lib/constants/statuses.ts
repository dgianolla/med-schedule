export const APPOINTMENT_STATUSES: Record<
  string,
  { label: string; color: string }
> = {
  scheduled: { label: "Agendado", color: "bg-blue-100 text-blue-800" },
  confirmed: { label: "Confirmado", color: "bg-green-100 text-green-800" },
  in_progress: {
    label: "Em atendimento",
    color: "bg-yellow-100 text-yellow-800",
  },
  completed: { label: "Concluído", color: "bg-gray-100 text-gray-800" },
  cancelled: { label: "Cancelado", color: "bg-red-100 text-red-800" },
  no_show: { label: "Não compareceu", color: "bg-orange-100 text-orange-800" },
};

export function getStatusInfo(status: string) {
  return (
    APPOINTMENT_STATUSES[status] || {
      label: status,
      color: "bg-gray-100 text-gray-800",
    }
  );
}

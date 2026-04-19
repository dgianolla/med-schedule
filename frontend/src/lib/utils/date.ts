import { format, parseISO } from "date-fns";
import { ptBR } from "date-fns/locale";

export function formatDate(dateStr: string) {
  return format(parseISO(dateStr), "dd/MM/yyyy", { locale: ptBR });
}

export function formatDateTime(dateStr: string) {
  return format(parseISO(dateStr), "dd/MM/yyyy 'às' HH:mm", { locale: ptBR });
}

export function formatTime(dateStr: string) {
  return format(parseISO(dateStr), "HH:mm", { locale: ptBR });
}

export function formatDateLong(dateStr: string) {
  return format(parseISO(dateStr), "EEEE, dd 'de' MMMM 'de' yyyy", {
    locale: ptBR,
  });
}

export function todayISO() {
  return format(new Date(), "yyyy-MM-dd");
}

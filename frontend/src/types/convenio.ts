export interface Convenio {
  id: string;
  name: string;
  code?: string | null;
  active: boolean;
  contact?: string | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateConvenioRequest {
  name: string;
  code?: string;
  active?: boolean;
  contact?: string;
  notes?: string;
}

export interface UpdateConvenioRequest {
  name?: string;
  code?: string;
  active?: boolean;
  contact?: string;
  notes?: string;
}

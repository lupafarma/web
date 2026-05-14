export type Medication = {
  cn: string;
  nombre: string;
  aportacion: string;
  huerfano: boolean;
  source_facturacion: string;

  tipo_farmaco: string | null;
  principio_activo: string | null;
  laboratorio: string | null;
  estado: string | null;
  pvp_iva: number | null;
  precio_referencia: number | null;
  menor_precio_agrupacion: number | null;
  agrupacion_code: string | null;
  agrupacion_nombre: string | null;

  pvl_estimated?: number;

  pvl_referencia_boe?: number;
  pvpiva_referencia_boe?: number;
  conjunto_referencia_code?: string;
  conjunto_principio_activo?: string;
  conjunto_via?: string;
  boe_observation?: string;
  source_boe?: string;
};

let cache: Promise<Map<string, Medication>> | null = null;

export function loadMedications(): Promise<Map<string, Medication>> {
  if (!cache) {
    cache = fetch("/medications.json")
      .then((res) => {
        if (!res.ok) {
          throw new Error(`No se pudo cargar /medications.json (HTTP ${res.status})`);
        }
        return res.json() as Promise<Record<string, Medication>>;
      })
      .then((data) => new Map(Object.entries(data)));
  }
  return cache;
}

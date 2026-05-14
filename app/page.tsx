"use client";

import { useEffect, useState } from "react";
import { loadMedications } from "@/lib/medications";

export default function Home() {
  const [count, setCount] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadMedications()
      .then((db) => setCount(db.size))
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : String(e)),
      );
  }, []);

  return (
    <main className="flex flex-1 items-center justify-center">
      <div className="text-center">
        <h1 className="text-3xl font-medium tracking-tight">
          Lupa — en desarrollo
        </h1>
        <p className="mt-4 text-zinc-600">
          {error
            ? `Error: ${error}`
            : count === null
              ? "Cargando…"
              : `Cargadas ${count.toLocaleString("es-ES")} presentaciones`}
        </p>
      </div>
    </main>
  );
}
